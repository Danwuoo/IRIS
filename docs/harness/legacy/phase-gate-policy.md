# Phase and Gate Policy

**Legacy Planning Replacement for `DevelopmentPlan.md`**

**Status:** Canonical (Project-internal, non-normative but binding)  
**Authority:** Subordinate to Section 1 normative contracts and Level contracts.

---

## 0. Purpose

This document replaces the retired `docs/harness/legacy/DevelopmentPlan.md`.

It defines:

* Phase identifiers (`A` through `E`)
* Phase-appropriate scope boundaries
* Regression gate activation policy by phase
* Promotion requirements between phases

This document does not override any normative architecture contract.

---

## 1. Phase Definitions

### Phase A

Diagnostics-first bootstrap:

* Verifier signals
* Failure tags
* Trace/logging skeleton
* No solver heuristics as primary policy

### Phase B

Tool generation and alignment:

* Failure-tag alignment
* Paired-task plumbing
* No correctness encoded into tool internals

### Phase C

Minimal closed loop in `src/`:

* All Level interfaces L0-L6 present (mounted or stubbed)
* Credit/failure attribution live
* Pretraining-first process diagnostics enforced

### Phase D

Concept diagnostics:

* Concept isolation/leakage monitoring through ConceptARC
* Attribution and diagnostic stability prioritized over leaderboard score

### Phase E

Regression and verifier harness hardening:

* `arc-agi-benchmarking` as regression/verifier probe harness
* No benchmark-shaped architectural shortcuts

---

## 2. Regression Suite Activation by Phase

Suites are defined in `docs/harness/legacy/regression.md`.
In that file, "Mandatory" means mandatory once activated by this section.

### 2.1 Activation Matrix

| Suite ID | Suite Name | A | B | C | D | E |
| --- | --- | --- | --- | --- | --- | --- |
| S1 | Smoke Regression | ON | ON | ON | ON | ON |
| S2 | Structural Regression | ON | ON | ON | ON | ON |
| S3 | Failure-Profile Regression | OBSERVE | OBSERVE | ON | ON | ON |
| S4 | Concept Isolation Regression | OFF | OBSERVE | ON | ON | ON |
| S5 | Paired Representation Regression | OFF | OBSERVE | ON | ON | ON |
| S6 | Credit Routing Regression | OBSERVE | OBSERVE | ON | ON | ON |
| S7 | Pretraining Diagnostics Regression | OBSERVE | OBSERVE | ON | ON | ON |
| S8 | Resume Consistency Regression | OFF | OFF | ON | ON | ON |

Legend:

* `ON` = blocking gate
* `OBSERVE` = collect/report only, non-blocking
* `OFF` = not required in this phase

---

## 3. Tolerance and Baseline Policy

The phase profile controls tolerance interpretation used by
`docs/harness/legacy/metrics.md` and `docs/harness/legacy/regression.md`.

Each regression run must declare:

* `phase`: one of `A`, `B`, `C`, `D`, `E`
* `baseline_id`: immutable baseline reference
* `tolerance_profile_id`: identifier for epsilon/tolerance configuration

Rules:

1. Tolerances (`epsilon`, calibration tolerance, leakage tolerance) must be fixed
   per `phase + tolerance_profile_id`.
2. Tolerances cannot be relaxed within the same profile after baseline freeze.
3. Profile changes require explicit annotation in regression artifacts.

---

## 4. Promotion Criteria

### A -> B

* S1/S2 pass rate stable
* Verifier and failure taxonomy logging available

### B -> C

* L0-L6 interfaces wired (stub allowed)
* Credit routing vector emitted and serialized
* S3/S6/S7 promoted from observe to blocking

### C -> D

* Concept leakage/isolation instrumentation stable
* S4/S5 active and stable under fixed tolerance profile

### D -> E

* Resume consistency (S8) stable
* Full regression artifact pipeline retained across runs

---

## 5. Migration Note

`docs/harness/legacy/DevelopmentPlan.md` is intentionally retired.
Any previous reference to that file must now point to this document.

---

## 6. Final Rule

If a change cannot be justified with:

* failure taxonomy impact,
* level attribution impact, and
* phase-appropriate gate policy impact,

the change is not ready for promotion.

---

**End of `phase-gate-policy.md`**
