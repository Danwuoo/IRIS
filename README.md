# IRIS — Integrated Reasoning via Internal State

IRIS 目前是一份 **模型架構與訓練治理設計作品**。此 checkout 只有文件，沒有 `src/`、測試、可執行模型、權重或實驗結果；不能把文件中的規格要求當成已運作的系統。[架構憲法](docs/01_Architecture_Constitution.md) 定義 single trunk、canonical State IR 與 learned control；[IRIS-X](IRIS-X.md) 是下一版 runtime 的非規範假設草案。

## 教授閱讀路線

1. [Professor-facing Repository Audit](PROFESSOR_AUDIT.md)：五面向判斷、文件缺失與合約不一致。
2. [Architecture Constitution](docs/01_Architecture_Constitution.md)：研究意圖與不可違反的架構邊界；末尾 appendix 為非規範 sketch。
3. [State IR Spec](docs/02_State_IR_Spec.md) → [Level Contracts](docs/03_Level_Contracts_L0-L6.md) → [Credit Assignment and Recovery](docs/04_Credit_Assignment_and_Recovery.md)：表徵、介面與責任如何連接。
4. [Eval Metrics](docs/05_Eval_Metrics_Spec.md) → [Phase Gates](docs/06_Regression_and_Phase_Gates.md) → [Training Run Governance](docs/08_Training_Run_Governance.md)：預定如何量測失敗與處理 resume，而非已執行的驗證報告。
5. [IRIS-X 草案](IRIS-X.md)：對可執行行動、context 與 side-effect 治理的未實作假設。它不覆蓋現行合約。

[原始文件索引](docs/00_INDEX.md) 與 [AGENTS.md](AGENTS.md) 提到的 `docs/09_Training_Profile_SingleH100_3B.md`、`docs/10_Glossary_and_Normative_Status.md`、`docs/11_Phase_D_Diagnostics_Design_Note.md`、`docs/12_Phase_E_Execution_Design_Note.md` 在本 checkout 缺失。不同規範對 Level 3–6 的責任及 credit vector 也有不一致，詳見 audit；本 README 不自行裁決。

## 如何核查

這個版本可重做的是文件審閱；目前沒有可查實的安裝、訓練或 benchmark 指令。建議先用上述相對連結閱讀，再在 repo 根目錄確認版本與追蹤檔案：

```powershell
git rev-parse HEAD
git ls-files
```

本次在 2026-10-11 核查 HEAD `69d7a7c1717bec5fd5b6c01a5038203270e20ce2`。文件中的 H100、3B、runtime lock 與 S1–S8 是設計／治理要求，沒有對應實際執行證據。本人、AI、第三方的既有貢獻歸屬與公開授權仍待作者確認；根目錄未找到 LICENSE。
