# 第1章の図解アニメーション（manim）

第1章の補足資料に埋め込む解説動画を、[manim Community](https://www.manim.community/) で作ります。
`make` を実行すると、各シーンの動画（1080p30 の MP4）とポスター画像（JPEG）が `chapter1/web/media/` に書き出されます。

| 出力ファイル | シーン | 埋め込み先 | 内容 |
|---|---|---|---|
| `ch1_self_attention.mp4` | `scenes/self_attention.py` | `supplement_transformer.html` の Section 2 | Q·Kᵀ → √d_k で割る → softmax → V の加重和を順に計算します。値はハンズオン③ Part 2 の「ネコ・が・サカナ・食べた」と同じです。 |
| `ch1_xor_relu.mp4` | `scenes/xor_relu.py` | `supplement_neural_network.html` の XOR の説明 | 線形変換と ReLU で平面が曲がり、XOR が 1 本の直線で分けられるようになる様子を示します。 |
| `ch1_gradient_descent.mp4` | `scenes/gradient_descent.py` | `supplement_linear_regression.html` の Section 3 | データに当てはめる直線と、損失の等高線上の軌跡を同時に動かします。データと学習率は資料のコード例と同じです。 |
| `ch1_embedding.mp4` | `scenes/embedding.py` | `supplement_transformer.html` の前置き（自然言語を「数値」に変換する） | 王様 − 男性 + 女性 を矢印でたどり、女王の近くに着地する様子を 2 次元で示します。4 単語の配置は資料の SVG と同じです。 |
| `ch1_rnn_vs_attention.mp4` | `scenes/rnn_vs_attention.py` | `supplement_transformer.html` の Section 1 | RNN が隠れ状態を順番に渡して「私」の情報が薄れる様子（イメージ）と、Self-Attention が「食べた」から全トークンへ一度につなぐ様子を比べます。注目度は資料の図と同じです。 |
| `ch1_causal_mask.mp4` | `scenes/causal_mask.py` | `supplement_transformer.html` の Section 2（因果マスク） | スコアの上三角を −∞ にして softmax を取り、生成時に注目度の三角形が 1 行ずつ伸びる様子を示します。値はハンズオン③ Part 3 と同じです。 |
| `ch1_temperature.mp4` | `scenes/temperature.py` | `supplement_inference_params.html` の Section 1 | T を 1.0 → 0.5 → 0.3 → 2.0 → 1.0 と動かし、logit ÷ T → softmax の確率が鋭くなったり平らになったりする様子を示します。logit と「猫」「犬」…は資料の図と同じです。 |
| `ch1_top_p.mp4` | `scenes/top_p.py` | `supplement_inference_params.html` の Section 2 | 累積確率が p = 0.9 以上になる 3 位まで残し、4・5 位を除外し、0.92 で再正規化してから 1 回サンプリングします。確率は資料の Top-p の図と同じです。最後に Top-k（k = 3）と対比します。 |

配色とフォントは `scenes/theme.py` にまとめています。
値は `assets/web-theme.css` の CSS 変数と同じなので、テーマを変えた場合は両方を更新してください。

## 環境を作ります

DGX（aarch64）では、`pip install manim` が失敗します。
依存パッケージの `glcontext` と `manimpango` に aarch64 向けのビルド済みバイナリがなく、ビルドには X11 と Pango の開発ヘッダー（`sudo apt install` が必要）が要るためです。
conda-forge にはビルド済みのバイナリがあるので、sudo なしで入る micromamba を使います。

リポジトリのルートで実行します。
`~/.local/micromamba` に micromamba とこの環境を置きます。

```bash
mkdir -p ~/.local/micromamba && cd ~/.local/micromamba \
  && curl -sL https://micro.mamba.pm/api/micromamba/linux-aarch64/latest | tar -xj bin/micromamba \
  && cd - \
  && MAMBA_ROOT_PREFIX=~/.local/micromamba ~/.local/micromamba/bin/micromamba create -y \
       -p ~/.local/micromamba/envs/dgx-manim -f chapter1/manim/environment.yml
```

環境には ffmpeg も含まれます。
日本語は OS の「Noto Sans CJK JP」を使うので、`fc-list :lang=ja` に表示されることを確認してください。

LaTeX は入れていません。
数式はページ側の KaTeX で表示し、動画の中では `Text` だけを使います。
`MathTex` や `Axes.add_coordinates()` は LaTeX を必要とするため使わず、軸の目盛りは `theme.tick_labels()` で付けます。

## 描画します

`chapter1/manim` で実行します。

```bash
cd chapter1/manim
make MANIM=~/.local/micromamba/envs/dgx-manim/bin/manim           # 1080p30 ですべてのシーンを描画
make preview MANIM=~/.local/micromamba/envs/dgx-manim/bin/manim   # 480p15 で確認（web/media には書き出さない）
```

シーンの `.py` か `theme.py` を変更した動画だけが再描画されます。
中間ファイルは `chapter1/manim/build/` に置かれ、Git の管理対象外です。

## シーンを追加する場合

1. `scenes/` にシーンのファイルを作り、`from theme import *` で配色とヘルパーを読み込みます。
2. `Makefile` の `SCENES` に「出力ファイル名:シーンファイル:シーンクラス」を追加します。
3. 資料に `<video>` を埋め込みます。既存の動画と同じ書き方（`controls`、`preload="metadata"`、`poster` にポスター画像）にそろえます。

資料の数値と動画の数値がずれないように、値はノートブックや資料のコード例と同じ式で計算してください。
