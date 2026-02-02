from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..levels import Level
from .suites import DEFAULT_SUITES


@dataclass(frozen=True)
class RegressionViolation:
    metric: str
    delta: float
    phase: str
    suspected_level: Optional[Level] = None
    note: str = ""

    def to_dict(self) -> Dict[str, object]:
        payload: Dict[str, object] = {
            "metric": self.metric,
            "delta": self.delta,
            "phase": self.phase,
        }
        if self.suspected_level:
            payload["suspected_level"] = str(self.suspected_level)
        if self.note:
            payload["note"] = self.note
        return payload


@dataclass
class RegressionSuiteResult:
    name: str
    passed: bool
    detail: str = ""

    def to_dict(self) -> Dict[str, object]:
        payload: Dict[str, object] = {"name": self.name, "status": "PASS" if self.passed else "FAIL"}
        if self.detail:
            payload["detail"] = self.detail
        return payload


@dataclass
class RegressionReport:
    suites: List[RegressionSuiteResult] = field(default_factory=list)
    violations: List[RegressionViolation] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    @property
    def status(self) -> str:
        return "FAIL" if self.violations else "PASS"

    def add_suite(self, name: str, passed: bool, detail: str = "") -> None:
        self.suites.append(RegressionSuiteResult(name=name, passed=passed, detail=detail))

    def add_violation(
        self,
        metric: str,
        delta: float,
        phase: str,
        suspected_level: Optional[Level] = None,
        note: str = "",
    ) -> None:
        self.violations.append(
            RegressionViolation(metric=metric, delta=delta, phase=phase, suspected_level=suspected_level, note=note)
        )

    def ensure_default_suites(self) -> None:
        present = {result.name for result in self.suites}
        for suite in DEFAULT_SUITES:
            if suite not in present:
                self.add_suite(name=suite, passed=False, detail="Not run")

    def to_dict(self) -> Dict[str, object]:
        self.ensure_default_suites()
        payload: Dict[str, object] = {
            "status": self.status,
            "suites": [suite.to_dict() for suite in self.suites],
            "violations": [violation.to_dict() for violation in self.violations],
        }
        if self.notes:
            payload["notes"] = list(self.notes)
        return payload

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=True, sort_keys=True)

