# 第2章のデータ

| パス | 使うノートブック | 内容 |
|---|---|---|
| `rag_docs/` | `ch2_03_rag.ipynb`・`ch2_04_evaluation.ipynb` | RAG の検索対象の文書（詳しくは `rag_docs/README.md`） |
| `dpo_preference.json` | `ch2_02_dpo.ipynb`・`scripts/train_dpo.py` | DPO の好みデータ 8 組（`prompt`・`chosen`・`rejected`）。テーマは「社内 QA アシスタントの答え方」で、chosen は結論から具体的に答え、知らないことは知らないと言う回答、rejected は曖昧・不正確・でっち上げの回答 |
