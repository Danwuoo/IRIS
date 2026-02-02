from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class ResumeConsistencyThresholds:
    validity_mean_delta: float
    confidence_mean_delta: float
    credit_l1_delta: float
    min_overlap_segments: int = 1


DEFAULT_RESUME_THRESHOLDS = ResumeConsistencyThresholds(
    validity_mean_delta=0.1,
    confidence_mean_delta=0.1,
    credit_l1_delta=0.2,
    min_overlap_segments=1,
)

PHASE_RESUME_THRESHOLDS: Dict[str, ResumeConsistencyThresholds] = {
    "A": DEFAULT_RESUME_THRESHOLDS,
    "B": DEFAULT_RESUME_THRESHOLDS,
    "C": DEFAULT_RESUME_THRESHOLDS,
    "D": DEFAULT_RESUME_THRESHOLDS,
    "E": DEFAULT_RESUME_THRESHOLDS,
}


def get_resume_consistency_thresholds(phase: str) -> ResumeConsistencyThresholds:
    return PHASE_RESUME_THRESHOLDS.get(str(phase).upper(), DEFAULT_RESUME_THRESHOLDS)
