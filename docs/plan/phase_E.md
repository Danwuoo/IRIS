# Phase E — arc-agi-benchmarking 作為回歸與 Verifier Harness

## 0. Phase 定位與非目標（Normative）

### 0.1 Phase 定位

Phase E 的唯一目的，是把 **arc-agi-benchmarking** 固定為：

- **回歸測試（regression harness）**
- **Verifier / Calibration 的外部一致性錨點**
- **跨 Phase 穩定性檢查器**

它不是：

- leaderboard 衝分階段
- 搜索或推理能力放大器
- 任務策略調優工具

### 0.2 明確非目標（對齊 What This Model Is Explicitly NOT）

Phase E **不做**以下任何事情：

- 不引入 task-specific heuristic 以迎合官方 verifier
- 不將 pass/fail 當成最終正確性判斷
- 不把 arc-agi-benchmarking 當作 solver 或 planner
- 不讓 benchmark schema 反向塑形 State IR 或 Program IR

---

## 1. 上位約束（必須遵守）

Phase E 的所有設計與產出，必須同時符合以下文件（僅引用，不重複定義）：

- `docs/System Invariants & Non-Negotiables.md`
- `docs/Routing, Gating, and Control Are Learnable.md`
- `docs/What This Model Is Explicitly NOT.md`
- `docs/State IR Canonical Spec.md`
- `docs/State IR Examples & Edge Cases.md`
- `docs/Level Contracts/Level 3–4 Contract.md`
- `docs/Level Contracts/Level 5–6 Contract.md`
- `docs/Credit Assignment & Failure Recovery Model.md`
- `docs/工具、benchmark 去官方化.md`

若 Phase E 與上述任一文件衝突，**Phase E 自動無效**。

---

## 2. 工具角色重定義：arc-agi-benchmarking

### 2.1 工具角色（重新定義）

在本系統中，arc-agi-benchmarking 被定義為三層結構：

1. **Parser / Schema 層**
    - 強制輸出格式、欄位完整性、資料合法性
2. **Verifier Supervision 層**
    - 為 Level 6 Verifier Head 提供外部一致性訊號
3. **Regression Harness**
    - 用於跨 Phase、跨版本的穩定性檢查

**禁止用途**：

- 作為內部 correctness oracle
- 作為 search termination 的硬 gate
- 作為訓練時唯一 reward

---

## 3. Phase E 的 repo 落點與結構

### 3.1 主要新增路徑

src/eval/arc_agi_benchmarking/

├── adapter.py # 對齊官方 schema 的輸出轉換

├── runner.py # 封裝 run_all / task list

├── verifier_bridge.py # 將官方 verifier 結果映射為 L6 訓練/診斷訊號

└── reports/

├── regression/

└── calibration/

### 3.2 禁止事項

- 不得修改 `tools/arc-agi-benchmarking/` 原始邏輯
- 不得在該工具中插入任何模型內部資訊
- 所有適配行為必須在 `src/eval/arc_agi_benchmarking/` 完成

---

## 4. Verifier 對齊策略（Level 6）

### 4.1 對齊目標

官方 verifier 的角色僅是：

> 外部一致性檢查器
> 

Level 6 的 verifier head 目標是學習：

- 與官方 verifier **高一致性**
- 但**不複製其規則**

### 4.2 對齊方式

- 官方 verifier 結果 → 作為 **noisy supervision**
- 與內部 verifier 的分歧 → 記錄為 calibration error
- 不允許 hard-code 對齊任何規則

### 4.3 校正輸出

Level 6 必須至少輸出：

- validity score
- confidence / calibration score
- failure-type logits（對齊 failure taxonomy）

---

## 5. Regression Harness 設計

### 5.1 核心問題（唯一允許的問題）

> 「我修了 A，是否悄悄毀了 B？」
> 

### 5.2 Regression 的對象

回歸檢查必須至少覆蓋：

- 不同 Phase 的核心能力
- 不同 failure 類型
- 不同 concept bucket（若已定義）

### 5.3 Regression 輸出

每次回歸必須輸出：

- pass/fail（整體）
- 各 failure 類型變化
- confidence calibration shift
- credit routing 分布變化（L6 → L3）

---

## 6. 與 Credit Assignment 的連動

### 6.1 信號流向（嚴格）

arc-agi-benchmarking

↓

Verifier discrepancy

↓

Level 6 診斷

↓

Credit routing distribution

↓

Level 3 recovery / policy adjustment

### 6.2 禁止事項

- 官方 verifier 結果 **不得**直接驅動：
    - search depth
    - beam size
    - termination
- 所有 recovery 行為必須經由 L3 的 learned policy

---

## 7. 與 Phase D（ConceptARC）的區隔

| 工具 | 角色 |
| --- | --- |
| ConceptARC | 概念級診斷與隔離 |
| arc-agi-benchmarking | 整體一致性與回歸 |

Phase E **不負責**概念拆解；若需要 concept 級分析，必須回到 Phase D 管線。

---

## 8. Gate 條件（Phase E 完成定義）

Phase E 視為完成，必須同時滿足：

1. arc-agi-benchmarking 可被一鍵跑成 regression
2. L6 verifier 與官方 verifier 有可量化一致性
3. regression 結果可跨 commit / branch 比較
4. 沒有任何 heuristic 或 hard rule 為了通過 benchmark 而存在

---

## 9. Phase E 的產出物清單

- `src/eval/arc_agi_benchmarking/` 全套 adapter
- regression 報表樣例
- calibration 報表樣例
- `docs/plan/regression.md` 中新增 Phase E gate 條款

---

## 10. Phase E 的退出條件

Phase E **不會「結束」**，而是進入 **Always-On** 狀態：

- 每次架構或訓練變更
- 必須通過 Phase E regression
- 若失敗，回退或觸發 failure recovery

---

**End of Phase E**