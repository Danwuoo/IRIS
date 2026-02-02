# Phase B — 工具改造：NVARC / re-arc

**定位：資料與任務生成層的「失敗語義放大器」**

---

## B.0 Phase 目標與邊界

### B.0.1 Phase 目標

Phase B 的目標不是提升整體解題率，而是**改造既有工具，使其成為可控、可診斷、可回歸的能力放大器**，具體而言：

1. 讓資料生成**對齊內部 failure taxonomy 與 Level 責任邊界**
2. 讓工具輸出可被：
    - Verifier（L6）穩定標註
    - Credit Router（L6）合理歸因
    - Regression harness（Phase E）重複驗證
3. 消除「工具即 oracle」「benchmark 即真理」的隱性假設

Phase B 是 **Phase C（模型 × 工具閉環）之前的必要前置條件**。

---

### B.0.2 明確不在本 Phase 處理的事項（Non-Goals）

- 不在 Phase B：
    - 設計或調整模型結構（屬於 Phase C）
    - 引入任何 symbolic shortcut 作為「正確性保證」
    - 以工具結果直接驅動控制邏輯（違反 *Routing, Gating, and Control Are Learnable*）

---

## B.1 上位約束與引用文件（必讀）

Phase B 的所有改造 **必須** 同時滿足以下文件的硬性約束：

- `docs/System Invariants & Non-Negotiables.md`
- `docs/Routing, Gating, and Control Are Learnable.md`
- `docs/What This Model Is Explicitly NOT.md`
- `docs/Credit Assignment & Failure Recovery Model.md`
- `docs/工具、benchmark 去官方化.md`

任何違反上述文件精神的工具改造，即使短期有效，也視為 **架構性錯誤**。

---

## B.2 核心原則：工具 ≠ 正解來源

### B.2.1 工具在本系統中的角色重新定義

| 項目 | 舊假設（需移除） | Phase B 新定義 |
| --- | --- | --- |
| NVARC | 任務覆蓋最大化 | **失敗型態定向放大器** |
| re-arc | 規則變形生成 | **歸納邊界破壞器（paired tasks）** |
| 工具輸出 | 近似正確答案 | **訓練 / 診斷信號來源** |

工具的存在價值，在於**塑造梯度與診斷密度**，而不是提供可依賴的「正確行為」。

---

## B.3 NVARC 改造規格（Conditional Generator）

### B.3.1 問題診斷（Why 官方用法不成立）

官方 NVARC 假設：

- 任務多樣性 ≈ 能力提升
- 任務難度分布 ≈ 模型瓶頸分布

在你的系統中，這兩個假設均 **不成立**，因為：

- 能力瓶頸是 **Level-conditional** 的
- 失敗是 **語義可分類、可重現的**

---

### B.3.2 改造目標

將 NVARC 改為 **conditional generator**，其條件空間不是「難度」，而是 **failure tag**。

### Failure tag（示例，非最終）

| failure_tag | 對齊 Level | 語義描述 |
| --- | --- | --- |
| `obj_split_merge` | L0 | 物件被錯誤分裂或合併 |
| `relation_overfit` | L0/L1 | 關係對稱但語義不同 |
| `procedure_misorder` | L2 | 局部正確、全局錯誤 |
| `premature_abstraction` | L5 | 規則存在例外 |

> 若目前 failure taxonomy 尚未穩定 → 不確定，需先回補 Phase A 的 verifier / tagging 能力，再進入 Phase B。
> 

---

### B.3.3 介面契約（必須滿足）

NVARC 改造後 **至少** 提供以下介面：

```yaml
generate(
  failure_tag: str,
  intensity: float,      # 放大強度（非難度）
  seed: Optional[int],
) -> List[Task]

```

約束：

- `failure_tag` 必須可追溯到 failure taxonomy
- `intensity` 不得直接映射為 grid size 或步數（避免隱性 heuristic）
- 所有生成任務需附帶 metadata：
    - `failure_tag`
    - `generator_config_hash`

---

### B.3.4 產出落點（repo）

- `tools/NVARC/configs/failure_tags.yml`
- `tools/NVARC/output/<failure_tag>/`
- Metadata 不得嵌入任務內容本身，必須為外部欄位

---

## B.4 re-arc 改造規格（Paired Tasks Generator）

### B.4.1 核心問題

原始 re-arc 假設：

> 規則可以被語法性枚舉，且模型應該對此不變。
> 

這對你的架構是 **危險假設**，因為它鼓勵：

- Symbolic shortcut
- Program IR 與 DSL 的語義混淆

---

### B.4.2 改造原則：Paired Tasks Only

re-arc **不得**直接輸出單一新任務，而是輸出 **成對任務**：

```
(Task A, Task B)

```

且必須滿足：

- 語義等價
- 表示不同
- 僅改變一個可控因素

### 合法變化示例

- 顏色 permutation（保持關係）
- 座標平移（保持 topology）
- 表示方式不同（block vs outline）

---

### B.4.3 用途限制（非常重要）

Paired tasks **不可**用於：

- 計算 accuracy
- 當作新訓練資料直接餵模型

Paired tasks **僅可**用於：

- 檢測 program / abstraction 是否 representation-invariant
- Verifier 一致性測試
- Regression 對比

---

### B.4.4 產出落點（repo）

- `tools/re-arc/pairs/`
    - `pair_id/`
        - `task_A.json`
        - `task_B.json`
        - `pair_meta.json`

`pair_meta.json` 必須包含：

- invariant type
- changed factor
- generator config hash

---

## B.5 與 Verifier / Credit Router 的接口關係

### B.5.1 Phase B 不訓練 Verifier，但**塑造其可訓練性**

所有工具輸出必須：

- 可被 verifier head 消費
- 可映射至 failure taxonomy
- 不隱含「正確性」

### B.5.2 嚴禁行為

- 禁止在工具中內嵌 correctness rule
- 禁止在工具中提前判定「哪個 Level 錯了」
- 禁止將工具結果直接轉為 control signal

---

## B.6 Phase B 驗收條件（Exit Criteria）

Phase B 視為完成，需同時滿足：

1. NVARC 可依 failure_tag 穩定生成任務
2. re-arc 只輸出 paired tasks，且 invariant 可被 verifier 檢測
3. 所有生成任務具備可追溯 metadata
4. 工具輸出可被 regression harness 重複使用
5. 無任何 symbolic shortcut 被引入

若任一條件未滿足 → Phase B **未完成**。

---

## B.7 Phase B 與後續 Phase 的依賴關係

- Phase C（模型 × 工具閉環）**強依賴** Phase B
- Phase E（回歸與 benchmarking）將直接消費 Phase B 產出

任何跳過 Phase B 的模型實驗，其結果 **不可被信任**。

---

**End of Phase B**