from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Sequence

from ..utils import softmax


@dataclass
class CandidateSelection:
    scores: List[float]
    weights: List[float]
    selected_index: int


class OutputRouter:
    """
    Output router that performs soft selection over candidate scores.
    """

    def __init__(self, temperature: float = 1.0, rng: random.Random | None = None) -> None:
        self.temperature = max(1e-6, float(temperature))
        self.rng = rng or random.Random()

    def select(self, scores: Sequence[float]) -> CandidateSelection:
        scores = [float(score) for score in scores]
        if not scores:
            return CandidateSelection(scores=[], weights=[], selected_index=-1)

        scaled = [score / self.temperature for score in scores]
        weights = softmax(scaled)
        selected_index = self._sample_index(weights)
        return CandidateSelection(scores=scores, weights=weights, selected_index=selected_index)

    def _sample_index(self, weights: Sequence[float]) -> int:
        threshold = self.rng.random()
        cumulative = 0.0
        for index, weight in enumerate(weights):
            cumulative += weight
            if threshold <= cumulative:
                return index
        return max(0, len(weights) - 1)
