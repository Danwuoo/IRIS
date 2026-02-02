from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Optional

from ..diagnostics import TraceEntry, TraceRecorder, VerifierOutput
from ..levels.level0 import Level0
from ..levels.level1 import Level1
from ..levels.level2 import Level2, ProgramCandidate
from ..levels.level3 import Budget, ControlSignals, Level3
from ..levels.level4 import Level4, MemoryReadResult
from ..levels.level5 import Level5
from ..levels.level6 import Level6
from ..routers import CandidateSelection, FusionRouter, InvocationRouter, OutputRouter
from ..schema import StateIR
from ..trunk import MambaTrunk


@dataclass
class PhaseCResult:
    task_id: str
    input_state: StateIR
    contextual_state: StateIR
    budget: Budget
    memory: MemoryReadResult
    candidates: List[ProgramCandidate]
    selection: CandidateSelection
    verifier: VerifierOutput
    trace: TraceEntry
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class PhaseCRunContext:
    trunk: MambaTrunk
    level0: Level0
    level1: Level1
    level2: Level2
    level3: Level3
    level4: Level4
    level5: Level5
    level6: Level6
    invocation_router: InvocationRouter
    fusion_router: FusionRouter
    output_router: OutputRouter
    recorder: TraceRecorder

    @classmethod
    def default(cls, trace_path: Optional[str] = None) -> "PhaseCRunContext":
        return cls(
            trunk=MambaTrunk(),
            level0=Level0(),
            level1=Level1(),
            level2=Level2(),
            level3=Level3(),
            level4=Level4(),
            level5=Level5(),
            level6=Level6(),
            invocation_router=InvocationRouter(),
            fusion_router=FusionRouter(),
            output_router=OutputRouter(),
            recorder=TraceRecorder(phase="C", output_path=trace_path),
        )

    def run_once(
        self,
        task_id: str,
        raw_input: object,
        failure_logits: Optional[Mapping[str, float]] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> PhaseCResult:
        # Level 0: State IR construction.
        l0 = self.level0.forward(raw_input)

        # Level 5: abstraction gating (macro policy).
        l5 = self.level5.forward(l0.state)

        # Trunk contextualization.
        contextual_state = self.trunk.contextualize(l5.state)

        # Level 1: dynamics / uncertainty signals.
        l1 = self.level1.forward(contextual_state)

        # Level 3: initial budget allocation.
        signals = ControlSignals(uncertainty=l1.uncertainty)
        budget = self.level3.forward(signals)
        invocation_gates = self.invocation_router.route()
        contextual_state.global_token.metadata.setdefault(
            "invocation_gates", invocation_gates.to_dict()
        )

        # Level 4: memory read and fusion placeholder.
        memory = self.level4.read(contextual_state, budget.retrieval_k)
        if memory.retrieved:
            self.fusion_router.fuse(contextual_state, [contextual_state] * len(memory.retrieved))

        # Level 2: program proposal/execution.
        candidates = list(self.level2.run(contextual_state, budget.program_beam))

        # Output routing (soft selection).
        selection = self.output_router.select([candidate.score for candidate in candidates])
        selected_state = contextual_state
        if selection.selected_index >= 0:
            selected_state = candidates[selection.selected_index].execution.state

        # Level 6: verification + credit routing.
        verifier = self.level6.verify(selected_state, failure_logits=failure_logits)

        trace = self.recorder.record(
            task_id=task_id,
            state=selected_state,
            verifier_output=verifier,
            metadata=metadata,
        )

        return PhaseCResult(
            task_id=task_id,
            input_state=l0.state,
            contextual_state=contextual_state,
            budget=budget,
            memory=memory,
            candidates=candidates,
            selection=selection,
            verifier=verifier,
            trace=trace,
            metadata=metadata or {},
        )


def run_phase_c(
    task_id: str,
    raw_input: object,
    failure_logits: Optional[Mapping[str, float]] = None,
    metadata: Optional[Dict[str, str]] = None,
    trace_path: Optional[str] = None,
) -> PhaseCResult:
    ctx = PhaseCRunContext.default(trace_path=trace_path)
    return ctx.run_once(
        task_id=task_id,
        raw_input=raw_input,
        failure_logits=failure_logits,
        metadata=metadata,
    )
