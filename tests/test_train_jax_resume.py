from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("jax")
pytest.importorskip("flax")
pytest.importorskip("optax")

from iris.train import ToyTrainConfig, run_toy_training
from iris.train.journal import load_journal


def test_pre_commit_crash_resume_keeps_single_applied_event(tmp_path: Path) -> None:
    output_dir = tmp_path / "toy_resume_jax"

    crash_config = ToyTrainConfig(
        output_dir=output_dir,
        segments=1,
        micro_steps=2,
        device="cpu",
        backend="jax",
        strict_jax=True,
        level_impl="mounted",
        crash_point="pre_commit",
        crash_segment=0,
    )
    with pytest.raises(RuntimeError):
        run_toy_training(crash_config)

    resume_config = ToyTrainConfig(
        output_dir=output_dir,
        segments=1,
        micro_steps=2,
        device="cpu",
        backend="jax",
        strict_jax=True,
        level_impl="mounted",
    )
    summary = run_toy_training(resume_config)
    assert summary["status"] == "Done"

    events = load_journal(output_dir / "segment_journal.jsonl")
    applied_segment0 = [
        event
        for event in events
        if int(event.get("segment_id", -1)) == 0 and event.get("status") == "APPLIED"
    ]
    assert len(applied_segment0) == 1
