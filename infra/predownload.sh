#!/usr/bin/env bash
# =============================================================================
# predownload.sh  —  モデル・データセットの事前ダウンロードスクリプト
#
# 使い方:
#   cd /home/chinchilla/pjt/sbcs-work/dgx-handson
#   source .venv/bin/activate
#   bash infra/predownload.sh
#
# ダウンロードするもの:
#   - MNIST データセット（torchvision 経由）
#   - meta-llama/Llama-3.2-1B-Instruct（HuggingFace Hub）
#
# 保存先（優先順）:
#   1. /data/shared/  が存在する場合 → 共有ストレージに保存（全ユーザーが共有）
#   2. それ以外 → ~/.cache/huggingface / ./data に保存
#
# 事前条件:
#   - setup.sh によるパッケージインストール済み
#   - Llama モデルは HuggingFace のアクセス許可が必要:
#       huggingface-cli login  （または HF_TOKEN 環境変数）
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

# 仮想環境の Python
VENV_PYTHON="${REPO_ROOT}/.venv/bin/python"
if [ ! -f "${VENV_PYTHON}" ]; then
  error ".venv が見つかりません。先に setup.sh を実行してください。"
  exit 1
fi

# =============================================================================
# Step 1: 保存先の決定
# =============================================================================
section "Step 1: 保存先の決定"

SHARED_ROOT="/data/shared"
if [ -d "${SHARED_ROOT}" ]; then
  DATA_DIR="${SHARED_ROOT}/datasets"
  HF_HOME="${SHARED_ROOT}/models"
  info "共有ストレージを使用します: ${SHARED_ROOT}"
  mkdir -p "${DATA_DIR}" "${HF_HOME}"
  # HuggingFace キャッシュを共有ストレージに向ける
  export HF_HOME="${HF_HOME}"
  info "HF_HOME=${HF_HOME}"
  info "DATA_DIR=${DATA_DIR}"

  # 共有ストレージの空き容量確認
  AVAIL_GB=$(df -BG "${SHARED_ROOT}" | awk 'NR==2{gsub("G",""); print $4}')
  info "共有ストレージの空き容量: ${AVAIL_GB} GB"
  if [ "${AVAIL_GB}" -lt 10 ]; then
    warn "空き容量が 10 GB 未満です。ダウンロードに失敗する可能性があります。"
  fi
else
  DATA_DIR="${REPO_ROOT}/data"
  HF_HOME="${HOME}/.cache/huggingface"
  warn "共有ストレージ (${SHARED_ROOT}) が見つかりません。ローカルに保存します。"
  info "DATA_DIR=${DATA_DIR}"
  info "HF_HOME=${HF_HOME}"
  mkdir -p "${DATA_DIR}"
fi

# =============================================================================
# Step 2: MNIST データセット
# =============================================================================
section "Step 2: MNIST データセットのダウンロード"

"${VENV_PYTHON}" - <<PYEOF
import sys, os
sys.stdout.reconfigure(line_buffering=True)

data_dir = "${DATA_DIR}"
print(f"  保存先: {data_dir}")

try:
    from torchvision import datasets, transforms

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])

    print("  訓練データをダウンロード中...")
    datasets.MNIST(root=data_dir, train=True,  download=True, transform=transform)
    print("  テストデータをダウンロード中...")
    datasets.MNIST(root=data_dir, train=False, download=True, transform=transform)
    print("  MNIST ダウンロード完了")

    # サイズ確認
    import os
    mnist_dir = os.path.join(data_dir, "MNIST")
    if os.path.exists(mnist_dir):
        total = sum(
            os.path.getsize(os.path.join(dp, f))
            for dp, _, fns in os.walk(mnist_dir)
            for f in fns
        )
        print(f"  MNIST サイズ: {total / 1024 / 1024:.1f} MB")

except Exception as e:
    print(f"  MNIST ダウンロード失敗: {e}", file=sys.stderr)
    sys.exit(1)
PYEOF

