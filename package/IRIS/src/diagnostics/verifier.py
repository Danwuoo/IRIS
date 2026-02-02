from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional

from ..failure_taxonomy import codes as failure_codes
from ..failure_taxonomy import normalize_credit_vector
from ..levels import Level
from ..schema import StateIR


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _signal_value(signals: Mapping[str, float], keys: tuple[str, ...], default: float) -> float:
    for key in keys:
        if key in signals:
            return float(signals[key])
    return default


@dataclass(frozen=True)
class CreditAttribution:
    vector: Dict[Level, float]

    @classmethod
    def uniform(cls) -> "CreditAttribution":
        return cls(normalize_credit_vector({}))

    @classmethod
    def from_dict(cls, payload: Mapping[str, float]) -> "CreditAttribution":
        vector: Dict[Level, float] = {}
        for key, value in payload.items():
            try:
                level = key if isinstance(key, Level) else Level(str(key))
            except ValueError:
                continue
            vector[level] = float(value)
        return cls(normalize_credit_vector(vector))

    def to_dict(self) -> Dict[str, float]:
        return {str(level): weight for level, weight in self.vector.items()}


@dataclass(frozen=True)
class VerifierOutput:
    validity: float
    confidence: float
    failure_logits: Dict[str, float]
    credit: CreditAttribution

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "VerifierOutput":
        raw_validity = float(payload.get("validity_score", payload.get("validity", 0.0)))
        raw_confidence = float(payload.get("confidence", raw_validity))
        raw_failure_logits = payload.get("failure_logits", {}) or {}
        logits = {code: float(raw_failure_logits.get(code, 0.0)) for code in failure_codes()}
        credit_payload = payload.get("credit", {}) or {}
        credit = CreditAttribution.from_dict(credit_payload)
        return cls(
            validity=raw_validity,
            confidence=raw_confidence,
            failure_logits=logits,
            credit=credit,
        )

    def to_dict(self) -> Dict[str, object]:
        validity = _clamp01(self.validity)
        return {
            "validity": validity,
            "validity_score": validity,
            "confidence": _clamp01(self.confidence),
            "failure_logits": dict(self.failure_logits),
            "credit": self.credit.to_dict(),
        }


class PhaseAVerifier:
    """
    Phase A verifier stub.

    This is intentionally light-weight: it emits calibrated fields without
    embedding task-specific heuristics or symbolic rules.
    """

    def evaluate(
        self,
        state: StateIR,
        signals: Optional[Mapping[str, float]] = None,
        failure_logits: Optional[Mapping[str, float]] = None,
        failure_hint: Optional[str] = None,
        credit_hint: Optional[Mapping[Level, float]] = None,
    ) -> VerifierOutput:
        _ = state  # placeholder to emphasize dependence on State IR
        signals = signals or {}

        validity = _clamp01(
            _signal_value(
                signals,
                ("validity_score", "validity", "task.validity_score"),
                0.0,
            )
        )
        confidence = _clamp01(
            _signal_value(
                signals,
                ("confidence", "task.confidence"),
                validity,
            )
        )

        logits: Dict[str, float] = {code: 0.0 for code in failure_codes()}
        if failure_logits:
            for code, value in failure_logits.items():
                if code not in logits:
                    raise ValueError(f"Unknown failure code '{code}'")
                logits[code] = float(value)
        elif failure_hint:
            if failure_hint not in logits:
                raise ValueError(f"Unknown failure hint '{failure_hint}'")
            logits[failure_hint] = 1.0

        credit = CreditAttribution(normalize_credit_vector(credit_hint or {}))
        return VerifierOutput(
            validity=validity,
            confidence=confidence,
            failure_logits=logits,
            credit=credit,
        )
