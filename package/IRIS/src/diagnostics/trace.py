from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional

from ..schema import StateIR, StateIRStats
from .verifier import VerifierOutput


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class TraceEntry:
    task_id: str
    phase: str
    state_ir_stats: StateIRStats
    verifier: VerifierOutput
    credited_levels: Dict[str, float]
    timestamp: str
    metadata: Dict[str, str]

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "TraceEntry":
        stats_payload = payload.get("state_ir_stats", {}) or {}
        stats = StateIRStats(
            num_objects=int(stats_payload.get("num_objects", 0)),
            num_relations=int(stats_payload.get("num_relations", 0)),
            num_events=int(stats_payload.get("num_events", 0)),
            num_macros=int(stats_payload.get("num_macros", 0)),
        )
        verifier_payload = payload.get("verifier", {}) or {}
        verifier = VerifierOutput.from_dict(verifier_payload)
        credited_levels = payload.get("credited_levels", verifier.credit.to_dict()) or {}
        metadata = payload.get("metadata", {}) or {}
        timestamp = str(payload.get("timestamp", "")) or _utc_now_iso()
        return cls(
            task_id=str(payload.get("task_id", "")),
            phase=str(payload.get("phase", "")),
            state_ir_stats=stats,
            verifier=verifier,
            credited_levels={str(key): float(value) for key, value in credited_levels.items()},
            timestamp=timestamp,
            metadata={str(key): str(value) for key, value in metadata.items()},
        )

    def to_dict(self) -> Dict[str, object]:
        payload = {
            "task_id": self.task_id,
            "phase": self.phase,
            "timestamp": self.timestamp,
            "state_ir_stats": asdict(self.state_ir_stats),
            "verifier": self.verifier.to_dict(),
            "credited_levels": dict(self.credited_levels),
        }
        if self.metadata:
            payload["metadata"] = dict(self.metadata)
        return payload

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=True, sort_keys=True)


class TraceRecorder:
    def __init__(self, phase: str = "A", output_path: Optional[str] = None) -> None:
        self.phase = phase
        self.output_path = output_path
        if self.output_path:
            directory = os.path.dirname(self.output_path)
            if directory:
                os.makedirs(directory, exist_ok=True)

    def record(
        self,
        task_id: str,
        state: StateIR,
        verifier_output: VerifierOutput,
        metadata: Optional[Dict[str, str]] = None,
    ) -> TraceEntry:
        stats = state.stats()
        entry = TraceEntry(
            task_id=task_id,
            phase=self.phase,
            state_ir_stats=stats,
            verifier=verifier_output,
            credited_levels=verifier_output.credit.to_dict(),
            timestamp=_utc_now_iso(),
            metadata=metadata or {},
        )
        if self.output_path:
            with open(self.output_path, "a", encoding="utf-8") as handle:
                handle.write(entry.to_json() + "\n")
        return entry


def load_trace_entries(path: str) -> List[TraceEntry]:
    entries: List[TraceEntry] = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            entries.append(TraceEntry.from_dict(payload))
    return entries
