#!/usr/bin/env python3
"""
第2章 SFT 学習スクリプト
Llama 3 8B + QLoRA + SFTTrainer による教師ありファインチューニング（ch2_01_sft.ipynb と同じ処理）

使用方法（JupyterLab のターミナルで、自分の作業ディレクトリ直下から）:
  gpu_queue.sh python chapter2/scripts/train_sft.py --rank 16 --max-steps 300

  gpu_queue.sh は同時に走る学習の本数を制限する（ノートブックの gpu_slot() と同じ枠）。
  枠が埋まっていれば空くまで待つ。ターミナルのプロセスはサーバー側で動くので、
  ブラウザを閉じたり SSH が切れたりしても学習は続く（JupyterLab が止まらない限り）。

出力（chapter2/outputs/sft_lora_r{rank}/）:
  adapter_model.safetensors など  学習した LoRA アダプタ（ch2_02・ch2_04 で読み込む）
  log_history.json                 損失などの学習ログ

環境変数:
  HF_HOME   HuggingFace キャッシュパス（当日は運営側で設定済み）
"""

import argparse
import json
from pathlib import Path

import torch
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from trl import SFTConfig, SFTTrainer

MODEL_NAME = "meta-llama/Meta-Llama-3-8B"
DATASET_NAME = "kunishou/databricks-dolly-15k-ja"
OUTPUT_ROOT = Path(__file__).resolve().parent.parent / "outputs"
TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]


def to_prompt_completion(sample: dict) -> dict:
    """1 件のデータを、プロンプト（指示と文脈）と完成させる部分（回答）の組にする"""
    instruction = sample["instruction"]
    context = sample.get("input") or sample.get("context") or ""   # 列名がデータセットの版で違うことがあるため両方見る
    response = sample.get("output") or sample.get("response") or ""
    prompt = f"### 指示:\n{instruction}\n\n"
    if context:
        prompt += f"### 文脈:\n{context}\n\n"
    prompt += "### 回答:\n"
    return {"prompt": prompt, "completion": response}


def parse_args():
    p = argparse.ArgumentParser(description="Llama 3 8B を QLoRA で SFT する")
    p.add_argument("--rank", type=int, default=16, help="LoRA の rank（既定 16）")
    p.add_argument("--alpha", type=int, default=None, help="LoRA の alpha（既定 rank の 2 倍）")
    p.add_argument("--max-steps", type=int, default=300, help="重みを更新する回数（既定 300）")
    p.add_argument("--n-train", type=int, default=10000, help="学習に使う件数（既定 10000）")
    p.add_argument("--lr", type=float, default=2e-4, help="学習率（既定 2e-4）")
    p.add_argument("--output-dir", type=Path, default=None, help="保存先（既定 chapter2/outputs/sft_lora_r{rank}）")
    return p.parse_args()


def main():
    args = parse_args()
    alpha = args.alpha or args.rank * 2
    output_dir = args.output_dir or OUTPUT_ROOT / f"sft_lora_r{args.rank}"

    print("=" * 60)
    print("SFT 学習スクリプト")
    print(f"  モデル       : {MODEL_NAME}")
    print(f"  データセット : {DATASET_NAME}（{args.n_train} 件まで）")
    print(f"  LoRA         : rank={args.rank}  alpha={alpha}")
    print(f"  更新回数     : {args.max_steps}  学習率: {args.lr}")
    print(f"  保存先       : {output_dir}")
    print("=" * 60)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cpu":
        print("⚠️  GPU が見つかりません。8B モデルの学習には GPU が必要です")

    # ── モデル（4bit QLoRA）────────────────────────────────────────────
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, clean_up_tokenization_spaces=False)
    tokenizer.pad_token = tokenizer.eos_token
    if device == "cuda":
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
        )
        model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, quantization_config=bnb_config, device_map="auto")
        model = prepare_model_for_kbit_training(model)
    else:
        model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, dtype=torch.float32)

    model = get_peft_model(model, LoraConfig(
        task_type="CAUSAL_LM",
        r=args.rank,
        lora_alpha=alpha,
        lora_dropout=0.05,
        target_modules=TARGET_MODULES,
        bias="none",
    ))
    model.print_trainable_parameters()

    # ── データ ─────────────────────────────────────────────────────────
    raw = load_dataset(DATASET_NAME, split="train")
    dataset = raw.map(to_prompt_completion, remove_columns=raw.column_names)
    dataset = dataset.filter(lambda x: x["completion"] and len(x["prompt"]) + len(x["completion"]) < 1000)
    dataset = dataset.shuffle(seed=42).select(range(min(args.n_train, len(dataset))))
    print(f"学習に使う件数: {len(dataset)}")

    # ── 学習 ───────────────────────────────────────────────────────────
    trainer = SFTTrainer(
        model=model,
        args=SFTConfig(
            output_dir=str(output_dir / "checkpoints"),
            max_steps=args.max_steps,
            per_device_train_batch_size=4,
            gradient_accumulation_steps=4,
            learning_rate=args.lr,
            lr_scheduler_type="cosine",
            warmup_steps=0.05,
            max_length=512,
            gradient_checkpointing=True,
            bf16=device == "cuda",
            logging_steps=10,
            save_strategy="steps",
            save_steps=100,
            save_total_limit=1,    # ディスクを節約するため、途中経過は最新の 1 つだけ残す
            report_to="none",      # 当日はオフライン。ログは log_history.json に保存する
        ),
        train_dataset=dataset,
        processing_class=tokenizer,
    )
    print("\n学習を始めます...")
    trainer.train()

    # ── 保存 ───────────────────────────────────────────────────────────
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    (output_dir / "log_history.json").write_text(json.dumps(trainer.state.log_history, indent=1))
    print(f"\n保存しました: {output_dir}")
    print("損失の推移:")
    for h in trainer.state.log_history:
        if "loss" in h:
            print(f"  step {h['step']:>4}: loss {h['loss']:.3f}")


if __name__ == "__main__":
    main()
