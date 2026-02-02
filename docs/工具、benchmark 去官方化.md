# 工具、benchmark 去官方化

| 工具 | 角色定位 | 功能範圍 |
| --- | --- | --- |
| **NVARC** | 大規模合成引擎 | 用於生成大量合成樣本、增強資料分布 |
| **re-arc (工具版本)** | 規則覆蓋生成工具 | 以規則或轉化策略覆蓋生成變體 |

| Benchmark | 角色定位 | 功能與價值 |
| --- | --- | --- |
| **ConceptARC** | 概念級泛化壓測 | 測試模型概念理解與 domain-general 泛化能力 |
| **arc-agi-benchmarking** | 官方績效評鑑 | 統一標準評測 + verifier supervision 控制 |

## 一、改「工具」：讓資料生成對齊你的內部失敗語義

### 1. NVARC：從「大量資料」→「定向能力放大器」

**官方用法問題**

NVARC 默認目標是「覆蓋更多 ARC-like 任務」，但這會導致兩個問題：

- 任務分布過於平均，**無法放大你模型真正脆弱的能力**
- 很難對齊到你內部的 Level / 模組責任邊界

**你應該怎麼改**

把 NVARC 改造成 **conditional generator**，條件不是「任務難度」，而是**失敗型態**：

| 失敗型態（你定義） | NVARC 生成約束 |
| --- | --- |
| 物件分裂/合併錯誤 | 強制生成 object ambiguity 任務 |
| 關係過度擬合 | 增加對稱但語義不同的關係 |
| 程序步驟錯序 | 多步但局部一致、全局錯誤的 transformation |
| abstraction 過早 | 任務中存在「例外破壞規則」 |

**關鍵點**

你不是在「擴充資料」，而是在**擴充某一類錯誤的梯度密度**。

如果你目前還沒辦法穩定標註這些錯誤 → **不確定**，那表示你要先補的是 verifier / failure taxonomy，而不是生成器。

---

### 2. re-arc（工具版本）：從「規則變體」→「歸納邊界破壞器」

**官方 re-arc 的隱含假設**

> 規則可被語法性地枚舉與變形
> 

這對人類 DSL 是成立的，但對你這種**反對 symbolic shortcut 的架構**，是危險的。

**你應該怎麼改**

不要讓 re-arc 直接產生「新任務」，而是產生 **paired tasks**：

- Task A：原始任務
- Task B：**只改一個「語義不變但表示不同」的因素**

例如：

- 顏色 permute，但關係不變
- 座標平移，但 topology 不變
- 局部 pattern 相同，但 global aggregation 不同

**用途**

這類 pair 不是拿來算 accuracy，而是用來測：

> 「模型內部的 program / abstraction 是否對 representation 不變？」
> 

---

## 二、改「Benchmark」：從排名 → 結構性診斷

### 3. ConceptARC：不要拿來比成績，要拿來拆概念

**常見錯誤用法**

- 把 ConceptARC 當成「高階 ARC」
- 用一個 aggregate score 判斷模型好壞

**你應該怎麼用**

ConceptARC 的真正價值是：**每一個 concept cluster 本身就是一個 controlled experiment**。

你應該做的是：

1. 把 ConceptARC 任務按 concept 標籤分桶
2. 對每個 concept：
    - 測 **單步成功率**
    - 測 **跨概念干擾率**（學了 A 是否破壞 B）
3. 記錄 failure trace（不是答案錯誤，是「哪一步失控」）

**關鍵指標不是 accuracy，而是：**

- concept isolation（概念是否可獨立啟動）
- concept leakage（是否被其他概念污染）

---

### 4. arc-agi-benchmarking：把它當 verifier harness，不是 leaderboard

**官方定位**

統一評測、submission 驗證、公平排名。

**你自己的用法應該是**

把它拆成三層：

1. **Parser / schema 層**
    
    → 確保你任何輸出都能被「冷酷地驗證」
    
2. **Verifier supervision 層**
    
    → 拿來訓練 / 校正你自己的 verifier head
    
    而不是直接用它的 pass/fail
    
3. **Regression harness**
    
    → 每次改架構，只問一句話：
    
    > 「我修了 A，是否悄悄毀了 B？」
    > 

**你不應該追求**

- 官方 leaderboard 分數最大化
- submission 格式 hack

---

## 三、你自己的「主線改造策略」（非常重要）

你可以把所有工具與 benchmark，重新整理成這個結構：

```
資料生成（NVARC / re-arc）
        ↓
失敗型態放大
        ↓
Concept 級拆解（ConceptARC）
        ↓
Verifier / Credit Router 校正
        ↓
Regression & 穩定性檢查（arc-agi-benchmarking）

```