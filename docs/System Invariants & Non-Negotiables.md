# System Invariants & Non-Negotiables

**(Authoritative Specification)**

## 0. Scope and Authority

This document defines **hard invariants** of the system.

They are **not** optimization hints, design preferences, or defaults.

Any agent, human or automated, operating on this model **must** treat these constraints as non-overridable.

Violations invalidate architectural correctness, even if empirical performance appears acceptable.

---

## 1. Trunk Uniqueness and Capacity Invariant

### 1.1 Single Large-Capacity Trunk

- The system **must contain exactly one** large-capacity neural trunk.
- This trunk is the **only** component permitted to hold the majority of model parameters.

Formally:

- The trunk (SSM/Mamba-based) is the **unique locus** of global contextualization.
- No other module may replicate, shadow, or bypass trunk-level capacity.

### 1.2 Non-Substitutability

- The trunk **cannot** be replaced, emulated, or approximated by:
    - Attention side-networks
    - Per-level deep stacks
    - Tool-level reasoning graphs
    - External planners with equivalent capacity

Any attempt to introduce a “secondary trunk,” even implicitly, is forbidden.

---

## 2. Mandatory Existence of All Levels

### 2.1 Structural Completeness

- All Levels **L0 through L6 must exist** in the parameter topology.
- Existence means:
    - Distinct parameter tensors are present.
    - Parameters are loadable and addressable.
    - Gradients can, in principle, flow to them.

A Level being “unused,” “gated off,” or “degenerate” at runtime does **not** exempt it from existence.

### 2.2 No Level Collapsing

- No Level may be collapsed into another Level’s logic.
- No Level may be reinterpreted as:
    - Pure control flow
    - A training-only artifact
    - A heuristic wrapper

Each Level represents a **distinct functional responsibility**, not an optimization convenience.

---

## 3. Weight-Based Control Invariant

### 3.1 Control Must Live in Parameters

All routing, gating, prioritization, and termination decisions must be:

- Parameterized
- Differentiable or relaxable
- Represented explicitly in learned weights

This includes, but is not limited to:

- Level invocation
- Search depth control
- Budget allocation
- Termination decisions
- Candidate selection and pruning

### 3.2 Router ≠ If–Else

- Hard-coded if–else logic is **not** an acceptable substitute for routing.
- Rule-based branching may exist **only** as a temporary technical debt, and must be:
    - Clearly marked
    - Isolated
    - Designed to be removable

If a decision influences *which computation happens*, it must ultimately be learnable.

---

## 4. Prohibition of Pure Handwritten DSL Execution

### 4.1 No Symbolic-Only Executors

- The system **must not** rely on a purely deterministic, handwritten DSL executor as its core reasoning engine.
- Program execution primitives must involve learned components.

Acceptable:

- Learned soft selection over objects
- Learned relation matching
- Parameterized transform operators
- Hybrid control flow with learned inner semantics

Forbidden:

- Fully symbolic interpreters where learning only ranks outputs
- Executors that operate independently of trunk representations

### 4.2 Executor Participation in Credit Assignment

- Program execution must participate in credit assignment.
- Failure signals must be attributable to execution behavior, not only proposal quality.

---

## 5. State IR Canonicality

### 5.1 Single Canonical State Representation

- There exists exactly one canonical **State IR**.
- All Levels, without exception, communicate through this IR (or projections thereof).

The trunk operates over this IR as a unified token sequence.

### 5.2 No Ad-Hoc Token Extensions

- Token types are closed under extension.
- Agents **must not** introduce new token categories without a system-level revision.

Any attempt to “just add a token type” is an architectural violation.

---

## 6. Trunk–Head Contract Boundary

### 6.1 Trunk Obligations

The trunk guarantees:

- Global contextualization of the full State IR
- Cross-token interaction
- Stable shared representations for all Levels

### 6.2 Head Restrictions

Heads and adapters **must not**:

- Demand attention mechanisms inside the trunk
- Require the trunk to encode task-specific control logic
- Depend on private, head-specific state propagation

Heads consume trunk representations; they do not redefine trunk semantics.

---

## 7. Anti-Shortcut Invariant

### 7.1 No Heuristic Replacement of Levels

- Performance shortcuts that bypass Levels are forbidden.
- Examples of forbidden shortcuts:
    - Planner-only Level 2
    - Rule-only Level 3 termination
    - Tool-first execution replacing Level 2 semantics
    - External memory without learned read/write gates

If a function exists conceptually, it must exist **in weights**.

### 7.2 No End-to-End Loss Collapse

- Training must respect level structure.
- A single undifferentiated end-to-end loss that ignores level responsibility boundaries is disallowed.

Credit assignment semantics must preserve:

- Inter-level causality
- Responsibility localization

---

## 8. Persistence of Routing and Fusion Parameters

- Routing, fusion, and selection parameters are **first-class citizens**.
- They must be:
    - Versioned
    - Saved with the model
    - Treated as part of the core system

They are not auxiliary metadata.

---

## 9. Explicit Non-Negotiability Clause

If a choice arises between:

- Architectural compliance
- Short-term performance, engineering convenience, or simplicity

**Architectural compliance wins without exception.**

Any agent that optimizes away these invariants is acting incorrectly, even if results improve.

---

## 10. Summary (Non-Exhaustive)

The system **must always** satisfy:

- One and only one large-capacity trunk
- Mandatory existence of all Levels
- Learnable routing and control
- No pure symbolic executors
- Single canonical State IR
- Clear trunk/head responsibility boundaries
- No heuristic shortcuts replacing weights

These are **invariants**, not suggestions.

---

**End of Document**