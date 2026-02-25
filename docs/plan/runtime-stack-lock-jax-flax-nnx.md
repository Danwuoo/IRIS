# Runtime Stack Lock for JAX + Flax NNX

**Document Type:** Design Note (Non-normative)  
**Status:** Draft lock policy  
**Non-Override Clause:** This note does not override system invariants, contracts, or regression gate policy.

---

## 0. Purpose

Define how runtime versions are pinned for single-H100 training to reduce API churn and resume inconsistency risk.

Related baseline:

- `docs/plan/single-h100-3b-training-profile.md`

---

## 1. Lock Surfaces

The following must be pinned as one tested set:

- `python`
- `jax`
- `jaxlib` (CUDA-compatible build)
- `flax` (NNX API)
- `optax`
- `orbax-checkpoint`
- `numpy`

Optional but recommended pins:

- `ml_dtypes`
- `tensorstore` (if checkpoint backend requires it)

---

## 2. Current Pin Status

| Package | Status | Version |
| --- | --- | --- |
| `python` | open | `UNDECIDED` |
| `jax` | open | `UNDECIDED` |
| `jaxlib` | open | `UNDECIDED` |
| `flax` | open | `UNDECIDED` |
| `optax` | open | `UNDECIDED` |
| `orbax-checkpoint` | open | `UNDECIDED` |
| `numpy` | open | `UNDECIDED` |

`UNDECIDED` is intentional until the stack is validated on target hardware.

---

## 3. Lock Validation Checklist

Before freezing versions, run and record:

1. Device init on target host (`H100` visible, BF16 path active)
2. Compile smoke for shape buckets `512/1024/2048`
3. One short train-resume loop using segment boundaries
4. Checkpoint save/load with Orbax
5. Resume consistency smoke aligned with `S8` expectations

If any check fails, do not freeze pins.

---

## 4. Upgrade Policy

- No ad-hoc package bump in active training runs
- Upgrade only as a full tested set (never single-package drift)
- Every upgrade must include:
  - previous vs new lock manifest
  - phase declaration
  - expected metric/failure impact
  - regression artifacts summary

---

## 5. Artifact Expectation

Runtime lock artifacts should be tracked in repo once available (for example lockfile/manifest under project root or `docs/plan/`).

This note defines policy only; it does not yet define a concrete lockfile format.

---

**End of Document**
