# Level 5–6 Contract

**Abstraction Management, Self-Monitoring, and Meta-Credit Assignment**

---

## 0. Scope and Intent

This document defines the **exclusive responsibilities, authority boundaries, and invariants** of **Level 5** and **Level 6**.

Together, these levels are responsible for:

* Managing **abstraction granularity over time**
* Monitoring system behavior and outcomes
* Routing **credit, blame, and revision pressure** across lower levels

They operate at the **meta-representational** and **meta-evaluative** layer of the system.

Critically:

* Level 5–6 **do not solve tasks**
* Level 5–6 **do not plan**
* Level 5–6 **do not introduce symbolic oversight**

They shape *how the system represents and corrects itself*, not *what answer it produces*.

---

## 1. Architectural Positioning

### 1.1 Role Separation

| Level   | Primary Role             | Core Question Answered                                   |
| ------- | ------------------------ | -------------------------------------------------------- |
| Level 5 | Abstraction management   | “At what granularity should the system think?”           |
| Level 6 | Self-monitoring & credit | “What went wrong, and where should pressure be applied?” |

### 1.2 Authority Boundaries

* Level 5 influences **representation**, not control flow
* Level 6 influences **learning pressure**, not execution logic
* Neither level may:

  * Override decisions from Level 3
  * Rewrite programs from Level 2
  * Inject domain knowledge

---

## 2. Level 5 Contract: Abstraction Management

### 2.1 Functional Responsibility

Level 5 governs **when and how the system shifts abstraction levels**, including:

* Aggregating fine-grained events into macro concepts
* Deciding whether to reason at:

  * Micro (object / event)
  * Meso (patterns / transformations)
  * Macro (summaries / schemas)

Level 5 does **not** create programs or concepts explicitly; it **modulates representation granularity**.

---

### 2.2 Mandatory Level 5 Modules

All Level 5 implementations **must include** the following learned modules.

---

#### 2.2.1 Macro Selector

**Purpose**
Decide whether abstraction should be introduced or refined.

**Input**

* Contextualized State IR
* Event and object token trajectories
* Signals from Level 3 (search pressure)

**Output**

* Soft gates indicating:

  * Whether to form macro representations
  * Preferred abstraction scale

**Requirements**

* Decisions must be probabilistic
* Must be reversible
* Must tolerate being ignored by downstream routing

---

#### 2.2.2 Macro Updater

**Purpose**
Construct or update macro-level tokens.

**Input**

* Aggregated object and event representations
* Existing macro tokens (if any)

**Output**

* New or updated macro tokens (M)
* Or gated no-op

**Hard Constraints**

* Macro tokens must remain compatible with State IR
* Macro tokens must not encode control logic
* Macro updates must be learnable and differentiable

---

### 2.3 Forbidden Shortcuts (Level 5)

Level 5 **must not**:

* Hard-code abstraction rules
* Collapse all reasoning into macros
* Encode symbolic schemas or templates
* Force macro usage downstream

If disabling macro tokens does not degrade performance over time, Level 5 is under-specified.

---

## 3. Level 6 Contract: Self-Monitoring and Meta-Credit

### 3.1 Functional Responsibility

Level 6 provides the system’s **internal evaluation and diagnosis layer**.

It is responsible for:

* Verifying candidate outcomes
* Estimating confidence and calibration
* Routing credit and blame signals to lower levels

Level 6 answers **“how trustworthy is this process?”**, not **“is this answer correct by definition?”**.

---

### 3.2 Mandatory Level 6 Modules

---

#### 3.2.1 Verifier Head

**Purpose**
Evaluate candidate solutions or executions.

**Input**

* Candidate outputs
* Execution traces
* Contextualized State IR

**Output**

* Validity scores
* Violation-type logits (optional but recommended)

**Requirements**

* Fully learned
* Task-agnostic in structure
* No hard-coded correctness rules

---

#### 3.2.2 Confidence / Calibration Head

**Purpose**
Estimate confidence in the current best candidate.

**Input**

* Verifier outputs
* Search and cost signals
* Trunk representations

**Output**

* Calibrated confidence score

**Notes**

* Confidence must be separable from correctness
* Used downstream by Level 3 for termination

---

#### 3.2.3 Credit Router

**Purpose**
Route diagnostic pressure to appropriate lower levels.

**Input**

* Failure patterns
* Low-confidence signals
* Execution and search traces

**Output**

* Soft preference over:

  * Re-running perception (Level 0)
  * Increasing rollout (Level 1)
  * Expanding program space (Level 2)
  * Increasing retrieval (Level 4)

**Hard Requirement**

Routing must be **learned**, not rule-based.

---

## 4. Interaction Between Level 5 and Level 6

* Level 6 may:

  * Influence future abstraction pressure indirectly
* Level 5 may:

  * Alter representations consumed by verification

Neither level may directly command the other.

All interaction is mediated through **explicit tokens and soft signals**.

---

## 5. Input / Output Semantic Contract

### 5.1 Input Assumptions

Level 5–6 must assume:

* Representations may be misleading
* Programs may succeed for the wrong reasons
* Verification signals may be noisy or delayed

### 5.2 Output Guarantees

Level 5–6 must guarantee:

* No irreversible decisions
* No hidden evaluators
* No silent failure masking

All outputs must be visible and consumable by other levels.

---

## 6. Training and Credit Assignment Assumptions

* Level 5–6 are trained via:

  * Long-horizon outcomes
  * Efficiency and robustness metrics
  * Failure recovery behavior
* Supervision is:

  * Sparse
  * Delayed
  * Often indirect

Therefore:

* Modules must be stable under weak gradients
* Outputs must be smooth and non-brittle
* Overconfidence must be penalizable

---

## 7. Forbidden Failure Modes

Level 5–6 must **not collapse into**:

* Hand-written abstraction rules
* Symbolic verifiers
* Post-hoc confidence heuristics
* Manual credit assignment logic

If Level 6 decisions can be replicated with if-else rules, the design is invalid.

---

## 8. Explicit Non-Goals (Level 5–6)

Level 5–6 are **explicitly not**:

* Oracles
* Truth judges
* Planners
* Debuggers for human inspection

They are **internal regulators**, not external authorities.

---

## 9. Stability and Evolution Clause

Future versions may:

* Improve abstraction smoothness
* Enhance calibration quality
* Refine credit routing granularity

Future versions may **not**:

* Introduce symbolic oversight
* Centralize control in Level 5–6
* Remove learnability or differentiability

---

**End of Level 5–6 Contract**