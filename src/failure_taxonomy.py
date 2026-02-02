from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Mapping

from .levels import Level, LEVEL_ORDER


@dataclass(frozen=True)
class FailureCategory:
    code: str
    level: Level
    description: str


# Canonical failure categories (metrics.md / regression.md).
FAILURE_CATEGORIES: Dict[str, FailureCategory] = {
    "F_REP": FailureCategory(
        code="F_REP",
        level=Level.L0,
        description="Representation failure (objects/relations/events wrong or missing)",
    ),
    "F_PROC": FailureCategory(
        code="F_PROC",
        level=Level.L2,
        description="Procedural failure (program induction/execution mis-specified)",
    ),
    "F_SEARCH": FailureCategory(
        code="F_SEARCH",
        level=Level.L3,
        description="Search/budget failure (termination/budget misallocated)",
    ),
    "F_MEM": FailureCategory(
        code="F_MEM",
        level=Level.L4,
        description="Memory failure (retrieval/write/consolidation issues)",
    ),
    "F_ABS": FailureCategory(
        code="F_ABS",
        level=Level.L5,
        description="Abstraction failure (macro granularity misuse)",
    ),
    "F_EVAL": FailureCategory(
        code="F_EVAL",
        level=Level.L6,
        description="Evaluation/calibration failure (verifier/credit routing)",
    ),
}


def codes() -> Iterable[str]:
    return FAILURE_CATEGORIES.keys()


def resolve(code: str) -> FailureCategory:
    try:
        return FAILURE_CATEGORIES[code]
    except KeyError as exc:
        raise ValueError(f"Unknown failure code '{code}'") from exc


def normalize_credit_vector(raw: Mapping[object, float]) -> Dict[Level, float]:
    """
    Normalize a credit vector over Levels, falling back to uniform if degenerate.
    """
    scores: Dict[Level, float] = {level: 0.0 for level in LEVEL_ORDER}
    for key, value in raw.items():
        try:
            level = key if isinstance(key, Level) else Level(str(key))
        except ValueError:
            continue
        scores[level] = max(0.0, float(value))

    total = sum(scores.values())
    if total <= 0.0:
        uniform = 1.0 / len(LEVEL_ORDER)
        return {level: uniform for level in LEVEL_ORDER}

    return {level: score / total for level, score in scores.items()}
