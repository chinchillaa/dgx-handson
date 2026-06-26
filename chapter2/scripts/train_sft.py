#!/usr/bin/env python3
"""
第2章 SFT 学習スクリプト
LLaMA 3 8B + LoRA + SFTTrainer による教師ありファインチューニング

使用方法:
  tmux new -s sft-train
  CUDA_VISIBLE_DEVICES=0 python scripts/train_sft.py

環境変数:
  CUDA_VISIBLE_DEVICES  使用する GPU の番号 (例: 0)
  HF_HOME               HuggingFace キャッシュパス（デフォルト: /data/shared/hf_cache）
  WANDB_PROJECT         wandb プロジェクト名（デフォルト: dgx-handson-sft）
"""

import os
import sys
import torch
from datetime import datetime
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
)
from peft import LoraConfig, TaskType, get_peft_model
from trl import SFTTrainer, SFTConfig

# ── 環境設定 ─────────────────────────────────────────────────────────────
HF_HOME = os.environ.get("HF_HOME", "/data/shared/hf_cache")
os.environ.setdefault("HF_HOME", HF_HOME)
os.environ.setdefault("TRANSFORMERS_CACHE", HF_HOME)
os.environ.setdefault("WANDB_PROJECT", "dgx-handson-sft")

# ── ハイパーパラメータ（ここを変更して実験） ──────────────────────────────
MODEL_NAME   = "meta-llama/Meta-Llama-3-8B"
DATASET_NAME = "kunishou/databricks-dolly-15k-ja"
OUTPUT_DIR   = f"./outputs/sft_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

LORA_RANK    = 16      # LoRA のランク。小さいほどパラメータ少・精度低
LORA_ALPHA   = 32      # LoRA のスケール係数。通常は rank * 2
LORA_DROPOUT = 0.05

MAX_SEQ_LEN  = 512
BATCH_SIZE   = 4       # GPU VRAM に合わせて調整
GRAD_ACCUM   = 4       # 実効バッチサイズ = BATCH_SIZE * GRAD_ACCUM = 16
LEARNING_RATE= 2e-4
NUM_EPOCHS   = 1
WARMUP_RATIO = 0.03
MAX_STEPS    = 200     # デモ用に短縮。本格的な学習は -1（エポック数で制御）


def format_instruction(sample: dict) -> str:
    """Alpaca 形式のプロンプトテンプレート"""
    instruction = sample.get("instruction", "")
    context     = sample.get("context", "")
    response    = sample.get("response", "")

    if context:
        return (
            f"### 指示:\n{instruction}\n\n"
            f"### 文脈:\n{context}\n\n"
            f"### 回答:\n{response}"
        )
    return (
        f"### 指示:\n{instruction}\n\n"
        f"### 回答:\n{response}"
    )


def main():
    print("=" * 60)
    print("SFT 学習スクリプト開始")
    print(f"  モデル    : {MODEL_NAME}")
    print(f"  データセット: {DATASET_NAME}")
    print(f"  LoRA rank : {LORA_RANK}  alpha: {LORA_ALPHA}")
    print(f"  出力先    : {OUTPUT_DIR}")
    print("=" * 60)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n使用デバイス: {device}")
    if device == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

    # ── 量子化設定（4bit QLoRA）────────────────────────────────────────
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )

    # ── モデル読み込み ──────────────────────────────────────────────────
    print("\nモデルを読み込み中...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=bnb_config if device == "cuda" else None,
        device_map="auto" if device == "cuda" else None,
        torch_dtype=torch.bfloat16 if device == "cuda" else torch.float32,
        trust_remote_code=True,
    )

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    # ── LoRA 設定 ──────────────────────────────────────────────────────
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=LORA_RANK,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        bias="none",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # ── データセット読み込み ────────────────────────────────────────────
    print("\nデータセットを読み込み中...")
    dataset = load_dataset(DATASET_NAME, split="train")
    dataset = dataset.map(
        lambda x: {"text": format_instruction(x)},
        remove_columns=dataset.column_names,
    )
    print(f"データ件数: {len(dataset)}")

    # ── 学習設定 ───────────────────────────────────────────────────────
    training_args = SFTConfig(
        output_dir=OUTPUT_DIR,
        num_train_epochs=NUM_EPOCHS,
        max_steps=MAX_STEPS,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM,
        learning_rate=LEARNING_RATE,
        warmup_ratio=WARMUP_RATIO,
        lr_scheduler_type="cosine",
        bf16=device == "cuda",
        fp16=False,
        logging_steps=10,
        save_steps=50,
        save_total_limit=2,
        report_to="wandb",
        run_name=f"sft-rank{LORA_RANK}-alpha{LORA_ALPHA}",
        max_seq_length=MAX_SEQ_LEN,
        dataset_text_field="text",
    )

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        tokenizer=tokenizer,
    )

    # ── 学習実行 ───────────────────────────────────────────────────────
    print("\n学習を開始します...")
    print("wandb でログを確認: https://wandb.ai/\n")
    trainer.train()

    # ── 保存 ──────────────────────────────────────────────────────────
    print("\nアダプタを保存中...")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print(f"保存完了: {OUTPUT_DIR}")

    print("\n学習完了！")
    print(f"次のステップ: ch2_04_evaluation.ipynb でモデルを評価してください")


if __name__ == "__main__":
    main()
