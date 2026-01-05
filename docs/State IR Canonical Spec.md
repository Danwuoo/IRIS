# State IR Canonical Specification

**Version 1.0 (Normative)**

## 1. Purpose and Scope

This document defines the **canonical State Intermediate Representation (State IR)** used across the entire system.

State IR is the *only* shared representational substrate consumed and produced by the Trunk and all Levels (L0–L6).

This specification exists to ensure:

- Cross-Level composability without implicit assumptions
- Architectural stability against uncontrolled token or modality expansion
- Clear semantic contracts independent of tensor shapes or implementation details

Any deviation from this specification constitutes an **architectural violation**, not an optimization.

---

## 2. Core Principles (Non-Negotiable)

1. **Single Canonical Representation**
    
    All internal reasoning state must be representable as State IR.
    
    No Level may introduce an alternative latent state space.
    
2. **Closed Token Type Set**
    
    The set of token types defined in this document is *closed*.
    
    New token types MAY NOT be added without a versioned revision of this spec.
    
3. **Uniform Trunk Processing**
    
    All State IR tokens are processed by the same Trunk without conditional routing at the representation level.
    
4. **Semantic, Not Procedural**
    
    State IR encodes *what the system believes the world/task/program state is*, not how it was produced.
    

---

## 3. Token Type System

State IR consists of a fixed set of token categories.

Each token is a vector in a shared latent space of dimension **d**.

### 3.1 Token Categories (Exhaustive)

| Token Type | Symbol | Cardinality | Description |
| --- | --- | --- | --- |
| Task Token | T | 1 | Encodes the task-level intent, objective, and constraints |
| Global Token | G | 1 | Aggregated global context and control-relevant state |
| Object Tokens | O | Nₒ | Discrete entities or structured units in the world |
| Relation Tokens | R | Nᵣ | Explicit relations between objects |
| Event Tokens | X | Nₓ | State transitions, actions, or temporal changes |
| Macro Tokens | M | Nₘ | Abstracted patterns, programs, or compressed histories |

No other token categories are permitted.

---

## 4. Canonical Sequence Construction

### 4.1 Concatenation Order (Mandatory)

All State IR instances MUST be constructed using the following fixed order:

```
Z = [ T ; G ; O₁…Oₙ ; R₁…Rₖ ; X₁…Xₘ ; M₁…Mₚ ]

```

Only the token categories defined in Section 3.1 may appear in `Z`. Program IR tokens are not State IR tokens and must never be concatenated into the canonical State IR sequence `Z`, even transiently.

Where:

- `T ∈ ℝ¹ˣᵈ`
- `G ∈ ℝ¹ˣᵈ`
- `O ∈ ℝᴺᵒˣᵈ`
- `R ∈ ℝᴺʳˣᵈ`
- `X ∈ ℝᴺˣˣᵈ`
- `M ∈ ℝᴺᵐˣᵈ`

Padding MAY be applied internally but MUST preserve relative ordering.

### 4.2 Ordering Stability

- Relative ordering *within* each token group MUST be stable across a reasoning cycle.
- Reordering tokens is considered a **state mutation** and must be explicitly produced by a learned module.

---

## 5. Token Semantics

### 5.1 Task Token (T)

The Task Token represents:

- Task objective
- Success criteria
- Global constraints
- Instructional priors

It MUST be present at all times and MUST NOT be removed or replaced.

### 5.2 Global Token (G)

The Global Token serves as:

- Cross-token aggregation point
- Control and routing context
- Memory fusion anchor

Heads MAY preferentially read from or write to G, but MUST NOT assume exclusivity.

### 5.3 Object Tokens (O)

Object Tokens represent:

- Discrete entities
- Structured components
- Symbolic units derived from perception or abstraction

They MUST be referentially stable within a reasoning cycle.

### 5.4 Relation Tokens (R)

Relation Tokens encode:

- Binary or higher-order relations between objects
- Structural, spatial, or logical links

Relations MUST NOT be implicitly encoded solely via object embeddings.

### 5.5 Event Tokens (X)

Event Tokens represent:

- State transitions
- Actions
- Temporal deltas between states

They are the only token type permitted to carry explicit temporal semantics.

### 5.6 Macro Tokens (M)

Macro Tokens represent:

- Learned abstractions
- Program fragments
- Compressed multi-step patterns

They MUST be treated as first-class tokens, not annotations.

---

## 6. Mandatory Embeddings

Every token in State IR MUST include the following additive embeddings:

### 6.1 Type Embedding (Required)

A learned embedding indicating token category:

- Task
- Global
- Object
- Relation
- Event
- Macro

Type embeddings are mandatory and MUST be consumed by the Trunk.

### 6.2 Structural Embedding (Conditional)

Applied where applicable:

- Object geometry or topology
- Relation endpoints or arity
- Program node roles (for Macro tokens)

Absence of structure MUST be encoded explicitly, not omitted.

### 6.3 Temporal Embedding (Restricted)

- Applied ONLY to Event Tokens and (optionally) Macro Tokens
- MUST NOT be applied to Object or Relation Tokens

---

## 7. State IR Mutability Rules

1. **Creation**
    
    New tokens MAY be created only by learned modules (e.g., L0, L2, L5).
    
2. **Deletion**
    
    Tokens MAY be dropped only via explicit learned gating or consolidation.
    
3. **Modification**
    
    Token content may change freely through Trunk processing and adapters.
    
4. **Persistence**
    
    Tokens persist across reasoning cycles unless explicitly removed.
    

---

## 8. Cross-Level Contract

All Levels (L0–L6):

- MUST consume State IR as defined here
- MUST produce State IR or scalar outputs derived from it
- MUST NOT bypass State IR to exchange hidden states

No Level may assume privileged access to pre- or post-Trunk representations.

---

## 9. Explicit Non-Goals

State IR is **not**:

- A human-readable program representation
- A symbolic execution trace
- A DSL or instruction sequence
- A tool invocation log

Any of the above must be *encoded into* State IR, not replace it.

---

## 10. Versioning and Extension Policy

- This specification is versioned.
- Any change to token types, ordering, or mandatory embeddings requires a new major version.
- Silent extensions or “temporary” token hacks are forbidden.

---

## 11. Compliance Requirement

Any model, agent, or training procedure claiming compatibility with this architecture MUST:

- Accept this State IR verbatim
- Reject undefined token types
- Preserve ordering and semantics as specified

Non-compliance is considered a **system-level defect**, not a performance trade-off.

---

**End of Document**
