"""本物と同じ repo_id で、ランダム重みの小さなモデルを HF キャッシュの形で作る（API 検証用）。"""
import json, os, shutil, sys, hashlib
from pathlib import Path

HF_HOME = Path(sys.argv[1]).resolve()
HUB = HF_HOME / "hub"

def place(repo_id, src_dir, kind="models"):
    d = HUB / f"{kind}--{repo_id.replace('/', '--')}"
    sha = hashlib.sha1(repo_id.encode()).hexdigest()
    snap = d / "snapshots" / sha
    if d.exists():
        shutil.rmtree(d)
    snap.mkdir(parents=True)
    (d / "refs").mkdir()
    (d / "refs" / "main").write_text(sha)
    for f in Path(src_dir).iterdir():
        shutil.copy(f, snap / f.name)
    print("placed", repo_id)

from tokenizers import Tokenizer, models, pre_tokenizers, trainers, decoders
from transformers import (PreTrainedTokenizerFast, LlamaConfig, LlamaForCausalLM,
                          BertConfig, BertModel, BertTokenizerFast)
import torch

tmp = HF_HOME / "_build"
shutil.rmtree(tmp, ignore_errors=True); tmp.mkdir(parents=True)

# 学習用コーパス: リポジトリの日本語文書
repo = Path(__file__).resolve().parents[2]
corpus = [p.read_text() for p in list((repo / "docs").glob("*.md")) + list((repo / "design").glob("*.md"))]

# --- Llama 風トークナイザ（byte-level BPE）---
tok = Tokenizer(models.BPE())
tok.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
tok.decoder = decoders.ByteLevel()
specials = ["<|begin_of_text|>", "<|end_of_text|>", "<|start_header_id|>", "<|end_header_id|>", "<|eot_id|>"]
tok.train_from_iterator(corpus, trainers.BpeTrainer(vocab_size=2000, special_tokens=specials,
                        initial_alphabet=pre_tokenizers.ByteLevel.alphabet()))
chat_template = (
    "{{ bos_token }}{% for m in messages %}<|start_header_id|>{{ m['role'] }}<|end_header_id|>\n\n"
    "{{ m['content'] }}<|eot_id|>{% endfor %}"
    "{% if add_generation_prompt %}<|start_header_id|>assistant<|end_header_id|>\n\n{% endif %}")
ptok = PreTrainedTokenizerFast(tokenizer_object=tok, bos_token="<|begin_of_text|>",
                               eos_token="<|end_of_text|>")
ptok.chat_template = chat_template
for rid, eos in [("meta-llama/Llama-3.2-1B-Instruct", "<|eot_id|>"), ("meta-llama/Meta-Llama-3-8B", "<|end_of_text|>")]:
    out = tmp / rid.replace("/", "_"); out.mkdir()
    ptok.eos_token = eos
    if rid.endswith("8B"):
        ptok.chat_template = None
    ptok.save_pretrained(out)
    torch.manual_seed(0)
    cfg = LlamaConfig(vocab_size=len(ptok), hidden_size=64, intermediate_size=128, num_hidden_layers=2,
                      num_attention_heads=4, num_key_value_heads=2, max_position_embeddings=2048,
                      bos_token_id=ptok.bos_token_id, eos_token_id=ptok.convert_tokens_to_ids(eos))
    LlamaForCausalLM(cfg).save_pretrained(out)
    place(rid, out)
    ptok.chat_template = chat_template

# --- BERT 系（埋め込み・BERTScore）---
wp = Tokenizer(models.WordPiece(unk_token="[UNK]"))
wp.pre_tokenizer = pre_tokenizers.BertPreTokenizer()
wp.train_from_iterator(corpus, trainers.WordPieceTrainer(vocab_size=3000,
                       special_tokens=["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"]))
btok = BertTokenizerFast(tokenizer_object=wp, unk_token="[UNK]", pad_token="[PAD]", cls_token="[CLS]",
                         sep_token="[SEP]", mask_token="[MASK]", model_max_length=512)
for rid, layers in [("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", 2),
                    ("sentence-transformers/all-MiniLM-L6-v2", 2),
                    ("bert-base-multilingual-cased", 12)]:
    out = tmp / rid.replace("/", "_"); out.mkdir()
    btok.save_pretrained(out)
    torch.manual_seed(1)
    BertModel(BertConfig(vocab_size=len(btok), hidden_size=32, num_hidden_layers=layers,
                         num_attention_heads=2, intermediate_size=64)).save_pretrained(out)
    if rid.startswith("sentence-transformers"):
        (out / "modules.json").write_text(json.dumps([
            {"idx": 0, "name": "0", "path": "", "type": "sentence_transformers.models.Transformer"},
            {"idx": 1, "name": "1", "path": "1_Pooling", "type": "sentence_transformers.models.Pooling"}]))
        (out / "sentence_bert_config.json").write_text(json.dumps({"max_seq_length": 128, "do_lower_case": False}))
        place(rid, out)
        pool = HUB / f"models--{rid.replace('/', '--')}" / "snapshots"
        snap = next(pool.iterdir()) / "1_Pooling"; snap.mkdir()
        (snap / "config.json").write_text(json.dumps({"word_embedding_dimension": 32, "pooling_mode_mean_tokens": True}))
    else:
        place(rid, out)
# --- dolly-15k-ja の代わりの JSON（ipython_fake_dolly.py が読む）---
import random
rid = "kunishou/databricks-dolly-15k-ja"
d = HUB / ("datasets--" + rid.replace("/", "--")); sha = hashlib.sha1(rid.encode()).hexdigest()
snap = d / "snapshots" / sha; snap.mkdir(parents=True, exist_ok=True); (d / "refs").mkdir(exist_ok=True); (d / "refs" / "main").write_text(sha)
random.seed(0); cats = ["open_qa", "closed_qa", "summarization", "brainstorming", "general_qa"]
rows = [{"output": f"回答{i}です。" * random.randint(1, 30), "index": str(i), "category": (c := random.choice(cats)),
         "input": ("文脈" * random.randint(5, 50)) if c in ("closed_qa", "summarization") else "",
         "instruction": f"質問{i}について教えてください。"} for i in range(300)]
(snap / "databricks-dolly-15k-ja.json").write_text(json.dumps(rows, ensure_ascii=False))
print("placed", rid)
shutil.rmtree(tmp)
