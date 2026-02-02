from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import torch
from torch import nn

from ..data.arc_agi import MAX_GRID_SIZE, NUM_COLORS
from ..schema import (
    EventToken,
    GlobalToken,
    MacroToken,
    ObjectToken,
    RelationToken,
    StateIR,
    TaskToken,
)
from ..trunk import TorchMambaTrunk


TOKEN_TYPE_IDS: Dict[type, int] = {
    TaskToken: 0,
    GlobalToken: 1,
    ObjectToken: 2,
    RelationToken: 3,
    EventToken: 4,
    MacroToken: 5,
}


@dataclass
class ModelOutput:
    color_logits: torch.Tensor
    height_logits: torch.Tensor
    width_logits: torch.Tensor


class StateIREmbedder(nn.Module):
    def __init__(
        self,
        task_vocab_size: int,
        max_grid_size: int = MAX_GRID_SIZE,
        num_colors: int = NUM_COLORS,
        hidden_size: int = 128,
        max_pairs: int = 16,
    ) -> None:
        super().__init__()
        self.max_grid_size = max_grid_size
        self.type_embed = nn.Embedding(len(TOKEN_TYPE_IDS), hidden_size)
        self.task_embed = nn.Embedding(task_vocab_size, hidden_size)
        self.pair_embed = nn.Embedding(max_pairs, hidden_size)
        self.color_embed = nn.Embedding(num_colors + 1, hidden_size)
        self.x_embed = nn.Embedding(max_grid_size, hidden_size)
        self.y_embed = nn.Embedding(max_grid_size, hidden_size)
        self.pad_embed = nn.Embedding(2, hidden_size)
        self.shape_proj = nn.Linear(2, hidden_size)

    def forward(self, state: StateIR, task_index: int, pair_index: int | None = None) -> torch.Tensor:
        tokens = [state.task, state.global_token] + list(state.objects) + list(state.relations) + list(state.events) + list(state.macros)
        device = self.type_embed.weight.device
        embeddings: list[torch.Tensor] = []

        for token in tokens:
            token_type_id = TOKEN_TYPE_IDS.get(type(token))
            if token_type_id is None:
                raise ValueError(f"Unknown token type: {type(token)}")
            base = self.type_embed(torch.tensor(token_type_id, device=device))
            if isinstance(token, TaskToken):
                task_vec = self.task_embed(torch.tensor(task_index, device=device))
                token_pair_index = pair_index
                if token_pair_index is None:
                    token_pair_index = token.metadata.get("pair_index")
                if token_pair_index is not None:
                    pair_id = max(0, min(int(token_pair_index), self.pair_embed.num_embeddings - 1))
                    pair_vec = self.pair_embed(torch.tensor(pair_id, device=device))
                    embeddings.append(base + task_vec + pair_vec)
                else:
                    embeddings.append(base + task_vec)
                continue
            if isinstance(token, GlobalToken):
                height = float(token.metadata.get("grid_height", 0))
                width = float(token.metadata.get("grid_width", 0))
                shape = torch.tensor([height, width], device=device)
                embeddings.append(base + self.shape_proj(shape))
                continue
            if isinstance(token, ObjectToken):
                x = int(token.metadata.get("x", 0))
                y = int(token.metadata.get("y", 0))
                color = int(token.metadata.get("color", 0))
                pad = int(token.metadata.get("pad", 0))
                obj = (
                    self.color_embed(torch.tensor(color, device=device))
                    + self.x_embed(torch.tensor(x, device=device))
                    + self.y_embed(torch.tensor(y, device=device))
                    + self.pad_embed(torch.tensor(pad, device=device))
                )
                embeddings.append(base + obj)
                continue
            embeddings.append(base)

        return torch.stack(embeddings, dim=0).unsqueeze(0)


