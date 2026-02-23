# Level 5-6 Contract

**Self-Evaluation, Recovery Policy, and Credit Attribution Hooks**

---

## 0. Scope and Intent

This document defines the contract for Level 5-6 as the learned self-evaluation
and recovery-attribution layer.

- Level 5 focuses on evaluation and verification signal quality.
- Level 6 focuses on recovery policy hooks and credit-assignment integration.

Both levels must remain learned, observable, and attribution-compatible.

---

## Authority & Optional Mounting

- This document defines a **Level Interface Contract**, not a fixed implementation or fixed capacity requirement.
- **Interface must exist**: even when this level is disabled in a checkpoint/config, its interface and I/O schema must remain available as a stub (no-op or low-capacity adapter).
- **Implementation may be mounted/disabled/replaced**: any mounted version must satisfy this contract (I/O consistency, observability, and credit attribution compatibility).
- Hard-orchestrated flow cannot replace learned control. If this level emits control/recovery signals, those signals must be learnable, trainable, and attributable.

---

## 1. Responsibilities

- Emit learned self-evaluation signals, including uncertainty and failure tags.
- Provide repair suggestions and credit-assignment hints as learned outputs.
- Support recovery policy without collapsing into hardcoded retry scripts.

---

## 2. Interface

### Inputs

- `state_in`: canonical State IR (or schema-compatible reference/slice).
- `context_in`: optional external context, including behavior trace/output summary.
- `control_in`: optional upstream control signals.
- `resource_budget`: optional limits (time/steps/memory).

### Outputs

- `state_out`: State IR updates with evaluation summary and credit hints.
- `control_out`: retry/reflect/branch gate logits or equivalent learned recovery suggestions (optional).
- `diagnostics`: confidence/uncertainty, failure tags, credit hints, error signatures, and recovery recommendation summary.

### Stub Behavior (when disabled)

- `state_out = state_in` (or minimal schema normalization only).
- `control_out` returns neutral/no-op.
- `diagnostics` must still emit a disabled marker and basic summary stats.

### Observability & Logging (minimum)

- Must support sampled logging of verification/recovery summaries, key gates/logits (if present), and failure/error codes (if present).
- Attribution must be traceable to trunk contribution and this level contribution, including stub mode.

---

## 3. Prohibited Patterns

- Hardcoded "if wrong then rerun N times" as default semantics.
- Rule-only verifier behavior that bypasses learned evaluation.
- Fixed recovery flowcharts replacing learned policy.
- Benchmark-shaped acceptance/rejection policy in contract semantics.

---

## 4. Compliance Checklist

1. Is the interface preserved even when disabled (with a valid stub)?
2. In disabled mode, does State IR remain consistent and unbroken?
3. Is there any semantic closed loop bypassing trunk (violation)?
4. Is minimum observability/diagnostics provided?
5. If control/routing signals exist, are they learned, trainable, and attributable?
6. Is any benchmark-specific assumption embedded in contract semantics?

---

**End of Level 5-6 Contract**