# Routing, Gating, and Control Are Learnable

**(Normative Contract Document)**

## 1. Purpose and Scope

This document defines the **non-negotiable philosophy and technical constraints** governing routing, gating, and control mechanisms in the system. Its purpose is to prevent the erosion of the model’s layered learning structure through hard-coded logic, heuristic shortcuts, or implicit procedural control.

This contract applies to **all inter-Level invocation decisions**, **intra-Level execution control**, and **cross-module fusion behaviors**, regardless of whether such decisions appear “engineering-related” or “performance-motivated.”

---

## 2. Core Principle

> **All routing, gating, and control decisions that affect model behavior MUST be represented in learnable parameters and participate in training, credit assignment, and calibration.**

Control is not an external orchestration layer.
Control is a **first-class learned capability**.

---

## 3. Definitions

### 3.1 Routing

Routing refers to decisions that determine:

* Which Levels are invoked (e.g., L1 rollout vs. L2 program induction),
* Which candidate states, programs, or memories are expanded or pruned,
* Which outputs are selected when multiple candidates exist.

### 3.2 Gating

Gating refers to continuous or discrete-valued signals that:

* Modulate contribution strength (e.g., soft enable/disable),
* Control residual fusion, memory read/write, macro updates,
* Influence budget allocation, search depth, or termination.

### 3.3 Control

Control refers to any mechanism that:

* Alters computational flow, iteration count, or resource allocation,
* Determines stopping conditions or retry behavior,
* Influences exploration vs. exploitation trade-offs.

---

## 4. Mandatory Learnability Requirements

### 4.1 No Behavioral Control Outside Weights

The following are **forbidden** as primary decision mechanisms:

* Hard-coded if/else logic that selects Levels, tools, or execution paths,
* Rule-based thresholds (including fixed confidence cutoffs),
* Hand-tuned heuristics that bypass learned signals,
* Deterministic controllers that do not expose gradients or learning signals.

All such logic, if temporarily unavoidable, **MUST** be explicitly labeled as *technical debt* (see Section 7).

---

### 4.2 Routers Are Not Conditionals

Routers **MUST NOT** degenerate into:

* Static dispatch tables,
* Deterministic pipelines,
* Task-type switches.

A Router is defined as a **parameterized function** producing:

* Soft or probabilistic routing decisions,
* Scores, logits, or gates that can be trained, calibrated, and overridden by learning.

---

## 5. Required Learnable Control Modules

The system **MUST** include learnable parameters for at least the following control surfaces:

### 5.1 Level Invocation Routing

* Decides whether and how strongly each Level (L1–L5) is invoked.
* Implemented via soft gates or scored selectors.
* Even when a Level is effectively “off,” its gate **must exist** and remain learnable.

### 5.2 State Fusion Routing

* Governs how outputs from rollout, program execution, memory retrieval, and macro abstraction are merged back into the State IR.
* Fusion **must not** be fixed summation or concatenation.
* At minimum, gated residual or FiLM-style modulation is required.

### 5.3 Output Selection Routing

* Resolves multiple candidate solutions, programs, or states.
* Selection **must** be learned (e.g., reranking, voting with learned weights).
* Deterministic tie-breaking is prohibited.

---

## 6. Separation of Concerns: What Control Is *Not*

### 6.1 Control Is Not Scheduling

* Execution order, batching, or hardware-level optimizations may exist,
  but **must not encode semantic decisions** about reasoning strategy.

### 6.2 Control Is Not DSL Semantics

* Program execution semantics may be partially structured,
  but **selection, matching, and applicability** of primitives must be learned.

### 6.3 Control Is Not Human-Interpretable Policy

* The system does not optimize for readability or symbolic clarity.
* Learned control may be opaque; this is acceptable and expected.

---

## 7. Hard Control as Explicit Technical Debt

Some hard control may exist temporarily due to tooling or infrastructure limitations (e.g., maximum loop counts, safety caps).

Such mechanisms **MUST** satisfy all of the following:

1. Explicitly documented as *temporary technical debt*, including the intended learned replacement and a removal criterion.
2. Isolated so they can be replaced by learned counterparts.
3. Non-binding under intended operation: hard control may only function as a guardrail (e.g., safety caps), not as routine policy (e.g., fixed beam size, fixed rollout depth, fixed termination rules).
4. Do not encode task-specific heuristics.
5. Do not silently bias credit assignment across Levels.

Failure to label hard control as technical debt constitutes a **contract violation**.

---

## 8. Credit Assignment Compatibility

All routing and gating signals **MUST** be compatible with:

* Backpropagation or surrogate learning signals,
* Cross-Level credit routing (e.g., L6 → L3 → L2/L1),
* Calibration and uncertainty estimation.

Any control decision that cannot, in principle, receive learning feedback is **disallowed**.

---

## 9. Non-Negotiable Constraints Summary

* Routing ≠ if/else
* Gating ≠ fixed thresholds
* Control ≠ external orchestration
* Efficiency optimizations ≠ behavioral logic

Violations of these constraints undermine the layered architecture and are considered **system-level failures**, not implementation details.

---

## 10. Design Intent (Non-Normative)

The long-term objective is a system where:

* Strategy emerges from learned signals,
* Resource allocation is adaptive and self-calibrating,
* Failures improve future control policies rather than being patched around.

This document exists to ensure that such emergence remains structurally possible.

---

**End of Contract**
