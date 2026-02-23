# Level 2 Contract

**Latent Procedure Induction and Mid-Level Program Structure**

---

## 0. Scope and Intent

This document defines the contract for Level 2 as a benchmark-agnostic, learned
procedure layer.

Level 2 is responsible for inducing reusable latent procedures from State IR and
providing structured intermediate reasoning signals without collapsing into a
handwritten solver.

---

## Authority & Optional Mounting

- This document defines a **Level Interface Contract**, not a fixed implementation or fixed capacity requirement.
- **Interface must exist**: even when this level is disabled in a checkpoint/config, its interface and I/O schema must remain available as a stub (no-op or low-capacity adapter).
- **Implementation may be mounted/disabled/replaced**: any mounted version must satisfy this contract (I/O consistency, observability, and credit attribution compatibility).
- Hard-orchestrated flow cannot replace learned control. If this level emits control/recovery signals, those signals must be learnable, trainable, and attributable.

---

## 1. Responsibilities

- Induce latent procedure candidates from canonical State IR.
- Emit reusable mid-level structure (for example subgoal sketches, constraint bundles, or action schemas in latent form).
- Support downstream control without forcing deterministic execution flow.

Level 2 must remain learned and differentiable in semantics. It must not become
an externalized symbolic engine.

---

## 2. Interface

### Inputs

- `state_in`: canonical State IR (or schema-compatible reference/slice).
- `context_in`: optional external context.
- `control_in`: optional decomposition/control hints.
- `resource_budget`: optional limits (time/steps/memory).

### Outputs

- `state_out`: State IR augmented with latent procedure candidates/program-like tokens.
- `control_out`: optional decomposition suggestions (non-binding, non-hardcoded).
- `diagnostics`: confidence/uncertainty, failure tags, credit hints, plus program quality signals (for example diversity, collapse indicators, consistency scores).

### Stub Behavior (when disabled)

- `state_out = state_in` (or minimal schema normalization only).
- `control_out` returns neutral/no-op.
- `diagnostics` must still emit a disabled marker and basic summary stats.

### Observability & Logging (minimum)

- Must support sampled logging of candidate summaries, scoring summaries, key gates/logits (if present), and failure/error codes (if present).
- Attribution must be traceable to trunk contribution and this level contribution, including stub mode.

---

## 3. Prohibited Patterns

- Handwritten DSL executor as primary semantics.
- Fixed search policy/flowchart embedded in this level.
- Rule-only planner behavior replacing learned procedure induction.
- Benchmark-shaped latent schema assumptions.

---

## 4. Compliance Checklist

1. Is the interface preserved even when disabled (with a valid stub)?
2. In disabled mode, does State IR remain consistent and unbroken?
3. Is there any semantic closed loop bypassing trunk (violation)?
4. Is minimum observability/diagnostics provided?
5. If control/routing signals exist, are they learned, trainable, and attributable?
6. Is any benchmark-specific assumption embedded in contract semantics?

---

**End of Level 2 Contract**