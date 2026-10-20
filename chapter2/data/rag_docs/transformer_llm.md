# Transformer と大規模言語モデル

Transformer は、2017 年の論文「Attention Is All You Need」で提案されたモデルの構造です。
RNN や LSTM に代わり、自然言語処理の標準的な構造になりました。

## Self-Attention の仕組み

Self-Attention では、文の中の各トークンが、ほかのすべてのトークンとの関連度を計算します。
Query（Q）、Key（K）、Value（V）の 3 つの行列を使い、次の式で計算します。

Attention(Q, K, V) = softmax(Q K^T / sqrt(d_k)) V

d_k は Key ベクトルの次元数です。

## 大規模言語モデル（LLM）の種類

- GPT 系: デコーダだけの構造。次のトークンを予測する課題で事前学習する
- BERT 系: エンコーダだけの構造。隠したトークンを当てる課題で事前学習する
- Llama、Mistral など: 重みが公開されている GPT 系のモデル

## ファインチューニングの手法

- SFT（Supervised Fine-Tuning、教師ありファインチューニング）: 指示と回答の組で学習し、指示に従って答える能力を付ける
- RLHF / DPO: 人が「良い」「悪い」と判断した回答の組から学習し、回答の好ましさを改善する
- LoRA（Low-Rank Adaptation）: 元の重みは固定したまま、小さな低ランク行列 B と A だけを学習する。学習するパラメータが全体の 1% 未満で済むため、少ないメモリでファインチューニングできる
- QLoRA: 元のモデルを 4bit に量子化して読み込み、そのうえで LoRA を学習する。8B のモデルでも、GPU 1 基のメモリで学習できる
