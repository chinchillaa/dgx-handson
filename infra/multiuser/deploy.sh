#!/usr/bin/env bash
# =============================================================================
# deploy.sh  —  教材・仮想環境・モデルを参加者用の共有ディレクトリに配置する（sudo 不要）
#
# 使い方（運営者のアカウントで、リポジトリ直下から）:
#   bash infra/multiuser/deploy.sh            # 教材・infra・MNIST を同期（初回は .venv とモデルも作る）
#   bash infra/multiuser/deploy.sh --venv     # .venv を作り直す（requirements やリポジトリの .venv を更新したとき）
#   HF_TOKEN=hf_xxx bash infra/multiuser/deploy.sh --models
#                                             # 足りないモデルを取得（infra/required_assets.py の一覧）
#
# 前提: sudo bash infra/multiuser/setup_account.sh 済み（/opt/handson が運営者のもの）
#
# 配置先（参加者用アカウント handson は読むだけ。書き換えられない）:
#   /opt/handson/app       教材（chapter*、solutions は除く）・assets・infra・data（MNIST）・.venv
#   /opt/handson/python    .venv が使う Python 本体
#   /opt/handson/hf_cache  モデル・データセット（HF_HOME）
#
# 教材を直したら再実行する。Web ページはすぐ反映される。ノートブックは
# 参加者のディレクトリにコピー済みなので、handson 側で handson.sh refresh が必要（開催前のみ）。
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
OPT="${HANDSON_OPT:-/opt/handson}"
APP="${OPT}/app"
PY_DIR="${OPT}/python"
HF_CACHE="${OPT}/hf_cache"
PY_VERSION="3.11"

GREEN='\033[0;32m'; AMBER='\033[0;33m'; RED='\033[0;31m'; RESET='\033[0m'; BOLD='\033[1m'
info() { echo -e "${GREEN}[INFO]${RESET}  $*"; }
warn() { echo -e "${AMBER}[WARN]${RESET}  $*"; }
error() { echo -e "${RED}[ERROR]${RESET} $*"; }
section() { echo -e "\n${BOLD}${GREEN}── $* ──────────────────────────────────────${RESET}"; }

if [ ! -w "${OPT}" ]; then
  error "${OPT} に書き込めません。先に sudo bash infra/multiuser/setup_account.sh を実行してください"
  exit 1
fi
command -v uv &>/dev/null || { error "uv が見つかりません"; exit 1; }

REBUILD_VENV=false; FETCH_MODELS=false
for arg in "$@"; do
  case "${arg}" in
    --venv) REBUILD_VENV=true ;;
    --models) FETCH_MODELS=true ;;
    *) error "不明なオプション: ${arg}"; exit 1 ;;
  esac
done

# 作るファイルは group 書き込みなし・other 権限なし（handson は読むだけ）
umask 027
# 所有グループは、setgid を付けた ${OPT} のグループ（handson）を引き継がせる。
#   - uv の既定はキャッシュからのハードリンクで、ファイルの所有グループが運営者のままになる → コピーにする
#   - rsync -a も元の所有グループを保つ → --no-group
export UV_LINK_MODE=copy
SHARED_GROUP="$(stat -c '%G' "${OPT}")"

# 運営者はグループ handson に属している必要がある（setup_account.sh が追加する）。
# 追加直後のシェルにはまだ反映されていないので、sg でグループを付けて実行し直す
if ! id -Gn | tr ' ' '\n' | grep -qx "${SHARED_GROUP}"; then
  if id -Gn "${USER}" | tr ' ' '\n' | grep -qx "${SHARED_GROUP}"; then
    exec sg "${SHARED_GROUP}" -c "$(printf '%q ' bash "$0" "$@")"
  fi
  error "${USER} がグループ ${SHARED_GROUP} に入っていません。sudo bash infra/multiuser/setup_account.sh を実行してください"
  exit 1
fi

# ── 教材・infra・MNIST ───────────────────────────────────────────────────────
section "教材・infra・MNIST → ${APP}"
mkdir -p "${APP}"
rsync -a --no-group --delete \
  --exclude='/.venv/' --exclude='.git/' --exclude='/design/' \
  --exclude='solutions/' --exclude='.ipynb_checkpoints/' --exclude='outputs/' --exclude='__pycache__/' \
  --include='/chapter1/***' --include='/chapter2/***' --include='/chapter3/***' \
  --include='/assets/***' --include='/infra/***' --include='/data/***' --include='/docs/***' \
  --include='/requirements.txt' --exclude='*' \
  "${REPO_ROOT}/" "${APP}/"
