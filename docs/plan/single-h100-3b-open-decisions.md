# Single-H100 3B Open Decisions

**Document Type:** Design Note (Non-normative)  
**Status:** Resolved decision register (`2026-02-26`)  
**Non-Override Clause:** This note does not override system invariants, State IR contracts, Level contracts, or phase-gate policy.

---

## 0. Purpose

Record the finalized values for the single-card 3B pretraining profile.

Related baseline:

- `docs/plan/single-h100-3b-training-profile.md`
- `docs/plan/runtime-stack-lock-jax-flax-nnx.md`
- `docs/Training Segment and Resume Rules (Design Note).md`

---

## 1. Decision Register (Resolved)

| ID | Status | Fixed Value | Failure/Metric Risk |
| --- | --- | --- | --- |
| `OD-01` | closed | `tokenizer.vocab_size = 100000`; protected IR/control sub-vocab required; `rep.tokenizer.ir_fragmentation_rate` target `0.0` | `F_REP/F_PROC`, `S5/S6/S7`, `prog.diversity` |
| `OD-02` | closed | lock manifest v1 required (driver/CUDA/cuDNN/jaxlib build/XLA flags/env vars/packages); upgrades frozen after Phase `C` baseline unless full baseline rebuild | `S1`, `S8` |
| `OD-03` | closed | segment boundary = optimizer-step boundary; no cross-accumulation; wall-clock target `40` min, hard max `45` min; one eval snapshot at each segment end | `S8`, journal replay |
| `OD-04` | closed | retention tiers: `recent=5 segments`, `daily=1`, `phase_milestone=1 permanent`; checkpoint must include model/optimizer/RNG/journal head/lock manifest id+sha | recovery reliability, ops risk, `S8` |
| `OD-05` | closed | per segment: lite probes `S1/S2` + `S3` when active; full activated suites every `24h` or `200` optimizer steps (whichever first); mandatory full regression before phase gate | drift detection latency |
| `OD-06` | closed | freeze tolerance profile at Phase `B -> C` promotion; tightening allowed, relaxation forbidden; epsilon persisted in versioned JSON artifact | gate ambiguity, false pass risk |
| `OD-07` | closed | debug/compile warmup may use `512/1024`; formal training uses single context bucket `1024`; bucket curriculum only in dedicated phase | distribution shift, compile cache churn |
| `OD-08` | closed | remat policy fixed to block-level through Phase `B`; remat changes require baseline checkpoint + full activated-suite regression + runtime manifest bump | `S1` numeric drift, `S8` resume drift |

---

## 2. Canonical Notes

- Regression suites are `S1` through `S8` per `docs/harness/legacy/phase-gate-policy.md`.
- References to `S9` are non-canonical and must be mapped to existing suites/metrics.
- "IR/control tokens" in `OD-01` means tokenizer-reserved strings used in text control markup. This does not change State IR token categories (`T/G/O/R/X/M`).

---

## 3. Closure Records

```text
[OD-01] status=closed
decision=tokenizer.vocab_size=100000; protected_ir_control_sub_vocab=required; rep.tokenizer.ir_fragmentation_rate_target=0.0
effective_date=2026-02-26
phase=C
expected_metric_impact=lower F_REP/F_PROC risk from control-token fragmentation; improved prog.diversity stability
regression_artifacts=S5,S6,S7 diffs with tokenizer.vocab_size metadata

[OD-02] status=closed
decision=runtime_lock_manifest_v1_required; phase_c_plus_upgrade_policy=frozen_unless_baseline_rebuild; checkpoint_metadata_add=[runtime_lock_manifest_id,runtime_lock_manifest_sha256]
effective_date=2026-02-26
phase=C
expected_metric_impact=lower resume drift and numeric drift risk
regression_artifacts=S1,S8 before/after aligned reports

[OD-03] status=closed
decision=segment_boundary=optimizer_step; cross_segment_accumulation=forbidden; segment_wall_clock_target_min=40; segment_wall_clock_hard_max_min=45; segment_end_eval_snapshot=required
effective_date=2026-02-26
phase=C
expected_metric_impact=improved replay determinism and failure localization
regression_artifacts=S8 segment-aligned comparisons

[OD-04] status=closed
decision=checkpoint_retention=[recent:5_segments,daily:1,phase_milestone:1_permanent]; checkpoint_minimum_payload=[model,optimizer,rng,journal_head,runtime_lock_manifest_ref]
effective_date=2026-02-26
phase=C
expected_metric_impact=improved crash recovery robustness without single-point rollback risk
regression_artifacts=retention policy logs + S8 resume checks

[OD-05] status=closed
decision=probe_lite_per_segment=[S1,S2,S3_if_active]; full_regression_interval=[24h_or_200_optimizer_steps_whichever_first]; pre_phase_gate_full_regression=mandatory
effective_date=2026-02-26
phase=C
expected_metric_impact=faster structural drift detection with bounded eval cost
regression_artifacts=scheduled probe logs + full suite reports

[OD-06] status=closed
decision=tolerance_profile_freeze_point=phase_B_to_C_promotion; tolerance_relaxation=forbidden; tightening=allowed; epsilon_artifact=versioned_json
effective_date=2026-02-26
phase=B/C
expected_metric_impact=prevents chronic drift masking and gate ambiguity
regression_artifacts=tolerance profile JSON + phase declaration metadata

[OD-07] status=closed
decision=training_context_bucket=1024_single; warmup_buckets=[512,1024]; mixed_bucket_curriculum=separate_phase_only
effective_date=2026-02-26
phase=C
expected_metric_impact=lower hidden distribution shift from mixed bucket usage
regression_artifacts=S2/S3/S7 comparisons under fixed bucket

[OD-08] status=closed
decision=remat_granularity=block_level_through_phase_B; remat_change_requires=[baseline_checkpoint,full_activated_suite_regression,runtime_manifest_bump]
effective_date=2026-02-26
phase=A/B/C
expected_metric_impact=controls S1 numeric order drift and S8 resume inconsistency
regression_artifacts=S1,S8 regressions across remat change boundary
```

---

## 4. Operational Rule

Any run configuration that deviates from these fixed values must be declared as a new proposal and cannot silently inherit this baseline.

---

**End of Document**
