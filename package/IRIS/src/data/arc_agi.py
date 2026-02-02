from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

from ..schema import GlobalToken, ObjectToken, StateIR, TaskToken

MAX_GRID_SIZE = 30
NUM_COLORS = 10


@dataclass(frozen=True)
class ArcPair:
    task_id: str
    pair_index: int
    pair_slot: int
    split: str
    input_grid: List[List[int]]
    output_grid: List[List[int]]


@dataclass(frozen=True)
class ArcTask:
    task_id: str
    train: List[ArcPair]
    test: List[ArcPair]


@dataclass(frozen=True)
class TaskVocab:
    index: Dict[str, int]

    def __len__(self) -> int:
        return len(self.index)

    def __getitem__(self, task_id: str) -> int:
        return self.index[task_id]


def _load_task(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_tasks(data_dir: str) -> List[ArcTask]:
    root = Path(data_dir)
    tasks: List[ArcTask] = []
    for path in sorted(root.glob("*.json")):
        task_id = path.stem
        payload = _load_task(path)
        train_pairs = _pairs_from_payload(task_id, payload.get("train", []), split="train", offset=0)
        test_pairs = _pairs_from_payload(
            task_id,
            payload.get("test", []),
            split="test",
            offset=len(train_pairs),
        )
        tasks.append(ArcTask(task_id=task_id, train=train_pairs, test=test_pairs))
    return tasks


def build_task_vocab(tasks: Sequence[ArcTask]) -> TaskVocab:
    index = {task.task_id: idx for idx, task in enumerate(tasks)}
    return TaskVocab(index=index)


def iter_pairs(
    tasks: Sequence[ArcTask],
    include_train: bool = True,
    include_test: bool = False,
) -> List[ArcPair]:
    pairs: List[ArcPair] = []
    for task in tasks:
        if include_train:
            pairs.extend(task.train)
        if include_test:
            pairs.extend(task.test)
    return pairs


def pad_grid(grid: Sequence[Sequence[int]], max_size: int = MAX_GRID_SIZE) -> Tuple[List[List[int]], Tuple[int, int]]:
    height = len(grid)
    width = len(grid[0]) if height else 0
    padded = [[0 for _ in range(max_size)] for _ in range(max_size)]
    for y in range(min(height, max_size)):
        for x in range(min(width, max_size)):
            padded[y][x] = int(grid[y][x])
    return padded, (height, width)


def build_state_ir_from_grid(
    grid: Sequence[Sequence[int]],
    task_id: str,
    max_size: int = MAX_GRID_SIZE,
    pair_index: int | None = None,
) -> StateIR:
    height = len(grid)
    width = len(grid[0]) if height else 0
    task_metadata = {"task_id": task_id}
    if pair_index is not None:
        task_metadata["pair_index"] = int(pair_index)
    task_token = TaskToken(metadata=task_metadata)
    global_token = GlobalToken(metadata={"grid_height": height, "grid_width": width, "max_size": max_size})
    objects: List[ObjectToken] = []
    for y in range(max_size):
        for x in range(max_size):
            if y < height and x < width:
                color = int(grid[y][x])
                pad = 0
            else:
                color = 0
                pad = 1
            objects.append(ObjectToken(metadata={"x": x, "y": y, "color": color, "pad": pad}))
    return StateIR(task=task_token, global_token=global_token, objects=objects)


def _pairs_from_payload(task_id: str, payload: Iterable[Dict[str, Any]], split: str, offset: int) -> List[ArcPair]:
    pairs: List[ArcPair] = []
    for idx, pair in enumerate(payload):
        input_grid = pair.get("input", [])
        output_grid = pair.get("output", [])
        pairs.append(
            ArcPair(
                task_id=task_id,
                pair_index=idx,
                pair_slot=offset + idx,
                split=split,
                input_grid=input_grid,
                output_grid=output_grid,
            )
        )
    return pairs
