from __future__ import annotations

import math
from typing import Iterable, List


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-float(value)))


def softmax(values: Iterable[float]) -> List[float]:
    values = [float(value) for value in values]
    if not values:
        return []
    max_value = max(values)
    exp_values = [math.exp(value - max_value) for value in values]
    total = sum(exp_values)
    if total <= 0.0:
        return [1.0 / len(values) for _ in values]
    return [value / total for value in exp_values]
