# Pure LM（90% of total tokens）

> 合計 = 90%。括號內是對應資料集在 HF 上的「要抽取欄位」與「抽取規則」。
> 
1. **60% — HuggingFaceFW/fineweb-edu（主幹一般文本，維持語言能力）** ([Hugging Face](https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu))
- **抽取欄位**：`text`（主要訓練文本），保留 `id/url/dump` 做 provenance，必要時用 `token_count/score/int_score` 做重採樣。([Hugging Face](https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu))
- **抽取規則**：
    - 先不做太激進的再過濾（FineWeb-Edu 本身已是教育品質過濾集）
    - 若你想更「教科書/推導」一點：可讓 sampling 權重 ∝ `score`（或只取 `int_score` 較高者）。([Hugging Face](https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu))
    - 小跑先用 sample configs（`sample-10BT/100BT/350BT`）([Hugging Face](https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu))
1. **10% — allenai/peS2o（文件抽取/學術長文：結構化敘述 + 公式/符號混合）** ([Hugging Face](https://huggingface.co/datasets/allenai/peS2o))
- **抽取欄位**：`text`（段落以 `\n\n` 分隔），保留 `id/source/created/added`。([Hugging Face](https://huggingface.co/datasets/allenai/peS2o))
- **抽取規則**：
    - 只用 `source="s2orc"`（full-text papers），避免只剩摘要的 `s2ag` 佔比過高。([Hugging Face](https://huggingface.co/datasets/allenai/peS2o))
1. **8% — bigcode/the-stack（程式碼主體；你要的「非註解、非自然語言化」）** ([Hugging Face](https://huggingface.co/datasets/bigcode/the-stack))
- **抽取欄位**：`content`（檔案內容），並用 `lang/ext/avg_line_length/alphanum_fraction` 做過濾。([Hugging Face](https://huggingface.co/datasets/bigcode/the-stack))
- **抽取規則（強烈建議照做）**：
    - **去註解/去 docstring/去 README/去 Markdown**（用語言對應的 comment/docstring 規則）
    - 先限制語言集合（例如 C/C++/Rust/Python/OCaml/Haskell/Java；避免 HTML/Markdown/TeX 佔比過大）
    - 用 `alphanum_fraction`、`avg_line_length` 排除「幾乎都自然語言」的檔（例如大量長行文字、license dump）。([Hugging Face](https://huggingface.co/datasets/bigcode/the-stack))
    - 使用時要注意授權與條款：The Stack 是多授權集合、需遵循原授權並有 provenance。([Hugging Face](https://huggingface.co/datasets/bigcode/the-stack))

> 補充：**不要用 the-stack-v2-dedup 當作你「直接抓內容」的來源**。它在 HF 上主要是 **file IDs**，內容需走 Software Heritage S3，bulk 下載還需要額外協議/憑證。([Hugging Face](https://huggingface.co/datasets/bigcode/the-stack-v2-dedup))
> 
1. **4% — open-web-math/open-web-math（數學符號推導：非敘述題、LaTeX 密度高）** ([Hugging Face](https://huggingface.co/datasets/open-web-math/open-web-math))
- **抽取欄位**：`text`（主文本），搭配 `metadata`（抽取訊號/數學含量）。([Hugging Face](https://huggingface.co/datasets/open-web-math/open-web-math))
- **抽取規則（讓它更接近你要的「符號推導」）**：
    - 以 `metadata.extraction_info.*`（例如 math score、mathjax/katex 訊號）挑 **高數學密度**文件，再丟棄「純敘述/論壇閒聊」那類。([Hugging Face](https://huggingface.co/datasets/open-web-math/open-web-math))
1. **2% — EleutherAI/proof-pile-2（config: algebraic-stack）（數學 code / 形式化數學 / CAS）** ([Hugging Face](https://huggingface.co/datasets/EleutherAI/proof-pile-2))
- **抽取欄位**：`text`（程式/形式化文本），`meta`（來源與子集相關 metadata）。([Hugging Face](https://huggingface.co/datasets/EleutherAI/proof-pile-2))
- **抽取規則**：
    - 你要的「非自然語言化」→ **優先抽** Python/Isabelle/Lean/Coq/Julia/TeX 這些在 AlgebraicStack 內 token 量也最大、且符號/規則密度高。([Hugging Face](https://huggingface.co/datasets/EleutherAI/proof-pile-2))
1. **2% — phanerozoic/Lean4-Mathlib（型別系統/λ-calculus 的實戰語料：dependent type + tactic scripts）** ([Hugging Face](https://huggingface.co/datasets/phanerozoic/Lean4-Mathlib))
- **抽取欄位**：用 `fact` 當作主要訓練文本；**不要**把 `docstring` 當主體（那是自然語言）。([Hugging Face](https://huggingface.co/datasets/phanerozoic/Lean4-Mathlib))
- **抽取規則**：
    - 只取 `type in {"theorem", ...}`（或你想要的定義類型）
    - 丟棄過短的 `fact`（避免碎片化）([Hugging Face](https://huggingface.co/datasets/phanerozoic/Lean4-Mathlib))
1. **2% — togethercomputer/RedPajama-Data-1T（subset: arxiv）（λ / 型別系統描述、推導規則段落的主來源）** ([Hugging Face](https://huggingface.co/datasets/togethercomputer/RedPajama-Data-1T))
- **抽取欄位**：`text` + `meta`（含 `url/timestamp/source/language...`），並確認 `red_pajama_subset="arxiv"`。([Hugging Face](https://huggingface.co/datasets/togethercomputer/RedPajama-Data-1T))
- **抽取規則（對準「cs.PL / logic / type theory」風格）**：
    - 在 `text` 內以 pattern 過濾：例如出現 `\Gamma`, `\vdash`, `\lambda`, `\Pi`, `\Sigma`, “type system”, “typing rule”, “subject reduction”, “type inference” 等（你可再加自己關鍵詞）
    - RedPajama 的 arXiv slice 來源是 **LaTeX source**，並且會移除 preamble/comments/macros/bibliographies（對你要的「規則→推導」通常是加分）。([Hugging Face](https://huggingface.co/datasets/togethercomputer/RedPajama-Data-1T))
1. **1% — crumb/openstax-text（「教科書式：規則→操作→結果」段落，CC BY）** ([Hugging Face](https://huggingface.co/datasets/crumb/openstax-text))
- **抽取欄位**：`text`。([Hugging Face](https://huggingface.co/datasets/crumb/openstax-text))
- **抽取規則**：
    - 用章節/段落內的格式線索挑選「procedural」：`Algorithm:`/`Procedure:`/`Step 1`/`Input/Output`/條列步驟/縮排 pseudo-code（OpenStax 內容很雜，必做段落級過濾）
    - 注意 OpenStax 的 CC BY 4.0 授權與 attribution 要求。([Hugging Face](https://huggingface.co/datasets/crumb/openstax-text))
1. **1% — togethercomputer/RedPajama-Data-1T（subset: stackexchange）（規則→操作→結果的補強，偏實務推導/演算法解釋）** ([Hugging Face](https://huggingface.co/datasets/togethercomputer/RedPajama-Data-1T))
- **抽取欄位**：`text` + `meta`，並確認 `red_pajama_subset="stackexchange"`。([Hugging Face](https://huggingface.co/datasets/togethercomputer/RedPajama-Data-1T))
- **抽取規則**：
    - 用 `meta.url`（或 `meta.source`）限制到你要的站點：例如 `cs.stackexchange.com`、`math.stackexchange.com`、`stackoverflow.com` 等
    - RedPajama 的 StackExchange slice 會去 HTML、組成 QA pair、依 score 排序（對「規則/步驟」很常見）。([Hugging Face](https://huggingface.co/datasets/togethercomputer/RedPajama-Data-1T))

---

## 四種成分對照（確保都有被覆蓋）

- **程式碼（非註解）**：The Stack 8% + Proof-Pile-2 AlgebraicStack 2% ([Hugging Face](https://huggingface.co/datasets/bigcode/the-stack))
- **λ-calculus / 型別系統描述**：RedPajama arXiv 2% + Lean4-Mathlib 2% ([Hugging Face](https://huggingface.co/datasets/togethercomputer/RedPajama-Data-1T))
- **演算法「規則→操作→結果」**：OpenStax 1% + RedPajama StackExchange 1% ([Hugging Face](https://huggingface.co/datasets/crumb/openstax-text))
- **數學符號推導（非敘述題）**：OpenWebMath 4% +（再加）AlgebraicStack 2%（偏符號/程式）([Hugging Face](https://huggingface.co/datasets/open-web-math/open-web-math))