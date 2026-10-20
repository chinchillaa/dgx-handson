# dgx-handson 進捗記録

> 別セッションの Claude Code がすぐに作業を再開するための引き継ぎドキュメント。
> 最終更新：2026-10-20（10/9〜10/14 の第1章の推敲・解説動画・試し場を記録し、第2章ノートブックの実態を反映）

---

## リポジトリ情報

| 項目 | 内容 |
|---|---|
| GitHub | https://github.com/chinchillaa/dgx-handson（Public） |
| ローカルパス | `/home/chinchilla/pjt/sbcs-work/dgx-handson/` |
| ブランチ | `main` |

---

## プロジェクト概要

DGX Spark（GB10・統合メモリ 128GB・GPU 1基）上で、最大10人が同時に参加する ML ハンズオンセッション用コンテンツ一式。
開催方式（共有アカウント＋参加者ごとの JupyterLab）は `design/DESIGN.md` 4章、手順は `docs/` の手順書を参照。
設計仕様は `design/DESIGN.md` が正とする。**実装に迷ったら必ず DESIGN.md に立ち返ること。**

### 3章構成

| 章 | テーマ | 状態 |
|---|---|---|
| 第1章 | 機械学習(AI)の仕組み | **完成**（2026-10-14 に推敲・解説動画 8 本・試し場 5 か所を追加） |
| 第2章 | AI を「強く」する（SFT・DPO・RAG） | **Web 資料完成**。ノートブック・演習・解答は 2026-10-20 に書き直し済み（DGX での実行は未） |
| 第3章 | AI エージェントを作ろう | 未着手 |

---

## ファイル一覧

✅ = 完成、🔶 = 書き直し済み・DGX での実行は未、📝 = 下書き（未実行・未検証）

```
dgx-handson/
├── .gitignore
├── requirements.txt                              ✅ 全章共通パッケージ
├── .claude/skills/tech-writing/                  ✅ 日本語技術文書の推敲規約（Web 資料・PR・手順書に適用）
├── assets/
│   └── web-theme.css                             ✅ 全 Web 資料の共通テーマ（配色変数・フォント。各ページの <style> の後に読み込む）
├── design/
│   ├── DESIGN.md                                 ✅ 設計仕様書（変更不可）
│   └── PROGRESS.md                               ✅ このファイル
├── chapter1/
│   ├── web/
│   │   ├── index.html                            ✅ 章の進行ガイド・目次
│   │   ├── supplement_linear_regression.html     ✅ 線形回帰・損失関数・勾配降下法（勾配降下法の試し場つき）
│   │   ├── supplement_neural_network.html        ✅ XOR問題・NN構造・活性化関数・PyTorch autograd（XOR 学習の試し場つき）
│   │   ├── supplement_transformer.html           ✅ 埋め込み・Self-Attention・Transformerブロック・LLMへのつながり（Self-Attention 計算機の試し場つき）
│   │   ├── supplement_pretraining.html           ✅ 自己教師あり学習・CLM・スケーリング則・活用方法（スケーリング則の試し場つき）
│   │   ├── supplement_inference_params.html      ✅ Temperature・Top-p/k・generate()パラメータ設定（サンプリングの試し場つき）
│   │   ├── ml_quadratic_demo.html                ✅ 学習過程の可視化デモ（index.html からリンク）
│   │   ├── quiz_ch1.html                         ✅ 理解確認クイズ（18問）JS採点付き
│   │   └── media/                                ✅ 解説動画 8 本（MP4）とポスター画像（JPEG）。manim で生成
│   ├── manim/                                    ✅ 解説動画の生成元（scenes/*.py・Makefile・environment.yml・README.md）
│   ├── notebooks/
│   │   ├── ch1_01_linear_regression.ipynb        ✅ NumPy勾配降下・学習率実験（解説用）
│   │   ├── ch1_02_mnist_nn.ipynb                 ✅ PyTorch 2層NN・MNIST分類（解説用）
│   │   ├── ch1_03_llm_inference.ipynb            ✅ Attention 実装〜LLM推論（解説用・47セル・約30分）
│   │   └── ch1_03_appendix_deep_dive.ipynb       ✅ HO-3 付録 深掘り編（42セル・約45分・任意）
│   ├── exercises/
│   │   ├── ex_01_linear_regression.ipynb         ✅ 穴埋め: predict/mse_loss/dw/db/更新式
│   │   ├── ex_02_mnist_nn.ipynb                  ✅ 穴埋め: fc1/fc2定義・forward・5ステップループ・evaluate
│   │   └── ex_03_llm_inference.ipynb             ✅ 穴埋め9問: Attention/因果マスク/残差/貪欲法/サンプリング（assert 自己チェック付き）
│   └── solutions/
│       ├── sol_01_linear_regression.ipynb        ✅ HO-1 解答
│       ├── sol_02_mnist_nn.ipynb                 ✅ HO-2 解答
│       └── sol_03_llm_inference.ipynb            ✅ HO-3 解答（実行検証済み・自己チェック9件通過）
├── chapter2/
│   ├── web/
│   │   ├── index.html                            ✅ 第2章トップ・手法選定フレームワーク
│   │   ├── supplement_sft.html                   ✅ SFT・LoRA・QLoRA 補足（4×4行列の数値例つき）
│   │   ├── supplement_dpo.html                   ✅ DPO 補足（参照モデル・損失関数図解・動的デモつき）
│   │   ├── supplement_rag.html                   ✅ RAG 補足（チャンクサイズ情報量目安つき）
│   │   ├── supplement_evaluation.html            ✅ 評価指標補足（ROUGE・BERTScore・LLM-as-judge）
│   │   └── quiz_ch2.html                         ✅ 第2章 理解確認クイズ
│   ├── data/rag_docs/                            ✅ RAG の検索対象（参加者手順書の写し＋機械学習の解説 3 本）
│   ├── notebooks/ch2_03_rag.ipynb                🔶 書き直し済み（35 セル）。DGX での実行・出力の保存は未
│   ├── exercises/ex_03_rag.ipynb                 🔶 穴埋め 4 問（assert 自己チェック付き）
│   ├── solutions/sol_03_rag.ipynb                🔶 解答
│   ├── notebooks/ch2_01_sft.ipynb                🔶 書き直し済み（33 セル）。DGX での実行・出力の保存は未
│   ├── exercises/ex_01_sft.ipynb                 🔶 穴埋め 4 問（assert 自己チェック付き）
│   ├── solutions/sol_01_sft.ipynb                🔶 解答
│   ├── scripts/train_sft.py                      🔶 書き直し済み（引数で rank・更新回数を指定。outputs/sft_lora_r{rank} に保存）
│   ├── data/dpo_preference.json                  ✅ DPO の好みデータ 8 組
│   ├── notebooks/ch2_02_dpo.ipynb                🔶 書き直し済み（27 セル）。DGX での実行・出力の保存は未
│   ├── exercises/ex_02_dpo.ipynb                 🔶 穴埋め 4 問（assert 自己チェック付き）
│   ├── solutions/sol_02_dpo.ipynb                🔶 解答
│   ├── scripts/train_dpo.py                      🔶 書き直し済み（引数で beta・更新回数を指定。outputs/dpo_lora_beta{beta} に保存）
│   ├── notebooks/ch2_04_evaluation.ipynb         🔶 書き直し済み（31 セル）。DGX での実行・出力の保存は未
│   ├── exercises/ex_04_evaluation.ipynb          🔶 穴埋め 4 問（assert 自己チェック付き）
│   └── solutions/sol_04_evaluation.ipynb         🔶 解答
├── chapter3/  （空ディレクトリ + .gitkeep のみ）
├── docs/
│   ├── operator_guide.md                             ✅ 開催側の手順書
│   └── participant_guide.md                          ✅ 参加者向けの手順書
└── infra/
    ├── setup.sh                                      ✅ 共有 .venv の構築（uv + パッケージ + Jupyter カーネル）
    ├── predownload.sh                                ✅ 全章のモデル・データセット事前ダウンロード
    ├── required_assets.py                            ✅ 事前取得するモデル・データセットの一覧
    ├── check_env.py                                  ✅ 環境確認（GPU・パッケージ・オフライン読み込み・起動条件）
    └── multiuser/
        ├── setup_account.sh                          ✅ 参加者用アカウント handson の作成
        ├── deploy.sh                                 ✅ 教材・.venv・モデルを /opt/handson に配置
        ├── restrict_ssh.sh                           ✅ handson の SSH を貸与 VM からの接続とトンネルに制限
        ├── welcome.sh                                ✅ ログイン時に接続元 IP から参加者番号を決めて URL を表示
        ├── handson.sh                                ✅ 参加者ごとの JupyterLab の起動・停止・URL 発行・教材配布
        ├── ipython_startup.py                        ✅ GPU メモリ上限 + gpu_slot()
        └── gpu_queue.sh                              ✅ スクリプト学習の同時実行制御
```

