from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence

from ..schema import StateIR
from ..utils import softmax


@dataclass
class FusionResult:
    state: StateIR
    weights: List[float]


class FusionRouter:
    """
    Minimal fusion router that records fusion weights without schema changes.
    """

    def fuse(
        self,
        base_state: StateIR,
        candidates: Sequence[StateIR],
        weights: Optional[Sequence[float]] = None,
    ) -> FusionResult:
        if not candidates:
            return FusionResult(state=base_state, weights=[])

        if weights is None:
            weights = softmax([0.0 for _ in candidates])
        else:
            weights = softmax(weights)

        # Placeholder: keep base_state and annotate fusion metadata.
        base_state.global_token.metadata.setdefault("fusion_weights", list(weights))
        base_state.global_token.metadata.setdefault("fusion_candidates", len(candidates))
        return FusionResult(state=base_state, weights=list(weights))
