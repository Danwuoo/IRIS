from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ..schema import StateIR, TokenBase


@dataclass
class TrunkConfig:
    hidden_size: int = 128
    mixer_scale: float = 0.0
    adapter_scale: float = 1.0


class MambaTrunk:
    """
    Minimal trunk placeholder that preserves the State IR contract.

    The trunk contextualizes tokens but does not perform routing, execution,
    or termination decisions.
    """

    def __init__(self, config: TrunkConfig | None = None) -> None:
        self.config = config or TrunkConfig()

    def contextualize(self, state: StateIR) -> StateIR:
        self._tag_tokens(state.canonical_sequence())
        return state

    def _tag_tokens(self, tokens: Iterable[TokenBase]) -> None:
        for token in tokens:
            token.metadata.setdefault("trunk_contextualized", True)


try:
    import torch
    from torch import nn
except ImportError:  # pragma: no cover - optional torch dependency
    torch = None
    nn = None


if nn is not None:

    class TorchMambaTrunk(nn.Module):
        """
        Torch-backed trunk placeholder for Phase C training.

        This token mixer stands in for a real Mamba/SSM trunk and must be
        replaced with the trunk contract implementation.
        """

        def __init__(self, hidden_size: int = 128, depth: int = 2) -> None:
            super().__init__()
            self.layers = nn.ModuleList(
                [
                    nn.Sequential(
                        nn.Linear(hidden_size, hidden_size),
                        nn.GELU(),
                        nn.Linear(hidden_size, hidden_size),
                    )
                    for _ in range(depth)
                ]
            )
            self.global_proj = nn.Sequential(
                nn.Linear(hidden_size, hidden_size),
                nn.GELU(),
                nn.Linear(hidden_size, hidden_size),
            )

        def forward(self, tokens: torch.Tensor) -> torch.Tensor:
            for layer in self.layers:
                global_context = tokens.mean(dim=1, keepdim=True)
                tokens = tokens + layer(tokens) + self.global_proj(global_context)
            return tokens

else:

    class TorchMambaTrunk:  # type: ignore[no-redef]
        def __init__(self, *args: object, **kwargs: object) -> None:
            raise ImportError("TorchMambaTrunk requires torch to be installed.")
