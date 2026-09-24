#!/usr/bin/env bash
# =============================================================================
# predownload.sh  —  モデル・データセットの事前ダウンロードスクリプト（運営者が実行）
#
# 使い方:
#   cd ~/dgx-handson
#   export HF_TOKEN=hf_xxxx      # Llama（gated モデル）の取得に必要
#   bash infra/predownload.sh
#
# ハンズオン当日、参加者の JupyterLab は HF_HUB_OFFLINE=1 で動く（handson.sh）。
# つまり「ここでダウンロードしたものだけが使える」。取得対象の一覧は
# infra/required_assets.py にあり、教材で新しいモデルやデータセットを使うときはそこに追加する。
#
# 保存先:
#   HuggingFace  → ${HF_HOME:-~/.cache/huggingface}（全参加者で共有）
#   MNIST        → <リポジトリ>/data（handson.sh が HANDSON_DATA_DIR で参加者に渡す）
#
# Llama は事前に HuggingFace でアクセス申請が必要:
#   https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct
#   https://huggingface.co/meta-llama/Meta-Llama-3-8B
# =============================================================================

set -euo pipefail

GREEN='\033[0;32m'
AMBER='\033[0;33m'
RED='\033[0;31m'
RESET='\033[0m'
BOLD='\033[1m'

info()    { echo -e "${GREEN}[INFO]${RESET}  $*"; }
warn()    { echo -e "${AMBER}[WARN]${RESET}  $*"; }
error()   { echo -e "${RED}[ERROR]${RESET} $*"; }
section() { echo -e "\n${BOLD}${GREEN}── $* ──────────────────────────────────────${RESET}"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

VENV_PYTHON="${REPO_ROOT}/.venv/bin/python"
if [ ! -f "${VENV_PYTHON}" ]; then
  error ".venv が見つかりません。先に setup.sh を実行してください。"
  exit 1
fi

export HF_HOME="${HF_HOME:-${HOME}/.cache/huggingface}"
export HF_HUB_OFFLINE=0
DATA_DIR="${REPO_ROOT}/data"

section "保存先"
info "HF_HOME=${HF_HOME}"
info "DATA_DIR=${DATA_DIR}"
AVAIL_GB=$(df -BG "${HOME}" | awk 'NR==2{gsub("G",""); print $4}')
info "空き容量: ${AVAIL_GB} GB（必要量の目安: 約 25 GB）"

section "ダウンロード"
"${VENV_PYTHON}" - "${DATA_DIR}" "${SCRIPT_DIR}" <<'PYEOF'
import sys
sys.stdout.reconfigure(line_buffering=True)
data_dir = sys.argv[1]
sys.path.insert(0, sys.argv[2])
from required_assets import MODELS, DATASETS, cached_model_path

failed = []

print("  MNIST（第1章）...")
try:
    from torchvision import datasets
    datasets.MNIST(root=data_dir, train=True,  download=True)
    datasets.MNIST(root=data_dir, train=False, download=True)
    print("    ✓ MNIST")
except Exception as e:
    print(f"    ✗ MNIST: {e}")
    failed.append("MNIST")

from huggingface_hub import snapshot_download
# 重みは safetensors のみ取得（.bin / .pth / onnx などの重複を避ける）
IGNORE = ["*.bin", "*.pth", "*.h5", "*.msgpack", "*.onnx", "*.ot", "original/*", "onnx/*", "openvino/*"]

for repo_id, purpose, gated in MODELS:
    print(f"  {repo_id}（{purpose}）...")
    if cached_model_path(repo_id):
        print("    ✓ キャッシュ済み")
        continue
    try:
        path = snapshot_download(repo_id, ignore_patterns=IGNORE)
        print(f"    ✓ {path}")
    except Exception as e:
        if gated:
            print(f"    ✗ {type(e).__name__}: {str(e)[:120]}（アクセス申請と HF_TOKEN を確認）")
            failed.append(repo_id)
            continue
        # 旧名のリポジトリ（bert-base-multilingual-cased など）は snapshot_download が
        # 失敗することがあるため、教材と同じ transformers 経由で取得する
        try:
            from transformers import AutoModel, AutoTokenizer
            AutoTokenizer.from_pretrained(repo_id)
            AutoModel.from_pretrained(repo_id)
            print("    ✓ transformers 経由で取得")
        except Exception as e2:
            print(f"    ✗ {type(e2).__name__}: {str(e2)[:200]}")
            failed.append(repo_id)

from datasets import load_dataset
for name, split, purpose in DATASETS:
    print(f"  {name}（{purpose}）...")
    try:
        ds = load_dataset(name, split=split)
        print(f"    ✓ {len(ds):,} 件")
    except Exception as e:
        print(f"    ✗ {type(e).__name__}: {str(e)[:200]}")
        failed.append(name)

if failed:
    print("\n  取得できなかったもの:")
    for f in failed:
        print(f"    - {f}")
    sys.exit(1)
PYEOF

echo ""
info "完了。オフラインで読み込めるかは次で確認できます:"
echo -e "    ${GREEN}.venv/bin/python infra/check_env.py${RESET}"
