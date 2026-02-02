from __future__ import annotations

from typing import List, Sequence

from ..diagnostics.trace import TraceEntry, load_trace_entries
from ..failure_taxonomy import codes as failure_codes
from ..levels import LEVEL_ORDER
from .report import RegressionReport
from .suites import DEFAULT_SUITES


def _validate_trace_entry(entry: TraceEntry) -> List[str]:
    issues: List[str] = []

    stats = entry.state_ir_stats
    if stats.num_objects < 0 or stats.num_relations < 0 or stats.num_events < 0 or stats.num_macros < 0:
        issues.append("state_ir_stats has negative counts")

    expected_codes = set(failure_codes())
    actual_codes = set(entry.verifier.failure_logits.keys())
    missing_codes = expected_codes - actual_codes
    extra_codes = actual_codes - expected_codes
    if missing_codes:
        issues.append(f"missing failure_logits: {sorted(missing_codes)}")
    if extra_codes:
        issues.append(f"unknown failure_logits: {sorted(extra_codes)}")

    expected_levels = {str(level) for level in LEVEL_ORDER}
    actual_levels = set(entry.credited_levels.keys())
    missing_levels = expected_levels - actual_levels
    extra_levels = actual_levels - expected_levels
    if missing_levels:
        issues.append(f"missing credited_levels: {sorted(missing_levels)}")
    if extra_levels:
        issues.append(f"unknown credited_levels: {sorted(extra_levels)}")

    credit_sum = sum(entry.credited_levels.get(str(level), 0.0) for level in LEVEL_ORDER)
    if abs(credit_sum - 1.0) > 1e-6:
        issues.append(f"credited_levels sum {credit_sum:.6f} != 1.0")

    if not (0.0 <= entry.verifier.validity <= 1.0):
        issues.append(f"verifier.validity out of range: {entry.verifier.validity}")
    if not (0.0 <= entry.verifier.confidence <= 1.0):
        issues.append(f"verifier.confidence out of range: {entry.verifier.confidence}")

    return issues


class RegressionRunner:
    def __init__(self, phase: str = "A", require_all_suites: bool = True) -> None:
        self.phase = phase
        self.require_all_suites = require_all_suites

    def run(self, traces: Sequence[TraceEntry]) -> RegressionReport:
        report = RegressionReport()

        if not traces:
            report.add_suite("smoke", passed=False, detail="No traces")
            report.add_violation(
                metric="regression.status",
                delta=1.0,
                phase=self.phase,
                note="smoke failed: no traces",
            )
            report.add_suite("structural", passed=False, detail="Not run")
        else:
            report.add_suite("smoke", passed=True, detail=f"{len(traces)} traces")

            structural_issues: List[str] = []
            for entry in traces:
                structural_issues.extend(_validate_trace_entry(entry))

            if structural_issues:
                report.add_suite("structural", passed=False, detail=f"{len(structural_issues)} issues")
                for issue in sorted(set(structural_issues)):
                    report.add_violation(
                        metric="regression.status",
                        delta=1.0,
                        phase=self.phase,
                        note=f"structural: {issue}",
                    )
            else:
                report.add_suite("structural", passed=True, detail="OK")

        not_run = [suite for suite in DEFAULT_SUITES if suite not in {"smoke", "structural"}]
        for suite in not_run:
            report.add_suite(suite, passed=False, detail="Not run")

        if self.require_all_suites and not_run:
            report.add_violation(
                metric="regression.status",
                delta=float(len(not_run)),
                phase=self.phase,
                note=f"suites not run: {', '.join(not_run)}",
            )

        return report

    def run_from_jsonl(self, path: str) -> RegressionReport:
        return self.run(load_trace_entries(path))
