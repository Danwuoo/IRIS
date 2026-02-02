# Phase C — 最小模型 × 工具閉環（Minimal Model–Tool Closed Loop）

## 0. Phase 定位與目標

Phase C 的目標是建立**第一個結構上正確、可被信用分配與診斷的最小可運行系統**，而非追求任務成功率。

本 Phase 必須完成：

1. **模型主幹（Trunk）＋ Level 0–6 Head 的第一次實體落地**
2. **State IR → Program → Execution → Verification → Credit Routing 的閉環**
3. **工具（datasets / re-arc / NVARC）僅作為資料與擾動來源，不承擔推理權威**
4. **所有控制、路由、終止行為均可被 L3/L6 診斷與學習**

> 成功標準不是「解得出 ARC 題」，
> 
> 
> 而是 **失敗時，系統知道「哪一層出了什麼類型的錯」**。
> 

---

## 1. 本 Phase 的硬性引用約束（不可違反）

Phase C 的所有設計與實作，必須滿足並可被以下文件約束：

### 1.1 State 與表示

- `docs/State IR Canonical Spec.md`
- `docs/State IR Examples & Edge Cases.md`

### 1.2 Level 職責與邊界

- `docs/Level Contracts/Level 2 Contract.md`
- `docs/Level Contracts/Level 5–6 Contract.md`
- `docs/Level Contracts/Level 0–1 Contract.md`（即使暫時弱化，權重仍需存在）

### 1.3 系統級不變量

- `docs/System Invariants & Non-Negotiables.md`
- `docs/Routing, Gating, and Control Are Learnable.md`
- `docs/Credit Assignment & Failure Recovery Model.md`
- `docs/What This Model Is Explicitly NOT.md`

任何違反上述文件的「捷徑型成功」在 Phase C 中都視為 **失敗**。

---

## 2. Phase C 的系統範圍（Scope）

### 2.1 **明確包含**

- 單一大容量 Trunk（SSM/Mamba 為主）
- Level 0–6 **全部存在的權重模組**
- Program IR（不進入 State IR）
- Verifier / Confidence / Credit Router 的最小可用版本
- 可觀測的 execution trace 與 failure signals

### 2.2 **明確不包含**

- 任務特化 heuristic
- 手寫 DSL executor 作為主要執行語義
- 固定 beam / depth / stop 規則
- 以工具或 benchmark 取代 verifier 的正確性判斷

---

## 3. Repo 實體落點（Phase C 新增 / 啟用）

### 3.1 原則

- **模型主體只落在 `src/`**
- `tools/` 永遠不承載核心推理或控制語義
- Phase C 是 `src/` 的第一次實質啟用

### 3.2 新增結構（建議）

src/

├── runner/

│ ├── run_once.py # 單次推理循環（Phase C 主入口）

│ └── interfaces.py # datasets / tools 的最小 adapter

│

├── schema/

│ ├── state_ir.py # 嚴格對齊 State IR Canonical Spec

│ ├── program_ir.py # Program tokens（非 State IR）

│ └── trace.py # execution / failure trace 結構

│

├── trunk/

│ └── mamba_trunk.py # 唯一大容量 trunk

│

├── levels/

│ ├── level0.py

│ ├── level1.py

│ ├── level2.py

│ ├── level3.py

│ ├── level4.py

│ ├── level5.py

│ └── level6.py

│

└── routers/

├── invocation_router.py

├── fusion_router.py

└── output_router.py

---

## 4. Phase C 的「最小閉環」定義

Phase C **必須至少跑通以下一次完整循環**：

State IR (Z)

→ Trunk contextualization

→ Level 4 (optional memory read)

→ Level 2 Program Proposal

→ Level 2 Neural Execution

→ Level 6 Verification / Confidence

→ Level 3 Termination / Budget update

→ Level 6 Credit Routing

### 4.1 關鍵要求

- **Program IR 永遠不得注入 State IR**
- Execution 對 State 的影響只能是：
    - ΔZ / gated residual / FiLM
- Verifier 不等於「答案比對器」
- Credit Router 輸出的是 **分佈，不是指令**

---

## 5. 各 Level 在 Phase C 的最小責任

### 5.1 Level 0–1（存在性優先）

- 權重模組必須存在並可被呼叫
- 可輸出退化（例如極簡 objectization）
- 不可被 code bypass 或 mock 掉

### 5.2 Level 2（核心）

- 至少能：
    - 提出 **多個** program 候選
    - 執行後產生 **可區分的結果表徵**
- 若 executor 尚有硬 control，**必須明確標註為 temporary technical debt**

### 5.3 Level 3（控制存在性）

- Budget / termination 為 learned head
- 即使初期行為近似 random，也不可寫死

### 5.4 Level 5（Abstraction）

- Macro token 可為空
- Selector / Updater 權重必須存在
- 不得用規則直接 collapse abstraction

### 5.5 Level 6（Phase C 的驗收核心）

- 必須輸出：
    - validity / violation logits
    - calibrated confidence
    - credit routing distribution（L0–L5）
- Phase C 是否成功，**主要由 L6 能否合理「指錯」判定**

---

## 6. 資料與工具在 Phase C 的角色

### 6.1 Dataset 使用策略

- `MiniARC`：必跑（smoke + regression）
- `ARC-AGI-1`：小子集即可
- `re_arc`：只用於 paired-task 或表示擾動

### 6.2 工具定位（嚴格）

- re-arc / NVARC：
    - 只能產生 **輸入與變體**
    - 不得提供正確性語義
- 所有正誤、置信、診斷 → **只來自 L6**

---

## 7. Phase C 的驗收條件（Gate）

Phase C **通過**，需同時滿足：

1. 系統可在錯誤輸出時，穩定產生：
    - 非零的 credit routing 分佈
    - 可重現的 failure 類型差異
2. 移除任一 Level（L0–L6）會：
    - 破壞閉環
    - 或導致診斷語義崩潰
3. 沒有任何 task-specific heuristic 被寫入 control code

Phase C **失敗** 的典型徵象：

- 任務成功但 L6 無法解釋原因
- L3 行為可被 if/else 完整替代
- 工具結果被當成 truth oracle 使用

---

## 8. Phase C 的輸出產物（Artifacts）

- `src/` 下完整模型骨架
- 一組可重跑的 failure trace（JSON 或等價格式）
- 能支持 Phase D（ConceptARC 診斷）與 Phase E（regression harness）的接口

---

## 9. 與後續 Phase 的銜接

- Phase D 將**不修改核心閉環**，只擴充診斷解析度
- Phase E 將把 Phase C 的 L6 + L3 行為放入回歸與破壞檢查

> Phase C 是唯一允許「大量失敗」的 Phase，
> 
> 
> 但 **不允許「不知道為什麼失敗」**。
>