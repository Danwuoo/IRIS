# Single-H100 3B Open Decisions

**Document Type:** Design Note (Non-normative)  
**Status:** Open decision register  
**Non-Override Clause:** This note does not override system invariants, State IR contracts, Level contracts, or phase-gate policy.

---

## 0. Purpose

Track decisions that remain unresolved for the single-card 3B pretraining profile.

Related baseline:

- `docs/plan/single-h100-3b-training-profile.md`

---

## 1. Decision Register

| ID | Topic | Options | Decision Needed | Failure/Metric Risk |
| --- | --- | --- | --- | --- |
| `OD-01` | Vocab size | `50k` vs `100k` | Final tokenizer-vocab target | `F_PROC`, `prog.diversity`, cost profile |
| `OD-02` | Exact stack pins | JAX/Flax/NNX/Optax/Orbax exact versions | Lock tested runtime set | Reproducibility, `S1`, `S8` |
| `OD-03` | Segment sizing | samples-per-segment and dataset slice mapping | Final segment boundary policy | Resume drift risk, `S8` |
| `OD-04` | Checkpoint retention | keep-last-N / archive cadence / storage budget | Long-run storage policy | Recovery reliability, ops risk |
| `OD-05` | Eval cadence | steps-per-regression probe | Cost vs drift detection latency | Late detection of gate regressions |
| `OD-06` | Tolerance profile | epsilon profile id and freeze point | Baseline/tolerance freeze | Gate ambiguity, false passes |
| `OD-07` | Bucket usage policy | 512/1024 use only debug or scheduled curriculum | Compile-vs-throughput tradeoff | Hidden distribution shift |
| `OD-08` | Remat evolution | keep block-only vs evaluate finer granularity later | Memory-throughput policy | Throughput instability |

---

## 2. Decision Criteria

Each decision must include:

1. Phase impact (`A|B|C|D|E`)
2. Expected failure-taxonomy impact (`F_REP|F_PROC|F_SEARCH|F_MEM|F_ABS|F_EVAL`)
3. Regression-suite impact (`S1` to `S8`)
4. Rollback path and artifact updates

Undeclared decisions are not promotion-ready.

---

## 3. Default Until Decided

Until each item is closed:

- Use the values in `single-h100-3b-training-profile.md`
- Treat unresolved pins/policies as implementation-risk hotspots
- Do not bypass contracts to "move faster"

---

## 4. Closure Format

When closing an item, append:

```text
[OD-XX] status=closed
decision=...
effective_date=YYYY-MM-DD
phase=...
expected_metric_impact=...
regression_artifacts=...
```

---

**End of Document**
