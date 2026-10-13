# IRIS — Integrated Reasoning via Internal State

IRIS 探索如何用單一主要參數主幹、共同的 State IR 與可學習控制，組織模型內部的推理、記憶及失敗恢復。目前 repository 保存的是**架構與訓練治理設計**，尚未提供模型實作、權重或實驗結果。

## 設計內容

核心問題是：不同推理階段如何共享狀態、維持清楚的介面，並將失敗歸因到可修正的環節？文件由架構限制出發，逐步定義狀態表示、Level 介面、credit routing、回歸測試與訓練恢復要求。

| 主題 | 閱讀入口 |
| --- | --- |
| 架構目標、single trunk 與 learned control | [Architecture Constitution](docs/01_Architecture_Constitution.md) |
| Canonical State IR、token inventory 與 Program IR 邊界 | [State IR Spec](docs/02_State_IR_Spec.md) |
| 各層的輸入、輸出與禁止事項 | [Level Contracts L0–L6](docs/03_Level_Contracts_L0-L6.md) |
| 失敗分類、credit assignment 與 recovery | [Credit Assignment and Recovery](docs/04_Credit_Assignment_and_Recovery.md) |
| 評估欄位與分階段回歸要求 | [Eval Metrics](docs/05_Eval_Metrics_Spec.md)、[Regression and Phase Gates](docs/06_Regression_and_Phase_Gates.md) |
| 資料攝取與訓練執行要求 | [Data Mixture](docs/07_Data_Mixture_and_Ingestion.md)、[Training Run Governance](docs/08_Training_Run_Governance.md) |

建議先讀 Architecture Constitution，再沿 State IR → Level Contracts → Credit Assignment 閱讀。評估與訓練文件描述的是預定驗證方法，不是已執行的測試報告。

[IRIS-X.md](IRIS-X.md) 是本庫保存的非規範 runtime 假設草案，不覆蓋架構契約，也不代表獨立 IRIS-X repository 的最新實作狀態。完整歷史索引見 [docs/00_INDEX.md](docs/00_INDEX.md)，文件權威與修改邊界見 [AGENTS.md](AGENTS.md)。

## 文件狀態與未決問題

目前有 01–08 設計文件。歷史索引及工作契約提到的以下文件不在這個版本中：

```text
docs/09_Training_Profile_SingleH100_3B.md
docs/10_Glossary_and_Normative_Status.md
docs/11_Phase_D_Diagnostics_Design_Note.md
docs/12_Phase_E_Execution_Design_Note.md
```

現有文件仍有三處需由架構作者作版本化裁決：

- 03 與 04／05 對 L3–L6 的責任分配不同，例如 budget/control、memory、abstraction 與 evaluation 的所屬層。
- 04 使用 `c0…c5`，05 使用 L0…L6；credit vector 的六維／七維語意尚未統一。
- 02 禁止將 Program IR tokens 拼入 `Z`，03 又以 `program-like tokens` 描述輸出；兩者的表示邊界尚待澄清。

README 不裁決這些衝突，也不修改規範。H100、3B、runtime lock 與 S1–S8 等文字是設計／治理要求，沒有對應的實際訓練或通過紀錄。

## 取得與核對版本

這是一個文件 repository，沒有安裝、訓練或 benchmark 執行入口。可用 Git 固定並核對正在閱讀的快照：

```sh
git rev-parse HEAD
git ls-files
```

目前未附 LICENSE；外部研究來源與設計歸屬仍需隨後續正式研究紀錄補齊。
