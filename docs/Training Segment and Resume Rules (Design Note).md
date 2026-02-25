# Training Segment and Resume Rules

**Document Type:** Design Note (Non-normative)  
**Status:** Engineering guidance only  
**Non-Override Clause:** This note does not override system invariants, State IR contracts, Level contracts, or control learnability rules.

---

## 0. Purpose

Define segment-based training, checkpoint boundaries, accumulation boundaries, and restart rules to avoid semantic drift during long runs.

---

## 1. Definitions

**Training Segment**  
An atomic training unit that groups a fixed data slice, its traces, and its metric emissions.

**Segment Status**

- `PENDING`: execute path completed, apply not committed
- `APPLIED`: optimizer/state update committed

A segment is either fully applied or not applied at all.

**Micro Step**  
One forward/backward pass on a microbatch.

**Optimizer Step**  
One applied update after a full accumulation window.

---

## 2. Two-Phase Commit: Execute / Apply

**Execute (interruptible)**

- Forward, rollout, verifier, credit routing, loss aggregation
- Gradient accumulation bookkeeping (no weight update)

**Apply (atomic)**

- Update model weights and optimizer state
- Update all behavior-affecting states (for example memory/macro stats/RNG state)

This preserves failure-recovery semantics and avoids partial credit assignment.

---

## 3. Segment and Accumulation Rules

1. Accumulation windows must be fully contained inside a single segment.
2. Cross-segment accumulation is forbidden.
3. A segment boundary must align to optimizer-step boundary.
4. Segment completion is recognized only after `APPLIED`.

If interruption occurs before apply, the segment remains `PENDING` and must be replayed.

---

## 4. Checkpoint Boundary and Frequency Rules

- Only write checkpoints after an `APPLIED` segment.
- Never checkpoint mid-execute.
- Maintain an append-only journal for `PENDING -> APPLIED`.
- Small checkpoint cadence: every `100` optimizer steps.
- Full checkpoint cadence: every `1000` optimizer steps.

### Minimum checkpoint content

- Model weights
- Optimizer state
- RNG state
- `segment_id_last_applied`
- `optimizer_step_id_last_applied`

### Recommended metadata

- `run_id`
- `dataset_slice_id`
- `code_version_hash`
- `config_hash`
- `phase`
- `tolerance_profile_id`

---

## 5. Restart Rules (Exactly-Once Apply)

- On resume, if the last segment is `PENDING`, discard and replay it.
- Only `APPLIED` segments are effective training progress.
- Resume must restore all behavior-affecting states.
- Resume path must not silently alter failure distribution.

---

## 6. Resume Consistency Signals (Regression-Friendly)

Segment-aligned comparisons should use:

- `task.validity_score`
- `task.confidence`
- `failure.credit`

The regression harness compares uninterrupted vs resumed paths at identical segment boundaries.

Gate linkage:

- Must satisfy `S8 Resume Consistency Regression` when active by phase policy.

---

## 7. Explicit Non-Goals

- This is not a new control policy.
- This does not introduce new State IR tokens or schema changes.
- This does not change credit routing ownership (L6 diagnosis, L3 recovery policy).

---

**End of Design Note**
