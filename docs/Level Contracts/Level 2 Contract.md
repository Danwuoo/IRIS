# Level 2 Contract

**Program Induction, Proposal, and Neural Execution Layer**

---

## 0. Scope and Intent

This document defines the **exclusive responsibilities, guarantees, and prohibitions** of **Level 2**.

Level 2 is the system’s **program induction layer**. Its role is to:

* Propose **structured, reusable procedural hypotheses**
* Execute those hypotheses **inside the neural substrate**
* Score and expose their outcomes to higher-level controllers

Level 2 is the **first layer allowed to reason over structure**, but it is **not allowed to externalize that structure into hard symbolic control**.

Any implementation that turns Level 2 into a hand-written DSL executor, rule engine, or planner is considered **architecturally invalid**, regardless of performance.

---

## 1. Architectural Positioning

### 1.1 Role in the Stack

* Level 2 sits **above**:

  * Perception and dynamics (Level 0–1)
* Level 2 sits **below**:

  * Meta-search, budget control, and termination (Level ≥3)

Level 2 **does not own**:

* Search depth
* Resource allocation
* Stopping criteria
* Memory policy

It **does own**:

* Program hypothesis space
* Program representation
* Program-conditioned state transformation

---

## 2. Definition of “Program” (Canonical Meaning)

Within this system, a **program** is defined as:

> A **learned, structured, tokenized procedure** that maps a State IR to another State IR (or to an answer token), whose semantics are *partially invariant across tasks*.

A program is **not required** to be:

* Human-readable
* Deterministic
* Symbolically interpretable

A program **must be**:

* Represented as tokens
* Embedded in the same latent space as State IR
* Executable by neural operators

---

## 3. Mandatory Level 2 Modules

All Level 2 implementations **must include** the following **weight-bearing** modules.

### 3.1 Program IR Embedding

**Purpose**
Provide a canonical latent representation for programs.

**Requirements**

* Program tokens must:

  * Share the same hidden dimension as State IR tokens
  * Remain outside the canonical State IR sequence (`Z`); programs are not State IR tokens even if they share a latent space
  * Support compositional structure (sequence, tree, or graph)
* Embedding must be learned
* No hard-coded opcode semantics are permitted

**Forbidden**

* Fixed symbolic AST without learned embeddings
* String-based or text-only programs without neural grounding

---

### 3.2 Program Proposal Head

**Purpose**
Generate candidate procedural hypotheses.

**Input**

* Contextualized State IR ( \tilde{Z} )
* Task and global tokens

**Output**

* A bounded set of candidate programs:
  [
  { P_1, P_2, \dots, P_K }
  ]

**Requirements**

* Proposal must be:

  * Probabilistic
  * Learnable
  * Conditioned on State IR
* Program length must be bounded but flexible
* Beam size (K) is externally controlled (not internal logic)

**Forbidden**

* Deterministic rule enumeration
* Hard-coded templates tied to specific domains
* If-else trees masquerading as “programs”

---

### 3.3 Neural Primitive Executor

**Purpose**
Execute a program **within the neural system**, not outside it.

**Input**

* Program tokens (P_i)
* State IR tokens (Z)

**Output**

* Updated State IR (Z') or output candidate tokens

**Hard Requirements**

* Core execution **must occur in learned operators**
* Primitive selection, matching, and parameterization must be differentiable
* Execution must expose intermediate representations to gradients

**Allowed (Transitional Only)**

* Limited hard control-flow guardrails (e.g., a maximum unrolling depth cap), explicitly labeled as temporary technical debt
* Minimal symbolic scaffolding *around* neural primitives

Any transitional hard control must satisfy the constraints in **Routing, Gating, and Control Are Learnable** (Section 7).

**Explicitly Forbidden**

* Pure symbolic DSL interpreters
* Deterministic rule engines
* “Neural proposer + symbolic executor” split

If the executor can be replaced by a Python function without changing learned behavior, the implementation is invalid.

---

### 3.4 Program Scorer / Value Head

**Purpose**
Provide an internal assessment of program quality.

**Input**

* Program representation
* Execution result representations

**Output**

* Scalar or vector scores

**Notes**

* Scores are **not decisions**
* They are signals for:

  * Reranking
  * Search control
  * Credit assignment

---

## 4. Input / Output Semantic Contract

### 4.1 Input Assumptions

Level 2 must assume:

* State IR is incomplete and uncertain
* Programs may fail, partially succeed, or be ill-posed
* Multiple incompatible programs may coexist

### 4.2 Output Guarantees

Level 2 must guarantee:

* Outputs are explicit tokens
* No hidden mutable state exists outside tokens
* Execution effects are visible to:

  * Level 3 (search control)
  * Level 6 (verification and credit)

---

## 5. Relationship to Search and Control

### 5.1 What Level 2 Does NOT Control

Level 2 **must not decide**:

* How many programs to propose
* How deep to search
* When to stop
* Whether to retry or backtrack

Those decisions belong to **Level 3 and above**.

### 5.2 What Level 2 MUST Support

Level 2 **must support**:

* Partial execution
* Aborted execution
* Reuse of programs across states
* Scoring without commitment

---

## 6. Training and Credit Assignment Assumptions

* Level 2 is trained via:

  * Downstream task success
  * Verification feedback
  * Comparative program scoring
* Gradients may arrive:

  * Late
  * Sparse
  * Indirectly via higher levels

Therefore:

* Program representations must be stable
* Executors must be robust to noisy supervision
* Proposal diversity is preferred over early convergence

---

## 7. Forbidden Failure Modes

Level 2 must **not collapse into**:

* A planner encoded as weights
* A heuristic rule set
* A symbolic solver wrapped in neural I/O
* A single monolithic “reasoning head”

If removing Level 3 reduces Level 2 to a complete solver, the design is incorrect.

---

## 8. Explicit Non-Goals (Level 2)

Level 2 is **explicitly not**:

* A full agent controller
* A search algorithm
* A symbolic programming language
* A human-readable reasoning trace generator

Interpretability is optional; **neural executability is mandatory**.

---

## 9. Stability and Evolution Clause

Future versions may:

* Improve program representations
* Increase executor expressiveness
* Reduce remaining hard control

Future versions may **not**:

* Remove neural execution
* Externalize logic into symbolic code
* Collapse Level 2 into Level 3 or vice versa

---

**End of Level 2 Contract**
