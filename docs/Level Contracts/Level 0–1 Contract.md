# Level 0-1 Contract

**IO Alignment, Representation Surface, and Short-Horizon Consistency**

---

## 0. Scope and Intent

This document defines the contract for Level 0-1 in a foundation-model setting.

- Level 0 handles input/output alignment and representation normalization.
- Level 1 handles short-horizon consistency, local aggregation, and lightweight state maintenance.
- This contract is benchmark-agnostic and task-agnostic.

---

## Authority & Optional Mounting

- This document defines a **Level Interface Contract**, not a fixed implementation or fixed capacity requirement.
- **Interface must exist**: even when this level is disabled in a checkpoint/config, its interface and I/O schema must remain available as a stub (no-op or low-capacity adapter).
- **Implementation may be mounted/disabled/replaced**: any mounted version must satisfy this contract (I/O consistency, observability, and credit attribution compatibility).
- Hard-orchestrated flow cannot replace learned control. If this level emits control/recovery signals, those signals must be learnable, trainable, and attributable.

---

## 1. Responsibilities

### 1.1 Level 0 Responsibilities

- Convert raw input channels into State IR-aligned observation fields.
- Apply format normalization and schema-safe tokenization.
- Maintain modality-agnostic input handling (text/image/other structured sources).

### 1.2 Level 1 Responsibilities

- Preserve local consistency across adjacent steps.
- Provide short-horizon memory/compression signals without taking over global reasoning.
- Expose uncertainty and representation quality signals for downstream levels.

### 1.3 Peripheral Modules

- Tokenizers, patch embedders, and compression helpers are allowed as peripherals.
- Peripherals must not become a semantic decision core or bypass trunk-level reasoning.

---

## 2. Interface

### Inputs

- `state_in`: canonical State IR (or schema-compatible reference/slice).
- `context_in`: optional external context.
- `control_in`: optional upstream control signals.
- `resource_budget`: optional limits (time/steps/memory).

### Outputs

- `state_out`: State IR updates for observation/surface-form fields.
- `control_out`: optional downstream control hints (default neutral).
- `diagnostics`: observable signals including confidence/uncertainty, failure tags, credit hints, plus encoding stats (for example normalization ratio, compression ratio, OOV/unknown statistics when applicable).

### Stub Behavior (when disabled)

- `state_out = state_in` (or minimal schema normalization only).
- `control_out` returns neutral/no-op.
- `diagnostics` must still emit a disabled marker and basic summary stats.

### Observability & Logging (minimum)

- Must support sampled logging of input summary, output summary, key gates/logits (if present), and failure/error codes (if present).
- Attribution must be traceable to trunk contribution and this level contribution, including stub mode.

---

## 3. Prohibited Patterns

- Benchmark-shaped assumptions embedded into contract semantics.
- Fixed mandatory module classes as the only valid implementation path.
- Hard-coded semantic routing that bypasses learned control.
- Semantic closed loops outside trunk dynamics.

---

## 4. Compliance Checklist

1. Is the interface preserved even when disabled (with a valid stub)?
2. In disabled mode, does State IR remain consistent and unbroken?
3. Is there any semantic closed loop bypassing trunk (violation)?
4. Is minimum observability/diagnostics provided?
5. If control/routing signals exist, are they learned, trainable, and attributable?
6. Is any benchmark-specific assumption embedded in contract semantics?

---

**End of Level 0-1 Contract**