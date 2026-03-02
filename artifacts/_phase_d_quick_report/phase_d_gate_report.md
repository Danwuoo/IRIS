# Phase D Gate Report

- Document Type: Design Note (Non-normative)
- Generated At (UTC): 2026-03-02T15:22:56.246818Z
- Phase: D
- Baseline ID: phase-d-v1
- Tolerance Profile ID: phase-d-default
- Change Class: Capability expansion (Phase D model-driven ARC diagnostics)
- Regression Status: **FAIL**

## 1) Suite Status
- S1: FAIL
- S2: PASS
- S3: FAIL
- S4: FAIL
- S5: FAIL
- S6: PASS
- S7: PASS
- S8: PASS
- S8_h100_packet: PASS

## 2) Violations
- [S1] smoke runtime checks: Traceback (most recent call last):
  File "C:\Users\wurre\Desktop\IRIS\scripts\s1_smoke.py", line 12, in <module>
    from iris.metrics import build_canonical_metrics, neutral_failure_credit
  File "C:\Users\wurre\Desktop\IRIS\src\iris\metrics\__init__.py", line 1, in <module>
    from .logging import append_jsonl, build_canonical_metrics, neutral_failure_credit, validate_failure_credit
  File "C:\Users\wurre\Desktop\IRIS\src\iris\metrics\logging.py", line 11, in <module>
    from ..arc.types import dominant_failure_code, failure_credit_to_code_distribution
  File "C:\Users\wurre\Desktop\IRIS\src\iris\arc\__init__.py", line 2, in <module>
    from .inference import ArcDiagnosticRunner, ArcEvalConfig, aggregate_failure_histogram, run_arc_diagnostic_eval
  File "C:\Users\wurre\Desktop\IRIS\src\iris\arc\inference.py", line 14, in <module>
    from ..train.checkpoint import load_checkpoint
  File "C:\Users\wurre\Desktop\IRIS\src\iris\train\__init__.py", line 1, in <module>
    from .eval import evaluate_latest_run
  File "C:\Users\wurre\Desktop\IRIS\src\iris\train\eval.py", line 11, in <module>
    from ..metrics import build_canonical_metrics, neutral_failure_credit
ImportError: cannot import name 'build_canonical_metrics' from partially initialized module 'iris.metrics' (most likely due to a circular import) (C:\Users\wurre\Desktop\IRIS\src\iris\metrics\__init__.py)
- [S3] failure taxonomy histogram drift: baseline failure histogram is missing
- [S4] concept.success_rate / concept.isolation_score / concept.leakage_score: baseline concept_breakdown is required in Phase C+
- [S5] paired.asymmetry_rate / paired.invariance.gap: baseline paired_representation_diff is required in Phase C+

## 3) Notes
- pairing_policy=adjacent
- max_reasoning_cycles=1
- termination_threshold=0.5000
- seed=17
- S8 local packet drift_clear=True
- S8 h100 packet status=PASS
- TEMPORARY TECHNICAL DEBT: max_reasoning_cycles hard cap. Removal criterion: remove after 3 consecutive full-runs show stable termination calibration.

## 4) Completion Checklist
- Mandatory docs consulted: `docs/10_Glossary_and_Normative_Status.md`, `docs/01_Architecture_Constitution.md`, `docs/02_State_IR_Spec.md`, `docs/03_Level_Contracts_L0-L6.md`, `docs/04_Credit_Assignment_and_Recovery.md`, `docs/05_Eval_Metrics_Spec.md`, `docs/06_Regression_and_Phase_Gates.md`, `docs/08_Training_Run_Governance.md`
- Change class: `Capability expansion (Phase D model-driven ARC diagnostics)`
- Expected failure-category impact: F_REP, F_PROC, F_SEARCH, F_EVAL visibility+attribution uplift.
- Technical debt guardrails introduced: TEMPORARY TECHNICAL DEBT: max_reasoning_cycles hard cap. Removal criterion: remove after 3 consecutive full-runs show stable termination calibration. Current max_reasoning_cycles=1.
- Termination: `Blocked`
