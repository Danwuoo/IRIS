from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from ..schema import ProgramIR, StateIR
from ..utils import clamp01, sigmoid, softmax


def _dot(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(float(x) * float(y) for x, y in zip(a, b))


@dataclass
class MemoryEntry:
    key: List[float]
    program: ProgramIR
    metadata: Dict[str, object] = field(default_factory=dict)


@dataclass
class MemoryReadResult:
    state: StateIR
    retrieved: List[MemoryEntry]
    similarities: List[float]


@dataclass
class MemoryWriteDecision:
    gate: float


@dataclass
class MemoryConfig:
    write_logit: float = 0.0


class MemoryKeyEncoder:
    def encode(self, state: StateIR) -> List[float]:
        stats = state.stats()
        return [float(stats.num_objects), float(stats.num_relations), float(stats.num_events), float(stats.num_macros)]


class MemoryStore:
    def __init__(self) -> None:
        self.entries: List[MemoryEntry] = []

    def read(self, state: StateIR, query: Sequence[float], k: int) -> MemoryReadResult:
        if not self.entries or k <= 0:
            return MemoryReadResult(state=state, retrieved=[], similarities=[])

        similarities = [_dot(query, entry.key) for entry in self.entries]
        weights = softmax(similarities)
        ranked = sorted(zip(self.entries, weights), key=lambda pair: pair[1], reverse=True)
        selected = ranked[:k]
        retrieved = [entry for entry, _ in selected]
        selected_weights = [weight for _, weight in selected]
        return MemoryReadResult(state=state, retrieved=retrieved, similarities=selected_weights)

    def write(self, entry: MemoryEntry) -> None:
        self.entries.append(entry)


class MemoryWriteGate:
    def __init__(self, config: MemoryConfig | None = None) -> None:
        self.config = config or MemoryConfig()

    def decide(self) -> MemoryWriteDecision:
        gate = clamp01(sigmoid(self.config.write_logit))
        return MemoryWriteDecision(gate=gate)


class Level4:
    """
    Level 4 placeholder: program/concept memory with learned gates.
    """

    def __init__(self, config: MemoryConfig | None = None) -> None:
        self.config = config or MemoryConfig()
        self.key_encoder = MemoryKeyEncoder()
        self.store = MemoryStore()
        self.write_gate = MemoryWriteGate(self.config)

    def read(self, state: StateIR, k: int) -> MemoryReadResult:
        query = self.key_encoder.encode(state)
        result = self.store.read(state, query, k)
        state.global_token.metadata.setdefault("mem.read.k", len(result.retrieved))
        if result.similarities:
            state.global_token.metadata.setdefault("mem.read.similarity", float(sum(result.similarities) / len(result.similarities)))
        return result

    def write(self, program: ProgramIR) -> MemoryWriteDecision:
        decision = self.write_gate.decide()
        # TEMPORARY TECHNICAL DEBT: gate thresholding is a stand-in until learned
        # stochastic write policies are integrated. Removal criterion: replace
        # thresholding with learned stochastic gating or differentiable writes.
        if decision.gate >= 0.5:
            entry = MemoryEntry(key=[decision.gate], program=program)
            self.store.write(entry)
        return decision
