from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional

from ..schema import (
    EventToken,
    GlobalToken,
    ObjectToken,
    RelationToken,
    StateIR,
    TaskToken,
)


@dataclass
class Level0Output:
    state: StateIR
    diagnostics: Dict[str, float]


class Level0:
    """
    Level 0 placeholder: converts raw inputs into canonical State IR tokens.
    """

    def forward(
        self,
        raw_input: Any,
        task_token: Optional[TaskToken] = None,
        global_token: Optional[GlobalToken] = None,
    ) -> Level0Output:
        if isinstance(raw_input, StateIR):
            state = raw_input
        elif _is_grid(raw_input):
            grid = raw_input
            height = len(grid)
            width = len(grid[0]) if height else 0
            objects = [
                ObjectToken(metadata={"x": x, "y": y, "color": int(grid[y][x])})
                for y in range(height)
                for x in range(width)
            ]
            state = StateIR(
                task=task_token or TaskToken(metadata={"source": "grid"}),
                global_token=global_token
                or GlobalToken(metadata={"grid_height": height, "grid_width": width}),
                objects=objects,
                relations=[],
                events=[],
                macros=[],
            )
        else:
            payload = raw_input if isinstance(raw_input, Mapping) else {}
            objects = [ObjectToken(payload=value) for value in payload.get("objects", [])]
            relations = [RelationToken(payload=value) for value in payload.get("relations", [])]
            events = [EventToken(payload=value) for value in payload.get("events", [])]
            state = StateIR(
                task=task_token or TaskToken(payload=payload.get("task")),
                global_token=global_token or GlobalToken(payload=payload.get("global")),
                objects=objects,
                relations=relations,
                events=events,
                macros=[],
            )

        stats = state.stats()
        diagnostics = {
            "rep.object.count": float(stats.num_objects),
            "rep.relation.count": float(stats.num_relations),
            "rep.event.count": float(stats.num_events),
        }
        return Level0Output(state=state, diagnostics=diagnostics)


def _is_grid(raw_input: Any) -> bool:
    if not isinstance(raw_input, list):
        return False
    if not raw_input:
        return False
    return all(isinstance(row, list) for row in raw_input)
