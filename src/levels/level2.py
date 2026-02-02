from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence

from ..schema import ProgramIR, ProgramToken, StateIR
from ..utils import clamp01


@dataclass
class ExecutionResult:
    state: StateIR
    trace: Dict[str, object]


@dataclass
class ProgramCandidate:
    program: ProgramIR
    execution: ExecutionResult
    score: float


@dataclass
class ProgramProposalConfig:
    base_score: float = 0.0


class Level2:
    """
    Level 2 placeholder: proposes and executes neural programs.
    """

    def __init__(self, config: ProgramProposalConfig | None = None) -> None:
        self.config = config or ProgramProposalConfig()
        self._counter = 0

    def propose(self, state: StateIR, beam_size: int) -> List[ProgramIR]:
        beam_size = max(1, int(beam_size))
        programs: List[ProgramIR] = []
        for _ in range(beam_size):
            program_id = self._counter
            self._counter += 1
            token = ProgramToken(payload={"program_id": program_id})
            programs.append(ProgramIR(tokens=[token], metadata={"origin": "L2"}))
        state.global_token.metadata.setdefault("prog.count", beam_size)
        return programs

    def execute(self, program: ProgramIR, state: StateIR) -> ExecutionResult:
        program_id = program.tokens[0].payload.get("program_id") if program.tokens else None
        state.global_token.metadata.setdefault("prog.exec.last_id", program_id)
        trace = {"program_id": program_id, "exec_status": "noop"}
        return ExecutionResult(state=state, trace=trace)

    def score(self, program: ProgramIR, execution: ExecutionResult) -> float:
        _ = execution
        return clamp01(self.config.base_score)

    def run(self, state: StateIR, beam_size: int) -> Sequence[ProgramCandidate]:
        candidates: List[ProgramCandidate] = []
        for program in self.propose(state, beam_size):
            execution = self.execute(program, state)
            score = self.score(program, execution)
            candidates.append(ProgramCandidate(program=program, execution=execution, score=score))
        return candidates
