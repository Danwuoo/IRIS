# DevelopmentPlan.md

**Integrated Development Plan for IRIS Architecture**

---

## 0. 計畫定位與閱讀指引

本文件定義 **IRIS（Integrated Reasoning via Internal State）** 的整體開發計畫骨架，目標是：

* 保證所有開發行為 **不違反既有規範與合約**
* 提供一條 **可增量推進、可回歸、可診斷** 的工程主線
* 將「工具 / benchmark / 資料」重新定位為 **診斷與壓測儀器**，而非智慧來源

本文件 **不承載實作細節**。
每個 Phase 的具體內容、接口、實驗策略，均放在：

```
docs/plan/phase_*.md
```

---

## 1. 計畫設計原則（不可違反）

以下文件構成 **本計畫的上位約束**。任何 Phase、PR、實驗或 shortcut，只要與下列文件衝突，即視為無效設計。

### 1.1 系統級硬約束（Authoritative）

* `docs/System Invariants & Non-Negotiables.md`
* `docs/Routing, Gating, and Control Are Learnable.md`
* `docs/What This Model Is Explicitly NOT.md`

**核心原則摘要（非替代原文）**

* 唯一大容量 trunk（SSM/Mamba）
* 所有 Level（L0–L6）必須存在於權重拓撲中
* routing / gating / control 必須可學，不得落入 if–else
* 不得以工具或 symbolic executor 取代 Level 2/3/6 的責任

---

### 1.2 State IR 規格（Normative）

* `docs/State IR Canonical Spec.md`
* `docs/State IR Examples & Edge Cases.md`

**計畫層級強制規則**

* 全系統僅存在一個 canonical State IR
* Phase 不得引入臨時 token 類型
* Program IR 永遠不屬於 State IR
* abstraction（macro）≠ program ≠ control

---

### 1.3 Level Contracts（不可跨界）

* `docs/Level Contracts/Level 0–1 Contract.md`
* `docs/Level Contracts/Level 2 Contract.md`
* `docs/Level Contracts/Level 3–4 Contract.md`
* `docs/Level Contracts/Level 5–6 Contract.md`

**計畫層級解讀**

* Phase 之間可以「晚啟用」某 Level
* **不允許**「暫時不存在」某 Level
* 不允許把失敗責任轉嫁到不屬於該 Level 的模組

---

### 1.4 Credit / Failure Recovery（強制對齊）

* `docs/Credit Assignment & Failure Recovery Model.md`

**計畫層級含義**

* 所有 Phase 都必須能被 failure taxonomy 診斷
* regression 的單位不是「任務」，而是「能力是否被破壞」

---

## 2. 開發節奏總覽（Phase A–E）

本計畫採 **Phase A → E 的單向推進**，但允許：

* 回退（rollback）
* 平行實驗（branch）
* 跨 Phase regression gate

| Phase | 核心目的                          | 是否允許留白  |
| ----- | ----------------------------- | ------- |
| A     | Failure / Verifier / Trace 基建 | 否       |
| B     | 工具改造（NVARC / re-arc）          | 否       |
| C     | 最小模型 × 工具閉環                   | 否       |
| D     | ConceptARC 作為診斷儀器             | 否       |
| E     | 官方 benchmark 作為回歸 harness     | 是（策略留白） |

---

## 3. Always-On（跨 Phase 永久啟用規則）

以下規則 **自 Phase A 起永久生效**，任何 Phase 均不得關閉。

### 3.1 Failure First 原則

* 不先追 accuracy / score
* 任何「能力提升」必須能對應到：

  * failure 類型減少
  * credit routing 更集中
  * recovery 行為更精準

---

### 3.2 無隱性智慧原則

* 工具 ≠ solver
* benchmark ≠ supervision oracle
* 若移除某工具後模型能力不變，表示該工具 **未參與智慧**

---

### 3.3 Regression Gate 強制存在

* 每次改動必須回答一句話：

> **「我修了 A，是否悄悄毀了 B？」**

* regression 定義與流程集中於：

  * `docs/plan/regression.md`
  * `docs/plan/metrics.md`

---

### 3.4 Resumable Training Consistency (Always-On)

* Training runs must support resume with semantic consistency between uninterrupted and resumed paths.
* Checkpoints are written only at segment boundaries; restart replays any pending segment to preserve exactly-once apply semantics.

---

## 4. Gate 規則（Phase 進出條件）

### 4.1 Phase 進入 Gate（Entry Gate）

任何 Phase 若無法滿足以下條件，**不得開始**：

1. 上一 Phase 的 regression 任務全部通過
2. failure taxonomy 無新增「無法歸因」類別
3. credit routing 分佈穩定（不確定：穩定性的數值門檻，需後續在 metrics.md 定義）

---

### 4.2 Phase 退出 Gate（Exit Gate）

Phase 結束必須產出：

* 可重跑的實驗流程
* 可回放的 trace
* 可比較的指標（before / after）

否則該 Phase 視為 **未完成**

---

## 5. Phase 對齊總覽

### Phase A — Failure / Verifier / Trace 基建

* **引用**

  * Credit Assignment & Failure Recovery
  * Routing, Gating, and Control Are Learnable
* **新增產出**

  * `docs/plan/metrics.md`
  * `docs/plan/regression.md`
* **目標**

  * 沒有「不知道怎麼錯」的 case

---

### Phase B — 工具改造（NVARC / re-arc）

* **核心引用**

  * `docs/工具、benchmark 去官方化.md`
* **工具角色**

  * NVARC：conditional failure amplifier
  * re-arc：paired task generator
* **產出**

  * failure-tagged generation config
  * paired task schema
* **目標**

  * 工具輸出能被 verifier / credit router 消化

---

### Phase C — 最小模型 × 工具閉環

* **核心約束**

  * State IR 規格
  * Level 2 / Level 5–6 Contract
* **程式碼落點**

  * `src/`
  * `src/runner/`
  * `src/schema/`
* **目標**

  * 一條完整「失敗 → 診斷 → recovery」閉環

---

### Phase D — ConceptARC 作為診斷儀器

* **工具**

  * `tools/ConceptARC/`
* **新增**

  * `docs/plan/conceptarc_buckets.md`
  * `src/eval/conceptarc/`
* **目標**

  * 從 aggregate score 轉為 concept isolation / leakage

---

### Phase E — 官方 benchmark 作為回歸 harness（策略留白）

* **工具**

  * `tools/arc-agi-benchmarking/`
* **定位**

  * parser / verifier supervision / regression harness
* **目標**

  * benchmark 只回答「是否退化」，不回答「是否聰明」

---

## 6. 文件結構與維護規則

### 6.1 主文件（本文件）

* 只放：

  * 原則
  * Gate
  * Phase 定義
* 不放：

  * API
  * hyperparameter
  * 實驗數值

---

### 6.2 Phase 子文件

* 每個 Phase 一個檔案
* 可自由增修
* 不得修改本文件中的硬規則

---

## 7. 結語：計畫的真正目的

本 Development Plan 的目的不是「跑出分數」，而是確保：

* 每一次失敗都 **可被理解**
* 每一次改進都 **不會破壞既有能力**
* 系統的智慧 **確實存在於權重與結構中**

若某一步讓你開始依賴：

* 手寫規則
* benchmark hack
* 工具當 oracle

那一步即使有效，也必須被視為 **偏離本計畫的錯誤路徑**。

---

**End of DevelopmentPlan.md**
