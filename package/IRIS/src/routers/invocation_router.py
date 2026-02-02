from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Mapping, Optional

from ..levels import LEVEL_ORDER, Level
from ..utils import sigmoid


@dataclass
class InvocationGates:
    per_level: Dict[Level, float]

    def to_dict(self) -> Dict[str, float]:
        return {str(level): float(value) for level, value in self.per_level.items()}


@dataclass
class InvocationRouterConfig:
    biases: Dict[Level, float] = field(default_factory=dict)
    signal_weights: Dict[Level, float] = field(default_factory=dict)


class InvocationRouter:
    """
    Learned routing placeholder that emits soft invocation gates per level.
    """

    def __init__(self, config: Optional[InvocationRouterConfig] = None) -> None:
        self.config = config or InvocationRouterConfig()

    def route(self, signals: Optional[Mapping[Level, float]] = None) -> InvocationGates:
        signals = signals or {}
        gates: Dict[Level, float] = {}
        for level in LEVEL_ORDER:
            bias = self.config.biases.get(level, 0.0)
            weight = self.config.signal_weights.get(level, 0.0)
            gates[level] = sigmoid(bias + weight * float(signals.get(level, 0.0)))
        return InvocationGates(per_level=gates)