---

## infra 動作確認ログ（2026-04-16）

ローカル環境（CPU のみ・GPU なし）で以下を検証済み。

| 手順 | 結果 |
|---|---|
| `setup.sh` — Python 3.11.10 + .venv 作成 + 全パッケージインストール | ✅ |
| `check_env.py` — 全パッケージ検出・動作テスト | ✅（GPU なし・HF 未ログインのみ警告） |
| `predownload.sh` — MNIST ダウンロード（63.5 MB） | ✅ `./data/MNIST` に保存 |
| `sol_01_linear_regression.ipynb` — 完全実行 | ✅ エラーなし・グラフ出力確認 |
| `sol_02_mnist_nn.ipynb` — 完全実行 | ✅ エラーなし・学習曲線出力確認 |
| `sol_03_llm_inference.ipynb` — インポート・ロジック関数 | ✅ TTR / Jaccard 正常動作 |
| `sol_03` — Llama モデルロード以降 | ✅ 2026-09-03 に DGX 上で完全実行を確認 |

### 修正済みバグ

| ファイル | バグ内容 | 修正内容 |
|---|---|---|
| `check_env.py` | `scikit-learn` が `scikit_learn` でインポートされ常に未検出 | パッケージ定義にインポート名フィールドを追加、`sklearn` に対応 |
| `check_env.py` / `predownload.sh` | `huggingface-cli login` が新バージョンで廃止 | `hf auth login` に更新 |
| `predownload.sh` | `except:` が `SystemExit` を捕捉し `exit(0)` が `exit(1)` に化ける | `except Exception:` + `sys.exit()` に修正 |

### Llama アクセス申請後の手順

```bash
bash infra/predownload.sh          # Llama ダウンロード（約 2.5 GB）
.venv/bin/jupyter nbconvert --to notebook --execute \
  --ExecutePreprocessor.timeout=600 \
  chapter1/solutions/sol_03_llm_inference.ipynb
```

---

## chapter2 Web 資料更新ログ（2026-06-30）

第2章の Web 資料を作成し、初学者が専門用語でつまずきにくいよう説明を補強済み。

| ファイル | 更新内容 |
|---|---|
| `chapter2/web/index.html` | SFT・DPO・RAG・評価指標の役割と手法選定フレームワークを整理 |
| `chapter2/web/supplement_sft.html` | SFT/LoRA/QLoRA の説明を補強。低ランク行列・rank・alpha・量子化を具体例つきで説明。LoRA は 4×4 重み行列の数値例で、`W` → `ΔW` → `W'` の更新まで記載 |
| `chapter2/web/supplement_dpo.html` | DPO/RLHF/preference data の説明を補強。参照モデルの役割、DPO 損失関数の図解、chosen/rejected 確率バーと beta スライダーの簡易デモを追加 |
| `chapter2/web/supplement_rag.html` | RAG の処理フロー、チャンク・ベクトル化・top-k・オーバーラップを例つきで説明。チャンクサイズ表に情報量の目安を追加 |
| `chapter2/web/supplement_evaluation.html` | ROUGE・BERTScore・LLM-as-judge の違いを、文字一致・意味類似・LLM評価の観点で整理 |
| `chapter2/web/quiz_ch2.html` | 解説文に用語補足を追加し、誤答時に復習しやすい内容へ更新 |

### 注意点

- `supplement_dpo.html` は理解補助のため、ページ内 JavaScript による簡易インタラクティブデモを含む。
- `DESIGN.md` の「動的エフェクト禁止」は印刷・PDF化を想定した原則だが、今回はユーザー指示により、学習理解を優先して限定的な動的図解を追加した。
- chapter2 のノートブック、演習、解答ファイルは未作成。

---

## マルチユーザー開催方式への移行（2026-09-24）

sudo なしの共有アカウント `user01` で最大10人が同時に参加する方式を正とし、既存資料をこれに合わせた。
方針は `DESIGN.md` 4章、手順は `docs/operator_guide.md`・`docs/participant_guide.md`。

### 実機（DGX Spark / GB10）で確認したこと

| 確認内容 | 結果 |
|---|---|
| `systemd-run --user` による cgroup 上限（sudo なし） | ✅ 使える |
| cgroup の `MemoryMax` が GPU 確保分を数えるか | ❌ 数えない（上限 4GB の中で GPU に 6GB 確保できた）→ PyTorch 側の上限を併用 |
| `set_per_process_memory_fraction` による GPU 上限 | ✅ 上限で `OutOfMemoryError` |
| 10人分の JupyterLab 起動・トークン認証 | ✅ トークンなしは 403 |
| p01 カーネルでの動作（`HF_HUB_OFFLINE=1`） | ✅ MNIST・Llama-1B 生成・MiniLM 埋め込み・BERTScore・dolly 読み込み |
| `gpu_slot()` と `gpu_queue.sh` の枠の共有 | ✅ スクリプトが2枠使用中はノートブックが待機し、空くと開始 |
| Llama-3-8B の QLoRA 学習（第2章） | ⏳ 未確認（モデル未ダウンロード。HF トークンが必要） |

### 既存資料の変更

| 対象 | 変更 |
|---|---|
| ノートブック17本 | `/data/shared` 参照を削除し、運営側が渡す `HF_HOME`・`HANDSON_DATA_DIR` を使う形に。第2章の `trainer.train()` を `gpu_slot()` で囲む。`gpu_queue.txt`・tmux・A100 前提の記述を削除 |
| `chapter2/scripts/train_*.py` | 使い方を `gpu_queue.sh` 経由に。`/data/shared`・`CUDA_VISIBLE_DEVICES` を削除 |
| `chapter1/web/index.html` | 「環境セットアップ」を「接続方法」に差し替え |
| `chapter2/web/index.html` | GPU 注意事項を順番待ち・メモリ上限の説明に差し替え |
| `infra/*` | `/data/shared` 前提をやめ、全章のモデルを `required_assets.py` の一覧で管理。`check_env.py` はオフライン読み込みと起動条件を確認 |
| Web ページの配信 | JupyterLab の中で HTML を開くとサンドボックス化され、数式・リンクが動かない。全員共通の静的サーバー（ポート 8800）で配信する形にし、参加者ディレクトリには `web/` を配らない。headless Firefox で KaTeX・CSS の描画を確認 |

### 参加者用アカウントの分離（2026-09-24）

共有アカウント `user01` のままでは、参加者が運営者の GitHub・Claude Code の認証情報と会話履歴を読めることを実機で確認した。sudo が使えるようになったため、参加者用アカウント `handson` を作り、教材・`.venv`・モデルを `/opt/handson`（`handson` は読み取り専用）に移した。

| 確認内容（p01 のカーネル、`handson` として） | 結果 |
|---|---|
| 運営者の GitHub・Claude Code の認証情報、リポジトリ | ✅ 読めない |
| `/opt/handson` の `.venv`・スクリプト・モデル | ✅ 書き換えも新規作成もできない |
| オフラインでの MNIST・Llama-1B 生成・埋め込み・BERTScore・dolly、GPU 上限、`gpu_slot()` | ✅ |
| 教材ページ（8800） | ✅ 解答は 404 |

作業中に見つけた落とし穴:

