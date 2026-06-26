#!/usr/bin/env python3
"""
第2章 DPO 学習スクリプト
SFT 済みモデルに DPOTrainer で preference alignment を適用する

使用方法:
  tmux new -s dpo-train
  CUDA_VISIBLE_DEVICES=1 python scripts/train_dpo.py \
      --sft_model_path ./outputs/sft_<timestamp>

環境変数:
  CUDA_VISIBLE_DEVICES  使用する GPU の番号
  HF_HOME               HuggingFace キャッシュパス
  WANDB_PROJECT         wandb プロジェクト名（デフォルト: dgx-handson-dpo）
"""

import os
import argparse
import json
import torch
from datetime import datetime
from datasets import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig, TaskType, get_peft_model
from trl import DPOTrainer, DPOConfig

# ── 環境設定 ─────────────────────────────────────────────────────────────
HF_HOME = os.environ.get("HF_HOME", "/data/shared/hf_cache")
os.environ.setdefault("HF_HOME", HF_HOME)
os.environ.setdefault("TRANSFORMERS_CACHE", HF_HOME)
os.environ.setdefault("WANDB_PROJECT", "dgx-handson-dpo")

# ── ハイパーパラメータ ───────────────────────────────────────────────────
LORA_RANK    = 8
LORA_ALPHA   = 16
LEARNING_RATE= 5e-5
BETA         = 0.1      # DPO の KL ペナルティ係数
MAX_SEQ_LEN  = 512
BATCH_SIZE   = 2
GRAD_ACCUM   = 4
NUM_EPOCHS   = 1
MAX_STEPS    = 50       # デモ用に短縮


# ── サンプル preference データセット ──────────────────────────────────────
# 本来は participants が手動で作成するデータ。ここはデモ用のサンプルを使用。
SAMPLE_PREFERENCE_DATA = [
    {
        "prompt": "Python でリストを逆順にする方法を教えてください。",
        "chosen": (
            "Python でリストを逆順にするには主に 2 つの方法があります。\n\n"
            "**1. `reversed()` 関数を使う**\n```python\nmy_list = [1, 2, 3, 4, 5]\n"
            "reversed_list = list(reversed(my_list))\nprint(reversed_list)  # [5, 4, 3, 2, 1]\n```\n\n"
            "**2. スライスを使う**\n```python\nreversed_list = my_list[::-1]\n```\n\n"
            "元のリストを変更せず新しいリストを返します。元のリスト自体を変更したい場合は "
            "`my_list.reverse()` を使ってください。"
        ),
        "rejected": (
            "リストを逆にするには reverse を使います。my_list.reverse() と書けば逆になります。"
        ),
    },
    {
        "prompt": "機械学習における過学習（overfitting）とは何ですか？",
        "chosen": (
            "過学習とは、モデルが訓練データに過度に適合してしまい、未知のデータ（テストデータ）に対して"
            "うまく予測できなくなる現象です。\n\n"
            "**原因**\n- モデルの複雑さに対してデータが少ない\n- 学習回数が多すぎる\n\n"
            "**対策**\n- 正則化（L1/L2）\n- ドロップアウト\n- データ拡張\n- 早期終了（Early Stopping）\n\n"
            "損失曲線で「訓練損失は下がるがバリデーション損失が上がり始める」パターンが過学習のサインです。"
        ),
        "rejected": (
            "過学習は訓練データを覚えすぎることです。テストで悪い結果になります。"
            "たくさんデータを集めれば解決します。"
        ),
    },
    {
        "prompt": "Git の rebase と merge の違いを教えてください。",
        "chosen": (
            "どちらもブランチの変更を統合する操作ですが、履歴の形が異なります。\n\n"
            "**merge**\n```\nA---B---C  main\n     \\\n      D---E  feature\n          ↓\nA---B---C---M  (マージコミット M が作られる)\n     \\      /\n      D---E\n```\n"
            "履歴が分岐のまま残り、いつ何とマージしたかが明確になります。\n\n"
            "**rebase**\n```\nA---B---C  main\n         \\\n          D'--E'  (feature のコミットが main の先頭に積み直される)\n```\n"
            "履歴が一直線になりすっきりしますが、コミット ID が変わります。\n\n"
            "**使い分け**: チーム開発では merge が安全。個人ブランチの整理には rebase が有効です。"
        ),
        "rejected": (
            "rebase はコミットを移動させます。merge はブランチをくっつけます。どちらも同じことができます。"
        ),
    },
]


def load_preference_data(data_path: str | None) -> Dataset:
    """JSON ファイルまたはサンプルデータから preference dataset を読み込む"""
    if data_path and os.path.exists(data_path):
        with open(data_path) as f:
            records = json.load(f)
        print(f"カスタム preference データを読み込み: {len(records)} 件 ({data_path})")
    else:
        records = SAMPLE_PREFERENCE_DATA
        print(f"サンプル preference データを使用: {len(records)} 件")
        print("  ヒント: --data_path で自作の JSON を指定できます")

    return Dataset.from_list(records)


def main():
    parser = argparse.ArgumentParser(description="DPO 学習スクリプト")
    parser.add_argument("--sft_model_path", type=str, default=None,
                        help="SFT 済みモデルのパス（省略時はベースモデルを使用）")
    parser.add_argument("--data_path", type=str, default=None,
                        help="preference データ JSON ファイルのパス")
    args = parser.parse_args()

    base_model = args.sft_model_path or "meta-llama/Meta-Llama-3-8B"
    output_dir = f"./outputs/dpo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    print("=" * 60)
    print("DPO 学習スクリプト開始")
    print(f"  ベースモデル: {base_model}")
    print(f"  beta        : {BETA}")
    print(f"  出力先      : {output_dir}")
    print("=" * 60)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n使用デバイス: {device}")

    # ── 量子化設定 ────────────────────────────────────────────────────
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    ) if device == "cuda" else None

    # ── モデル・トークナイザー読み込み ────────────────────────────────
    print("\nモデルを読み込み中...")
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        quantization_config=bnb_config,
        device_map="auto" if device == "cuda" else None,
        torch_dtype=torch.bfloat16 if device == "cuda" else torch.float32,
        trust_remote_code=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token

    # ── LoRA 設定 ──────────────────────────────────────────────────────
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=LORA_RANK,
        lora_alpha=LORA_ALPHA,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        bias="none",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # ── データセット読み込み ────────────────────────────────────────────
    dataset = load_preference_data(args.data_path)

    # ── 学習設定 ───────────────────────────────────────────────────────
    training_args = DPOConfig(
        output_dir=output_dir,
        num_train_epochs=NUM_EPOCHS,
        max_steps=MAX_STEPS,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM,
        learning_rate=LEARNING_RATE,
        beta=BETA,
        bf16=device == "cuda",
        logging_steps=5,
        save_steps=25,
        save_total_limit=2,
        report_to="wandb",
        run_name=f"dpo-beta{BETA}",
        max_length=MAX_SEQ_LEN,
        max_prompt_length=256,
    )

    trainer = DPOTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        tokenizer=tokenizer,
    )

    # ── 学習実行 ───────────────────────────────────────────────────────
    print("\nDPO 学習を開始します...")
    trainer.train()

    print("\nアダプタを保存中...")
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    print(f"保存完了: {output_dir}")
    print("\n学習完了！SFT モデルと出力を比較してみてください。")


if __name__ == "__main__":
    main()
