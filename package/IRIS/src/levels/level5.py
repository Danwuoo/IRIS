from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..schema import MacroToken, StateIR
from ..utils import clamp01, sigmoid


@dataclass
class Level5Output:
    state: StateIR
    macro_gate: float


@dataclass
class Level5Config:
    macro_logit: float = 0.0


class Level5:
    """
    Level 5 placeholder: manages abstraction granularity via macro tokens.
    """

    def __init__(self, config: Optional[Level5Config] = None) -> None:
        self.config = config or Level5Config()

    def forward(self, state: StateIR) -> Level5Output:
        macro_gate = clamp01(sigmoid(self.config.macro_logit))
        state.global_token.metadata.setdefault("abs.granularity", macro_gate)
        # Macro updates are omitted for now; macro_gate remains as a learnable signal.
        return Level5Output(state=state, macro_gate=macro_gate)

    def update_macro(self, state: StateIR, payload: object | None = None) -> StateIR:
        token = MacroToken(payload=payload)
        state.macros.append(token)
        return state