- `/opt/handson` の setgid が、`deploy.sh` の実行で外れた。**所有グループに属さないユーザーが `chmod` すると、Linux は setgid を外す**ため。運営者をグループ `handson` に入れ、`deploy.sh` の最後にグループと setgid を付け直すようにした
- uv の既定はキャッシュからの**ハードリンク**で、`.venv` のファイルの所有グループが運営者のままになる → `UV_LINK_MODE=copy`
- uv の既定の Python（`~/.local/share/uv/python`）は `handson` から読めない → `UV_PYTHON_INSTALL_DIR=/opt/handson/python`
- datasets は読むだけでもキャッシュにロックファイルを書く → データセットだけ参加者ごとにコピーし `HF_DATASETS_CACHE` で渡す

### 注意点

- huggingface_hub の `snapshot_download(local_files_only=True)` は、使わない onnx / .bin まで揃っていないと `IncompleteSnapshotError` になる。キャッシュ確認は `required_assets.cached_model_path()` を使う
- `bert-base-multilingual-cased` は旧名リポジトリで、`snapshot_download` が 404 になる。`predownload.sh` は transformers 経由で取得する
- transformers 5.x は `TRANSFORMERS_CACHE` を無視する（`HF_HOME` だけ設定すればよい）

---

## 第1章 Web 資料の推敲・解説動画・試し場（2026-10-09〜10-14）

第1章の Web 資料を推敲し、解説動画と試し場（ページ内で値を動かせるデモ）を加えた。PR #9 で main にマージ済み。

### 推敲と誤りの訂正（2026-10-09）

`.claude/skills/tech-writing` の規約で 8 ページを推敲した（です・ます調、文の分割、用語の統一、太字は結論と用語の初出だけ）。あわせて次の誤りを直した。

| ページ | 訂正内容 |
|---|---|
| 線形回帰 | 出力例を実行結果（初期損失 145.37 など）に差し替え。学習率の表を実測の挙動に修正 |
| `ml_quadratic_demo.html` | 学習率の初期値 0.05 は発散するため 0.01 に変更。収束していないときに「収束完了」を出さない |
| 推論パラメータ | Temperature / Top-p の図の値、repetition_penalty の式、do_sample の既定値の説明 |
| 事前学習 | Chinchilla の比較相手（Gopher）、Llama の学習コスト |
| Transformer | 注目度の図の値の矛盾、Bahdanau 論文の記述、「銀行」の例 |
| クイズ | 後から表示する解説の数式が描画されない |

### 解説動画（manim）

`chapter1/manim/` に 8 シーンを置き、`make` で 1080p30 の MP4 とポスター画像を `chapter1/web/media/` に書き出す。シーンと埋め込み先の対応は `chapter1/manim/README.md` の表を参照。

- 動画内の数値は、資料のコード例とハンズオン③と同じ式で計算している。資料の数値を変えたら動画も作り直すこと
- DGX（aarch64）では `pip install manim` が失敗する（glcontext / manimpango のビルド済みバイナリがない）。conda-forge（micromamba）で環境を作る
- LaTeX は入れていない。動画内は `Text` だけを使い、`MathTex` は使わない
- 配色は `scenes/theme.py` と `assets/web-theme.css` の両方で定義している。テーマを変えるときは両方を直す

### 試し場（2026-10-09・10-14）

| ページ | 試し場の内容 |
|---|---|
| `supplement_linear_regression.html` | 勾配降下法。損失の地形（2D 等高線／3D 曲面）上で学習率による収束・振動・発散を確かめる。データはコード例と同じ `np.random.seed(42)` の 50 点 |
| `supplement_neural_network.html` | XOR を 2 層 NN で学習。活性化関数とノード数で決定境界が変わる |
| `supplement_transformer.html` | 「太郎はリンゴを食べた。それは甘かった。」の 7 単語で Self-Attention を計算。2 つのヘッドを切り替えられる |
| `supplement_pretraining.html` | スケーリング則。N と D から損失と計算量を求め、最適な配分と実在モデルを比べる。定数は Epoch AI の再当てはめ値（Besiroglu et al., 2024）。Hoffmann et al. の丸めた定数では最適な D/N が約 90 になり、本文の約 1:20 と食い違うため |
| `supplement_inference_params.html` | temperature / top_k / top_p を動かしてサンプリングを試す |

### Attention の説明の書き直し（2026-10-14）

`supplement_transformer.html` を高校数学（ベクトルと内積）だけで読めるように書き直し、ハンズオン③のノートブックの説明もそろえた。

- 例文を「太郎はリンゴを食べた。それは甘かった。」に統一。「それ」がリンゴを 99% 参考にするまでを手計算の表で追う
- 用語: Q・K・V は「探しているもの・自分が何者か・相手へ渡す情報」、QKᵀ は「合い具合」、softmax 後は「参考にする割合」
- 表記: 1 単語ぶんは小文字 $q_i, k_i, v_i$（ベクトル）、全単語を積んだものは大文字 $Q, K, V$（行列）。$d_k$ は Key ベクトルの次元数
- Multi-Head の例: 「食べた」の Head 1「誰が食べた？」→ 太郎、Head 2「何を食べた？」→ リンゴ（説明用の例である旨を注記）
- 専門的な内容（固定次元ボトルネック、Pre-Norm、RMSNorm、SwiGLU、RoPE、Attention Sink など）は削らず「もっと詳しく」に移した
- `ch1_03_llm_inference.ipynb` は説明文・コメント・表示文字列・グラフのラベルだけを変え（変数名・関数名は変更なし）、GPU で再実行して出力を保存した
- 動画 `ch1_self_attention` と `ch1_causal_mask` を同じ例で作り直した

> **注**：ノートブックのミニチュア（「ネコ が サカナ 食べた」）はそのまま残っている。Web 資料の例（太郎・リンゴ）とは別の例だが、ノートブックの数値（食べた → サカナ 0.99 など）は変えていない。

### DESIGN.md との関係

DESIGN.md の「アニメーション・動的エフェクトは使用しない」に対し、解説動画と試し場はユーザーの指示で追加した（第2章 DPO のデモと同じ扱い）。静的な図と本文だけでも内容が読めるように書いている。

---

## 第2章ノートブックの書き直し（2026-10-20〜）

2026-06-26 の下書きは、現行のライブラリ（transformers 5.x・trl 1.x・langchain 1.x）では動かなかった。ハンズオンごとに書き直している。

### 下書きで見つかった問題

| 対象 | 問題 |
|---|---|
| 全体 | `SFTConfig(max_seq_length=…)`・`DPOConfig(max_prompt_length=…)`・`SFTTrainer(tokenizer=…)` は trl 1.x で廃止（`max_length`・`processing_class` に変わった）。`langchain.text_splitter`・`langchain.schema` は langchain 1.x で削除 |
| RAG | 埋め込みモデル `all-MiniLM-L6-v2` は英語専用なのに、「日本語にも対応」と書いていた |
| RAG | 生成モデルが「ELYZA または gpt2-ja」で、事前取得の一覧にない（当日はオフラインなので動かない）。しかもプロンプトを作るだけで生成していなかった |
| RAG | `chunk_size` は `length_function=len`（文字数）なのに「256 / 512 / 1024 token」と説明していた |
| RAG | `Chroma.from_documents()` を同じ名前で再実行すると、同じチャンクが二重に入る |
| 評価 | 回答も LLM-as-judge も手書きのダミーで、DESIGN.md の「3 条件で回答させて採点する」になっていなかった |
| 演習 | 自己チェックがなく、正解したかどうか分からない |

### ハンズオン③ RAG（2026-10-20）

