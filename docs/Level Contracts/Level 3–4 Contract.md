# Level 3–4 Contract

**Meta-Search Control and Program / Concept Memory**

---

## 0. Scope and Intent

This document defines the **exclusive responsibilities, authority boundaries, and invariants** of **Level 3** and **Level 4**.

Together, these levels are responsible for:

* Governing **how computation is spent**, not *what* is computed
* Managing **search, retries, and termination** without solving the task
* Providing **long-horizon reuse of programs and abstractions** without hard-coding behavior

They form the system’s **control and memory substrate**, but **not its intelligence core**.

Any implementation that turns Level 3–4 into a planner, solver, or hand-written policy engine is considered **architecturally invalid**, even if it improves efficiency.

---

## 1. Architectural Positioning

### 1.1 Layer Roles at a Glance

| Level   | Primary Role                   | Does NOT Do                       |
| ------- | ------------------------------ | --------------------------------- |
| Level 3 | Meta-search & resource control | Solve tasks, induce programs      |
| Level 4 | Program / concept memory       | Decide usage policy heuristically |

### 1.2 Authority Separation

* **Level 3** controls *when* and *how much* computation occurs
* **Level 4** controls *what is stored and retrieved*
* **Neither level** controls:

  * Task semantics
  * Program content
  * Execution logic

All decisions must be **soft, learned, and weight-based**.

---

## 2. Level 3 Contract: Meta-Search and Resource Control

### 2.1 Functional Responsibility

Level 3 is responsible for **meta-level decisions** about computation, including:

* Search breadth and depth
* Invocation of other levels
* Termination and retry decisions

Level 3 reasons **about the process**, not the problem.

---

### 2.2 Mandatory Level 3 Modules

All Level 3 implementations **must include** the following **learned modules**.

---

#### 2.2.1 Budget Controller

**Purpose**
Allocate computational resources dynamically.

**Input**

* Contextualized State IR
* Signals from Level 1 (uncertainty)
* Signals from Level 6 (confidence, failure diagnostics), treated as evidence rather than direct control

**Output**

* Soft control parameters, e.g.:

  * Proposal beam size
  * Rollout depth
  * Retrieval count
  * Tool / module enablement
  * Stop / continue logits

Only Level 3 may emit these compute-control parameters. Other levels may provide evidence, but must not directly set budgets or termination.

**Requirements**

* Outputs must be continuous or probabilistic
* No hard thresholds or fixed schedules
* Must be trainable end-to-end

---

#### 2.2.2 Node Expansion / Priority Scorer

**Purpose**
Rank candidate states or programs for further exploration.

**Input**

* Candidate node representations
* Program and execution embeddings

**Output**

* Scalar priority or expansion score

**Notes**

* This is **not** a planner
* It does not generate successors
* It only scores *given* candidates

---

#### 2.2.3 Termination Head

**Purpose**
Decide whether computation should stop.

**Input**

* Best current candidate
* Confidence and cost signals
* Search statistics (embedded)

**Output**

* Stop / continue decision logits
* Optional retry-mode modifiers

**Hard Requirement**

Termination must be **learned**, not rule-based.

---

### 2.3 Forbidden Shortcuts (Level 3)

Level 3 **must not**:

* Encode domain-specific strategies
* Hard-code search algorithms (e.g., DFS, A*)
* Implement symbolic control flow
* Override or rewrite program logic

If Level 3 can solve a task without Level 2, the design is invalid.

---

## 3. Level 4 Contract: Program and Concept Memory

### 3.1 Functional Responsibility

Level 4 provides **persistent memory** for:

* Programs
* Program fragments
* Abstract concepts derived from experience

Its purpose is **reuse and consolidation**, not recall of ground truth.

---

### 3.2 Nature of Memory

Memory entries are:

* Learned embeddings
* Opaque to symbolic inspection
* Interpretable only through neural interaction

Memory is **content-addressable**, but **policy-free**.

---

### 3.3 Mandatory Level 4 Modules

---

#### 3.3.1 Memory Key Encoder

**Purpose**
Produce queries for memory retrieval.

**Input**

* Contextualized State IR
* Task and global tokens

**Output**

* Query embedding (q)

**Requirements**

* Fully learned
* Stable under small input perturbations

---

#### 3.3.2 Memory Read Fusion

**Purpose**
Integrate retrieved memory into the current state.

**Input**

* Retrieved memory embeddings
* Current State IR

**Output**

* Updated State IR

**Requirements**

* Fusion must be gated
* Memory must never overwrite state destructively
* Fusion effects must be reversible or ignorable

---

#### 3.3.3 Write Gate

**Purpose**
Decide whether to write new memory.

**Input**

* Program traces
* Execution outcomes
* Verification signals

**Output**

* Write / no-write gate
* Memory type logits (program, concept, fragment)

**Forbidden**

* Always-write behavior
* Manual triggers

---

#### 3.3.4 Consolidation Gate

**Purpose**
Prevent memory explosion and redundancy.

**Input**

* New memory candidate
* Retrieved similar entries

**Output**

* Merge / replace / ignore decision

**Notes**

This gate is the only allowed mechanism for memory pruning.

---

## 4. Interaction Between Level 3 and Level 4

* Level 3 **requests** retrieval budget
* Level 4 **returns** memory-conditioned representations
* Level 3 **does not**:

  * Inspect memory contents
  * Choose specific entries
* Level 4 **does not**:

  * Decide when retrieval is “necessary”
  * Trigger search or retries

This separation is mandatory.

---

## 5. Input / Output Semantic Contract

### 5.1 Input Assumptions

Level 3–4 must assume:

* Programs may fail unpredictably
* Confidence signals are noisy
* Memory may be misleading or stale

### 5.2 Output Guarantees

Level 3–4 must guarantee:

* All decisions are exposed as explicit signals
* No hidden global state exists
* No irreversible control is applied

---

## 6. Training and Credit Assignment Assumptions

* Level 3–4 are trained via:

  * Efficiency outcomes
  * Verification success
  * Long-horizon credit assignment
* Supervision is:

  * Sparse
  * Delayed
  * Often comparative

Therefore:

* Policies must be smooth
* Decisions must be revisable
* Exploration bias is preferred over rigidity

---

## 7. Forbidden Failure Modes

Level 3–4 must **not collapse into**:

* A hard-coded search algorithm
* A rule-based memory cache
* A heuristic controller tuned per task
* An external database with manual policies

If removing learning does not break behavior, the design is incorrect.

---

## 8. Explicit Non-Goals (Level 3–4)

Level 3–4 are **explicitly not**:

* Planners
* Solvers
* Symbolic controllers
* Knowledge bases with truth guarantees

They are **meta-structures**, not intelligence cores.

---

## 9. Stability and Evolution Clause

Future iterations may:

* Improve control smoothness
* Enhance consolidation strategies
* Expand memory representations

Future iterations may **not**:

* Introduce hard logic
* Collapse control into heuristics
* Merge Level 3–4 responsibilities into other levels

---

**End of Level 3–4 Contract**
