from __future__ import annotations

from enum import Enum
from typing import List


class Level(str, Enum):
    """Canonical Level identifiers (L0-L6)."""

    L0 = "L0"
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    L4 = "L4"
    L5 = "L5"
    L6 = "L6"

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.value


LEVEL_ORDER: List[Level] = [
    Level.L0,
    Level.L1,
    Level.L2,
    Level.L3,
    Level.L4,
    Level.L5,
    Level.L6,
]

__all__ = ["Level", "LEVEL_ORDER"]
