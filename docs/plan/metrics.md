# Metrics Specification

**Failure Taxonomy · Diagnostic Signals · Regression Gates**

**Status:** Canonical (Project-internal, non-normative but binding)
**Audience:** Model / Tool / Evaluation / Training Pipeline
**Applies to:** Phase A–E (Always-On)

---

## 0. Purpose and Non-Goals

### 0.1 Purpose

This document defines a **single, unified metrics vocabulary** for the entire system, covering:

* Failure taxonomy (semantic, Level-addressable)
* Diagnostic signals emitted by each Level
* Verifier- and controller-consumable scores
* Regression and gate criteria across phases

The metrics defined here are the **only allowed basis** for:

* Credit routing (L6 → others)
* Recovery strategy selection (via L3)
* Benchmark interpretation (ConceptARC, arc-agi-benchmarking)
* Architecture change validation (“did we break something?”)

---

### 0.2 Explicit Non-Goals

This document does **not**:

* Define loss functions
* Define optimization algorithms
* Define training schedules
* Replace Level Contracts or System Invariants

Metrics describe **what is observed**, not **how learning happens**.

---

## 1. Metric Taxonomy Overview

All metrics fall into one of four classes:

1. **Outcome Metrics** – Was the final result acceptable?
2. **Failure Taxonomy Metrics** – *Why* did it fail, semantically?
3. **Process / Diagnostic Metrics** – What happened internally?
4. **Regression Gate Metrics** – Did a change violate invariants?

Only these four classes are permitted.

---

## 2. Outcome Metrics (Global)

### 2.1 Task-Level Outcome

| Metric                | Type          | Description                       |
| --------------------- | ------------- | --------------------------------- |
| `task.success`        | bool          | Final output accepted by verifier |
| `task.validity_score` | float ∈ [0,1] | Verifier validity (continuous)    |
| `task.confidence`     | float ∈ [0,1] | Calibrated confidence (L6)        |

**Rules**

* `task.success` MUST be derived from verifier logic, not dataset labels directly.
* Confidence MUST be separable from correctness.

---

### 2.2 Cost / Efficiency (Secondary)

| Metric                   | Type | Notes                  |
| ------------------------ | ---- | ---------------------- |
| `cost.total_steps`       | int  | Total reasoning cycles |
| `cost.program_proposals` | int  | Total L2 proposals     |
| `cost.rollout_steps`     | int  | L1 unroll depth (sum)  |
| `cost.retrieval_calls`   | int  | L4 reads               |

These metrics **must never** be used alone to judge model quality.

---

## 3. Failure Taxonomy (Canonical)

Failure taxonomy is **semantic**, **Level-addressable**, and **exclusive** in definition (but credit may be distributed).

### 3.1 Failure Category Codes

| Code       | Category                         | Primary Level |
| ---------- | -------------------------------- | ------------- |
| `F_REP`    | Representation Failure           | L0 / L1       |
| `F_PROC`   | Procedural Failure               | L2            |
| `F_SEARCH` | Search / Budget Failure          | L3            |
| `F_MEM`    | Memory Failure                   | L4            |
| `F_ABS`    | Abstraction Failure              | L5            |
| `F_EVAL`   | Evaluation / Calibration Failure | L6            |

These codes are **mandatory**. No ad-hoc categories are allowed.

---

### 3.2 Failure Attribution Vector (Mandatory)

For every failed (or low-confidence) attempt, the system MUST emit:

```
failure.credit = {
  L0: c0,
  L1: c1,
  L2: c2,
  L3: c3,
  L4: c4,
  L5: c5,
  L6: c6
}
```

Constraints:

* `ck ∈ [0,1]`
* `Σ ck = 1`
* Produced by **L6 Credit Router**
* Consumed by **L3 recovery policy** and training

Hard attribution (single Level) is **not allowed**.

---

## 4. Level-Specific Diagnostic Metrics

### 4.1 Level 0–1 (Representation & Dynamics)

| Metric                | Type  | Description                   |
| --------------------- | ----- | ----------------------------- |
| `rep.object.count`    | int   | Number of object tokens       |
| `rep.relation.count`  | int   | Number of relation tokens     |
| `rep.event.count`     | int   | Number of event tokens        |
| `rep.object.entropy`  | float | Slot / assignment uncertainty |
| `dyn.violation_score` | float | Constraint / energy violation |
| `dyn.uncertainty`     | float | Predictive uncertainty        |

**Interpretation**

