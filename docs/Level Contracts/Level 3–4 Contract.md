# Level 3-4 Contract

**Learned Decomposition, Multi-Step Control, and Resource Policy**

---

## 0. Scope and Intent

This document defines the contract for Level 3-4 as the learned policy layer for
multi-step decomposition and control.

- Level 3 focuses on decomposition and subgoal management.
- Level 4 focuses on multi-step control, budget allocation, branching, and
  repair-trigger policy.

Both levels are policy layers, not benchmark-specific schedulers.

---

## Authority & Optional Mounting

- This document defines a **Level Interface Contract**, not a fixed implementation or fixed capacity requirement.
- **Interface must exist**: even when this level is disabled in a checkpoint/config, its interface and I/O schema must remain available as a stub (no-op or low-capacity adapter).
- **Implementation may be mounted/disabled/replaced**: any mounted version must satisfy this contract (I/O consistency, observability, and credit attribution compatibility).
- Hard-orchestrated flow cannot replace learned control. If this level emits control/recovery signals, those signals must be learnable, trainable, and attributable.

---

## 1. Responsibilities

- Produce learned decomposition hints and subgoal progression signals.
- Emit learned control signals for next-step intent, branching preference, and
  budget usage.
- Coordinate multi-step progress without hardcoding an execution schedule.

---

## 2. Interface

### Inputs

- `state_in`: canonical State IR (or schema-compatible reference/slice).
- `context_in`: optional external context and optional Level 2 procedure hints.
- `control_in`: optional upstream control signals.
- `resource_budget`: optional limits (time/steps/memory).

### Outputs

- `state_out`: State IR updates for plan trace/subgoal-trace fields (if defined by schema).
- `control_out`: next-step intention, gate logits, branch weights, or equivalent learned control suggestions.
- `diagnostics`: confidence/uncertainty, failure tags, credit hints, plus step-efficiency, loop/stall indicators, and budget usage summary.

### Stub Behavior (when disabled)

- `state_out = state_in` (or minimal schema normalization only).
- `control_out` returns neutral/no-op so trunk control remains live.
- `diagnostics` must still emit a disabled marker and basic summary stats.

### Observability & Logging (minimum)

- Must support sampled logging of subgoal/control summaries, key gates/logits,
  branch/termination summaries, and failure/error codes (if present).
- Attribution must be traceable to trunk contribution and this level contribution, including stub mode.

---

## 3. Prohibited Patterns

- Rule-based scheduler as the default semantics.
- Hardcoded branch/termination policy replacing learned control.
- Deterministic flowchart that bypasses trunk-mediated control dynamics.
- Benchmark-shaped control assumptions encoded as contract behavior.

---

## 4. Compliance Checklist

1. Is the interface preserved even when disabled (with a valid stub)?
2. In disabled mode, does State IR remain consistent and unbroken?
3. Is there any semantic closed loop bypassing trunk (violation)?
4. Is minimum observability/diagnostics provided?
5. If control/routing signals exist, are they learned, trainable, and attributable?
6. Is any benchmark-specific assumption embedded in contract semantics?

---

**End of Level 3-4 Contract**