info "同期しました（solutions・design・.git は配置しません）"

# ── Python と .venv ──────────────────────────────────────────────────────────
if [ ! -x "${APP}/.venv/bin/python" ] || ${REBUILD_VENV}; then
  section "Python ${PY_VERSION} と .venv"
  # uv の既定の置き場所（~/.local/share/uv）は handson から読めないので、共有ディレクトリに入れる
  # --no-bin: ~/.local/bin に実行ファイルを置かない（運営者の環境を変えない）
  UV_PYTHON_INSTALL_DIR="${PY_DIR}" uv python install --no-bin "${PY_VERSION}"
  # uv python find はカレントの .venv を拾うことがあるので、共有ディレクトリから直接探す
  PYTHON_BIN="$(ls -d "${PY_DIR}"/cpython-"${PY_VERSION}".*/bin/python"${PY_VERSION}" 2>/dev/null | sort -V | tail -1)"
  case "${PYTHON_BIN}" in
    "${PY_DIR}"/*) info "Python: ${PYTHON_BIN}" ;;
    *) error "共有ディレクトリ外の Python が選ばれました: ${PYTHON_BIN}"; exit 1 ;;
  esac
  rm -rf "${APP}/.venv"
  uv venv --quiet "${APP}/.venv" --python "${PYTHON_BIN}"
  # リポジトリの .venv と同じバージョンをそのまま入れる（uv のキャッシュが効くので速い）
  LOCK="$(mktemp)"
  uv pip freeze --python "${REPO_ROOT}/.venv/bin/python" > "${LOCK}"
  uv pip install --quiet --python "${APP}/.venv/bin/python" -r "${LOCK}"
  rm -f "${LOCK}"
  info ".venv: $("${APP}/.venv/bin/python" -c 'import torch; print("torch", torch.__version__, "/ CUDA", torch.cuda.is_available())')"
fi

# ── モデル・データセット ─────────────────────────────────────────────────────
section "モデル・データセット → ${HF_CACHE}"
if [ ! -d "${HF_CACHE}" ]; then
  SRC="${HF_HOME:-${HOME}/.cache/huggingface}"
  if [ -d "${SRC}" ]; then
    rsync -a --no-group "${SRC}/" "${HF_CACHE}/"
    rm -f "${HF_CACHE}/token" "${HF_CACHE}/stored_tokens"   # トークンは配置しない
    info "${SRC} からコピーしました"
  else
    mkdir -p "${HF_CACHE}"
  fi
fi
if ${FETCH_MODELS}; then
  HF_HOME="${HF_CACHE}" bash "${REPO_ROOT}/infra/predownload.sh" || warn "取得できなかったものがあります（上の ✗ を参照）"
  rm -f "${HF_CACHE}/token" "${HF_CACHE}/stored_tokens"
  # predownload.sh が更新した MNIST を反映
  rsync -a --no-group "${REPO_ROOT}/data/" "${APP}/data/"
else
  info "足りないモデルは: HF_TOKEN=hf_xxx bash infra/multiuser/deploy.sh --models"
fi

# ── 権限 ─────────────────────────────────────────────────────────────────────
section "権限"
# rsync -a はディレクトリの権限をコピー元に合わせるため setgid が外れることがある。最後にまとめて直す
chgrp -hR "${SHARED_GROUP}" "${OPT}"
find "${OPT}" -type d -exec chmod g+s {} +
chmod -R g+rX,g-w,o-rwx "${OPT}"
info "$(stat -c '%A %U:%G' "${OPT}") ${OPT}（${SHARED_GROUP} は読むだけ）"
WRONG="$(find "${OPT}" ! -group "${SHARED_GROUP}" | head -5)"
if [ -n "${WRONG}" ]; then
  error "所有グループが ${SHARED_GROUP} でないファイルがあります（${SHARED_GROUP} から読めません）:"
  echo "${WRONG}"
  exit 1
fi

echo ""
info "完了。参加者用 JupyterLab は handson で起動します:"
echo -e "    ${GREEN}ssh handson@localhost bash ${APP}/infra/multiuser/handson.sh start${RESET}"
