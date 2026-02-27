# Regression & Stability Harness

> **Purpose**
> This document defines the *canonical regression framework* for the project.
> Its sole question is:
>
> **「我修了 A，是否悄悄毀了 B？」**
>
> This is **not** a leaderboard, not a performance report, and not an optimization guide.
> It is an *architectural safety net* that prevents silent capability collapse across Levels, concepts, and tools.

---

## 0. Scope and Authority

This document is **normative for development workflow**.

Any architectural or training change **MUST** be evaluated against this regression harness **before** being considered valid.

If a change improves aggregate accuracy but violates a regression gate defined here, the change is **rejected**.

This document is subordinate only to:

* System Invariants & Non-Negotiables
* Level Contracts (L0–L6)
* Credit Assignment & Failure Recovery Model
* Routing, Gating, and Control Are Learnable

Phase IDs, suite activation states, and promotion rules are sourced from
`docs/harness/legacy/phase-gate-policy.md`.

---

## 1. Regression Philosophy (Non-Negotiable)

### 1.1 Regression ≠ Accuracy

Regression testing answers **stability questions**, not performance questions.

We care about:

* Capability preservation
* Failure localization stability
* Credit routing consistency
* Concept isolation

A model that is *better on average* but *worse in attribution or isolation* is considered **regressed**.

---

### 1.2 Named Failure Is the Atomic Unit

All regression signals are defined over **failure types**, not tasks.

If a regression cannot be mapped to a known failure category, that indicates:

* Missing failure taxonomy
* Insufficient verifier signal

In that case, the correct response is **to improve diagnostics**, not to waive regression.

---

### 1.3 Pretraining-First Priority

Regression prioritizes **process/diagnostic stability** over outcome gains:

* Primary: failure attribution, credit routing, calibration, concept isolation, paired invariance
* Secondary: task success rate / aggregate benchmark score

If secondary improves while primary degrades, the change is rejected.

---

## 2. Canonical Failure Taxonomy (Regression Keys)

All regressions are indexed by the following canonical categories.

### 2.1 Representation Failures (L0 / L1)

* Object split / merge instability
* Missing or spurious objects
* Relation hallucination or collapse
* Event misattribution across steps
* Inconsistent state across rollouts

### 2.2 Procedural Failures (L2)

* Program step order inversion
* Correct primitive, wrong scope
* Local consistency with global failure
* Program overfitting to representation quirks

### 2.3 Search / Control Failures (L3)

* Premature termination
* Over-search on low-value branches
* Under-exploration when uncertainty is high
* Instability across random seeds

### 2.4 Memory Failures (L4)

* Relevant program not retrieved
* Irrelevant memory reused
* Overwriting useful abstractions
* Consolidation collapse

### 2.5 Abstraction Failures (L5)

* Over-early abstraction
* Over-general macro masking exceptions
* Under-abstraction leading to combinatorial explosion

### 2.6 Evaluation / Credit Failures (L6)

* Accepting invalid solutions
* Rejecting valid solutions
* Miscalibrated confidence
* Incorrect credit routing distribution

These categories are **stable identifiers** used throughout regression logs, metrics, and gates.

---

## 3. Regression Axes

Every regression run evaluates the model along **orthogonal axes**.

A change is accepted **only if it does not regress on any axis**, unless explicitly waived.

### 3.1 Dataset Axis

Minimum required coverage:

* MiniARC (sanity & edge cases)
* ARC-AGI-1 (baseline stability)
* ARC-AGI-2 (core stress)
* re-arc paired tasks (representation invariance)
* ConceptARC (concept isolation)
* arc-agi-benchmarking (probe/regression harness only)

### 3.2 Concept Axis

Measured per concept bucket (from ConceptARC):

* Single-concept success
* Cross-concept interference
* Concept leakage rate

### 3.3 Level Axis

For each Level (L0–L6):

* Invocation frequency
* Diagnostic signal entropy
* Credit assignment mass

### 3.4 Control Axis

* Budget stability (search depth, beam, rollout)
* Termination consistency
* Sensitivity to noise / seed

---

## 4. Required Regression Suites

In this section, "Mandatory" means mandatory once activated by the current phase
profile in `docs/harness/legacy/phase-gate-policy.md`.

### 4.1 Smoke Regression (Mandatory, Fast)

**Purpose**: Detect catastrophic breakage.

**Coverage**:

* MiniARC (full)
* ARC-AGI-1 (small fixed subset)

**Checks**:

* Parser validity
* Verifier executable
* No NaNs / crashes
* Basic success rate within tolerance

**Gate**:

* Any crash or parser failure → **hard block**

---

### 4.2 Structural Regression (Mandatory)

**Purpose**: Ensure architectural contracts remain intact.

**Checks**:

* All Levels instantiated
* No token schema drift
* Tokenizer protected IR/control strings remain atomic (`rep.tokenizer.ir_fragmentation_rate == 0` once configured)
* No new hard-coded control paths
* Routing outputs remain learnable (non-degenerate)

