# Training Segment and Resume Rules

**Document Type:** Design Note (Non-normative)
**Status:** Engineering guidance only
**Non-Override Clause:** This note does not override system invariants, State IR contracts, Level contracts, or control learnability rules.

---

## 0. Purpose

Define segment-based training, checkpoint boundaries, and restart rules to avoid semantic drift when resuming training runs.

---

## 1. Definitions

**Training Segment**

An atomic unit of training that groups a fixed task subset or batch slice plus its derived traces and metrics.

**Segment Status**

* `PENDING`: Execute completed, apply not committed.
* `APPLIED`: Weights and state updates committed.

A segment is either fully applied or not applied at all.

---

## 2. Two-Phase Commit: Execute / Apply

**Execute (interruptible)**

* Forward, rollout, verifier, credit routing, loss aggregation.
* No weight or optimizer updates.

**Apply (atomic)**

* Update weights and optimizer state.
* Update any state that affects future behavior (for example: memory, macro statistics).

This preserves failure recovery semantics and avoids partial credit assignment.

---

## 3. Checkpoint Boundary Rules

* Only write checkpoints after an `APPLIED` segment.
* Never checkpoint mid-execute.
* Maintain an append-only segment journal to track `PENDING -> APPLIED` transitions.

**Minimum checkpoint content**

* Model weights
* Optimizer state
* RNG state (Python/torch/numpy if used)
* `segment_id_last_applied`

**Recommended metadata**

* `run_id`
* `dataset_slice_id`
* `code_version_hash`
* `config_hash`

---

## 4. Restart Rules (Exactly-Once Apply)

* On resume, if the last segment is `PENDING`, discard and replay it.
* Only `APPLIED` segments are considered effective training progress.
* Resume must restore all states that can influence behavior to preserve semantic consistency.

---

## 5. Resume Consistency Signals (Regression-Friendly)

Segment-aligned comparisons should use existing metrics:

* `task.validity_score`
* `task.confidence`
* `failure.credit`

The regression harness should compare uninterrupted vs resumed paths at the same segment boundary.

---

## 6. Explicit Non-Goals

* This is not a new control policy.
* This does not introduce new State IR tokens or schema changes.
* This does not change credit routing or learnability requirements.

---

**End of Design Note**