* High entropy + downstream failure → `F_REP`
* Low entropy but wrong → likely upstream masking (invalid)

---

### 4.2 Level 2 (Program Induction & Execution)

| Metric                   | Type  | Description                        |
| ------------------------ | ----- | ---------------------------------- |
| `prog.count`             | int   | Programs proposed                  |
| `prog.diversity`         | float | Embedding dispersion               |
| `prog.exec.success_rate` | float | Partial execution viability        |
| `prog.exec.instability`  | float | Sensitivity to small perturbations |
| `prog.score.spread`      | float | Score variance                     |

**Interpretation**

* Low diversity + failure → premature convergence
* High exec instability → executor semantics problem (`F_PROC`)

---

### 4.3 Level 3 (Search & Control)

| Metric                      | Type  | Description               |
| --------------------------- | ----- | ------------------------- |
| `search.depth.max`          | int   | Max depth used            |
| `search.termination_margin` | float | Stop confidence margin    |
| `search.retry_count`        | int   | Number of retries         |
| `search.budget_pressure`    | float | Learned budget saturation |

**Interpretation**

* Early stop + low confidence → `F_SEARCH`
* Excessive retries → masking upstream failures (flag)

---

### 4.4 Level 4 (Memory)

| Metric                     | Type  | Description          |
| -------------------------- | ----- | -------------------- |
| `mem.read.k`               | int   | Retrieved items      |
| `mem.read.similarity`      | float | Avg similarity       |
| `mem.write.gate`           | float | Write probability    |
| `mem.consolidation.action` | enum  | merge / new / ignore |

**Interpretation**

* High similarity but failure → stale memory (`F_MEM`)
* Frequent writes → memory pollution risk

---

### 4.5 Level 5 (Abstraction)

| Metric              | Type  | Description              |
| ------------------- | ----- | ------------------------ |
| `abs.macro.count`   | int   | Active macro tokens      |
| `abs.granularity`   | float | Micro ↔ Macro scale      |
| `abs.override_rate` | float | Macro ignored downstream |

**Interpretation**

* Macro present but ignored → underpowered abstraction
* Macro dominates failures → over-abstraction (`F_ABS`)

---

### 4.6 Level 6 (Verification & Calibration)

| Metric                   | Type  | Description                |
| ------------------------ | ----- | -------------------------- |
| `eval.false_accept_rate` | float | Invalid accepted           |
| `eval.false_reject_rate` | float | Valid rejected             |
| `eval.calibration_error` | float | ECE / similar              |
| `eval.disagreement`      | float | Internal verifier variance |

**Interpretation**

* High false accept → `F_EVAL` critical
* High disagreement → unreliable credit routing

---

## 5. ConceptARC-Specific Metrics

ConceptARC is treated as a **diagnostic instrument**, not a leaderboard.

### 5.1 Per-Concept Bucket Metrics

For each concept bucket:

| Metric                    | Description                        |
| ------------------------- | ---------------------------------- |
| `concept.success_rate`    | Accuracy within bucket             |
| `concept.isolation_score` | Independence from other concepts   |
| `concept.leakage_score`   | Performance degradation when mixed |
| `concept.failure_profile` | Distribution over failure codes    |

Regression is defined as **worsening isolation or increased leakage**, even if global accuracy improves.

---

## 6. Regression Gate Metrics (Phase-Blocking)

Regression gates are **hard checks** evaluated after any architecture or training change.

### 6.1 Mandatory Gates

A change is **blocked** if ANY of the following hold:

1. Any failure category rate increases by > ε without compensating decrease elsewhere
2. `eval.calibration_error` increases monotonically
3. ConceptARC leakage increases for any stable concept bucket
4. Credit attribution collapses to a single Level across tasks
5. Cost decreases only by masking failures (e.g., early termination)

ε is project-defined but MUST be fixed per phase.

---

### 6.2 Gate Output Schema

```
regression.status = PASS | FAIL
regression.violations = [
  { metric, delta, phase, suspected_level }
]
```

No silent passes are allowed.

---

## 7. Logging and Storage Requirements

* All metrics MUST be serializable (JSON/YAML)
* Per-attempt logs MUST include:

  * State ID
  * Phase
  * Dataset / tool source
  * Full failure credit vector
* Aggregation MUST NOT discard tail failures

---

## 8. Final Invariants

* No metric may bypass Level identity
* No failure may be recorded without a taxonomy code
* No regression may be waived without explicit annotation

> **If a behavior cannot be expressed in these metrics, it does not exist for the system.**

---

**End of `metrics.md`**