**Gate**:

* Any invariant violation → **hard block**

---

### 4.3 Failure-Profile Regression (Mandatory)

**Purpose**: Detect silent redistribution of errors.

**Method**:

* Compare failure taxonomy histograms before/after change
* Measure KL divergence per failure category

**Gate**:

* Large unexplained shift in failure distribution → **block**
* Shift explained by explicit design goal → **allowed with annotation**

---

### 4.4 Concept Isolation Regression (Mandatory)

**Purpose**: Ensure concepts remain independently usable.

**Method**:

* Run ConceptARC per concept bucket
* Measure:

  * Concept isolation score
  * Concept leakage score

**Gate**:

* Any concept whose isolation decreases beyond tolerance → **block**

---

### 4.5 Paired Representation Regression (Mandatory)

**Purpose**: Detect representation overfitting.

**Data**:

* re-arc paired tasks (A/B with semantic invariance)

**Checks**:

* A success but B failure → representation sensitivity
* Divergent internal programs for invariant pairs

**Gate**:

* Increased asymmetry rate → **block**

---

### 4.6 Credit Routing Regression (Mandatory)

**Purpose**: Ensure diagnosis logic remains stable.

**Method**:

* Compare L6 credit distributions for identical failure cases

**Gate**:

* Collapse to single-Level blame
* Excessive entropy loss

Either condition → **block**

---

### 4.7 Pretraining Diagnostics Regression (Mandatory)

**Purpose**: Keep pretraining process metrics stable across updates.

**Method**:

* Compare before/after on:

  * `failure.credit.collapse_rate`
  * `eval.calibration_error`
  * `prog.diversity`
  * `rep.tokenizer.ir_fragmentation_rate` (text/IR-control pipelines only)
  * `search.termination_margin` (failure-masking checks)

**Gate**:

* Credit collapse rate increase beyond tolerance → **block**
* Calibration degradation beyond tolerance → **block**
* Program diversity collapse → **block**
* Any increase in `rep.tokenizer.ir_fragmentation_rate` beyond tolerance → **block**
* Cost gain caused by failure masking → **block**

---

### 4.8 Resume Consistency Regression (Mandatory)

**Purpose**: Prevent semantic drift between uninterrupted and resumed training.

**Method**:

* Fix seed and dataset slice.
* Path A: run N segments without interruption.
* Path B: interrupt at a segment boundary, resume from checkpoint, run remaining segments.
* Compare segment-aligned metrics distributions at the same boundary using `task.validity_score`, `task.confidence`, `failure.credit`.

**Gate**:

* Any drift above epsilon defined in regression/metrics config -> **block**
* Missing or inconsistent segment boundary alignment -> **block**

---

## 5. Regression Gates

Regression gates are **binary** unless explicitly marked otherwise.

### 5.1 Hard Gates (Non-Waivable)

Hard gates apply when their corresponding suites/metrics are in `ON` state for
the current phase profile.

* System invariant violation
* Token schema drift
* Removal or bypass of a Level
* Hard-coded control replacing learned routing
* Verifier non-functional
* Credit attribution collapse
* Calibration degradation beyond tolerance
* Concept leakage increase
* Paired invariance regression

### 5.2 Soft Gates (Waivable with Justification)

* Minor performance loss with structural gain
* Temporary increase in search cost
* Known diagnostic rebalancing

Soft gate waivers **must** include:

* Failure category affected
* Intended long-term fix
* Removal criterion

---

## 6. Regression Artifacts (Required Outputs)

Each regression run **must produce**:

1. **Summary Report**

   * Pass/fail per suite
   * Block reasons (if any)

2. **Failure Profile Diff**

   * Before/after histograms

3. **Concept Breakdown**

   * Per-concept isolation & leakage

4. **Credit Routing Diff**

   * L6 distributions comparison

Artifacts are stored under a versioned directory and must be retained.

---

## 7. Change Classification

Every change **must declare** its expected regression impact:

* Pure refactor (no behavior change expected)
* Targeted fix (which failure category?)
* Capability expansion (which concepts?)

Undeclared changes that cause regressions are **automatically rejected**.

---

## 8. When Regression Fails

If a regression gate blocks a change:

1. Identify **which failure category regressed**
2. Identify **which Level is implicated**
3. Decide one of:

   * Fix the regression
   * Narrow the change scope
   * Improve diagnostics (if attribution is unclear)

Ignoring a regression is **never** an acceptable option.

---

## 9. Explicit Non-Goals

This regression harness does **not**:

* Optimize leaderboard scores
* Guarantee monotonic accuracy gains
* Provide human-readable explanations

Its sole role is to **preserve architectural integrity over time**.

---

## 10. Final Rule

> **If you cannot explain why a regression is acceptable in terms of Level responsibility and failure taxonomy, it is not acceptable.**

This document exists to make silent degradation impossible.
