# Level 0–1 Contract

**Perception and World-Dynamics Layer Specification**

---

## 0. Scope and Purpose

This document defines the **non-negotiable contract** for **Level 0** and **Level 1** modules in the system.

Level 0–1 are responsible for:

* Converting raw observations into **canonical State IR tokens**
* Providing a **learned, weight-based notion of environment dynamics**
* Supplying uncertainty, constraints, and state transitions to higher levels

This contract explicitly **does not** describe:

* Planning, search, or program induction (Level ≥2)
* Control-flow logic or routing policies (handled elsewhere)
* Task-specific heuristics or symbolic solvers

Any implementation that violates this contract is considered **architecturally invalid**, even if it performs well empirically.

---

## 1. Architectural Positioning

### 1.1 Role in the Overall System

* Level 0–1 sit **below** all reasoning, planning, and abstraction layers.
* They are **upstream producers** of State IR and **downstream consumers** of Trunk representations.
* They must be usable in both:

  * Single-step (static) inference
  * Multi-step rollout (agentic / interactive) settings

### 1.2 Capacity and Authority Limits

* Level 0–1 **may not**:

  * Encode task-specific strategies
  * Decide termination
  * Perform search, branching, or symbolic execution
* Level 0–1 **must**:

  * Represent uncertainty
  * Remain differentiable and learnable end-to-end
  * Preserve information rather than compress it prematurely

---

## 2. Level 0 Contract: State IR Construction

### 2.1 Functional Responsibility

Level 0 is responsible for transforming raw inputs into a **valid initial State IR**:

[
Z_0 = [T; G; O; R; X]
]

where token semantics are canonical and shared system-wide.

### 2.2 Mandatory Modules

All Level 0 implementations **must include** the following weight-bearing modules:

#### 2.2.1 Objectizer Head

* **Input**: Raw perceptual input (grid, image, symbolic stream, etc.)
* **Output**: Object tokens (O_0)
* **Requirements**:

  * Produces a *set* or *unordered collection*
  * Supports soft assignment / slot uncertainty
  * Learned extraction (no hard-coded connected components)

#### 2.2.2 Relation Inducer

* **Input**: Object tokens (O_0)
* **Output**: Relation tokens (R_0)
* **Requirements**:

  * Relations must be explicit tokens (not implicit matrices)
  * Edge existence and type must be learnable
  * No fixed adjacency rules

#### 2.2.3 Eventizer

* **Input**: State differences or interaction signals
* **Output**: Event tokens (X_0)
* **Requirements**:

  * Must exist even in static tasks
  * Can emit empty or near-zero tokens when unused
  * Must not encode control or intent

### 2.3 Forbidden Shortcuts (Level 0)

Level 0 **must not**:

* Emit pre-solved task features
* Collapse objects into a single global vector
* Hard-code domain rules (e.g., grid connectivity, physics laws)
* Bypass tokenization by writing directly into Trunk internals

---

## 3. Level 1 Contract: World Dynamics and Local Consistency

### 3.1 Functional Responsibility

Level 1 provides a **learned model of local state evolution**, without planning or intent.

It answers:

* “If this state changes, *how* might it change?”
* “How confident are we in this prediction?”
* “Does this candidate state violate learned constraints?”

It does **not** answer:

* “Which future is better?”
* “Which action should be taken?”
* “When should we stop?”

---

### 3.2 Mandatory Modules

#### 3.2.1 Dynamics Operator

* **Input**:

  * Contextualized state (\tilde{Z}_t) (post-Trunk)
  * Optional action/tool tokens
* **Output**:

  * Predicted next state (\hat{Z}_{t+1}) or (\Delta Z)
* **Requirements**:

  * Fully neural and learnable
  * Supports multi-step unrolling
  * Does not branch or search

#### 3.2.2 Constraint / Energy Head

* **Input**: Candidate state tokens
* **Output**: Scalar or token-wise constraint scores
* **Purpose**:

  * Soft validity
  * Plausibility filtering
* **Notes**:

  * Must not enforce hard rejection
  * Higher levels decide usage

#### 3.2.3 Uncertainty Head

* **Input**: Rollout or prediction representations
* **Output**: Uncertainty estimates
* **Requirements**:

  * Differentiable
  * Calibratable
  * Consumable by Level 3 and Level 6

---

## 4. Input / Output Semantic Contract

### 4.1 Input Assumptions

Level 0–1 **must assume**:

* Inputs are incomplete, noisy, or ambiguous
* Higher levels may reinterpret or override outcomes
* Their outputs are *hypotheses*, not truths

### 4.2 Output Guarantees

Level 0–1 **must guarantee**:

* Outputs are valid State IR tokens
* Token ordering and typing follow canonical spec
* No hidden side channels or auxiliary states exist outside tokens

---

## 5. Interaction with the Trunk

* Level 0 produces **pre-Trunk tokens**
* Level 1 consumes **post-Trunk contextualized tokens**
* Neither level may:

  * Inject private recurrent state into the Trunk
  * Assume specific Trunk internals (e.g., attention, SSM form)

All communication is via **explicit token representations only**.

---

## 6. Training and Credit Assignment Assumptions

* Level 0–1 must be trainable via:

  * Downstream task loss
  * Rollout consistency
  * Verification feedback routed from higher levels
* They must tolerate:

  * Being partially gated off
  * Sparse or delayed gradients
* They must not rely on:

  * Dense step-wise supervision
  * Hand-aligned labels

---

## 7. Explicit Non-Goals (Level 0–1)

Level 0–1 are **explicitly not**:

* Planners
* Solvers
* Program executors
* Symbolic reasoners
* Task-specific feature engineers

Any attempt to “upgrade” Level 0–1 into these roles is a violation of system design.

---

## 8. Contract Stability Clause

This contract is **stable across tasks and domains**.

Future changes may:

* Extend token types
* Improve parameterization
* Refine uncertainty modeling

Future changes may **not**:

* Remove mandatory modules
* Introduce hard-coded logic
* Shift planning or control into Level 0–1

---

**End of Level 0–1 Contract**