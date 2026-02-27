# Runtime Stack Lock for JAX + Flax NNX

**Document Type:** Design Note (Non-normative)  
**Status:** Active lock policy (decision values fixed)  
**Non-Override Clause:** This note does not override system invariants, contracts, or regression gate policy.

---

## 0. Purpose

Define how runtime versions are pinned for single-H100 training to reduce API churn and resume inconsistency risk.

Related baseline:

- `docs/plan/single-h100-3b-training-profile.md`

---

## 1. Lock Surfaces

The following must be pinned as one tested set:

### 1.1 System / Driver Surface (must be recorded)

- GPU model (e.g., `H100 80GB`)
- NVIDIA driver version
- CUDA runtime version
- cuDNN version (if present/used by the runtime)
- OS + kernel (or container image id, if containerized)

### 1.2 Python + JAX Surface (must be pinned)

- `python`
- `jax`
- `jaxlib` (CUDA-compatible build; record build tag/hash)
- `flax` (NNX API)
- `optax`
- `orbax-checkpoint`
- `numpy`

Optional but recommended pins:

- `ml_dtypes`
- `tensorstore` (if checkpoint backend requires it)

### 1.3 Compilation / XLA Surface (must be recorded)

- `XLA_FLAGS` (full string)
- JAX/XLA-related env vars that can affect numerics or compilation (record full key/value pairs), for example:
  - `JAX_ENABLE_X64`, `JAX_DEFAULT_MATMUL_PRECISION`, `JAX_DISABLE_JIT`
  - `XLA_PYTHON_CLIENT_MEM_FRACTION`, `XLA_PYTHON_CLIENT_PREALLOCATE`

---

## 2. Lock Decision Values

| Surface | Decision | Value |
| --- | --- | --- |
| `lock_manifest.required` | fixed | `true` |
| `lock_manifest.schema` | fixed | `iris.runtime_lock_manifest/v1` |
| `phase_c_plus_upgrade_policy` | fixed | `frozen_unless_baseline_rebuild` |
| `checkpoint.runtime_lock_manifest_id` | fixed | required |
| `checkpoint.runtime_lock_manifest_sha256` | fixed | required |
| `python/jax/jaxlib/flax/optax/orbax/numpy` | fixed policy | exact versions must be pinned in manifest before Phase `C` gate |

Version numbers are run/environment-specific and must be taken from the validated lock manifest, not from ad-hoc package snapshots.

---

## 3. Lock Validation Checklist

Before freezing versions, run and record:

1. Device init on target host (`H100` visible, BF16 path active)
2. Compile smoke for shape buckets `512/1024` (and `2048` only in dedicated bucket-curriculum phase)
3. One short train-resume loop using segment boundaries
4. Checkpoint save/load with Orbax
5. Resume consistency smoke aligned with `S8` expectations

If any check fails, do not freeze pins.

---

## 4. Upgrade Policy

- No ad-hoc package bump in active training runs
- Upgrade only as a full tested set (never single-package drift)
- Phase `C` baseline freeze: **no upgrades** unless the change is treated as a baseline rebuild with full activated-suite regression artifacts.
- Every upgrade must include:
  - previous vs new lock manifest
  - phase declaration
  - expected metric/failure impact
  - regression artifacts summary

---

## 5. Artifact Expectation

Runtime lock artifacts should be tracked in repo once available (for example lockfile/manifest under project root or `docs/plan/`).

### 5.1 Lock Manifest Format (v1, JSON)

Store a single manifest artifact per validated stack. Minimum required fields:

```json
{
  "schema": "iris.runtime_lock_manifest/v1",
  "created_at": "YYYY-MM-DDTHH:MM:SSZ",
  "phase": "A|B|C|D|E",
  "host": {
    "os": "...",
    "kernel": "...",
    "gpu": "...",
    "nvidia_driver": "...",
    "cuda_runtime": "...",
    "cudnn": "..."
  },
  "python": { "version": "...", "packages": [{ "name": "jax", "version": "...", "hash": "..." }] },
  "jax": {
    "jax": "...",
    "jaxlib": "...",
    "jaxlib_build": "...",
    "xla_flags": "...",
    "env": { "JAX_ENABLE_X64": "...", "JAX_DEFAULT_MATMUL_PRECISION": "..." }
  }
}
```

### 5.2 Checkpoint Metadata Requirement

Every checkpoint (segment or full) must record:

- `runtime_lock_manifest_id`
- `runtime_lock_manifest_sha256`

This is required for `S8` resume investigations and to prevent silent "same checkpoint, different runtime" drift.

---

**End of Document**
