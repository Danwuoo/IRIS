# Pretraining Objective Spec

**Document Type:** Design Note (Non-normative)  
**Authority:** This note does not override system invariants, State IR contracts, trunk contract, Level contracts, or phase-gate policy.

---

## 1. Purpose

This document defines the operational meaning of **pretraining-first** for IRIS and ties it to the active single-card planning profile.

Primary profile references:

- `docs/plan/single-h100-3b-training-profile.md`
- `docs/plan/single-h100-3b-open-decisions.md`
- `docs/plan/runtime-stack-lock-jax-flax-nnx.md`

---

## 2. Objective Hierarchy

### 2.1 Primary Objective (Process/Diagnostic)

Training and iteration are optimized for stable internal behavior distributions:

- Failure taxonomy observability and stability
- L6 credit routing quality (no collapse)
- Calibration quality (no degradation)
- Program diversity at L2
- Macro usage / abstraction observability at L5
- Recovery signal quality through L3/L6 loop

### 2.2 Secondary Objective (Outcome)

Outcome metrics are secondary probes:

- Task success / benchmark score
- Cost and throughput

Secondary improvement cannot justify regression in primary process signals.

---

## 3. Data and Benchmark Boundaries

### 3.1 Training Mixture Source of Truth

Training mixture policy is governed by:

- `docs/Data Mixture & Ingestion Specification.md`

This includes:

- Pure LM: `90%`
- IR-aligned Synthetic: `10%`
- Benchmark datasets: `0%` in training (regression probe only)

### 3.2 Benchmark Role Constraints

- `ConceptARC` and `arc-agi-benchmarking` are probe/regression harnesses.
- Tools/benchmarks may provide perturbation and offline reports.
- Tools/benchmarks must not provide runtime truth authority, routing policy, or control decisions.

Verifier semantics remain in L6 and recovery policy remains in L3.

---

## 4. Runtime Profile Binding

The active pretraining profile assumes:

- Single-card `1x H100 80GB`
- Main context length `2048`
- BF16 compute with FP32-sensitive paths
- Segment-safe checkpoint/resume policy

Detailed hyperparameters are defined in:

- `docs/plan/single-h100-3b-training-profile.md`
- `docs/Training Segment and Resume Rules (Design Note).md`

---

## 5. Gate Requirements (Pretraining-First)

Any architecture/training-impacting change must pass:

- Credit routing distribution does not collapse
- Calibration does not degrade
- Concept leakage does not increase
- Paired invariance does not worsen
- Structural contracts remain valid (State IR / trunk / Level existence / learnable control)

This gate answers the canonical question:

> "If I fixed A, did I silently break B?"

---

## 6. Development vs Training Separation

- **Development loop:** small-slice fast diagnostics, failure attribution checks, regression diffs.
- **Training loop:** longer runs with process/diagnostic gates and probe regression checks.
- Promotion from development to training requires no unresolved primary-gate regressions.

---

## 7. Final Rule

If profile-level throughput gains conflict with primary process gates, the change is treated as regression.

---

**End of Document**
