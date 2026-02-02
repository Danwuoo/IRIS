from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Mapping


class SegmentStatus(str, Enum):
    PENDING = "PENDING"
    APPLIED = "APPLIED"


def _parse_status(value: object) -> SegmentStatus:
    text = str(value or "").upper()
    if text == SegmentStatus.PENDING.value:
        return SegmentStatus.PENDING
    return SegmentStatus.APPLIED


@dataclass(frozen=True)
class CheckpointManifest:
    run_id: str
    segment_id_last_applied: int
    status: SegmentStatus
    dataset_slice_id: str
    code_version_hash: str
    config_hash: str

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "CheckpointManifest":
        return cls(
            run_id=str(payload.get("run_id", "")),
            segment_id_last_applied=int(payload.get("segment_id_last_applied", -1)),
            status=_parse_status(payload.get("status", SegmentStatus.APPLIED.value)),
            dataset_slice_id=str(payload.get("dataset_slice_id", "")),
            code_version_hash=str(payload.get("code_version_hash", "")),
            config_hash=str(payload.get("config_hash", "")),
        )

    def to_dict(self) -> Dict[str, object]:
        return {
            "run_id": self.run_id,
            "segment_id_last_applied": int(self.segment_id_last_applied),
            "status": self.status.value,
            "dataset_slice_id": self.dataset_slice_id,
            "code_version_hash": self.code_version_hash,
            "config_hash": self.config_hash,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=True, sort_keys=True)


@dataclass(frozen=True)
class SegmentJournalEntry:
    run_id: str
    segment_id: int
    status_from: SegmentStatus
    status_to: SegmentStatus
    dataset_slice_id: str
    started_at: str
    applied_at: str
    duration_ms: int
    failure_code: str = ""
    artifact_paths: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "SegmentJournalEntry":
        artifacts = payload.get("artifact_paths", {}) or {}
        return cls(
            run_id=str(payload.get("run_id", "")),
            segment_id=int(payload.get("segment_id", -1)),
            status_from=_parse_status(payload.get("status_from", SegmentStatus.PENDING.value)),
            status_to=_parse_status(payload.get("status_to", SegmentStatus.APPLIED.value)),
            dataset_slice_id=str(payload.get("dataset_slice_id", "")),
            started_at=str(payload.get("started_at", "")),
            applied_at=str(payload.get("applied_at", "")),
            duration_ms=int(payload.get("duration_ms", 0)),
            failure_code=str(payload.get("failure_code", "")),
            artifact_paths={str(key): str(value) for key, value in artifacts.items()},
        )

    def to_dict(self) -> Dict[str, object]:
        payload: Dict[str, object] = {
            "run_id": self.run_id,
            "segment_id": int(self.segment_id),
            "status_from": self.status_from.value,
            "status_to": self.status_to.value,
            "dataset_slice_id": self.dataset_slice_id,
            "started_at": self.started_at,
            "applied_at": self.applied_at,
            "duration_ms": int(self.duration_ms),
        }
        if self.failure_code:
            payload["failure_code"] = self.failure_code
        if self.artifact_paths:
            payload["artifact_paths"] = dict(self.artifact_paths)
        return payload

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=True, sort_keys=True)


@dataclass
class SegmentJournal:
    entries: List[SegmentJournalEntry] = field(default_factory=list)

    def append(self, entry: SegmentJournalEntry) -> None:
        self.entries.append(entry)

    def to_jsonl(self) -> str:
        return "\n".join(entry.to_json() for entry in self.entries)
