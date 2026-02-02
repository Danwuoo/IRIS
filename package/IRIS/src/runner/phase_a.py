from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping, Optional

from ..diagnostics import PhaseAVerifier, TraceEntry, TraceRecorder
from ..levels import Level
from ..schema import StateIR


@dataclass
class PhaseARunContext:
    verifier: PhaseAVerifier
    recorder: TraceRecorder

    @classmethod
    def default(cls, trace_path: Optional[str] = None) -> "PhaseARunContext":
        return cls(
            verifier=PhaseAVerifier(),
            recorder=TraceRecorder(phase="A", output_path=trace_path),
        )

    def run(
        self,
        task_id: str,
        state: StateIR,
        signals: Optional[Mapping[str, float]] = None,
        failure_logits: Optional[Mapping[str, float]] = None,
        failure_hint: Optional[str] = None,
        credit_hint: Optional[Mapping[Level, float]] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> TraceEntry:
        verifier_output = self.verifier.evaluate(
            state=state,
            signals=signals,
            failure_logits=failure_logits,
            failure_hint=failure_hint,
            credit_hint=credit_hint,
        )
        return self.recorder.record(
            task_id=task_id,
            state=state,
            verifier_output=verifier_output,
            metadata=metadata,
        )


def run_phase_a(
    task_id: str,
    state: StateIR,
    signals: Optional[Mapping[str, float]] = None,
    failure_logits: Optional[Mapping[str, float]] = None,
    failure_hint: Optional[str] = None,
    credit_hint: Optional[Mapping[Level, float]] = None,
    metadata: Optional[Dict[str, str]] = None,
    trace_path: Optional[str] = None,
) -> TraceEntry:
    ctx = PhaseARunContext.default(trace_path=trace_path)
    return ctx.run(
        task_id=task_id,
        state=state,
        signals=signals,
        failure_logits=failure_logits,
        failure_hint=failure_hint,
        credit_hint=credit_hint,
        metadata=metadata,
    )
