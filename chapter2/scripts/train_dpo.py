#!/usr/bin/env python3
"""
第2章 DPO 学習スクリプト
SFT 済みのアダプタに、DPOTrainer で好みのデータを学習させる（ch2_02_dpo.ipynb と同じ処理）

使用方法（JupyterLab のターミナルで、自分の作業ディレクトリ直下から）:
  gpu_queue.sh python chapter2/scripts/train_dpo.py --beta 0.1 --max-steps 60

  gpu_queue.sh は同時に走る学習の本数を制限する（ノートブックの gpu_slot() と同じ枠）。
  枠が埋まっていれば空くまで待つ。ターミナルのプロセスはサーバー側で動くので、
  ブラウザを閉じたり SSH が切れたりしても学習は続く（JupyterLab が止まらない限り）。

入力:
  --sft-dir    SFT のアダプタ（既定 chapter2/outputs/sft_lora_r16。なければベースモデルに新しい LoRA を付ける）
  --data       好みのデータ（既定 chapter2/data/dpo_preference.json。prompt・chosen・rejected のリスト）

出力（chapter2/outputs/dpo_lora_beta{beta}/）:
  adapter_model.safetensors など  学習した LoRA アダプタ（ch2_04 で読み込める）
  log_history.json                 損失・報酬などの学習ログ

環境変数:
  HF_HOME   HuggingFace キャッシュパス（当日は運営側で設定済み）
"""

import argparse
import json
from pathlib import Path

import torch
from datasets import Dataset
from peft import LoraConfig, PeftModel, get_peft_model, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from trl import DPOConfig, DPOTrainer

MODEL_NAME = "meta-llama/Meta-Llama-3-8B"
CH2_DIR = Path(__file__).resolve().parent.parent
OUTPUT_ROOT = CH2_DIR / "outputs"


def parse_args():
    p = argparse.ArgumentParser(description="SFT 済みのアダプタに DPO をかける")
    p.add_argument("--sft-dir", type=Path, default=OUTPUT_ROOT / "sft_lora_r16", help="SFT のアダプタ")
    p.add_argument("--data", type=Path, default=CH2_DIR / "data" / "dpo_preference.json", help="好みのデータ（JSON）")
    p.add_argument("--beta", type=float, default=0.1, help="参照モデルから離れすぎないためのブレーキ（既定 0.1）")
    p.add_argument("--max-steps", type=int, default=60, help="重みを更新する回数（既定 60）")
    p.add_argument("--lr", type=float, default=5e-5, help="学習率（既定 5e-5）")
    p.add_argument("--output-dir", type=Path, default=None, help="保存先（既定 chapter2/outputs/dpo_lora_beta{beta}）")
    return p.parse_args()


def main():
    args = parse_args()
    output_dir = args.output_dir or OUTPUT_ROOT / f"dpo_lora_beta{args.beta}"

    records = json.loads(args.data.read_text(encoding="utf-8"))
    dataset = Dataset.from_list(records)

    print("=" * 60)
    print("DPO 学習スクリプト")
    print(f"  モデル       : {MODEL_NAME}")
    print(f"  SFT アダプタ : {args.sft_dir}")
    print(f"  好みのデータ : {args.data}（{len(dataset)} 組）")
    print(f"  beta         : {args.beta}  更新回数: {args.max_steps}  学習率: {args.lr}")
    print(f"  保存先       : {output_dir}")
    print("=" * 60)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cpu":
        print("⚠️  GPU が見つかりません。8B モデルの学習には GPU が必要です")

    # ── モデル（4bit + SFT のアダプタ）────────────────────────────────
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, clean_up_tokenization_spaces=False)
    tokenizer.pad_token = tokenizer.eos_token
    if device == "cuda":
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
        )
        base = AutoModelForCausalLM.from_pretrained(MODEL_NAME, quantization_config=bnb_config, device_map="auto")
        base = prepare_model_for_kbit_training(base)
    else:
        base = AutoModelForCausalLM.from_pretrained(MODEL_NAME, dtype=torch.float32)

    if (args.sft_dir / "adapter_config.json").exists():
        # 参照モデルには、DPOTrainer がこのアダプタのコピー（ref）を作って使う
        model = PeftModel.from_pretrained(base, args.sft_dir, is_trainable=True)
    else:
        print(f"⚠️  {args.sft_dir} が見つからないため、ベースモデルに新しい LoRA を付けます（参照モデルはベースモデル）")
        model = get_peft_model(base, LoraConfig(
            task_type="CAUSAL_LM", r=16, lora_alpha=32, lora_dropout=0.05, bias="none",
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        ))
    model.print_trainable_parameters()

    # ── 学習 ───────────────────────────────────────────────────────────
    trainer = DPOTrainer(
        model=model,
        args=DPOConfig(
            output_dir=str(output_dir / "checkpoints"),
            beta=args.beta,
            max_steps=args.max_steps,
            per_device_train_batch_size=2,
            gradient_accumulation_steps=2,
            learning_rate=args.lr,
            lr_scheduler_type="cosine",
            warmup_steps=0.1,
            max_length=512,
            gradient_checkpointing=True,
            bf16=device == "cuda",
            logging_steps=5,
            save_strategy="no",
            report_to="none",    # 当日はオフライン。ログは log_history.json に保存する
        ),
        train_dataset=dataset,
        processing_class=tokenizer,
    )
    print("\n学習を始めます...")
    trainer.train()

    # ── 保存（参照モデル用のコピー ref は保存しない）──────────────────
    model.save_pretrained(output_dir, selected_adapters=["default"])
    tokenizer.save_pretrained(output_dir)
    (output_dir / "log_history.json").write_text(json.dumps(trainer.state.log_history, indent=1))
    print(f"\n保存しました: {output_dir}")
    print(f"{'step':>5} {'loss':>7} {'margin':>8} {'正解率':>6}")
    for h in trainer.state.log_history:
        if "rewards/margins" in h:
            print(f"{h['step']:>5} {h['loss']:>7.3f} {h['rewards/margins']:>+8.3f} {h['rewards/accuracies']:>6.2f}")


if __name__ == "__main__":
    main()
