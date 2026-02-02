# Phase D — ConceptARC 作為診斷儀器

> **Phase 定位一句話**：
> Phase D 不追求「更高解題率」，而是把 **ConceptARC** 轉化為一個**可結構化讀取的診斷儀器**，用來暴露 abstraction、program reuse、credit routing 與 concept isolation 的系統性問題。

---

## D.0 Phase 目標與非目標

### D.0.1 核心目標（必須同時滿足）

1. **把 ConceptARC 從 benchmark 轉為 diagnostic harness**

   * 不再只輸出 aggregate accuracy
   * 必須輸出 *per-concept*、*per-failure-type*、*per-Level* 的診斷訊號

2. **建立 concept isolation / leakage 的可觀測指標**

   * 能回答：學會 A concept，是否破壞 B concept？
   * 能定位：是 L2 program、L5 abstraction、還是 L4 memory 導致干擾

3. **讓 ConceptARC 成為 Phase E 回歸的上游訊號來源**

   * Phase D 的輸出，必須能被 Phase E regression harness 直接引用

---

### D.0.2 明確非目標（避免誤用）

* ❌ 不以 ConceptARC score 作為模型選型或排名依據
* ❌ 不引入 task-specific heuristic 解法
* ❌ 不將 ConceptARC 視為「更難的 ARC 題庫」
* ❌ 不允許 shortcut（例如：針對單一 concept 寫特判）

---

## D.1 上位約束（引用，不重述）

Phase D **必須完全服從**以下規範文件：

* `docs/System Invariants & Non-Negotiables.md`
* `docs/State IR Canonical Spec.md`
* `docs/State IR Examples & Edge Cases.md`
* `docs/Routing, Gating, and Control Are Learnable.md`
* `docs/Credit Assignment & Failure Recovery Model.md`
* `docs/Level Contracts/Level 3–4 Contract.md`
* `docs/Level Contracts/Level 5–6 Contract.md`

任何 ConceptARC 的使用方式，只要違反上述文件，即視為 **Phase D 失敗**。

---

## D.2 ConceptARC 的角色重定義

### D.2.1 官方 ConceptARC 的「錯誤預設」

官方常見用法隱含以下假設（**本計畫全部拒絕**）：

* ConceptARC = 高階 ARC
* Aggregate score = 概念理解能力
* 任務彼此獨立

---

### D.2.2 在本系統中的正確定位

在本計畫中，**ConceptARC 是一組 controlled experiments**：

* 每一個 concept bucket = 一個受控干擾實驗
* 任務不是 IID，而是 **共享概念但干擾其他模組**

ConceptARC 的價值在於：

> 讓你看到「系統在哪一層開始把概念搞混」。

---

## D.3 Concept 分桶策略（必須顯式定義）

### D.3.1 文件落點

* `docs/plan/conceptarc_buckets.md`

此文件 **必須存在**，且為 Phase D 的核心產出之一。

---

### D.3.2 最低要求的分桶維度

每一個 ConceptARC 任務，至少要被標註到以下維度：

1. **Primary Concept**

   * 例如：Copy / Count / InsideOutside / Symmetry / Order …

2. **Secondary Interference Concepts**（可為空）

   * 任務中是否隱含其他概念（干擾源）

3. **Expected Abstraction Level**

   * micro / meso / macro
   * 用於對齊 Level 5 行為

4. **Canonical Failure Expectation（預期易錯點）**

   * 表示這類 concept *通常* 會在哪一層出錯（L2/L5/L6）

> 若此標註無法穩定完成，**不確定**：代表 verifier / failure taxonomy 尚未成熟，需回退 Phase C/B 修補。

---

## D.4 必須產出的診斷指標（不是 accuracy）

### D.4.1 Concept Isolation Score

**定義**：

* 在只啟用 / 微調 concept A 時，concept B 的表現變化量

**用途**：

* 偵測 abstraction 或 memory 是否過度共享

---

### D.4.2 Concept Leakage Index

**定義**：

* 在 concept A bucket 中，模型是否錯誤啟動 concept B 對應的 program / macro

**可觀測訊號來源**：

* L2 program proposal 分佈
* L5 macro selector gate
* L4 memory retrieval 類型

---

### D.4.3 Failure Attribution Matrix（Concept × Level）

對每個 concept bucket，輸出：

* L0–L6 的 credit routing 分佈統計
* 是否集中於單一層（健康）或發散（架構問題）

---

## D.5 系統實作落點（repo 對齊）

### D.5.1 評測程式碼

* `src/eval/conceptarc/`

  * loader：讀取 ConceptARC corpus
  * runner：統一呼叫 Phase C 的 runner
  * collector：收集 verifier / credit / macro / program trace

---

### D.5.2 不允許的實作方式

* ❌ 在 tools/ConceptARC 內直接改規則
* ❌ 為 concept 寫 if-else routing
* ❌ 在 evaluation code 中隱式 hard gate Level

所有控制與診斷，**只能讀取權重輸出，不得注入邏輯**。

---

## D.6 與 Level 5 / Level 6 的強制對齊

### D.6.1 Level 5（Abstraction）對齊檢查

ConceptARC 必須能回答：

* 哪些 concept 對 macro abstraction 敏感？
* macro 被 suppress 時，是否改善或惡化？

若所有 concept 對 macro 無差異：
→ Level 5 形同虛設（Phase D fail）。

---

### D.6.2 Level 6（Verifier / Credit Router）對齊檢查

ConceptARC 必須暴露：

* verifier 是否對某些 concept 系統性過度自信 / 保守
* credit 是否錯誤集中到 L3（search）而非真正責任層

---

## D.7 Phase Gate（進入 Phase E 的必要條件）

Phase D **完成的最低條件**：

1. `conceptarc_buckets.md` 完成且可被他人理解
2. 至少一個 **明確的 concept leakage 案例** 被定位到具體 Level
3. ConceptARC 診斷輸出已被接入 `docs/plan/regression.md`

若只能得到「某些題比較難」：
→ Phase D 未完成。

---

## D.8 典型失敗模式（提前列出）

* 把 ConceptARC 當成 tuning 集
* 用 aggregate score 說故事
* 發現 leakage 卻用 heuristic mask 掉
* 把 abstraction 問題誤歸因為 search 不夠

以上任一出現，即表示 **違反 Phase D 設計意圖**。

---

## D.9 Phase D 的交付物總表

| 類型 | 必須產出                              |
| -- | --------------------------------- |
| 文件 | `docs/plan/conceptarc_buckets.md` |
| 程式 | `src/eval/conceptarc/`            |
| 指標 | isolation / leakage / attribution |
| 對齊 | regression harness 可直接引用          |

---

**Phase D 結語**：

> 如果 Phase D 做得對，你會第一次清楚看到：
> 「這個系統不是不會解題，而是在哪一層開始不誠實地泛化。」
