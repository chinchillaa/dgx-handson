# dgx-handson 進捗記録

> 別セッションの Claude Code がすぐに作業を再開するための引き継ぎドキュメント。
> 最終更新：2026-04-16（第1章・infra 完成）

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
| 第2章 | AI を「強く」する（SFT・DPO・RAG） | 未着手 |
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
│   │   └── ch1_03_llm_inference.ipynb            ✅ HuggingFace LLM推論パラメータ探索（解説用）
│   ├── exercises/
│   │   ├── ex_01_linear_regression.ipynb         ✅ 穴埋め: predict/mse_loss/dw/db/更新式
│   │   ├── ex_02_mnist_nn.ipynb                  ✅ 穴埋め: fc1/fc2定義・forward・5ステップループ・evaluate
│   │   └── ex_03_llm_inference.ipynb             ✅ 穴埋め: generate_text/TTR/Jaccard計算
│   └── solutions/
│       ├── sol_01_linear_regression.ipynb        ✅ HO-1 解答
│       ├── sol_02_mnist_nn.ipynb                 ✅ HO-2 解答
│       └── sol_03_llm_inference.ipynb            ✅ HO-3 解答
├── chapter2/  （空ディレクトリ + .gitkeep のみ）
├── chapter3/  （空ディレクトリ + .gitkeep のみ）
└── infra/
    ├── setup.sh                                      ✅ 環境構築（uv + venv + パッケージ + Jupyter カーネル）
    ├── predownload.sh                                ✅ MNIST + Llama-3.2-1B-Instruct 事前ダウンロード
    └── check_env.py                                  ✅ 環境確認（GPU・パッケージ・共有ストレージ・HF認証）
```

---

## 残タスク

### chapter2・chapter3

| 章 | 状態 |
|---|---|
| 第2章（SFT・DPO・RAG） | 未着手 |
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

## 作業ルール（CLAUDE.md より）

- ファイル生成・更新・プログラム実行の前に**必ず作業計画を報告し y/n で確認**を取る
- 読み取り・ディレクトリ確認などの非破壊操作は確認不要
- パッケージインストールは `uv pip install`（`pip` 直接使用禁止）
- 一時ファイルは `/home/chinchilla/.claude/temp/` 以下に保存
- 会話は日本語で行う
- GitHub push は各ファイル完成ごとに実施