| 決めたこと | 理由 |
|---|---|
| 検索対象に **参加者手順書の写し**（`chapter2/data/rag_docs/handson_participant_guide.md`）を加えた | LLM が事前学習で読んでいない知識なので、「RAG なしでは答えられず、RAG ありなら答えられる」差がはっきり出る。DESIGN.md 1.3 のプロダクト例「社内ドキュメント QA」にも合う。写しなので、`docs/participant_guide.md` を変えたら写しも更新する（`rag_docs/README.md` に記載） |
| 埋め込みを `paraphrase-multilingual-MiniLM-L12-v2` に変更 | 日本語対応で、e5 系のような `query:` / `passage:` の接頭辞が要らず、説明が簡単。`required_assets.py`・DESIGN.md 4.5 の表・`supplement_rag.html` のコード例も更新 |
| 生成は `Llama-3.2-1B-Instruct`（第1章と同じ） | 取得済みで、第2章 RAG の上限（RAM 6GB / GPU 5GB）に収まる |
| チャンクの大きさは Llama のトークナイザで数える（`from_huggingface_tokenizer`） | DESIGN.md の「256 / 512 / 1024 token」をそのまま実験できる |
| 検索の良し悪しを **当たり率**（hit rate@k）で測る | 7 問の質問と「答えが書かれた箇所の文字列」の組を用意し、上位 k 件に含まれるかで判定。chunk_size × k の表を作る。DESIGN.md の「評価を感覚ではなく指標で」に合わせた |
| `build_vectorstore()` で `reset_collection()` してから入れる | セルの再実行で二重に入るのを防ぐ |

ノートブックの数値（当たり率・回答）を断定する文は書いていない。DGX で実行したら、出力を見て本文の「〜のはずです」を確かめること。

### ハンズオン① SFT（2026-10-20）

| 決めたこと | 理由 |
|---|---|
| データを `prompt` / `completion` の組にして `SFTTrainer` に渡す | trl 1.x はこの形式だと **回答の部分だけで損失を計算** する（終了トークンも含む）。ノートブックで、1 件目のどこを学習するかを表示して確かめる |
| dolly の列名は `input`/`context`・`output`/`response` の両方を見る | 下書きは `context`・`response` だけを見ていた。kunishou 版は `input`・`output` の可能性があり（**DGX で `raw.column_names` を要確認**）、その場合は空の文脈・空の回答で学習していた |
| 学習前の回答（Part 2）と学習後の回答（Part 7）を同じプロンプトで並べる | DESIGN.md 第2章の「同一の入力で出力を並べる」。ベースモデルが止まらずに次の `### 指示:` を書き始める様子と比べる |
| SFT 後に参加者手順書の質問をする（Part 7-2） | 「SFT は答え方、知識は RAG」を体験させ、ハンズオン③・④につなぐ |
| `report_to='none'` にし、`log_history` の損失・正解率・学習率をグラフにする | 当日は `WANDB_MODE=offline`（`handson.sh`）で wandb の画面が使えない。DESIGN.md 第2章の「wandb でログを監視」からの変更。`index.html`・`supplement_sft.html` の wandb の記述も直した |
| アダプタを `chapter2/outputs/sft_lora_r{rank}` に保存 | 下書きは時刻つきのディレクトリで、DPO・評価から見つけられなかった。スクリプト `train_sft.py` も同じ場所に保存する（`--rank`・`--max-steps` などを引数で指定） |
| `requirements.txt`・`check_env.py` に `bitsandbytes` を追加 | 下書きは QLoRA なのに bitsandbytes が一覧になかった。**GB10（aarch64・CUDA 13）で 4bit 読み込みが動くかは未確認** |

学習時間の「約15分」は目安で、実測していない（60 回更新 × 16 件 × 最大 512 トークン）。リハーサルで測ること。

### ハンズオン② DPO（2026-10-20）

| 決めたこと | 理由 |
|---|---|
| ハンズオン①のアダプタ（`outputs/sft_lora_r16`）を `PeftModel.from_pretrained(..., is_trainable=True)` で読み、その続きから DPO する | 下書きはベースモデルに新しい LoRA を付けていて、「SFT モデルに DPO」になっていなかった。trl 1.x は、アダプタ付きのモデルを渡すとアダプタのコピー（`ref`）を作り、**SFT 後のモデルを参照モデル** にする。アダプタがなければベースモデルに新しい LoRA を付けて続ける |
| 好みのデータを `chapter2/data/dpo_preference.json`（8 組）に置き、ノートブックとスクリプトで共有する | テーマは「社内 QA アシスタントの答え方」（結論から具体的に／知らないことは知らないと言う／パスワードは断る）。DESIGN.md の「5〜10 件を手で作らせる」に合わせ、本編で 1 組以上、演習で 3 組を参加者が追加する |
| 学習データにない 1 組で `log π(chosen) − log π(rejected)` を学習前後で測る | 補足資料 2-2 の「参照モデル 40% → 学習中 60%」の考え方を、本物のモデルの数値で確かめる。演習の課題 2 でこの関数を実装し、`labels` を付けた損失から求めた値と一致するかで自己チェックする |
| `rewards/chosen`・`rewards/rejected`・`rewards/margins`・`rewards/accuracies` をグラフにする | DPO の学習ログの読み方。最初の損失が ln 2 ≈ 0.693 になる理由も説明する |
| 保存は `save_pretrained(..., selected_adapters=['default'])` | そのまま保存すると参照用の `ref` も書き出される |

### ハンズオン④ 評価（2026-10-20）

| 決めたこと | 理由 |
|---|---|
| 10 問を「一般 5 問」と「参加者手順書 5 問」に分ける | 一般の質問は 3 条件の差が出にくく、手順書の質問は RAG だけが答えられるはず。手法選定の判断基準（知識が要るなら RAG）を数字で確かめられる |
| 3 条件の回答を実際に生成する（下書きは手書きのダミー） | 1 つの 8B（4bit）+ SFT アダプタで、「素の LLM」は `disable_adapter()`、「RAG あり」は `### 文脈:` に検索結果を入れる。8B を 2 つ読まずに済む。どの条件も最初の `###` の手前で切って比べる |
| ROUGE-L は文字単位のトークナイザで計算する | `rouge_score` の既定は英数字以外を捨てる。日本語では同じ文どうしでも 0 点、英字が混ざると「AI」だけで 1.000 点になる（`supplement_evaluation.html` の例がそうだった）。ページのコード例を直し、実際の出力（0.727 / 0.566 / 0.727）を載せた |
| BERTScore は `model_type='bert-base-multilingual-cased'` を明示する | `lang='ja'` でも同じモデルが選ばれるが（`lang2model` は既定値つきの辞書）、どのモデルで測ったかを明示するため |
| LLM-as-judge は `Llama-3.2-1B-Instruct` の「1」〜「5」の確率から期待値を出す | 書かせると形式がばらつく。期待値なら毎回同じ値で、細かい差も出る。下書きは文字の重なりで点を付けるダミー関数だった |
| 採点の前に、採点役を確かめる（模範解答・無関係・正反対の 3 例） | 1B の採点役は弱い。点数は参考値と明記した |
| 演習は ROUGE-L の LCS を自分で実装し、「正反対」（否定を足しただけの回答）にだまされる指標を探す | 文字単位の ROUGE-L は「言い換え」0.253 に対し「正反対」0.914（実測）。指標が何を測っているかを体感させる |
| 第2章は通して SFT と同じ上限（RAM 8GB / GPU 14GB）で進める | 評価で 8B を読むため。DESIGN.md 4.3・運営者ガイド 4-2 の表を更新。`index.html` の 2-4 のバッジを「CPU可」から「GPU必須」に変更 |

### 検証の方法と限界

クラウドの作業環境からは Hugging Face に接続できない。そこで、本物と同じ repo_id で **ランダム重みの小さなモデル**（Llama・BERT・sentence-transformers）を作って HF キャッシュの形で置き、`HF_HUB_OFFLINE=1` で `jupyter nbconvert --execute` した。確かめたのは「現行のライブラリで最後までエラーなく動くこと」だけで、回答の中身や当たり率の値は意味を持たない。

