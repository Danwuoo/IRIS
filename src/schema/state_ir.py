from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Sequence


class StateIRError(ValueError):
    """Raised when the canonical State IR contract is violated."""


@dataclass
class TokenBase:
    payload: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskToken(TokenBase):
    ...


@dataclass
class GlobalToken(TokenBase):
    ...


@dataclass
class ObjectToken(TokenBase):
    ...


@dataclass
class RelationToken(TokenBase):
    ...


@dataclass
class EventToken(TokenBase):
    ...


@dataclass
class MacroToken(TokenBase):
    ...


@dataclass(frozen=True)
class StateIRStats:
    num_objects: int
    num_relations: int
    num_events: int
    num_macros: int


@dataclass
class StateIR:
    """
    Canonical State IR container following the mandatory order:
    [T; G; O*; R*; X*; M*].
    """

    task: TaskToken
    global_token: GlobalToken
    objects: List[ObjectToken] = field(default_factory=list)
    relations: List[RelationToken] = field(default_factory=list)
    events: List[EventToken] = field(default_factory=list)
    macros: List[MacroToken] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.validate()

    @staticmethod
    def empty() -> "StateIR":
        """Return an empty-but-valid State IR with placeholder T/G tokens."""
        return StateIR(task=TaskToken(), global_token=GlobalToken())

    def validate(self) -> None:
        if not isinstance(self.task, TaskToken):
            raise StateIRError("Task token must be present and of type TaskToken")
        if not isinstance(self.global_token, GlobalToken):
            raise StateIRError("Global token must be present and of type GlobalToken")

        for token in self.objects:
            if not isinstance(token, ObjectToken):
                raise StateIRError("All object tokens must be ObjectToken instances")

        for token in self.relations:
            if not isinstance(token, RelationToken):
                raise StateIRError("All relation tokens must be RelationToken instances")

        for token in self.events:
            if not isinstance(token, EventToken):
                raise StateIRError("All event tokens must be EventToken instances")

        for token in self.macros:
            if not isinstance(token, MacroToken):
                raise StateIRError("All macro tokens must be MacroToken instances")

    def stats(self) -> StateIRStats:
        return StateIRStats(
            num_objects=len(self.objects),
            num_relations=len(self.relations),
            num_events=len(self.events),
            num_macros=len(self.macros),
        )

    def canonical_sequence(self) -> Sequence[TokenBase]:
        """Expose the ordered token sequence for downstream trunk consumption."""
        return (
            [self.task, self.global_token]
            + list(self.objects)
            + list(self.relations)
            + list(self.events)
            + list(self.macros)
        )

