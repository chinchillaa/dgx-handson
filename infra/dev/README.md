# 偽のモデルでノートブックを検証する（開発用）

Hugging Face に接続できない環境（クラウドの作業環境など）で、ノートブックが **現行のライブラリで最後までエラーなく動くか** を確かめるための道具です。DGX の本番環境では使いません。

本物と同じ repo_id で、ランダム重みの小さなモデル（Llama・Qwen2・BERT・sentence-transformers）と偽の dolly-15k-ja を HF キャッシュの形で作り、`HF_HUB_OFFLINE=1` で実行します。

```bash
bash infra/dev/run_nb.sh setup                                   # 初回だけ（.dev/ に venv と偽のモデルを作る）
bash infra/dev/run_nb.sh chapter2/notebooks/ch2_03_rag.ipynb     # 実行結果は .dev/out/ に保存
bash infra/dev/run_nb.sh test                                    # chapter3/agent_kit.py の単体テスト
```

## 分かること・分からないこと

| 分かる | 分からない |
|---|---|
| import・API の呼び方・引数名が現行のライブラリで通るか | 回答の中身、当たり率・損失・スコアの値（ランダム重みなので意味がない） |
| セルの順番どおりに実行して、変数のつながりが切れていないか | bitsandbytes の 4bit 読み込み（CPU では通らない） |
| 演習の自己チェック（assert）が解答で通るか | 本物のモデルがツールを正しく呼ぶか（`test` は台本どおりのモデルでループだけを確かめる） |

- 偽の Qwen のチャットテンプレートは、Qwen2.5 のツール呼び出しの形式（`<tools>`・`<tool_call>`・`<tool_response>`）をまねて書いたもので、本物とは細部が違う可能性があります
- dolly-15k-ja は、オフラインではハブのキャッシュから読めないため、IPython の起動スクリプト（`ipython_fake_dolly.py`）で `load_dataset` を偽の JSON に差し替えます。スクリプト（`chapter2/scripts/*.py`）を確かめるときは、このファイルを先に `exec` してください