| 対象 | 結果（transformers 5.20・langchain 1.4・langchain-chroma 1.1・chromadb 1.5） |
|---|---|
| `ch2_03_rag.ipynb` | ✅ 全セル実行・エラー 0 |
| `sol_03_rag.ipynb` | ✅ 全セル実行・自己チェック 4 件通過 |
| `ch2_01_sft.ipynb` | ✅ 全セル実行・エラー 0（CPU・量子化なし。trl 1.16・peft 0.21） |
| `sol_01_sft.ipynb` | ✅ 全セル実行・自己チェック 4 件通過 |
| `scripts/train_sft.py` | ✅ `--max-steps 20` で学習・保存まで |
| `ch2_02_dpo.ipynb` | ✅ 全セル実行・エラー 0（SFT のアダプタあり。`ref` アダプタが作られることを確認） |
| `sol_02_dpo.ipynb` | ✅ 全セル実行・自己チェック 4 件通過 |
| `scripts/train_dpo.py` | ✅ `--max-steps 10` で学習・保存まで（保存先に `ref` が含まれないことを確認） |
| `ch2_04_evaluation.ipynb` | ✅ 全セル実行・エラー 0（SFT のアダプタあり） |
| `sol_04_evaluation.ipynb` | ✅ 全セル実行・自己チェック 4 件通過 |

dolly-15k-ja は、オフラインではハブのキャッシュから読めないため、テストのときだけ IPython の起動スクリプトで `load_dataset` を偽の JSON に差し替えた。bitsandbytes（4bit）の経路は CPU では通らないので未検証。

---

## 残タスク

### 開催方式

| 項目 | 状態 |
|---|---|
| Llama-3-8B のダウンロード（HF のアクセス申請＋`HF_TOKEN`） | 未（2026-10-06 に `check_env.py` で再確認。`/opt/handson/hf_cache` と `~/.cache/huggingface` のどちらも README・LICENSE だけで、重みはない） |
| 第2章の上限値（RAM 8GB / GPU 14GB / 同時2本）の確認 | 未（10人同時リハーサルで確認） |
| 10人同時リハーサル | 未 |
| 参加者用アカウント `handson` への移行 | 済（2026-09-24） |
| 参加者の接続経路 | 会社の PC からは DGX に届かない（社内接続ソフトで遮断、携帯回線からは経路なし）ため、管理者から貸与 VM（1人1台、10台）を借りる方式に決定（2026-10-06）。参加者手順書・運営者ガイドを VM 経由に更新済み |
| 貸与 VM の IP の確認 | 済: 1号機〜10号機 = 10.1.3.221〜230（固定）。p01〜p10 に対応させる |
| `restrict_ssh.sh 10.1.3.219 10.1.3.{221..230}` の適用 | 適用済み（2026-10-06 13:34。運営者の VM 10.1.3.219 を含む）。確認: 運営者の `ssh handson@localhost` は可、許可外の接続元（10.1.3.220）は `Permission denied ()`、トンネルは localhost:8801 は通り 10.1.3.1:80・localhost:22 は `administratively prohibited`。sshd は同じ項目なら最初の値が勝つため、許可外の接続元の Match を先に書く順序にスクリプトを修正（再実行で反映） |
| 貸与 VM からの接続確認 | 運営者の VM（10.1.3.219）から handson でログインできることを確認（2026-10-06）。同じ VM では VS Code の自動ポート転送が 8800/8801 を確保していたため、ssh -L は bind で失敗した（参加者の VM では VS Code を使わない限り起きない） |
| ログイン時の URL 表示（`welcome.sh`） | 実装済み（2026-10-06）。貸与 VM から handson でログインすると、接続元の IP から参加者番号を決めてトークン付き URL を表示し、待機してトンネルを保つ（ForceCommand。参加者は DGX のシェルを使えなくなる）。参加者の SSH コマンドから `-N` を外した。`deploy.sh` → `sudo restrict_ssh.sh 10.1.3.219 10.1.3.{221..230}` で反映済み（2026-10-06 13:34）。運営者の VM（10.1.3.219）の PowerShell から接続し、「登録されていません」の表示が文字化けせずに出ること、その接続のトンネルで教材ページ（localhost:8800）が開けることを確認。PR #7 で main にマージ済み（2026-10-06）。**未確認: 貸与 VM（10.1.3.221〜230）からの p01〜p10 の表示**（2026-10-06 時点で、これらの VM からの SSH の記録は auth.log・journal ともになし。リハーサルで確認する） |
| 運営者の VM を参加者に渡すかの判断 | 未（渡すなら運営者の情報を消す） |
| 第2章の書き直しに伴う DGX 側の更新 | **未**（2026-10-20 追加）。`bash infra/setup.sh`（bitsandbytes・langchain-text-splitters・langchain-huggingface・langchain-chroma を追加）→ `bash infra/predownload.sh`（埋め込みモデルを `paraphrase-multilingual-MiniLM-L12-v2` に変更）→ `deploy.sh --models` → `check_env.py` |
| 第2章ノートブックの DGX での実行と出力の保存 | **未**。クラウド環境では HF に接続できず、ランダム重みの小さなモデルで「最後までエラーなく動くこと」だけを確認した。本物のモデルでの出力・数値は未確認 |

### chapter2・chapter3

| 章 | 状態 |
|---|---|
| 第2章（SFT・DPO・RAG） | Web 資料完成。ノートブック・演習・解答・スクリプトを 2026-10-20 にすべて書き直し済み。**DGX での実行と出力の保存は未** |
| 第3章（AI エージェント） | 未着手 |

---

## デザインシステム

supplement ページは `supplement_linear_regression.html` のデザインを**完全に踏襲**する。
新規ファイルを作るときは同ファイルをテンプレートとして参照すること。

### カラー変数

2026-07-06 から、配色変数・フォント・質感は `assets/web-theme.css` で一元管理している。
各ページは自分の `<style>` の**後に** Google Fonts と `../../assets/web-theme.css` を読み込み、同じ変数を上書きする。
ページ内 `<style>` の `:root` にも旧値が残っているが、実際に効くのは `web-theme.css` の値。**配色を変えるときは `web-theme.css` と `chapter1/manim/scenes/theme.py` を直す。**

主な変数（値は `web-theme.css` が正）:

```css
--bg / --surface / --surface2            /* 背景・カード・薄いサーフェス */
--border / --border-strong               /* ボーダー */
--text / --text-sub / --text-muted       /* テキスト */
--green / --green-mid / --green-bg / --green-border   /* メインアクセント（ディープフォレストグリーン #0D4A38） */
--amber / --amber-bg / --amber-border / --amber-text  /* 注意 */
--red / --red-bg / --red-border          /* 警告 */
--code-bg / --code-out                   /* コードブロック・出力 */
--font-body / --font-display / --font-mono
--shadow-sm / --shadow-card / --shadow-hover
```

### CDN

```html
<!-- Tailwind CSS -->
<script src="https://cdn.tailwindcss.com"></script>

<!-- highlight.js（ダークテーマ） -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script>hljs.highlightAll();</script>

<!-- KaTeX -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body, {delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}]});"></script>
```

### フォント

`web-theme.css` の変数で指定する。Google Fonts から読み込み、読めないときはシステムフォントに落ちる。

