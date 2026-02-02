from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Mapping, Optional

from ..diagnostics import CreditAttribution, VerifierOutput
from ..failure_taxonomy import codes as failure_codes
from ..failure_taxonomy import normalize_credit_vector
from ..failure_taxonomy import resolve as resolve_failure
from ..levels import LEVEL_ORDER, Level
from ..schema import StateIR
from ..utils import clamp01, sigmoid, softmax


@dataclass
class Level6Config:
    validity_logit: float = 0.0
    confidence_logit: float = 0.0
    credit_bias: Dict[Level, float] = field(default_factory=dict)


class CreditRouter:
    def __init__(self, bias: Optional[Mapping[Level, float]] = None) -> None:
        self.bias = dict(bias or {})

    def route(self, failure_logits: Optional[Mapping[str, float]] = None) -> CreditAttribution:
        logits = {level: float(self.bias.get(level, 0.0)) for level in LEVEL_ORDER}
        if failure_logits:
            for code, value in failure_logits.items():
                if code not in failure_codes():
                    continue
                level = resolve_failure(code).level
                logits[level] += float(value)
        weights = softmax(logits.values())
        credit = {level: weight for level, weight in zip(LEVEL_ORDER, weights)}
        return CreditAttribution(normalize_credit_vector(credit))


class Level6:
    """
    Level 6 placeholder: verifier, confidence, and credit routing.
    """

    def __init__(self, config: Optional[Level6Config] = None) -> None:
        self.config = config or Level6Config()
        self.credit_router = CreditRouter(self.config.credit_bias)

    def verify(
        self,
        state: StateIR,
        failure_logits: Optional[Mapping[str, float]] = None,
    ) -> VerifierOutput:
        validity = clamp01(sigmoid(self.config.validity_logit))
        confidence = clamp01(sigmoid(self.config.confidence_logit))
        logits = {code: 0.0 for code in failure_codes()}
        if failure_logits:
            for code, value in failure_logits.items():
                if code in logits:
                    logits[code] = float(value)
        credit = self.credit_router.route(logits)
        state.global_token.metadata.setdefault("eval.confidence", confidence)
        return VerifierOutput(
            validity=validity,
            confidence=confidence,
            failure_logits=logits,
            credit=credit,
        )
