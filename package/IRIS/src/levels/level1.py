from __future__ import annotations

from dataclasses import dataclass

from ..schema import StateIR
from ..utils import clamp01, sigmoid


@dataclass
class Level1Output:
    predicted_state: StateIR
    constraint_score: float
    uncertainty: float


@dataclass
class Level1Config:
    constraint_logit: float = 0.0
    uncertainty_logit: float = 0.0


class Level1:
    """
    Level 1 placeholder: produces learned dynamics and uncertainty signals.
    """

    def __init__(self, config: Level1Config | None = None) -> None:
        self.config = config or Level1Config()

    def forward(self, state: StateIR) -> Level1Output:
        constraint = clamp01(sigmoid(self.config.constraint_logit))
        uncertainty = clamp01(sigmoid(self.config.uncertainty_logit))
        state.global_token.metadata.setdefault("level1.constraint_score", constraint)
        state.global_token.metadata.setdefault("level1.uncertainty", uncertainty)
        return Level1Output(predicted_state=state, constraint_score=constraint, uncertainty=uncertainty)