# =============================================================================
# Step 3: HuggingFace ログイン確認
# =============================================================================
section "Step 3: HuggingFace ログイン確認"

HF_LOGGED_IN=false

if [ -n "${HF_TOKEN:-}" ]; then
  info "HF_TOKEN 環境変数が設定されています"
  HF_LOGGED_IN=true
elif "${VENV_PYTHON}" -c "
from huggingface_hub import whoami
try:
    info = whoami()
    print(f'  ログイン済み: {info[\"name\"]}')
    exit(0)
except:
    exit(1)
" 2>/dev/null; then
  HF_LOGGED_IN=true
else
  warn "HuggingFace にログインしていません。"
  warn "Llama モデルのダウンロードには認証が必要です。"
  echo ""
  echo "  以下のいずれかでログインしてください:"
  echo ""
  echo "    方法 1: .venv/bin/hf auth login"
  echo "    方法 2: export HF_TOKEN=hf_xxxxxxxxxxxx  (アクセストークン)"
  echo ""
  echo "  また、以下の URL でモデルへのアクセス申請が必要です:"
  echo "    https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct"
  echo ""
  read -rp "  ログインせずに続行しますか？Llama のダウンロードはスキップされます。[y/N]: " CONTINUE
  if [[ ! "${CONTINUE}" =~ ^[Yy]$ ]]; then
    info "スクリプトを終了します。ログイン後に再実行してください。"
    exit 0
  fi
fi

# =============================================================================
# Step 4: Llama-3.2-1B-Instruct のダウンロード
# =============================================================================
section "Step 4: meta-llama/Llama-3.2-1B-Instruct のダウンロード"

MODEL_NAME="meta-llama/Llama-3.2-1B-Instruct"

if [ "${HF_LOGGED_IN}" = "false" ]; then
  warn "HuggingFace 未ログインのためスキップします"
else
  info "モデルのダウンロードを開始します（初回: 約 2.5 GB）..."
  info "HF_HOME: ${HF_HOME}"

  "${VENV_PYTHON}" - <<PYEOF
import sys, os
sys.stdout.reconfigure(line_buffering=True)

os.environ["HF_HOME"] = "${HF_HOME}"
model_name = "${MODEL_NAME}"
print(f"  モデル: {model_name}")

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch

    print("  トークナイザーをダウンロード中...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    print(f"  トークナイザー完了 (語彙サイズ: {tokenizer.vocab_size:,})")

    print("  モデルをダウンロード中（時間がかかります）...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
    )
    params = sum(p.numel() for p in model.parameters())
    print(f"  モデル完了 (パラメータ数: {params / 1e9:.2f}B)")

    # キャッシュサイズ確認
    cache_dir = os.path.join("${HF_HOME}", "hub")
    if os.path.exists(cache_dir):
        total = sum(
            os.path.getsize(os.path.join(dp, f))
            for dp, _, fns in os.walk(cache_dir)
            for f in fns
        )
        print(f"  HF キャッシュ合計: {total / 1024 / 1024 / 1024:.2f} GB")

except Exception as e:
    print(f"  モデルダウンロード失敗: {e}", file=sys.stderr)
    print("  アクセス権限がない場合は以下を確認してください:", file=sys.stderr)
    print("    https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct", file=sys.stderr)
    sys.exit(1)
PYEOF
fi

# =============================================================================
# 完了メッセージ
# =============================================================================
echo ""
echo -e "${BOLD}${GREEN}════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}${GREEN}  事前ダウンロード完了！${RESET}"
echo -e "${BOLD}${GREEN}════════════════════════════════════════════════════${RESET}"
echo ""
echo -e "  ダウンロードしたデータ:"
echo -e "    MNIST データセット  → ${DATA_DIR}"
if [ "${HF_LOGGED_IN}" = "true" ]; then
echo -e "    Llama-3.2-1B-Instruct → ${HF_HOME}"
fi
echo ""
echo -e "  環境確認:"
echo -e "    ${GREEN}python infra/check_env.py${RESET}"
echo ""
