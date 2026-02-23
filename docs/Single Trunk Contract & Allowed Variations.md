# Single Trunk Contract & Allowed Variations

## 0. Scope 與權威層級

- 本文件定義 IRIS 的 **single trunk** 必要條件、可允許的變體、以及違規判準。
- 本文件是架構層合約：**不依賴任何特定 benchmark**；benchmark 僅屬評估工具，不得反向定義 trunk 結構。
- 本文件不規定 trunk 必須是 attention / SSM / hybrid；僅規定它們必須滿足的行為與接口。

---

## 1. 定義

### 1.1 Trunk（主幹）

- Trunk = 主要承載模型能力的參數集合，負責：
    - 將輸入映射到 State IR（或其等價內部表徵）
    - 執行控制、路由、信用分配（credit）相關的主要學習動態
    - 生成輸出（或生成可被 head 解碼的內部狀態）

### 1.2 「第二個 trunk」的判準（Multi-trunk 反模式）

以下任一條成立，即視為**第二個 trunk**（違規），除非被明確標註為「低容量 adapter」並通過容量門檻（見 1.3）：

- **參數量級判準**：存在一個獨立模組，其參數量或 FLOPs 長期穩定地達 trunk 的顯著比例（建議門檻：≥ 25%）。
- **獨立優化判準**：該模組有獨立 optimizer state/學習率排程，且其學習對核心能力至關重要。
- **語義閉環判準**：該模組形成一個能自行完成「理解→推理→決策→輸出」的閉環，而 trunk 只扮演 IO 或轉接。
- **競爭路由判準**：路由在兩個大模組間做主決策，且任何一方都可在多數步驟中繞過另一方完成主要運算。

> 這些判準的目的：禁止「雙腦分裂」與不可追責的能力外包。

### 1.3 低容量模組（Allowed Peripheral Capacity）

- 允許存在 peripheral modules（例如 tokenizer、IO adapters、memory index、輕量 head、監控器），但它們必須：
    - 不形成語義閉環
    - 不取代 trunk 的推理/控制決策
    - capacity 明顯低於 trunk（建議：≤ 5–10% 參數量或推理 FLOPs，取嚴者）

---

## 2. Single Trunk 核心不變量

### 2.1 單一主幹責任

- 所有「語義層」決策（分解、控制、路由、信用分配策略、修復策略）必須在 trunk 的 learned dynamics 中可見、可訓練、可歸因。
- 禁止把語義決策硬編碼在外圍管線（例如規則式 planner、固定流程圖、手寫 search policy）中。

### 2.2 Trunk 與 State IR 的一致性

- Trunk 必須以 State IR（或其等價 schema）作為主要內部狀態表示（canonical internal representation）。
- 允許在 trunk 內部有多個 latent spaces，但必須能映射回 canonical State IR（至少在接口點上）。

### 2.3 可觀測性（Observability）

- Trunk 的關鍵狀態必須可被 instrumentation 觀測（例如：中間 state、control logits、routing gate、信用分配信號）。
- 若出於效率採用壓縮或 checkpointing，仍須提供可還原/可抽樣的觀測鉤子。

---

## 3. Allowed Variations（允許的 trunk family）

以下任一類均允許，只要滿足第 2 節不變量與第 4 節接口要求：

### 3.1 Attention-based

- 全注意力、稀疏注意力、線性注意力、MoE-attention 等
- 允許長上下文策略（滑窗、分塊、外部 KV 壓縮），但不得形成第二個語義閉環。

### 3.2 SSM/Sequence Model-based

- 任意 SSM/Hyena/Mamba-like family
- 允許 state cache、selective scan 變體、chunked recurrence

### 3.3 Hybrid

- Attention + SSM 混合、分層 block、交替堆疊
- 關鍵限制：混合仍然是一個 trunk（共享訓練目標/主狀態、無獨立大腦）

### 3.4 Retrieval-augmented（僅作為外圍、非第二大腦）

- 允許 retrieval index / vector store 作為外部 memory
- 必須滿足：
    - retrieval 不具語義閉環
    - retrieval policy（何時查、查什麼、怎麼用）主要由 trunk learned 控制

---

## 4. Interfaces（trunk 必須提供的對外接口）

### 4.1 IO 接口

- `encode(inputs) -> StateIR/LatentState`
- `step(state, inputs/control) -> state'`
- `decode(state) -> outputs` 或 `produce_logits(state)`

（具體函式名可不同，但語義要等價：編碼、狀態更新、解碼/輸出。）

### 4.2 Control/Routing 接口（若系統定義了 learned control）

- Trunk 必須輸出可訓練的 control signals（例如 gate/logits/latent commands）
- 並允許在訓練/評估時抽樣、干預、或記錄這些信號（for credit assignment）

### 4.3 Level Interfaces 的挂載點（對齊你的決策 2）

- Trunk 必須提供 level interface 的掛載點（即使某些 level 實作關閉，也保留 stub）
- stub 必須：
    - 不破壞 State IR 流
    - 不引入新的語義閉環
    - 對 observability 一致

---

## 5. Prohibited Patterns（明確禁止）

### 5.1 Dual-core / Two-brain

- 任何形式的「大 encoder + 大 solver」並行，互相可替代完成主要推理

### 5.2 Hard-coded semantic control flow

- 規則式 planner 主導步驟、硬編排 search policy、固定推理流程圖
- 允許工程級限制（資源上限、安全 gating），但不得承擔語義分解與決策

### 5.3 Benchmark-shaped trunk

- 為單一 benchmark 直接特化 trunk 結構（例如固定動作空間、固定步數、固定 grid-specific pipeline）
- 可針對 benchmark 加 heads/adapters，但 trunk contract 不得被 benchmark 反向塑形

---

## 6. Compliance Checklist（驗收清單）

在 PR 或設計 review 時，至少回答：

1. 本變更是否引入第二個 trunk？依 1.2 判準逐條否定。
2. peripheral modules 的容量是否低於門檻？是否可能形成語義閉環？
3. control/routing 是否仍為 learned？是否被硬編排取代？
4. trunk 是否仍能產生/維持 canonical State IR？
5. Level interfaces 的挂載點是否仍存在（就算關閉實作）？
6. 是否出現 benchmark-shaped trunk 的特化？

---

## 7. Rationale

- Single trunk 的目的：避免能力與責任分裂，確保 credit assignment 與 failure recovery 可歸因、可學習、可擴展。
- Architecture-agnostic 的目的：允許你在 scaling/吞吐/長上下文等工程權衡下切換 trunk family，而不破壞系統合約。
