# System Invariants & Non-Negotiables

**(Authoritative Specification, v2)**

## 0. Document Positioning

### 0.1 Purpose

This document defines the immutable architectural constraints for IRIS as a
**foundation pretraining base model**.

These invariants are **task-agnostic** and **benchmark-agnostic**.

### 0.2 Non-Goal

This document does **not** define any specific benchmark (including ARC) as a
primary optimization target.

Benchmarks are evaluation instrumentation only.

### 0.3 Authority

Any implementation, refactor, or extension that violates this document is
architecturally invalid, even if short-term metrics improve.

---

## 1. Trunk Invariants

### 1.1 Single Trunk

- IRIS must contain exactly one **single trunk** that serves as the primary
  parameter-bearing substrate.
- The trunk is **architecture-agnostic** at this invariant layer. It may be
  attention-based, SSM-based, hybrid, or another equivalent family.
- Introducing a second parallel network at comparable capacity (a second
  "brain") is forbidden.

### 1.2 Trunk Computational Responsibility

- Core cognitive computation must be attributable to trunk learning dynamics,
  including representation formation, control, and the primary credit-assignment
  loop.
- Engineering scaffolding is allowed (for example tokenizer, IO adapters,
  cache, retrieval index), but scaffolding must not hard-code semantic control
  flow.

---

## 2. State IR Invariants

### 2.1 Canonical Internal Representation

- State IR is the canonical internal representation consumed by the trunk and
  shared across levels.
- Ad-hoc internal state channels that bypass canonical State IR are forbidden.

### 2.2 Schema Stability

- State IR schema must remain stable across tasks and data modalities.
- State IR must not be specialized for a single benchmark or benchmark-specific
  token assumptions.

### 2.3 Controlled Evolution

- Any State IR schema change requires explicit, versioned specification updates.
- Silent token/category drift is forbidden.

---

## 3. Learnable Routing and Control Invariants

### 3.1 Learned-by-Default Control

- Routing, gating, and control signals must be learnable and represented in
  model parameters.
- Hard-coded orchestration is not an acceptable primary decision mechanism.

### 3.2 Guardrails vs. Semantics

- Safety gating and resource limits are allowed as engineering guardrails.
- Guardrails must not perform semantic decomposition or decide reasoning steps
  as routine policy.

---

## 4. Level Interface and Mounting Invariants

### 4.1 Level Interfaces Must Exist

- IRIS defines Level interfaces (L0-L6 or an equivalent explicitly defined set).
- Interfaces must exist even when a level implementation is disabled in a given
  checkpoint/config.
- For disabled levels, the system must preserve:
  - IO contract
  - State naming compatibility
  - Trunk interaction points via a stub (no-op or low-capacity adapter)

This ensures levels can be remounted without breaking trunk or State IR
consistency.

### 4.2 Optional Mounting and Configurable Attachment

- Level implementations may be disabled, replaced, or attached at different
  capacities.
- Any mounted implementation must satisfy the corresponding Level contract,
  including observability and credit-assignment compatibility.

---

## 5. Credit Assignment and Failure Recovery Invariants

### 5.1 Attributable Credit Assignment

- The system must support attributable credit assignment for output and behavior.
- Attribution must be traceable to trunk contributions and, when mounted,
  per-level contributions.

### 5.2 Learned Recovery

- If failure-recovery behaviors exist (retry, reflection, repair, self-check),
  they must be part of learned policy.
- Hard-coded recovery flowcharts are forbidden as default behavior.

---

## 6. Status of Benchmarks and Tools

### 6.1 Benchmarks

- Benchmarks (including ARC) are **evaluation instrumentation** in this
  specification.
- Benchmarks are not architecture invariants.
- Benchmarks are not the sole source of training objectives.

### 6.2 Tools

- Toolchains (solver, search, external programs) may be used for data
  generation, monitoring, and evaluation.
- Toolchains must not replace trunk-learned reasoning or control.

---

## 7. Explicit Non-Negotiability Clause

If there is a tradeoff between architectural compliance and short-term
performance or convenience, architectural compliance takes precedence.

---

## 8. Summary

IRIS must always preserve:

- one and only one primary trunk
- architecture-agnostic trunk family at invariant level
- canonical, benchmark-agnostic State IR
- learnable routing and control
- persistent level interfaces with optional mounting
- attributable credit assignment and learned failure recovery
- benchmark/tooling as instrumentation, not intelligence substrate

These are invariants, not suggestions.

---

**End of Document**
