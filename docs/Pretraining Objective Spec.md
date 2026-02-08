# Pretraining Objective Spec

**Document Type:** Design Note (Non-normative)  
**Authority:** This note does not override system invariants, State IR contracts, trunk contract, or Level contracts.

---

## 1. Purpose

This document defines the operational meaning of **pretraining-first** for IRIS:

* IRIS is developed as a general pretraining foundation model.
* ARC-family benchmarks are used as **probe/regression instruments**, not primary optimization targets.
* Phase C closed-loop remains mandatory:

  * `State IR -> L2 propose/execute -> L6 verify/credit -> L3 control/recovery`

---

## 2. Objective Hierarchy

### 2.1 Primary Objective (Process/Diagnostic)

Training and iteration are optimized for stable internal behavior distributions:

* Failure taxonomy observability and stability
* L6 credit routing quality (no collapse)
* Calibration quality (no degradation)
* Program diversity at L2
* Macro usage / abstraction observability at L5
* Recovery signal quality through L3/L6 loop

### 2.2 Secondary Objective (Outcome)

Outcome metrics are secondary probes:

* Task success / benchmark score
* Cost and throughput

Secondary improvement cannot justify regression in primary process signals.

---

## 3. Data and Benchmark Boundaries

### 3.1 Multi-Source Pretraining Inputs

Phase C+ pretraining data sources:

* `MiniARC`
* `ARC-AGI` (e.g., ARC-AGI-1/2)
* `re-arc`
* `ConceptARC`

### 3.2 Benchmark Role Constraints

* `ConceptARC` and `arc-agi-benchmarking` are probe/regression harnesses.
* Tools/benchmarks may provide data, perturbation, and offline reports.
* Tools/benchmarks must not provide runtime truth authority, routing policy, or control decisions.

Verifier semantics remain in L6 and recovery policy remains in L3.

---

## 4. Gate Requirements (Pretraining-First)

Any architecture/training-impacting change must pass:

* Credit routing distribution does not collapse
* Calibration does not degrade
* Concept leakage does not increase
* Paired invariance does not worsen
* Structural contracts remain valid (State IR / trunk / Level existence / learnable control)

This gate answers the canonical question:

> 「我修了 A，是否悄悄毀了 B？」

---

## 5. Development vs Training Separation

* **Development loop:** small-slice fast diagnostics, failure attribution checks, regression diffs.
* **Training loop:** multi-source runs with process/diagnostic gates and probe regression hard checks.
* Promotion from development to training requires no unresolved primary-gate regressions.

---

**End of Document**

