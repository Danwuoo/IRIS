from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple

import torch
from torch import nn

from ..data.arc_agi import ArcPair, TaskVocab, build_state_ir_from_grid, pad_grid
from ..modeling import ArcTokenModel


@dataclass
class TrainingConfig:
    epochs: int = 5
    learning_rate: float = 1e-3
    shape_loss_weight: float = 0.1
    device: str = "cpu"


@dataclass
class TrainingMetrics:
    loss: float
    accuracy: float


class PhaseCTrainer:
    def __init__(self, model: ArcTokenModel, config: TrainingConfig) -> None:
        self.model = model.to(config.device)
        self.config = config
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=config.learning_rate)
        self.loss_fn = nn.CrossEntropyLoss(ignore_index=-1)

    def train(self, pairs: Sequence[ArcPair], vocab: TaskVocab) -> List[TrainingMetrics]:
        history: List[TrainingMetrics] = []
        for _ in range(self.config.epochs):
            metrics = self._run_epoch(pairs, vocab, train=True)
            history.append(metrics)
            if metrics.accuracy >= 1.0:
                break
        return history

    def evaluate(self, pairs: Sequence[ArcPair], vocab: TaskVocab) -> TrainingMetrics:
        return self._run_epoch(pairs, vocab, train=False)

    def _run_epoch(self, pairs: Sequence[ArcPair], vocab: TaskVocab, train: bool) -> TrainingMetrics:
        if train:
            self.model.train()
        else:
            self.model.eval()

        total_loss = 0.0
        total_correct = 0
        total_samples = 0

        for pair in pairs:
            state = build_state_ir_from_grid(
                pair.input_grid,
                task_id=pair.task_id,
                max_size=self.model.max_grid_size,
                pair_index=pair.pair_slot,
            )
            padded, (height, width) = pad_grid(pair.output_grid, max_size=self.model.max_grid_size)
            height = max(1, min(height, len(padded)))
            width = max(1, min(width, len(padded[0]) if padded else 1))
            target = torch.tensor(padded, device=self.config.device)
            target_mask = torch.zeros_like(target, dtype=torch.bool)
            target_mask[:height, :width] = True
            target_flat = target.clone()
            target_flat[~target_mask] = -1

            task_index = vocab[pair.task_id]
            output = self.model(state, task_index, pair_index=pair.pair_slot)
            logits = output.color_logits.squeeze(0)
            loss_grid = self.loss_fn(logits.view(-1, logits.shape[-1]), target_flat.view(-1))

            shape_h_target = torch.tensor([height - 1], device=self.config.device)
            shape_w_target = torch.tensor([width - 1], device=self.config.device)
            loss_shape = self.loss_fn(output.height_logits, shape_h_target) + self.loss_fn(output.width_logits, shape_w_target)

            loss = loss_grid + self.config.shape_loss_weight * loss_shape

            if train:
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

            total_loss += float(loss.item())
            pred_grid, _ = self.model.predict(state, task_index, pair_index=pair.pair_slot)
            if pred_grid == pair.output_grid:
                total_correct += 1
            total_samples += 1

        avg_loss = total_loss / max(1, total_samples)
        accuracy = total_correct / max(1, total_samples)
        return TrainingMetrics(loss=avg_loss, accuracy=accuracy)


@torch.no_grad()
def predict_pairs(model: ArcTokenModel, pairs: Sequence[ArcPair], vocab: TaskVocab) -> List[Tuple[ArcPair, List[List[int]]]]:
    model.eval()
    predictions: List[Tuple[ArcPair, List[List[int]]]] = []
    for pair in pairs:
        state = build_state_ir_from_grid(
            pair.input_grid,
            task_id=pair.task_id,
            max_size=model.max_grid_size,
            pair_index=pair.pair_slot,
        )
        task_index = vocab[pair.task_id]
        pred_grid, _ = model.predict(state, task_index, pair_index=pair.pair_slot)
        predictions.append((pair, pred_grid))
    return predictions
