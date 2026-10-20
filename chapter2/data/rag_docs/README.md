# RAG の検索対象の文書

`chapter2/notebooks/ch2_03_rag.ipynb` と `ch2_04_evaluation.ipynb` が読み込む文書です。

| ファイル | 内容 | 役割 |
|---|---|---|
| `handson_participant_guide.md` | このハンズオンの参加者向け接続手順書（`docs/participant_guide.md` の写し） | LLM が事前学習で読んでいない知識。RAG なしでは答えられない |
| `ml_basics.md` | 機械学習の 3 分類 | 一般的な知識。LLM もある程度知っている |
| `deep_learning.md` | ニューラルネットワークと過学習の対策 | 同上 |
| `transformer_llm.md` | Transformer・LLM・ファインチューニング手法 | 同上 |

`docs/participant_guide.md` を更新したら、この写しも更新してください（`ch2_03` の検索実験の質問と正解のキーワードが、この文書の内容に依存しています）。