| 変数 | フォント |
|---|---|
| `--font-body` | Zen Kaku Gothic New → ヒラギノ角ゴ・游ゴシック・メイリオ |
| `--font-display`（見出し） | Zen Old Mincho → ヒラギノ明朝・游明朝 |
| `--font-mono` | IBM Plex Mono → SF Mono・Menlo・Consolas |

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Zen+Old+Mincho:wght@400;700;900&family=Zen+Kaku+Gothic+New:wght@400;500;700&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/web-theme.css">
```

### 主要コンポーネントクラス

| クラス/要素 | 用途 |
|---|---|
| `.section-rule` | セクション見出し（大型半透明番号 + ラベル + h2） |
| `.card` | 通常カード（白地・細ボーダー・角丸10px） |
| `.card-math` | 数式カード（白地・1.5px強ボーダー） |
| `.note-green` | 緑の左ボーダー注釈ボックス |
| `.note-amber` | 琥珀の左ボーダー注釈ボックス（注意） |
| `.note-red` | 赤の左ボーダー注釈ボックス（警告） |
| `.code-label` | コードブロック上部のmacOS風ヘッダー |
| `.output-block` | ターミナル風の出力表示エリア |
| `.summary-block` | まとめセクション（ディープグリーン背景） |
| `.var-table` | 変数定義テーブル（モノスペース変数名+説明） |
| `.label` | セクション種別ラベル（小文字大文字・追跡） |

### DESIGN.md の制約（厳守）

- アニメーション・動的エフェクト禁止（印刷・PDF出力を想定）。例外: 第1章の解説動画・試し場、第2章 DPO のデモはユーザー指示で追加済み
- 外部 CDN 以外の依存を持たない（例外: 共通テーマ `assets/web-theme.css` と `media/` の動画）
- `pip` コマンド禁止 → `uv pip` を使用
- `device="cuda"` の固定禁止 → `torch.cuda.is_available()` で分岐
- `openai` パッケージ禁止 → HuggingFace + LangChain に統一
- APIキーのハードコード禁止 → 環境変数経由

---

## ユーザーからの指示・方針メモ

### コアメッセージ（必ず反映すること）

> **「AI とは、複雑な入出力を扱えるようにした関数である」**

- `index.html` 冒頭の紺ボックスに明記済み
- 各補足資料でも「関数」という視点を軸に説明を組み立てること
- 特にニューラルネットワークの説明では「関数を複雑にする部品」として位置づける

### section 1-1 の「関数とは何か」導入（index.html に実装済み）

Step 1〜4 の段階的拡張で「関数」の解釈を広げる構成:

1. $y = ax + b$（最もシンプルな線形関数）
2. $y = w_1x_1 + w_2x_2 + b$（多変数）
3. $\mathbf{y} = \mathbf{W}\mathbf{x} + \mathbf{b}$（行列によるベクトル変換）
4. 活性化関数 + 層の積み重ね → 非線形化 → LLM へ

### 各ページの標準構成

supplement ページ:
```
ヘッダー（パンくず + タイトル + 対応ノートブック名）
│
├─ 目標ボックス（このページで理解すること）
│
├─ Section 0（前置き・背景知識）
├─ Section 1（メインコンテンツ①）
│   ├─ 説明文
│   ├─ 数式カード（card-math）
│   └─ コード例 + 実行済み出力
├─ Section 2 ...
│
├─ まとめ（summary-block / ディープグリーン背景）
└─ ナビゲーション（← 前ページ / 次ページ →）
```

---

## HO-3 改訂ログ（2026-09-03）

ハンズオン③を「推論パラメータ探索のみ（約30分）」から
**「Transformer と Attention をゼロから作り、LLM を動かすまで（約75〜90分）」** に全面改訂した。

### 改訂の意図

DESIGN.md 第1章の設計方針「抽象度を段階的に上げる：線形回帰 → NN → Transformer → LLM」のうち、
**Transformer / Attention の段だけがハンズオン不在**で、座学（`supplement_transformer.html`）のみだった。
「動くコードが先、説明は後」という基本方針に沿わせるため、この段を実装ハンズオン化した。

### `ch1_03_llm_inference.ipynb` の構成（84セル）

| Part | 内容 | 到達点 |
|---|---|---|
| 0 | セットアップ・モデルロード | — |
| 1 | トークン化 → 埋め込み → コサイン類似度 | 意味がベクトルの距離として表れることを確認 |
| 2 | Self-Attention をゼロから実装 | 4トークン×4次元のミニチュアで Q/K/V を手で設計し、注目度を可視化 |
| 3 | 因果マスク・Multi-Head を実装 | LLM が左から右にしか書けない理由を構造として理解 |
| 4 | Transformer ブロックを `nn.Module` で構築 | 本物の `LlamaDecoderLayer` と部品を照合。パラメータ内訳を可視化 |
| 5 | 実 Llama の Attention を可視化 | 第3層ヘッド31 が "it → cat" に 0.50 注目していることを発見 |
| 6 | 次トークン予測・貪欲法生成・KV キャッシュ | `generate()` を使わず生成。KV キャッシュで 2.4 倍高速化を実測 |
| 7 | temperature / top_p を確率分布上で可視化 → 生成実験 | 旧 Step3〜5（TTR・Jaccard・repetition_penalty）を統合 |

### 教材設計上の要点

- **Part 2 のミニチュア世界**：各次元に「名詞性・動詞性・生き物性・食べ物性」という
  人間が読める意味を割り当て、$W_Q, W_K$ を手で設計することで
  「食べた → サカナ に 0.99 注目」という**意味の読める注目度**を作った。
  そのうえで Part 2-5 でランダム重みと比較し、「学習とは何を獲得することか」に接続している。
- **Part 5 の Attention Sink**：多くのヘッド（82%）が文頭トークンに注目を捨てる現象を
  コラムとして明示した。これを説明しないと、実 Attention マップを見た参加者が混乱する。
- **Part 2 → Part 5 の伏線回収**が全体の軸。「自分で作る → 本物と照合する → 使いこなす」の順。

### Web 資料の追随修正（`chapter1/web/`）

ノートブック改訂に合わせ、第1章 Web 資料の不整合を解消した。

| ファイル | 修正内容 |
|---|---|
| `supplement_transformer.html` | **因果マスクの節を新設**（4×4 の ○× 図・$-\infty$ マスクの式・実装1行）。**Attention Sink のコラム**を追加（実測 72%）。Multi-Head を Llama-3.2-1B の実数（32ヘッド×16層＝512枚、GQA）に更新。位置エンコーディング→**RoPE**、LayerNorm→**RMSNorm**、FFN→**SwiGLU/SiLU** を追記。ブロック図を **Post-Norm → Pre-Norm** に修正（ノートブック実装と一致させるため）。各節に HO-3 の Part 番号への導線を追加 |
| `supplement_inference_params.html` | コード例の `torch_dtype` を **`dtype`** に修正（transformers 5.x）。**`use_cache`（KV キャッシュ）のカードを追加**。Greedy の説明に「HO-3 Part 6〜7 で generate() を使わず実装する」導線を追加 |
| `supplement_pretraining.html` | 規模感の比較表に **HO-3 で使う Llama-3.2-1B の行**を追加。Causal Masking と「1文から複数サンプル」に HO-3 Part 3 / Part 6 への導線を追加 |
| `quiz_ch1.html` | **13問 → 17問**。選択式に Q6（Q・K・V の役割）・Q7（因果マスクの理由）、穴埋めに Q13（`-inf` マスク）、記述式に Q17（なぜ毎回違う答えが返るか）を追加。設問 ID・表示番号・採点ロジック・スコア分母（客観 10 → 13）をすべて繰り下げ済み |
| `index.html` | HO-3 の題目・説明・所要時間（30→75分）を更新。到達目標に「Self-Attention と Transformer ブロックを自分で実装できる」を追加。1-3 / 1-5 の講義カードに HO-3 の Part 番号を明記。所要時間サマリを実習 135 分・合計約 4 時間に更新 |

> **注**：`supplement_transformer.html` の Attention 例図（「私 は 昨日 食べた 寿司」）は
> ノートブックのミニチュア（「ネコ が サカナ 食べた」）と異なるが、これは意図的にそのまま残している。
> 図は一般的な例示であり矛盾はなく、代わりに図の直下に
> 「HO-3 Part 2 でこの図をコードで再現する」旨のブリッジを置いた。

### 解説方針の改訂（2026-09-03 追記・動画リサーチ反映）

AIcia Solid Project「ディープラーニングの世界」vol.24（Attention）・vol.28（Transformer）を
参照し、説明の切り口を以下のとおり見直した。

| 取り込んだ説明装置 | 反映先 |
|---|---|
| **Attention は「あいまい検索できる辞書」** — Python の `dict` は「キーが完全一致したら値を1個返す」、Attention は「キーに似ている度合いに応じて全部の値を混ぜて返す」 | ch1_03 Part 2 冒頭、`supplement_transformer.html` Section 2、quiz Q6 |
| **「内積＝類似度」がこの式で一番大事** — ここが腑に落ちればあとはおまけ | ch1_03 Part 2-4、`supplement_transformer.html`（数式カード直後） |
| **$W^Q, W^K$ は「ねじる」ためにある** — $Q=K=X$ のままだと自分と自分の内積が最大になり「自分に注目してください」という無意味な機構になる。だから角度を変えてからぶつける | **ch1_03 Part 2-2 を新設**、`supplement_transformer.html` に節を新設、quiz Q18 |
| **Multi-Head は「いろんな角度から類似度を測る」** | ch1_03 Part 3-2、`supplement_transformer.html` |
| **$\sqrt{d_k}$ の直感**「次元が増えるとベクトルは長くなる」 | ch1_03 Part 2-5、`supplement_transformer.html` |
| **教科書の式はバッチ版**。まず1クエリ分に分解して読む | ch1_03 Part 2 冒頭の補足 |
| **Attention の原点は翻訳の単語対応**（Bahdanau 2014）。原論文に "attention" の語はなく "soft align"/"soft search" | `supplement_transformer.html` Section 1 コラム |
| **Encoder-Decoder の固定次元ボトルネック**が Attention 誕生の直接の動機 | `supplement_transformer.html` Section 1「問題⓪」 |

#### 最大の改善：ch1_03 Part 2-2「まず、重み行列なしでやってみる」の新設

従来は $W_Q, W_K$ を天下り的に与えていたため、**「なぜ射影行列が必要なのか」が説明されていなかった**。
そこで、$Q=K=X$（重み行列なし）で Attention を計算する**失敗する実験**を先に置いた。

```
重み行列なし（Q = K = X）の注目度       →  W_Q, W_K あり
  食べた → 自分   0.35                    食べた → サカナ  0.99
  食べた → サカナ 0.22                    食べた → 自分    0.00
