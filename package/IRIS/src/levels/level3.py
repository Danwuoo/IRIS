from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from ..utils import clamp01, sigmoid


@dataclass
class ControlSignals:
    uncertainty: float = 0.0
    confidence: float = 0.0
    validity: float = 0.0


@dataclass
class Budget:
    program_beam: int
    rollout_depth: int
    retrieval_k: int
    stop_probability: float


@dataclass
class BudgetControllerConfig:
    beam_logit: float = 0.0
    rollout_logit: float = 0.0
    retrieval_logit: float = 0.0
    stop_logit: float = 0.0
    max_program_beam: int = 4
    max_rollout_depth: int = 3
    max_retrieval_k: int = 4


class BudgetController:
    """
    Learned budget controller placeholder for Level 3.

    TEMPORARY TECHNICAL DEBT: conversion from soft logits to integer budgets
    via rounding/clamping should be replaced with learned budget emitters.
    Removal criterion: budgets are produced directly by learned heads without
    hard min/max clamps.
    """

    def __init__(self, config: BudgetControllerConfig | None = None) -> None:
        self.config = config or BudgetControllerConfig()

    def allocate(self, signals: ControlSignals) -> Budget:
        beam_prob = sigmoid(self.config.beam_logit + signals.uncertainty)
        rollout_prob = sigmoid(self.config.rollout_logit + signals.uncertainty)
        retrieval_prob = sigmoid(self.config.retrieval_logit + signals.validity)
        stop_prob = sigmoid(self.config.stop_logit + (1.0 - signals.confidence))

        program_beam = max(1, int(round(beam_prob * self.config.max_program_beam)))
        rollout_depth = max(1, int(round(rollout_prob * self.config.max_rollout_depth)))
        retrieval_k = max(0, int(round(retrieval_prob * self.config.max_retrieval_k)))

        return Budget(
            program_beam=program_beam,
            rollout_depth=rollout_depth,
            retrieval_k=retrieval_k,
            stop_probability=clamp01(stop_prob),
        )


class NodeExpansionScorer:
    def score(self, candidate_scores: Sequence[float]) -> Sequence[float]:
        return list(candidate_scores)


class TerminationHead:
    def decide(self, budget: Budget) -> float:
        return clamp01(budget.stop_probability)


class Level3:
    """
    Level 3 placeholder: provides budget allocation and termination signals.
    """

    def __init__(self, controller: BudgetController | None = None) -> None:
        self.controller = controller or BudgetController()
        self.expansion_scorer = NodeExpansionScorer()
        self.termination_head = TerminationHead()

    def forward(self, signals: ControlSignals) -> Budget:
        return self.controller.allocate(signals)
