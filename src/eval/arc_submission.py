from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List

from ..data.arc_agi import ArcPair


@dataclass(frozen=True)
class SubmissionConfig:
    model_name: str = "iris-phase-c"
    provider: str = "local"
    test_id: str = "iris-phase-c"


def write_submission(
    predictions: Iterable[tuple[ArcPair, List[List[int]]]],
    output_dir: str,
    config: SubmissionConfig | None = None,
) -> None:
    config = config or SubmissionConfig()
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)

    grouped: Dict[str, List[tuple[ArcPair, List[List[int]]]]] = {}
    for pair, grid in predictions:
        grouped.setdefault(pair.task_id, []).append((pair, grid))

    for task_id, items in grouped.items():
        payload: List[Dict[str, object]] = []
        for pair, grid in items:
            payload.append(
                {
                    "attempt_1": _attempt_payload(
                        answer=grid,
                        task_id=task_id,
                        pair_index=pair.pair_index,
                        config=config,
                    )
                }
            )
        with (root / f"{task_id}.json").open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)


def _attempt_payload(
    answer: List[List[int]],
    task_id: str,
    pair_index: int,
    config: SubmissionConfig,
) -> Dict[str, object]:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "answer": answer,
        "metadata": {
            "model": config.model_name,
            "provider": config.provider,
            "start_timestamp": now,
            "end_timestamp": now,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "user", "content": "ARC task prompt omitted"},
                },
                {
                    "index": 1,
                    "message": {"role": "assistant", "content": "Predicted grid output"},
                },
            ],
            "reasoning_summary": None,
            "kwargs": {},
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "completion_tokens_details": {
                    "reasoning_tokens": 0,
                    "accepted_prediction_tokens": 0,
                    "rejected_prediction_tokens": 0,
                },
            },
            "cost": {
                "prompt_cost": 0.0,
                "completion_cost": 0.0,
                "reasoning_cost": None,
                "total_cost": 0.0,
            },
            "task_id": task_id,
            "pair_index": pair_index,
            "test_id": config.test_id,
        },
        "correct": None,
    }
