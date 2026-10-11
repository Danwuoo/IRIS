# Professor-facing Repository Audit — IRIS

IRIS 的可展示價值是架構思考與可觀測性／訓練治理設計。現有 checkout 不提供可執行模型或實驗；設計規格有缺失文件和尚待作者裁決的內部不一致。應以設計作品送審，不宣稱系統已實作、訓練或驗證。[來源：文件索引](docs/00_INDEX.md)、[架構憲法](docs/01_Architecture_Constitution.md)、[訓練治理](docs/08_Training_Run_Governance.md)、[IRIS-X 草案](IRIS-X.md)。

- 審閱日期：2026-10-11。
- 審閱 HEAD：`69d7a7c1717bec5fd5b6c01a5038203270e20ce2`。
- 文件角色：Design Note (Non-normative)。本文件是一次性 repository audit，不覆蓋規範或決定架構衝突。
- 變更分類：Pure refactor，僅整理文件入口，無模型行為或 failure-category 影響；文件範圍終態：Done。
- 起始工作樹乾淨；本次只新增 README 與本文件。

## 評分與可核查依據

分數是本次 repository 審查判斷，不是研究成績。共用尺度：1＝入口或證據缺失；2＝部分具備且重要限制；3＝可沿文件核查但有公開前缺口；4＝易審閱且範圍內可重現；5＝獨立重現與個人歸屬完整。

| 面向 | 分數 | 本地依據與理由 |
|---|---:|---|
| Readiness | 2/5 | [README](README.md) 提供設計作品入口；[文件索引](docs/00_INDEX.md) 列出的重要文件缺失。無執行入口或結果，應限定為設計展示。 |
| Readability | 2/5 | [憲法](docs/01_Architecture_Constitution.md)、[State IR](docs/02_State_IR_Spec.md)、[Level](docs/03_Level_Contracts_L0-L6.md) 有結構與例子，但 Level 責任和 credit vector 跨文件不一致，且缺 authority/glossary 文件。 |
| Verifiability | 1/5 | [Phase Gates](docs/06_Regression_and_Phase_Gates.md) 要求 S1–S8 工件，[Training Governance](docs/08_Training_Run_Governance.md) 要求 runtime lock、journal、checkpoint；本次 `git ls-files` 僅有 Markdown 與 AGENTS，沒有相應程式、測試或執行工件。 |
| Technical Depth | 3/5 | [State IR](docs/02_State_IR_Spec.md) 明定 token inventory、ordering、Program IR 邊界；[credit/recovery](docs/04_Credit_Assignment_and_Recovery.md) 與 [segment/resume 治理](docs/08_Training_Run_Governance.md) 有具體合約，足供設計討論；實務可行性與效果未驗證。 |
| Individual Contribution | 1/5 | [IRIS-X](IRIS-X.md) 及 [規範文件](docs/01_Architecture_Constitution.md) 未提供申請者本人／AI／第三方的逐項責任與來源清單。commit 身分不能替代作者確認。 |

## 閱讀與技術追問

