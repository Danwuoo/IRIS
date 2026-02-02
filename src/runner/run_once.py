from __future__ import annotations

from typing import Mapping, Optional

from .phase_c import PhaseCResult, PhaseCRunContext, run_phase_c


def run_once(
    task_id: str,
    raw_input: object,
    failure_logits: Optional[Mapping[str, float]] = None,
    trace_path: Optional[str] = None,
) -> PhaseCResult:
    return run_phase_c(
        task_id=task_id,
        raw_input=raw_input,
        failure_logits=failure_logits,
        trace_path=trace_path,
    )


__all__ = ["PhaseCResult", "PhaseCRunContext", "run_phase_c", "run_once"]
