from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from ..diagnostics.trace import TraceEntry, load_trace_entries
from ..failure_taxonomy import codes as failure_codes
from ..levels import LEVEL_ORDER
from .report import RegressionReport
from .suites import DEFAULT_SUITES
from .thresholds import get_resume_consistency_thresholds


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


_RESUME_PATH_ALIASES = {
    "a": "uninterrupted",
    "b": "resumed",
    "uninterrupted": "uninterrupted",
    "resumed": "resumed",
}


def _normalize_resume_path(value: str) -> Optional[str]:
    return _RESUME_PATH_ALIASES.get(value.strip().lower())


@dataclass
class _ResumeSegmentAggregate:
    dataset_slice_id: str
    seed: str
    count: int = 0
    validity_sum: float = 0.0
    confidence_sum: float = 0.0
    credit_sums: Dict[str, float] = field(default_factory=dict)

    def add(self, entry: TraceEntry) -> None:
        self.count += 1
        self.validity_sum += float(entry.verifier.validity)
        self.confidence_sum += float(entry.verifier.confidence)
        for level in LEVEL_ORDER:
            key = str(level)
            self.credit_sums[key] = self.credit_sums.get(key, 0.0) + float(entry.credited_levels.get(key, 0.0))

    def mean_validity(self) -> float:
        return self.validity_sum / max(1, self.count)

    def mean_confidence(self) -> float:
        return self.confidence_sum / max(1, self.count)

    def mean_credit(self) -> Dict[str, float]:
        if self.count <= 0:
            return {str(level): 0.0 for level in LEVEL_ORDER}
        return {str(level): self.credit_sums.get(str(level), 0.0) / self.count for level in LEVEL_ORDER}


class RegressionRunner:
    def __init__(self, phase: str = "A", require_all_suites: bool = True) -> None:
        self.phase = phase
        self.require_all_suites = require_all_suites

    def _run_resume_consistency(self, traces: Sequence[TraceEntry], report: RegressionReport) -> None:
        thresholds = get_resume_consistency_thresholds(self.phase)
        if not traces:
            report.add_suite("resume_consistency", passed=False, detail="No traces")
            report.add_violation(
                metric="regression.status",
                delta=1.0,
                phase=self.phase,
                note="resume_consistency failed: no traces",
            )
            return

        issues: List[str] = []
        aggregates: Dict[Tuple[str, str], _ResumeSegmentAggregate] = {}
        has_resume_metadata = False

        for entry in traces:
            metadata = entry.metadata or {}
            if not metadata:
                continue
            if not any(key in metadata for key in ("segment_id", "resume_path", "dataset_slice_id", "seed")):
                continue

            has_resume_metadata = True
            missing = [key for key in ("segment_id", "resume_path", "dataset_slice_id", "seed") if not metadata.get(key)]
            if missing:
                issues.append(f"resume metadata missing {missing} (task_id={entry.task_id})")
                continue

            segment_status = str(metadata.get("segment_status", "APPLIED")).upper()
            if segment_status != "APPLIED":
                issues.append(
                    f"segment_status {segment_status} not APPLIED (segment_id={metadata.get('segment_id')})"
                )
                continue

            resume_path = _normalize_resume_path(str(metadata.get("resume_path")))
            if resume_path is None:
                issues.append(
                    f"unknown resume_path {metadata.get('resume_path')} (segment_id={metadata.get('segment_id')})"
                )
                continue

            segment_id = str(metadata.get("segment_id"))
            dataset_slice_id = str(metadata.get("dataset_slice_id"))
            seed = str(metadata.get("seed"))
            key = (segment_id, resume_path)
            aggregate = aggregates.get(key)
            if aggregate is None:
                aggregate = _ResumeSegmentAggregate(dataset_slice_id=dataset_slice_id, seed=seed)
                aggregates[key] = aggregate
            else:
                if aggregate.dataset_slice_id != dataset_slice_id:
                    issues.append(f"dataset_slice_id mismatch (segment_id={segment_id}, path={resume_path})")
                if aggregate.seed != seed:
                    issues.append(f"seed mismatch (segment_id={segment_id}, path={resume_path})")

            aggregate.add(entry)

        if not has_resume_metadata:
            report.add_suite("resume_consistency", passed=False, detail="No resume metadata")
            report.add_violation(
                metric="regression.status",
                delta=1.0,
                phase=self.phase,
                note="resume_consistency failed: missing resume metadata",
            )
            return

        segments: Dict[str, Dict[str, _ResumeSegmentAggregate]] = {}
        for (segment_id, resume_path), aggregate in aggregates.items():
            segments.setdefault(segment_id, {})[resume_path] = aggregate

        overlapping = {
            segment_id: paths
            for segment_id, paths in segments.items()
            if "uninterrupted" in paths and "resumed" in paths
        }
        if len(overlapping) < thresholds.min_overlap_segments:
            issues.append("insufficient overlapping segments for resume consistency check")

        drift_detected = False
        for segment_id, paths in overlapping.items():
            a = paths["uninterrupted"]
            b = paths["resumed"]
            if a.dataset_slice_id != b.dataset_slice_id:
                issues.append(f"dataset_slice_id mismatch across paths (segment_id={segment_id})")
            if a.seed != b.seed:
                issues.append(f"seed mismatch across paths (segment_id={segment_id})")

            validity_delta = abs(a.mean_validity() - b.mean_validity())
            if validity_delta > thresholds.validity_mean_delta:
                drift_detected = True
                report.add_violation(
                    metric="task.validity_score",
                    delta=validity_delta,
                    phase=self.phase,
                    note=f"resume_consistency segment {segment_id} > {thresholds.validity_mean_delta}",
                )

            confidence_delta = abs(a.mean_confidence() - b.mean_confidence())
            if confidence_delta > thresholds.confidence_mean_delta:
                drift_detected = True
                report.add_violation(
                    metric="task.confidence",
                    delta=confidence_delta,
                    phase=self.phase,
                    note=f"resume_consistency segment {segment_id} > {thresholds.confidence_mean_delta}",
                )

            credit_a = a.mean_credit()
            credit_b = b.mean_credit()
            credit_delta = sum(
                abs(credit_a.get(str(level), 0.0) - credit_b.get(str(level), 0.0)) for level in LEVEL_ORDER
            )
            if credit_delta > thresholds.credit_l1_delta:
                drift_detected = True
                report.add_violation(
                    metric="failure.credit",
                    delta=credit_delta,
                    phase=self.phase,
                    note=f"resume_consistency segment {segment_id} > {thresholds.credit_l1_delta}",
                )

        for issue in issues:
            report.add_violation(
                metric="regression.status",
                delta=1.0,
                phase=self.phase,
                note=f"resume_consistency: {issue}",
            )

        passed = not issues and not drift_detected
        detail = "OK" if passed else "Issues detected"
        report.add_suite("resume_consistency", passed=passed, detail=detail)

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

        self._run_resume_consistency(traces, report)

        not_run = [
            suite
            for suite in DEFAULT_SUITES
            if suite not in {"smoke", "structural", "resume_consistency"}
        ]
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
