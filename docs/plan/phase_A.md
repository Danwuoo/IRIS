# Phase A — Failure / Verifier / Trace 基建

## 0. Phase 定位與目標

**Phase A 的唯一目標**是建立一套 **可診斷、可歸因、可回歸** 的失敗與驗證基礎設施，

使後續所有 Phase（B–E）的改動都能回答同一個問題：

> 「這次改動修正了哪一類失敗？是否引入了新的退化？」
> 

本 Phase **不追求整體任務成功率提升**，也**不引入完整模型能力**；

任何在 Phase A 中直接優化 accuracy 的行為，均視為架構越權。

---

## 1. 上位約束（必讀，不可違反）

Phase A 的設計與實作，**必須完全服從**以下文件；若發生衝突，以合約文件為準：

### 1.1 系統級不變量

- `docs/System Invariants & Non-Negotiables.md`
- `docs/Routing, Gating, and Control Are Learnable.md`
- `docs/What This Model Is Explicitly NOT.md`

### 1.2 State IR 規格

- `docs/State IR Canonical Spec.md`
- `docs/State IR Examples & Edge Cases.md`

### 1.3 Credit / Failure 規範

- `docs/Credit Assignment & Failure Recovery Model.md`

### 1.4 Level Contracts（僅引用，Phase A 不實作完整能力）

- `docs/Level Contracts/Level 0–1 Contract.md`
- `docs/Level Contracts/Level 5–6 Contract.md`

---

## 2. Phase A 不做的事（明確排除）

為避免後續責任混淆，本 Phase **明確不包含**：

- ❌ 完整 Level 2 program induction
- ❌ 搜尋策略、beam policy、termination heuristic
- ❌ 工具（NVARC / re-arc）的語義改造
- ❌ ConceptARC 或 arc-agi-benchmarking 的正式接入
- ❌ 任務特化規則、hard-coded solver

Phase A 的所有產出，都必須是 **診斷性、結構性**，而非解題性。

---

## 3. 核心交付物一覽

Phase A 必須交付以下 **三類基礎設施**：

1. **Failure Taxonomy（失敗分類體系）**
2. **Verifier / Diagnostic Signal（驗證與診斷信號）**
3. **Trace / Logging / Regression Skeleton（可回溯記錄與最小回歸骨架）**

---

## 4. Failure Taxonomy（失敗分類體系）

### 4.1 設計原則

Failure taxonomy 的目的不是「描述錯誤答案」，而是：

- 對齊 **Level 責任邊界**
- 能被 **Verifier Head** 消費
- 能被 **Credit Router** 用於歸因
- 能被 **回歸測試**穩定比對

**禁止**以下類型的分類方式：

- 任務語義導向（例如「畫錯顏色」、「沒看懂規則」）
- 表面症狀導向（例如「輸出全黑」、「shape 不對」）

---

### 4.2 Canonical Failure Categories（對齊合約）

所有 failure **至少**需映射到以下一級分類（可多選）：

| 類別 | Level | 語義說明 |
| --- | --- | --- |
| Representation Failure | L0 / L1 | State IR 本身錯誤或不一致 |
| Procedural Failure | L2 | 程序歸納 / 執行語義錯誤 |
| Search / Budget Failure | L3 | 計算資源配置錯誤 |
| Memory Failure | L4 | 檢索 / 寫入 / 合併錯誤 |
| Abstraction Failure | L5 | 抽象粒度錯誤 |
| Evaluation / Diagnosis Failure | L6 | 驗證或信心校準錯誤 |

> 若某失敗無法歸入任何一類，不確定是否代表 taxonomy 不完整或 trace 資訊不足；此狀態必須被顯式記錄。
> 

---

### 4.3 文件落點

- `docs/plan/metrics.md`

最低結構要求（可擴充，但不得刪減）：

```yaml
failure_taxonomy:
  - code: L0_OBJECT_MISS
    level: L0
    description: object token 缺失或過度碎裂
  - code: L1_DYNAMICS_INCONSISTENT
    level: L1
    description: rollout 狀態不一致
  - code: L2_PROGRAM_MISORDER
    level: L2
    description: 程序步驟順序錯誤
  - code: L5_OVER_ABSTRACTION
    level: L5
    description: macro 過度合併導致語義丟失

```

---

## 5. Verifier / Diagnostic Signal（Level 6 骨架）

### 5.1 設計立場

Verifier 在 Phase A **不是判斷對錯的裁判**，而是：

- 產生 **連續、可校準的診斷信號**
- 對 failure taxonomy 提供 **logit / score**
- 為後續 Credit Router 提供證據

禁止：

- Hard rule 判斷
- Symbolic correctness check
- 任務特化 verifier

---

### 5.2 必備輸出（即使為 stub）

每次推理至少產生：

| Signal | 說明 |
| --- | --- |
| validity_score | 軟性有效性分數 |
| confidence | 校準後信心（不等於 validity） |
| failure_logits | 對 failure taxonomy 的分佈 |

> 若某 signal 無法可靠估計，允許輸出「不確定」，但不得省略欄位。
> 

---

### 5.3 實作狀態要求

Phase A 允許：

- verifier 為弱模型或隨機初始化
- 校準效果很差

但**不允許**：

- verifier 完全缺席
- verifier 只輸出 binary pass/fail

---

## 6. Trace / Logging / 回溯能力

### 6.1 Trace 的語義要求

Trace 的目標不是 debug 程式碼，而是：

- 重建一次推理「發生了什麼」
- 支援 failure attribution
- 支援跨版本比較

---

### 6.2 最低 Trace 欄位

每一個 task / attempt 至少記錄：

```json
{
  "task_id": "...",
  "state_ir_stats": {
    "num_objects": 0,
    "num_relations": 0,
    "num_events": 0,
    "num_macros": 0
  },
  "verifier": {
    "validity": 0.32,
    "confidence": 0.21,
    "failure_logits": { "L2_PROGRAM_MISORDER": 0.6 }
  },
  "credited_levels": {
    "L2": 0.55,
    "L5": 0.25
  }
}

```

---

## 7. Regression Skeleton（最小回歸骨架）

### 7.1 目的

Phase A 的 regression **不測性能，只測穩定性**：

- failure 分佈是否漂移
- verifier 校準是否惡化
- 是否出現新 failure 類型

---

### 7.2 文件落點（新增）

- `docs/plan/regression.md`

最低內容要求：

- 固定 task 子集（可先用 MiniARC + ARC-AGI-1 小樣本）
- 固定輸出指標（failure 分佈、confidence histogram）
- 明確的 fail 條件（例如：某類 failure 比例 ↑ X%）

---

## 8. Phase A 完成條件（Exit Criteria）

Phase A **完成**的判定標準：

1. Failure taxonomy 文件存在且被實際使用
2. 每次推理都能產生結構化 trace
3. Verifier / credit routing 信號可被消費
4. regression skeleton 可重跑、可比對

**不要求**：

- 高準確率
- 好看的結果
- 任務成功

---

## 9. 與後續 Phase 的接口保證

Phase A 的所有輸出，後續 Phase **不得破壞**，只能擴充：

- Phase B：工具改造必須產生對齊的 failure 標籤
- Phase C：模型能力提升不得移除 trace / verifier
- Phase D/E：所有評測都必須回饋到 Phase A 的 failure 度量

---

## 10. 最終聲明（不可刪）

> Phase A 的價值不在於「模型現在能不能解題」，
> 
> 
> 而在於 **未來任何退化都無法被悄悄掩蓋**。
> 

若 Phase A 做得正確，後續所有失敗都將是「可解釋的失敗」，

而不是「神秘的退化」。