# dgx-handson 進捗記録

> 別セッションの Claude Code がすぐに作業を再開するための引き継ぎドキュメント。
> 最終更新：2026-09-03（HO-3 を Transformer/Attention 実装ハンズオンへ全面改訂）

---

## リポジトリ情報

| 項目 | 内容 |
|---|---|
| GitHub | https://github.com/chinchillaa/dgx-handson（Public） |
| ローカルパス | `/home/chinchilla/pjt/sbcs-work/dgx-handson/` |
| ブランチ | `main` |

---

## プロジェクト概要

DGX（A100 x8）上で実施する ML ハンズオンセッション用コンテンツ一式。
設計仕様は `design/DESIGN.md` が正とする。**実装に迷ったら必ず DESIGN.md に立ち返ること。**

### 3章構成

| 章 | テーマ | 状態 |
|---|---|---|
| 第1章 | 機械学習(AI)の仕組み | **完成** |
| 第2章 | AI を「強く」する（SFT・DPO・RAG） | **Web 資料完成・説明改善済み** |
| 第3章 | AI エージェントを作ろう | 未着手 |

---

## 完成済みファイル

```
dgx-handson/
├── .gitignore
├── requirements.txt                              ✅ 全章共通パッケージ
├── design/
│   ├── DESIGN.md                                 ✅ 設計仕様書（変更不可）
│   └── PROGRESS.md                               ✅ このファイル
├── chapter1/
│   ├── web/
│   │   ├── index.html                            ✅ 章の進行ガイド・目次
│   │   ├── supplement_linear_regression.html     ✅ 線形回帰・損失関数・勾配降下法
│   │   ├── supplement_neural_network.html        ✅ XOR問題・NN構造・活性化関数・PyTorch autograd
│   │   ├── supplement_transformer.html           ✅ 埋め込み・Self-Attention・Transformerブロック・LLMへのつながり
│   │   ├── supplement_pretraining.html           ✅ 自己教師あり学習・CLM・スケーリング則・活用方法
│   │   ├── supplement_inference_params.html      ✅ Temperature・Top-p/k・generate()パラメータ設定
│   │   └── quiz_ch1.html                         ✅ 理解確認クイズ（選択式5・穴埋め5・記述式3）JS採点付き
│   ├── notebooks/
│   │   ├── ch1_01_linear_regression.ipynb        ✅ NumPy勾配降下・学習率実験（解説用）
│   │   ├── ch1_02_mnist_nn.ipynb                 ✅ PyTorch 2層NN・MNIST分類（解説用）
│   │   └── ch1_03_llm_inference.ipynb            ✅ Transformer/Attention 実装〜LLM推論（解説用・84セル）
│   ├── exercises/
│   │   ├── ex_01_linear_regression.ipynb         ✅ 穴埋め: predict/mse_loss/dw/db/更新式
│   │   ├── ex_02_mnist_nn.ipynb                  ✅ 穴埋め: fc1/fc2定義・forward・5ステップループ・evaluate
│   │   └── ex_03_llm_inference.ipynb             ✅ 穴埋め9問: Attention/因果マスク/残差/貪欲法/サンプリング（assert 自己チェック付き）
│   └── solutions/
│       ├── sol_01_linear_regression.ipynb        ✅ HO-1 解答
│       ├── sol_02_mnist_nn.ipynb                 ✅ HO-2 解答
│       └── sol_03_llm_inference.ipynb            ✅ HO-3 解答（実行検証済み・自己チェック9件通過）
├── chapter2/
│   └── web/
│       ├── index.html                            ✅ 第2章トップ・手法選定フレームワーク
│       ├── supplement_sft.html                   ✅ SFT・LoRA・QLoRA 補足（4×4行列の数値例つき）
│       ├── supplement_dpo.html                   ✅ DPO 補足（参照モデル・損失関数図解・動的デモつき）
│       ├── supplement_rag.html                   ✅ RAG 補足（チャンクサイズ情報量目安つき）
│       ├── supplement_evaluation.html            ✅ 評価指標補足（ROUGE・BERTScore・LLM-as-judge）
│       └── quiz_ch2.html                         ✅ 第2章 理解確認クイズ
├── chapter3/  （空ディレクトリ + .gitkeep のみ）
└── infra/
    ├── setup.sh                                      ✅ 環境構築（uv + venv + パッケージ + Jupyter カーネル）
    ├── predownload.sh                                ✅ MNIST + Llama-3.2-1B-Instruct 事前ダウンロード
    └── check_env.py                                  ✅ 環境確認（GPU・パッケージ・共有ストレージ・HF認証）
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

## 残タスク

### chapter2・chapter3

| 章 | 状態 |
|---|---|
| 第2章（SFT・DPO・RAG） | Web 資料完成。ノートブック・演習・解答は未作成 |
| 第3章（AI エージェント） | 未着手 |

---

## デザインシステム

supplement ページは `supplement_linear_regression.html` のデザインを**完全に踏襲**する。
新規ファイルを作るときは同ファイルをテンプレートとして参照すること。

### カラー変数（`<style>` の `:root` に定義）

```css
--bg:           #F7F5F0   /* ページ背景（ウォームオフホワイト） */
--surface:      #FFFFFF   /* カード背景 */
--surface2:     #F0EDE6   /* 薄いサーフェス */
--border:       #DDD8CE   /* 通常ボーダー */
--border-strong:#C5BFB2   /* 強調ボーダー */
--text:         #1C1917   /* 本文テキスト */
--text-sub:     #57534E   /* サブテキスト */
--text-muted:   #A8A29E   /* ミュートテキスト */
--green:        #0D4A38   /* メインアクセント（ディープフォレストグリーン） */
--green-mid:    #1A6B52   /* 中間グリーン */
--green-bg:     #EAF3EF   /* グリーン背景 */
--green-border: #A7CBB9   /* グリーンボーダー */
--amber:        #7C5C00   /* 注意色 */
--amber-bg:     #FFF8E6
--amber-border: #E8C96A
--red:          #991B1B   /* 警告色 */
--red-bg:       #FEF2F2
--code-bg:      #18181B   /* コードブロック背景 */
--code-out:     #27272A   /* 出力ブロック背景 */
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

システムフォントスタックを使用（外部フォント CDN は使わない）:

```css
font-family: -apple-system, BlinkMacSystemFont, "Hiragino Kaku Gothic ProN",
             "Hiragino Sans", "Yu Gothic Medium", "Meiryo", sans-serif;
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

- アニメーション・動的エフェクト禁止（印刷・PDF出力を想定）
- 外部 CDN 以外の依存を持たない（単体で動作）
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
