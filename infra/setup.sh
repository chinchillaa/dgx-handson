#!/usr/bin/env bash
# =============================================================================
# setup.sh  —  DGX ハンズオン環境構築スクリプト
#
# 使い方:
#   cd /home/chinchilla/pjt/sbcs-work/dgx-handson
#   bash infra/setup.sh
#
# 実行すること:
#   1. uv の存在確認（未インストールの場合は案内を表示）
#   2. Python 仮想環境 .venv の作成
#   3. requirements.txt からパッケージをインストール
#   4. Jupyter カーネルの登録
#   5. 日本語フォント（IPAexGothic）のインストール確認
# =============================================================================

set -euo pipefail

# ── カラー出力 ──────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
AMBER='\033[0;33m'
RED='\033[0;31m'
RESET='\033[0m'
BOLD='\033[1m'

info()    { echo -e "${GREEN}[INFO]${RESET}  $*"; }
warn()    { echo -e "${AMBER}[WARN]${RESET}  $*"; }
error()   { echo -e "${RED}[ERROR]${RESET} $*"; }
section() { echo -e "\n${BOLD}${GREEN}── $* ──────────────────────────────────────${RESET}"; }

# ── スクリプトのルートをリポジトリ直下に固定 ───────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"
info "作業ディレクトリ: ${REPO_ROOT}"

# =============================================================================
# Step 1: uv の確認
# =============================================================================
section "Step 1: uv の確認"

if ! command -v uv &>/dev/null; then
  error "uv が見つかりません。以下のコマンドでインストールしてください:"
  echo ""
  echo "    curl -LsSf https://astral.sh/uv/install.sh | sh"
  echo "    source \$HOME/.cargo/env   # または新しいシェルを起動"
  echo ""
  exit 1
fi

UV_VERSION=$(uv --version)
info "uv バージョン: ${UV_VERSION}"

# =============================================================================
# Step 2: Python バージョン確認
# =============================================================================
section "Step 2: Python バージョン確認"

PYTHON_BIN=$(uv python find 3.10 2>/dev/null || uv python find 3.11 2>/dev/null || echo "")
if [ -z "${PYTHON_BIN}" ]; then
  warn "Python 3.10/3.11 が見つかりません。uv でインストールします..."
  uv python install 3.11
  PYTHON_BIN=$(uv python find 3.11)
fi
PYTHON_VERSION=$("${PYTHON_BIN}" --version)
info "使用する Python: ${PYTHON_BIN} (${PYTHON_VERSION})"

# =============================================================================
# Step 3: 仮想環境の作成
# =============================================================================
section "Step 3: 仮想環境の作成"

VENV_DIR="${REPO_ROOT}/.venv"

if [ -d "${VENV_DIR}" ]; then
  warn ".venv が既に存在します。スキップします。"
  warn "再作成する場合は 'rm -rf .venv' を実行してから再度このスクリプトを実行してください。"
else
  info ".venv を作成中..."
  uv venv "${VENV_DIR}" --python "${PYTHON_BIN}"
  info ".venv を作成しました: ${VENV_DIR}"
fi

# 仮想環境の Python パスを設定
VENV_PYTHON="${VENV_DIR}/bin/python"
VENV_PIP="${VENV_DIR}/bin/pip"

# =============================================================================
# Step 4: パッケージのインストール
# =============================================================================
section "Step 4: パッケージのインストール"

REQUIREMENTS="${REPO_ROOT}/requirements.txt"
if [ ! -f "${REQUIREMENTS}" ]; then
  error "requirements.txt が見つかりません: ${REQUIREMENTS}"
  exit 1
fi

info "パッケージをインストール中... (初回は数分かかります)"
uv pip install --python "${VENV_PYTHON}" -r "${REQUIREMENTS}"
info "パッケージのインストール完了"

# CUDA 対応の PyTorch が必要な場合（GPU が検出されたとき）
if command -v nvidia-smi &>/dev/null; then
  CUDA_VERSION=$(nvidia-smi | grep -oP 'CUDA Version: \K[0-9.]+' | head -1)
  info "CUDA ${CUDA_VERSION} を検出しました"
  # PyTorch が既に CUDA 対応でインストールされているか確認
  if "${VENV_PYTHON}" -c "import torch; assert torch.cuda.is_available(), 'no cuda'" 2>/dev/null; then
    info "PyTorch は CUDA 対応です"
  else
    warn "PyTorch が CPU 版の可能性があります。必要に応じて手動で再インストールしてください:"
    echo "    uv pip install --python .venv/bin/python torch torchvision \\"
    echo "        --index-url https://download.pytorch.org/whl/cu121"
  fi
fi

# =============================================================================
# Step 5: Jupyter カーネルの登録
# =============================================================================
section "Step 5: Jupyter カーネルの登録"

KERNEL_NAME="dgx-handson"
KERNEL_DISPLAY="DGX Hands-on (Python)"

if "${VENV_PYTHON}" -m ipykernel install --user --name "${KERNEL_NAME}" --display-name "${KERNEL_DISPLAY}" 2>/dev/null; then
  info "Jupyter カーネルを登録しました: '${KERNEL_DISPLAY}'"
  info "ノートブック起動時にカーネルとして '${KERNEL_DISPLAY}' を選択してください"
else
  warn "Jupyter カーネルの登録に失敗しました（ipykernel が未インストールの可能性があります）"
fi

# =============================================================================
# Step 6: 日本語フォントの確認
# =============================================================================
section "Step 6: 日本語フォントの確認"

if fc-list 2>/dev/null | grep -qi "ipagothic\|ipaexgothic\|ipa"; then
  info "IPA フォントが検出されました"
else
  warn "IPA フォントが見つかりません。matplotlib の日本語表示に必要です。"
  if command -v apt-get &>/dev/null; then
    echo ""
    echo "    sudo apt-get install -y fonts-ipafont"
    echo "    # インストール後、フォントキャッシュを更新"
    echo "    python -c \"import matplotlib; matplotlib.font_manager._rebuild()\""
  fi
fi

# =============================================================================
# 完了メッセージ
# =============================================================================
echo ""
echo -e "${BOLD}${GREEN}════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}${GREEN}  セットアップ完了！${RESET}"
echo -e "${BOLD}${GREEN}════════════════════════════════════════════════════${RESET}"
echo ""
echo -e "  仮想環境を有効化するには:"
echo -e "    ${GREEN}source .venv/bin/activate${RESET}"
echo ""
echo -e "  Jupyter Lab を起動するには:"
echo -e "    ${GREEN}source .venv/bin/activate && jupyter lab${RESET}"
echo ""
echo -e "  環境確認スクリプト:"
echo -e "    ${GREEN}python infra/check_env.py${RESET}"
echo ""
echo -e "  モデル・データ事前ダウンロード:"
echo -e "    ${GREEN}bash infra/predownload.sh${RESET}"
echo ""
