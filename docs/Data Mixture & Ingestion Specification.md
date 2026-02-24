# Data Mixture & Ingestion Specification

## 1. Scope

This document defines:

* The global training data mixture
* The internal composition of the Pure LM corpus
* The structure of IR-aligned synthetic data
* The role of benchmark datasets
* Data quality and ingestion constraints
* Change control requirements

This specification is considered a stability-critical training configuration.
Modifications require phase-gated review and regression validation.

---

# 2. Global Data Mixture

## 2.1 Top-Level Composition

| Category                 | Ratio | Description                                   |
| ------------------------ | ----- | --------------------------------------------- |
| Pure LM (Primary Corpus) | 90%   | Standard language model pretraining data      |
| IR-aligned Synthetic     | 10%   | Mechanism-aligned capability reinforcement    |
| Benchmark Data           | 0%    | Regression probe only (not used for training) |

Benchmark datasets (e.g., ARC-family) must not be included in training data and must not influence mixture composition.

---

# 3. Pure LM (90%)

## 3.1 Internal Composition

| Subcategory             | Ratio | Notes                                  |
| ----------------------- | ----- | -------------------------------------- |
| General Clean Text      | 80%   | Books, web text, code, curated corpora |
| Document-Extracted Text | 10%   | PDF / HTML / Word / PPT → clean text   |

### Document-Extracted Text Policy

* Initial allocation: **10% of Pure LM**
* Upper bound: **15%**, subject to stability review
* Inclusion requires passing the Data QA Gate (Section 3.3)

---

## 3.2 Ingestion Constraints

### Allowed Input Formats

* PDF
* HTML
* Word
* PPT

### Ingestion Rules

* Only `clean_text (UTF-8)` may enter the tokenizer.
* Metadata (source, extractor version, hash, provenance) must remain external to token sequences.
* No modification or expansion of the State IR token type set is permitted.

State IR schema stability must be preserved.

---

## 3.3 Data QA Gate (Mandatory)

Document-derived text must satisfy all of the following:

1. Control / non-printable character ratio ≤ 2%
2. Repetition rate ≤ 20% (template/header/footer contamination filter)
3. No severe fragmentation (e.g., average line length < 20 characters with excessive line breaks)
4. Language distribution consistent with expected corpus distribution
5. Extractor version must be pinned and logged

Documents failing any criterion must be excluded from the primary corpus.

Extractor version changes are treated as distributional shifts and require regression validation.

---

# 4. IR-aligned Synthetic (10%)

## 4.1 Objective

Synthetic data is used to reinforce core architectural mechanisms:

* Credit assignment
* Learned routing / gating
* Failure recovery
* Stable state evolution

Synthetic data must not become the dominant optimization objective.

---

## 4.2 Composition

| Category                  | Ratio | Target Mechanism                |
| ------------------------- | ----- | ------------------------------- |
| Multi-step Credit Tasks   | 3%    | Delayed reward / credit routing |
| Routing / Gating Tasks    | 3%    | Learned control flow            |
| Failure Recovery Tasks    | 2%    | Error detection and correction  |
| Structured World Modeling | 2%    | Stable state update dynamics    |

---

## 4.3 Synthetic Constraints

* Must not introduce new State IR token categories.
* Must not enforce fixed reasoning templates.
* Must remain ≤ 10% of total training tokens.
* ARC-family datasets are strictly regression probes, not synthetic sources.

---

# 5. Benchmark Policy

Benchmark datasets:

* Are not included in training.
* Serve exclusively as regression probes.
* Must not influence mixture ratios.
* Must not shape synthetic generation strategies.

---

# 6. Monitoring Requirements

The training pipeline must track:

1. Loss and perplexity sliced by data source
2. Character distribution drift
3. Language distribution drift
4. Document proportion over time
5. Synthetic task performance distribution

Significant drift requires investigation and potential gating.

---

# 7. Change Control

The following changes require regression gating:

* Adjustment of mixture ratios
* Document corpus proportion changes
* Extractor version updates
* Synthetic composition changes
* Addition of new synthetic categories
* Inclusion of benchmark data in training

---

# 8. Final Mixture Summary

```
80% General Clean Text
10% Document-Extracted Text
10% IR-aligned Synthetic (3/3/2/2)

Benchmark datasets = regression only
No State IR schema drift
Synthetic ≤ 10%
```

---

This specification establishes a stable, pretraining-first data regime aligned with architectural invariants and long-run training stability.
