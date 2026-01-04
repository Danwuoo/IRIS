# Mamba Trunk Contract & Allowed Variations

## 1. Purpose and Scope

This document defines the **strict contract** governing the **Mamba / SSM Trunk** within the system architecture, together with the **explicitly allowed implementation variations**.

Its purpose is to prevent architectural drift in which:

* the trunk is implicitly weakened, bypassed, or replaced;
* reasoning or control logic is relocated into heads, routers, or external code;
* attention-like or side-channel networks are introduced without constraint.

This document is **binding** on all downstream heads, adapters, routers, and training procedures.

---

## 2. Role of the Trunk (Normative)

### 2.1 Single Source of High-Capacity Representation

The Mamba Trunk is the **only high-capacity neural substrate** in the system.

Formally:

* Let ( Z \in \mathbb{R}^{L \times d} ) be the canonical State IR token sequence.
* The trunk computes a contextualized representation
  [
  \tilde{Z} = \mathrm{Trunk}(Z)
  ]
* All semantic integration across **objects, relations, events, programs, memory, control, and verification** must occur **primarily inside the trunk**.

No other module may replicate this role.

---

### 2.2 Mandatory Semantic Guarantees

The trunk **must guarantee** the following semantic properties:

1. **Global Contextualization**
   Each output token in ( \tilde{Z} ) reflects information aggregated from:

   * task-level intent,
   * global state,
   * cross-token interactions (object–relation–event–macro).

2. **Level-Agnostic Representations**
   The trunk output must be usable *without modification* by:

   * perceptual heads (L0),
   * dynamics and rollout modules (L1),
   * program induction and execution (L2),
   * search control and routing (L3),
   * memory read/write (L4),
   * abstraction management (L5),
   * verification and credit routing (L6).

3. **No Task-Specific Commitments**
   The trunk must not encode:

   * hard assumptions about program structure,
   * symbolic execution order,
   * planner-specific control flow,
   * tool semantics.

These belong to heads and learned routing, not the trunk.

---

## 3. Input Contract (Strict)

### 3.1 Accepted Inputs

The trunk **only** accepts:

* Canonical **State IR token sequences**, after:

  * token-type embeddings,
  * structural embeddings,
  * optional time embeddings (event/macro tokens only).

No raw sensory inputs, program ASTs, memory entries, or tool outputs may bypass the State IR layer.

---

### 3.2 Prohibited Inputs

The trunk **must not** directly consume:

* pre-attended tensors,
* planner-expanded trees,
* symbolic stacks or call frames,
* externally executed DSL traces,
* side-channel control vectors not embedded as tokens.

If information must influence the trunk, it must be expressed as **tokens**.

---

## 4. Output Contract (Strict)

### 4.1 Output Semantics

The trunk outputs a sequence ( \tilde{Z} ) with:

* identical token cardinality and ordering as input ( Z );
* enriched semantic content, not discrete decisions.

The trunk **does not**:

* choose actions,
* decide termination,
* select tools,
* rank programs,
* gate levels.

These decisions are delegated to heads and routers.

---

### 4.2 Stability Requirements

The trunk output must be:

* numerically stable under multi-step rollouts,
* robust to partial gating of downstream modules,
* invariant to which Level consumes it.

---

## 5. Prohibited Responsibilities (Non-Negotiable)

The following responsibilities are **explicitly forbidden** inside the trunk:

1. **Hard Control Logic**

   * if/else branching,
   * loop unrolling,
   * early termination signals.

2. **Discrete Search**

   * tree expansion,
   * beam management,
   * candidate pruning.

3. **Symbolic Execution**

   * DSL interpretation,
   * rule application,
   * graph rewriting.

4. **Explicit Attention Substitution**

   * full self-attention layers used to bypass SSM inductive bias,
   * hidden transformer blocks masquerading as “mixers”.

Violation of any item above constitutes a **contract breach**.

---

## 6. Relationship to Heads and Adapters

### 6.1 What Heads May Assume

Heads and adapters may assume that the trunk provides:

* rich contextual embeddings,
* disentangled but correlated token semantics,
* sufficient capacity for abstraction and long-range dependency.

They **may not assume**:

* task-specific disentanglement,
* pre-separated symbolic roles,
* planner-ready structures.

---

### 6.2 What Heads Must Not Require

Heads **must not require** the trunk to:

* emit executable programs,
* maintain explicit stacks or traces,
* encode search depth,
* preserve deterministic symbolic equivalence.

If such requirements arise, they must be implemented **within the head’s own learned parameters**, not pushed upstream.

---

## 7. Allowed Variations (Explicit)

The following variations are **permitted**, provided they respect the core contract.

### 7.1 Trunk Depth and Width

* Number of Mamba / SSM blocks: variable.
* Hidden dimension ( d ): configurable.
* Parameter count scaling: allowed, provided the trunk remains the dominant capacity holder.

---

### 7.2 Lightweight Token Mixing

To compensate for SSM limitations, the trunk **may include**:

* low-rank token mixing,
* gated residual cross-token projections,
* small learned mixers operating on token groups.

Constraints:

* must be strictly capacity-limited,
* must not approximate full attention,
* must not become the primary computation path.

---

### 7.3 Adapter Injection Points

Adapters may be inserted:

* at selected trunk layers,
* with low-rank or small-MLP form,
* conditioned on Level identity.

Adapters **must not**:

* introduce new global computation paths,
* bypass trunk layers,
* accumulate depth comparable to the trunk.

---

### 7.4 Precision Partitioning

The trunk may operate under:

* BF16 / FP16 execution,
* with explicit FP32 accumulation where required.

Precision choices are considered **implementation details**, not semantic changes.

---

## 8. Explicit Non-Variations (Forbidden)

The following changes are **not allowed**, even if empirically beneficial:

* replacing the trunk with a transformer,
* adding parallel attention trunks,
* introducing planner-specific sub-trunks,
* moving routing logic into trunk layers,
* using the trunk as a DSL executor.

---

## 9. Contract with Training and Credit Assignment

The trunk is trained under the assumption that:

* credit assignment may be indirect and delayed,
* multiple Levels influence loss signals,
* failures may be attributed downstream.

Therefore:

* the trunk must remain **general-purpose**,
* it must not specialize prematurely for any single Level,
* it must tolerate conflicting gradients.

---

## 10. Summary (Normative)

**The Mamba Trunk is:**

* the only high-capacity network,
* a universal semantic integrator,
* agnostic to task, program, and control,
* mandatory for all information flow.

**The Mamba Trunk is not:**

* a planner,
* an executor,
* a router,
* an attention surrogate,
* a symbolic engine.

Any deviation from this contract requires a **new architecture**, not a local modification.