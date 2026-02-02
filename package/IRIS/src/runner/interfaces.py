from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class TaskSpec:
    task_id: str
    payload: object
    metadata: Dict[str, str] = field(default_factory=dict)
