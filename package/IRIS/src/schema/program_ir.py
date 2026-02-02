from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Sequence


class ProgramIRError(ValueError):
    """Raised when the Program IR contract is violated."""


@dataclass
class ProgramToken:
    payload: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProgramIR:
    """
    Canonical Program IR container.

    Program tokens must remain outside the State IR sequence, even if they
    share the same latent dimension.
    """

    tokens: List[ProgramToken] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.validate()

    @staticmethod
    def empty() -> "ProgramIR":
        return ProgramIR(tokens=[])

    def validate(self) -> None:
        for token in self.tokens:
            if not isinstance(token, ProgramToken):
                raise ProgramIRError("All program tokens must be ProgramToken instances")

    def token_sequence(self) -> Sequence[ProgramToken]:
        return list(self.tokens)