class ArcTokenModel(nn.Module):
    def __init__(
        self,
        task_vocab_size: int,
        max_grid_size: int = MAX_GRID_SIZE,
        num_colors: int = NUM_COLORS,
        hidden_size: int = 128,
        depth: int = 2,
        max_pairs: int = 16,
        use_pair_bias: bool = False,
        pair_bias_hidden: int | None = None,
        pair_bias_scale: float = 1.0,
        pair_bias_only: bool = False,
    ) -> None:
        super().__init__()
        self.max_grid_size = max_grid_size
        self.num_colors = num_colors
        self.use_pair_bias = use_pair_bias
        self.pair_bias_scale = float(pair_bias_scale)
        self.pair_bias_only = pair_bias_only
        self.embedder = StateIREmbedder(
            task_vocab_size=task_vocab_size,
            max_grid_size=max_grid_size,
            num_colors=num_colors,
            hidden_size=hidden_size,
            max_pairs=max_pairs,
        )
        self.trunk = TorchMambaTrunk(hidden_size=hidden_size, depth=depth)
        self.color_head = nn.Linear(hidden_size, num_colors)
        self.height_head = nn.Linear(hidden_size, max_grid_size)
        self.width_head = nn.Linear(hidden_size, max_grid_size)
        self.pair_bias_proj = None
        self.pair_shape_proj = None
        if self.use_pair_bias:
            bias_hidden = hidden_size if pair_bias_hidden is None else int(pair_bias_hidden)
            self.pair_bias_proj = nn.Sequential(
                nn.Linear(hidden_size, bias_hidden),
                nn.GELU(),
                nn.Linear(bias_hidden, max_grid_size * max_grid_size * num_colors),
            )
            self.pair_shape_proj = nn.Sequential(
                nn.Linear(hidden_size, bias_hidden),
                nn.GELU(),
                nn.Linear(bias_hidden, max_grid_size * 2),
            )

    def forward(self, state: StateIR, task_index: int, pair_index: int | None = None) -> ModelOutput:
        tokens = self.embedder(state, task_index, pair_index=pair_index)
        tokens = self.trunk(tokens)
        global_token = tokens[:, 1, :]
        object_tokens = tokens[:, 2 :, :]
        expected_len = self.max_grid_size * self.max_grid_size
        if object_tokens.shape[1] != expected_len:
            raise ValueError(f"Expected {expected_len} object tokens, got {object_tokens.shape[1]}")
        color_logits = self.color_head(object_tokens)
        color_logits = color_logits.view(1, self.max_grid_size, self.max_grid_size, self.num_colors)
        pair_index_value = pair_index if pair_index is not None else state.task.metadata.get("pair_index")
        height_logits = self.height_head(global_token)
        width_logits = self.width_head(global_token)

        if self.pair_bias_only and not self.use_pair_bias:
            raise ValueError("pair_bias_only requires use_pair_bias=True")
        if self.pair_bias_only and pair_index_value is None:
            raise ValueError("pair_bias_only requires a valid pair_index")

        if self.use_pair_bias and pair_index_value is not None and self.pair_bias_proj is not None:
            device = color_logits.device
            task_vec = self.embedder.task_embed(torch.tensor(task_index, device=device))
            pair_id = max(0, min(int(pair_index_value), self.embedder.pair_embed.num_embeddings - 1))
            pair_vec = self.embedder.pair_embed(torch.tensor(pair_id, device=device))
            pair_context = task_vec + pair_vec
            bias = self.pair_bias_proj(pair_context)
            bias = bias.view(1, self.max_grid_size, self.max_grid_size, self.num_colors)
            if self.pair_bias_only:
                color_logits = bias * self.pair_bias_scale
            else:
                color_logits = color_logits + bias * self.pair_bias_scale
            if self.pair_shape_proj is not None:
                shape_bias = self.pair_shape_proj(pair_context)
                shape_bias = shape_bias.view(1, self.max_grid_size * 2)
                height_bias = shape_bias[:, : self.max_grid_size]
                width_bias = shape_bias[:, self.max_grid_size :]
                if self.pair_bias_only:
                    height_logits = height_bias * self.pair_bias_scale
                    width_logits = width_bias * self.pair_bias_scale
                else:
                    height_logits = height_logits + height_bias * self.pair_bias_scale
                    width_logits = width_logits + width_bias * self.pair_bias_scale

        return ModelOutput(
            color_logits=color_logits,
            height_logits=height_logits,
            width_logits=width_logits,
        )

    @torch.no_grad()
    def predict(self, state: StateIR, task_index: int, pair_index: int | None = None) -> Tuple[list[list[int]], Tuple[int, int]]:
        output = self.forward(state, task_index, pair_index=pair_index)
        height = int(output.height_logits.argmax(dim=-1).item() + 1)
        width = int(output.width_logits.argmax(dim=-1).item() + 1)
        grid = output.color_logits.argmax(dim=-1).squeeze(0).cpu().tolist()
        height = max(1, min(height, self.max_grid_size))
        width = max(1, min(width, self.max_grid_size))
        cropped = [row[:width] for row in grid[:height]]
        return cropped, (height, width)
