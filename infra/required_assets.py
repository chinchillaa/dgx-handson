"""ハンズオンで使うモデル・データセットの一覧（predownload.sh と check_env.py が参照する）。

当日の参加者環境は HF_HUB_OFFLINE=1 で動くため、教材で新しいモデルや
データセットを使うときは必ずここに追加し、predownload.sh を再実行すること。
"""

import json
import os

# (repo_id, 用途, gated か)
MODELS = [
    ("meta-llama/Llama-3.2-1B-Instruct",       "第1章 LLM 推論",        True),
    ("meta-llama/Meta-Llama-3-8B",             "第2章 SFT / DPO / 評価", True),
    ("sentence-transformers/all-MiniLM-L6-v2", "第2章 RAG 埋め込み",    False),
    ("bert-base-multilingual-cased",           "第2章 BERTScore",       False),
]

# (name, split, 用途)
DATASETS = [
    ("kunishou/databricks-dolly-15k-ja", "train", "第2章 SFT"),
]


def weights_complete(path: str) -> bool:
    """スナップショットに safetensors の重みが全シャード揃っているか。"""
    index = os.path.join(path, "model.safetensors.index.json")
    if os.path.exists(index):
        with open(index) as f:
            shards = set(json.load(f)["weight_map"].values())
        return all(os.path.exists(os.path.join(path, s)) for s in shards)
    return os.path.exists(os.path.join(path, "model.safetensors"))


def cached_model_path(repo_id: str):
    """オフラインで読み込めるならスナップショットのパス、読めないなら None。"""
    # snapshot_download(local_files_only=True) は、使わない onnx / .bin まで揃っていないと
    # IncompleteSnapshotError になるため、config.json の位置からスナップショットを特定する
    from huggingface_hub import try_to_load_from_cache

    config = try_to_load_from_cache(repo_id, "config.json")
    if not isinstance(config, str):
        return None
    path = os.path.dirname(config)
    return path if weights_complete(path) else None
