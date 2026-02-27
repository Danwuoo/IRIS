# Single-H100 3B Training Profile

**Document Type:** Design Note (Non-normative)  
**Status:** Active planning baseline (OD values applied)  
**Phase Intent:** Phase C-compatible training profile  
**Non-Override Clause:** This note does not override system invariants, State IR contracts, Level contracts, trunk contract, or learnable-control requirements.

---

## 0. Change Declaration

- Change class: `Targeted fix`
- Target failure categories / signals:
  - `F_SEARCH` stability risks caused by long-run single-card budget pressure and noisy small-batch updates
  - `F_EVAL` / `eval.calibration_error` drift risks from unstable mixed-precision and resume behavior
- Expected impact:
  - No architectural contract changes
  - Better training-run reproducibility and resume consistency (`S8`)

---

## 1. Scope

This profile is a single-card architecture-validation and small-scale pretraining profile.

- Hardware: `1x H100 80GB`
- Distributed strategy: none (`no DP`, `no TP`)
- Training mode: from-scratch pretraining
- Core stack direction: `JAX + Flax NNX` with `Optax` and `Orbax`

This is not a large-scale production LLM deployment profile.

---

## 2. Fixed Engineering Decisions

| Category | Decision |
| --- | --- |
| Framework | `JAX` |
| Model API | `Flax NNX` (not Linen) |
| Model size target | `~3B parameters` |
| Compute precision | `BF16` compute on H100 |
| Master weights | `FP32` |
| LN / logits | `FP32` |
| Accumulators | `FP32` |
| Activation strategy | Block-level `jax.remat` from start (see `OD-08`) |
| Shape policy | Formal training uses single bucket `1024`; `512/1024` allowed for compile warmup only (see `OD-07`) |
| Main context length | `1024` |
| Microbatch | `2` |
| Gradient accumulation | Enabled |
| Cross-segment accumulation | Forbidden |
| Runtime lock policy | Lock manifest v1 required; Phase `C+` upgrades frozen unless baseline rebuild (see `OD-02`) |

---

## 3. Optimizer and LR Schedule

| Item | Value |
| --- | --- |
| Optimizer | `AdamW` |
| `beta1` | `0.9` |
| `beta2` | `0.95` |
| `eps` | `1e-8` |
| `weight_decay` | `0.1` |
| Gradient clipping | Global norm `1.0` |
| Peak LR | `3e-4` |
| Warmup | `2000 optimizer steps` |
| Decay | Cosine |
| Final LR | `3e-5` |

---

## 4. Effective Batch Design

| Item | Value |
| --- | --- |
| `seq_len` | `1024` |
| `microbatch` | `2` |
| tokens per forward | `2048` |
| target tokens per optimizer step | `~1,000,000` |
| accumulation steps | `~488` (`2048 * 488 = 999,424`) |

Notes:

- Effective batch is achieved via accumulation only.
- Segment boundaries must not cut through an accumulation window.

---

## 5. Checkpoint and Resume Policy

| Item | Policy |
| --- | --- |
| Small checkpoint | Every `100` optimizer steps |
| Full checkpoint | Every `1000` optimizer steps |
| Segment sizing | Target `40` minutes; hard max `45` minutes; must align to optimizer-step boundary |
| Segment journal | Append-only |
| Resume consistency | Must pass `S8 Resume Consistency Regression` |
| Segment semantics | Two-phase `PENDING -> APPLIED` |
| Checkpoint retention | Three-tier: recent `5` segments + daily `1` + per-phase milestone `1` permanent |
| Runtime lock manifest | Must record `runtime_lock_manifest_id` and `runtime_lock_manifest_sha256` in checkpoint metadata |
| Segment-end evaluation | One eval snapshot at each segment end (lite metrics allowed) |

Detailed execution and restart semantics are defined in:

- `docs/Training Segment and Resume Rules (Design Note).md`

---

## 6. 3B Topology Recommendation (Training Profile Layer)

| Parameter | Value |
| --- | --- |
| Layers | `28` |
| Hidden dim | `2560` |
| Attention heads | `20` |
| Head dim | `128` |
| FFN multiplier | `4` |
| Vocab | `100k` fixed, with protected IR/control sub-vocab (no merge/split on protected strings) |

This section is a training profile recommendation, not a contract-level architecture rewrite.

---

## 7. Data Policy Binding

- Data mixture is governed by `docs/Data Mixture & Ingestion Specification.md`.
- This profile assumes:
  - Pure LM: `90%`
  - IR-aligned synthetic: `10%`
  - Benchmark data: `0%` in training (regression probe only)

---

## 8. Technical Debt Guardrails

The following hard controls are temporary guardrails and must not become semantic policy:

1. Fixed single training bucket (`1024`)
2. Compile-warmup bucket restriction (`512/1024` only)
3. Hard clip (`global norm = 1.0`)

Removal criteria:

- Stable compile behavior and cache hit rate under planned dynamic-shape alternatives
- No regression in primary process gates:
  - `failure.credit.collapse_rate`
  - `eval.calibration_error`
  - `prog.diversity`
  - `search.termination_margin`

Intended learned replacement:

- Learned budget/control adaptation remains in L3/L6 policies; guardrails remain safety caps only.

---

## 9. Regression and Artifact Expectations

For architecture/training-impacting updates under this profile:

- Keep phase declaration explicit in artifacts (`phase = C|D|E` as applicable)
- Maintain baseline/tolerance profile integrity (`tolerance_profile_id` frozen at Phase `B -> C`, tightening-only afterward)
- Run activated suites per `phase-gate-policy.md`
- Block on any hard-gate violation
- Eval cadence is fixed:
  - Per segment: lite probes `S1/S2` + `S3` when active
  - Every `24h` or `200` optimizer steps (whichever first): full activated suites
  - Before phase gate: mandatory full regression

---

## 10. Related Documents

- `docs/plan/single-h100-3b-open-decisions.md`
- `docs/plan/runtime-stack-lock-jax-flax-nnx.md`
- `docs/Pretraining Objective Spec.md`
- `docs/Training Segment and Resume Rules (Design Note).md`

---

**End of Document**