```

意味を持つトークン（ネコ・サカナ・食べた）はすべて自分自身が最大になり、
動詞が目的語を見つけられない。この失敗を見せてから $W_Q, W_K$ を「解決策」として導入する構成にした。
2つの注目度マップを並べた比較図も追加。

> **注意**：「どの行も自分自身が最大」は不正確（助詞「が」は特徴が無いためほぼ均等 0.24〜0.26）。
> 実行結果に合わせて「意味を持つトークンは」と限定して記述している。

ch1_03 は 84 → **88 セル**、quiz は 17 → **18 問**（記述式 Q18 を追加、番号繰り下げ不要）。

### 30分版への圧縮と付録への分割（2026-09-03）

「内容は良いが量が多すぎる」というレビューを受け、本編を **88 → 47 セル（約30分）** に絞り、
外した内容を **`ch1_03_appendix_deep_dive.ipynb`（42セル・約45分）** に退避した。

#### 本編（30分・47セル）に残したもの

| Part | 内容 |
|---|---|
| 0 | セットアップ・モデルロード |
| 1 | トークン化 → 埋め込み → コサイン類似度（埋め込み行列の説明は類似度セルに畳み込み） |
| 2 | Self-Attention をゼロから（W なしの失敗 → ねじる → 実装 → 比較図 → 出力ベクトル） |
| 3 | 因果マスク（Multi-Head は付録へ） |
| 4 | **本物の Llama の1層を print して部品を照合するだけ**（自作クラスは付録へ） |
| 5 | 実 Llama の Attention 可視化（it→cat の1枚のみ） |
| 6 | 次トークン予測 → 貪欲法生成 |
| 7 | temperature / top_p の分布可視化 → generate() で2温度比較 |

#### 付録（任意・42セル）に退避したもの

| 付録 | 内容 | 元 Part |
|---|---|---|
| A | √d_k の実験、学習前のランダム重み、日英トークン効率 | 2-5・2-6・1-1 |
| B | Multi-Head Attention を作る | 3-2 |
| C | Transformer ブロックを nn.Module で組み立て＋パラメータ内訳 | 4 |
| D | 層ごとの Attention の違い、Attention Sink の実測 | 5 |
| E | 全位置ぶんの予測、KV キャッシュ、サンプリングの自作実装 | 6-1・6-3・7-3 |
| F | TTR・Top-p 実験・Jaccard・repetition_penalty | 7-5〜7-8 |

**付録は独立して動く。** 冒頭の「準備」セル1つで、本編で定義した関数・変数
（`scaled_dot_product_attention` / `causal_self_attention` / `plot_attention` /
ミニチュア世界 `X` / 実モデルの注目度 `A` / `generate_text` など）をまとめて再現する。
関数定義は本編ノートブックから機械的に抽出しているため、本編と付録で実装がズレない。

#### 実行時間の実測（DGX / GB10）

| ノートブック | セル数 | 全セル実行 | エラー |
|---|---|---|---|
| `ch1_03_llm_inference.ipynb` | 47（code 21） | **13 秒** | 0 |
| `ch1_03_appendix_deep_dive.ipynb` | 42（code 19） | 32 秒 | 0 |

（本編は生成を伴う重い実験を付録へ移したため、実行時間が 34 秒 → 13 秒に短縮）

#### 追随修正

- `index.html`：HO-3 を「実習 30分」に戻し、付録を「発展（任意・約45分）」として別枠で記載。
  所要時間サマリを実習 90 分・合計約 3.5 時間に修正。到達目標4 から「Transformer ブロック」を外した
- Web 補足資料の「ハンズオン③ Part N」参照を、本編／付録のどちらを指すかに合わせて全件修正
  （Attention Sink → 付録 D、KV キャッシュ → 付録 E-2、ブロック組み立て → 付録 C など）
- `ex_03` / `sol_03` の課題4・課題7 に、対応する解説が付録にある旨の注記を追加

### 第1章 全体整合チェック（2026-09-03）

`chapter1/notebooks` と `chapter1/web` を機械的に突き合わせ、1つの教材として
連動しているかを検証した。

#### 検証して問題なかった項目

| 検証項目 | 結果 |
|---|---|
| web → ノートブック／HTML のファイル参照が実在するか | 全件実在 |
| web が参照する「Part N」「N-M」「付録 X」が実在するか | 全件実在 |
| web に書かれた数値が実行結果と一致するか | 全件一致（下表） |
| 所要時間の内訳と合計 | 講義95分＝20+20+25+15+15、実習90分＝30×3、合計200分≈3.5時間で整合 |
| クイズが参照する補足資料の Section 番号 | 全件実在（NN Section 0 は「前置き」ラベル） |
| 補足資料のコード例とノートブック実装（`TwoLayerNN` の構造） | 一致 |
| 「MNIST は20万パラメータ」 | 784×256+256 + 256×10+10 = 203,530 で正しい |
| 古い記述の残骸（ELYZA・75分・88セル・旧タイトル等） | なし |

検証した数値：`食べた→サカナ 0.99` / `W なし時 自分0.35 vs サカナ0.22` /
`第3層ヘッド31 の it→cat 0.504` / `32ヘッド・16層・512枚` / `d_model 2048` /
`FFN 8192` / `1.24B` / `Attention Sink 平均0.719（82%）` / `481トークンで2.4倍`。

#### 見つかって修正した不整合

| # | 内容 | 修正 |
|---|---|---|
| 1 | **補足資料のナビ連鎖が切れていた**。`supplement_transformer.html`（1-3）の「次」が `index.html` になっており、事前学習（1-4）→推論パラメータ（1-5）へ進めなかった。一方 `supplement_pretraining.html` の「前」は Transformer を指しており片方向だった | 「次の補足資料：事前学習 →」に修正。1-1 から 1-5 まで一本につながった |
| 2 | `supplement_pretraining.html`（1-4）は対応ノートブックとして `ch1_03` を指すのに、`ch1_03` 側の「対応セクション」に 1-4 が無く片方向だった | `ch1_03` の対応セクションを「1-3・1-4・1-5」に修正 |
| 3 | `ex_03` / `sol_03` の課題 4・7 は付録が対応するのに、ヘッダーの対応ノートブックが本編のみだった | 付録を併記 |

### 30分版分割時の記述ミス修正（2026-09-03）

30分版への分割時、Part 4 の冒頭が**旧構成（Part 3 に Multi-Head があった頃）の文面のまま**残っており、
「Part 2〜3 で作った部品は、正規化・Multi-Head Self-Attention・FFN の 3 つでした」と、
**実際には作っていないものを作ったと書いていた**（レビュー指摘により発覚）。

本編 Part 2〜3 で実際に作っているのは以下だけ。

- `W_Q, W_K, W_V`（Q・K・V を作る射影行列）
- `scaled_dot_product_attention()`
- `causal_self_attention()`

正規化・Multi-Head・FFN・残差接続はいずれも本編では作らず、付録 B / C に移動済み。

| 修正箇所 | 内容 |
|---|---|
| `ch1_03` Part 4 冒頭 | 「作ったもの」と「まだ作っていない部品」を 2 つの表に分けて明示 |
| `ch1_03` Part 4 対応表 | 「本編で作ったか」列を追加。`o_proj` / 正規化 / `mlp` は「未（→付録 B・C）」と明記 |
| `ch1_03` まとめ表 | 「同じ部品構成」→「自分が書いた Attention が、名前まで同じ形で本物の中に入っていた」 |
| `supplement_transformer.html` | 「`q_proj` / `o_proj` / `input_layernorm` といった名前まで同じ部品」→ 本編で作ったのは `q/k/v_proj` に相当する部分だけ、と限定 |
| `index.html` 1-3 カード | 「Part 2〜5 でそのまま実装します」→ 実装は Part 2〜3、ブロック組み立ては付録 C と明記 |

> **教訓**：ノートブックを分割・再編したら、「〜で作った」「〜を実装する」と書いてある
> 箇所を全件洗い直すこと。分割前は正しかった記述が、分割後に嘘になる。

### 事前学習 Section 4 の再編（2026-09-03）

`supplement_pretraining.html` Section 4「事前学習済みモデルの活用方法」を
**4アプローチ → 3アプローチ**に再編した。

| 変更前 | 変更後 |
|---|---|
| ① ゼロショット<br>② Few-shot プロンプティング | **① プロンプトエンジニアリング**（ゼロショット / Few-shot を表で内包） |
| ③ ファインチューニング（SFT / LoRA） | ② ファインチューニング（SFT / LoRA） |
| ④ RAG（検索拡張生成） | ③ RAG（検索拡張生成） |

ゼロショットと Few-shot は「モデルに手を加えず、入力の書き方だけでタスクを定義する」
という同じアプローチの、例を与える件数の違いにすぎない。分けて並べると
「追加学習なしの手段が 3 つあるように見える」という誤解を招くため統合した。

**第2章の手法選定フレームワーク（`chapter2/web/index.html`）が既に
「Prompt Engineering」を 1 つの手法として扱っている**ため、この統合で章間の整合も取れた。

- 「アプローチ選択の目安」の図は、ゼロショットと Few-shot の 2 円を残したまま
  破線の枠で括り「プロンプトエンジニアリング」とラベル付けした
  （2 つの間にある「タスク特化度の差」の情報を失わないため）。
  枠は y=73〜139 で、X 軸線（y=140）と交差しないことをレンダリングで確認済み
- 「例を何十件も並べたくなったら、ファインチューニングを検討する合図」という
  実務上の判断基準を注意点に追加
- まとめ 04 を「まずプロンプトエンジニアリング、足りなければ RAG・ファインチューニング
  ——安い手段から順に」に更新

### 各ページ冒頭の「読み始める前に」ブロック（2026-09-03）

> **注意**：当初「LLM の本質は次トークンの統計的予測」を LLM 関連の全ページに
> 同一文面で入れたが、**同じ文章の繰り返しは読み飛ばされる**というレビュー指摘を受け、
> **`supplement_transformer.html` のみに残し、他はセクション固有のメッセージに書き換えた。**

現在の各ページ冒頭のメッセージは以下のとおり。**同じ文面は 1 つもない。**

| ページ | 冒頭のメッセージ |
|---|---|
| `index.html` | **AI とは、「複雑な入出力を扱えるようにした関数」である**（章全体の核心。既存のまま） |
| `supplement_linear_regression.html` | ブロックなし（「このページで理解すること」から開始。従来どおり） |
| `supplement_neural_network.html` | 同上 |
| `supplement_transformer.html` | **LLM がしているのは、次に来る単語（トークン）を統計的に予測すること——それだけ**。モデルが複雑になっても本質は変わらない |
| `supplement_pretraining.html` | **LLM の知識は、誰も教えていません**。MNIST と違い、テキストそのものが正解になる。だから人手のラベル付けから解放され、桁違いのデータ量で学習できた |
| `supplement_inference_params.html` | **推論パラメータは、モデルを一切変えません**。変えるのは確率分布から「どのトークンを選ぶか」という最後の一手だけ。最も安く速い出力制御の手段 |

ノートブック側（`ch1_03_llm_inference.ipynb` と付録）には、次トークン予測の
コアメッセージを引き続き配置している。Web の補足資料とは別の媒体であり、
ノートブックは Part 6 でその主張を実際に検証する構成になっているため。

#### （参考）当初の実装

LLM 関連の解説すべての**冒頭**に、章を貫くコアメッセージを配置した。

> **LLM がしているのは、次に来る単語（トークン）を統計的に予測すること——それだけです。**
> この本質は、モデルがどれだけ新しく複雑になっても変わらない。
> パラメータが数千億個になっても、推論モデルでも、マルチモーダルモデルでも、
> 中核にあるのは同じ次トークン予測。変わったのは予測の精度と扱えるトークンの種類だけ。

| 配置先 | 形式 |
|---|---|
| `chapter1/web/index.html` | 既存の「この章の核心」（AI＝関数）ブロック内に、区切り線を挟んで併記 |
| `chapter1/web/supplement_transformer.html` | 目標ボックスの**前**に `summary-block`（濃緑）で配置 |
| `chapter1/web/supplement_pretraining.html` | 同上 |
| `chapter1/web/supplement_inference_params.html` | 同上 |
| `chapter1/notebooks/ch1_03_llm_inference.ipynb` | タイトルセル冒頭に引用ブロックで配置 |
| `chapter1/notebooks/ch1_03_appendix_deep_dive.ipynb` | タイトルセル冒頭に短縮版 |

**同じ文面の貼り付けにはせず、各ページの主題に結ぶ一文を末尾に付けている。**

- Transformer：「Attention も Transformer も、この予測を上手くやるための仕組みにすぎない」
- 事前学習：「事前学習とは、まさにこの『次トークン予測』の練習そのもの」
- 推論パラメータ：「temperature も top_p も、予測された確率分布からどう選ぶかを決めているだけ」
- 付録：「これから見る込み入った仕組みはすべて、その予測を上手くやるための工夫にすぎない」

`quiz_ch1.html` は設問ページのため対象外。線形回帰・ニューラルネットワークの補足資料も
LLM の解説ではないため対象外とした。

### `ex_03` / `sol_03`

課題9問＋チャレンジ2問。各課題末尾に `assert` による**自己チェック**を入れ、
`✅ OK` が出れば正解と分かるようにした。特に課題4（残差接続）は
「全パラメータを 0 にしたとき出力が入力と一致するか」で残差の有無を判定している。

### 動作検証（DGX / GB10・torch 2.13・transformers 5.16）

| 対象 | 結果 |
|---|---|
| `ch1_03_llm_inference.ipynb` 全84セル実行 | ✅ エラー0件・約34秒 |
| `sol_03_llm_inference.ipynb` 全セル実行 | ✅ エラー0件・自己チェック9件すべて通過 |

### 既知の注意点

- モデルロードに `attn_implementation='eager'` が**必須**（Part 5 で `output_attentions=True` を使うため）。
  SDPA / FlashAttention では Attention 重みが返らない。
- transformers 5.x では `torch_dtype` が deprecated。`dtype` を使うこと。
- `AutoTokenizer.from_pretrained(..., clean_up_tokenization_spaces=False)` を指定しないと
  BPE トークナイザの警告が出る。

---

## 作業ルール（CLAUDE.md より）

- ファイル生成・更新・プログラム実行の前に**必ず作業計画を報告し y/n で確認**を取る
- 読み取り・ディレクトリ確認などの非破壊操作は確認不要
- パッケージインストールは `uv pip install`（`pip` 直接使用禁止）
- 一時ファイルは `/home/chinchilla/.claude/temp/` 以下に保存
- 会話は日本語で行う
- GitHub push は各ファイル完成ごとに実施