依 [README 路線](README.md#教授閱讀路線)，先確認「單一主要參數主幹」和「控制策略可學習」的設計選擇，再問 [State IR](docs/02_State_IR_Spec.md) 如何把 Program IR 更新映射回既有 tokens。最後以 [Training Run Governance](docs/08_Training_Run_Governance.md) 的 execute/apply、journal 與 checkpoint commit 順序，討論 crash recovery 要如何被驗證。這些是設計問題，沒有已完成實作可作答的證據。

本次以文件導覽改善可讀性，未加入程式或修改規範。

## 公開前必須處理

| 問題 | 本地依據 | 完成條件 |
|---|---|---|
| 必讀文件與索引承諾不符 | [AGENTS.md §1](AGENTS.md)、[00_INDEX](docs/00_INDEX.md) | 由作者確認 `09_Training_Profile_SingleH100_3B`、`10_Glossary_and_Normative_Status`、`11_Phase_D_Diagnostics_Design_Note`、`12_Phase_E_Execution_Design_Note` 是否應存在或屬已移除文件；本次標為 `Unavailable in checkout`，不代寫。 |
| Level 3–6 的規範責任不一致 | [03 Level 3–4 / 5–6](docs/03_Level_Contracts_L0-L6.md)；[04 §3–5](docs/04_Credit_Assignment_and_Recovery.md)；[05 §3–4](docs/05_Eval_Metrics_Spec.md) | 03 將 L4 定義為 budget/control、L5 定義為 evaluation；04/05 則指定 L3 search/budget、L4 memory、L5 abstraction、L6 evaluation。由權責作者作版本化裁決；本次不選定哪份應被改寫。 |
| Credit distribution 的維度不一致 | [04 §4.2](docs/04_Credit_Assignment_and_Recovery.md)；[05 §3.2](docs/05_Eval_Metrics_Spec.md) | 04 定義 `c0…c5`，05 定義 L0…L6。由作者確認排除或包含 L6 的語意與版本；目前不能宣稱存在唯一可直接實作的 credit contract。 |
| L2 與 Program IR 邊界文字有歧義 | [02 §4.1 / examples §9](docs/02_State_IR_Spec.md)；[03 Level 2 Outputs](docs/03_Level_Contracts_L0-L6.md) | 02 禁止 Program IR tokens 拼入 `Z`，03 以 `program-like tokens` 描述 `state_out`。需確認該詞指既有 token 的 embedding 更新或新增 token；本次不推定相容。 |
| 設計與實作／結果可能混淆 | [08 治理](docs/08_Training_Run_Governance.md)、[IRIS-X 假設草案](IRIS-X.md) | 申請材料一致標為架構設計／概念草案；沒有實驗就不把單卡 profile、resume、S1–S8 寫成已驗證成果。 |
| 個人貢獻、引用來源與公開授權未確認 | [既有設計文件](docs/01_Architecture_Constitution.md)、[IRIS-X](IRIS-X.md)；本地未找到 LICENSE | 作者確認本人／AI／第三方的想法、撰文與設計責任，列出實際參考來源；由權利人決定公開與再利用授權。 |

規範衝突涉及的架構推定停在以上列舉，沒有默默裁決或改動只讀合約。本次不補缺失文件、實作或驗證證據。

## 可宣稱與不能宣稱

| 可由本 checkout 支持 | 目前不能支持 |
|---|---|
| 提出 single trunk、State IR、learned control 與可歸因 recovery 的設計約束。[來源](docs/01_Architecture_Constitution.md) | 這些模組或 learned policies 已實作、正常運作或帶來能力提升。 |
| 定義一套分 phase 的回歸與 resume 驗證要求。[來源](docs/06_Regression_and_Phase_Gates.md) | S1–S8 已通過，或 exactly-once training resume 已被實驗證明。 |
| IRIS-X 是非規範 agent runtime 假設草案。[來源](IRIS-X.md) | 已有 breakthrough runtime、可形式驗證的 agent 或已完成整體閉環。 |

既有設計的本人／AI／第三方歸屬均未確認。本次 README 與 audit 為 AI 協助撰寫，只整理文件邊界。

## 本次核查與限制

本次讀取 [AGENTS.md](AGENTS.md)、[00_INDEX](docs/00_INDEX.md)、實際存在的 01–08 文件相關內容與 [IRIS-X](IRIS-X.md)，以 `git rev-parse HEAD`、`git ls-files`、工作樹及本地路徑確認檔案集合。必讀 `10_Glossary_and_Normative_Status` 不存在，無法完成完整 authority-map 核讀；只做非規範展示文件，不進行依賴該文件的實作。

沒有安裝、訓練或 benchmark 可執行，本次未執行任何研究測試。上述分數不代表設計可行性、原創性或研究效果得到獨立驗證。
