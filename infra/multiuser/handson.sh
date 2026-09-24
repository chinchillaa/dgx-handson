#!/usr/bin/env bash
# =============================================================================
# handson.sh  —  1アカウント共有で最大10人分の JupyterLab を立てる運営スクリプト
#
# sudo なしで動く。参加者ごとに次を分ける:
#   - 作業ディレクトリ    ~/handson-work/pNN/（教材のコピー）
#   - JupyterLab          127.0.0.1:88NN（トークン付き、SSH トンネル経由でのみ到達）
#   - CPU メモリ上限      systemd-run --user の cgroup（MemoryMax）
#   - GPU メモリ上限      カーネル起動時に torch.cuda.set_per_process_memory_fraction
#                         ※ GB10 では cgroup が GPU 確保分を数えないため別途必要
#   - 放置カーネル        30分アイドルで自動終了
#   - 重い学習の同時実行数 gpu_slot()（ノートブック）/ gpu_queue.sh（スクリプト）
#
# 教材の Web ページ（chapter*/web）は全員共通の静的サーバー 127.0.0.1:8800 で配信する。
# JupyterLab の中で HTML を開くとサンドボックス化され、KaTeX などのスクリプトと
# 相対リンクが動かないため。参加者は SSH トンネルに -L 8800:localhost:8800 を追加する。
#
# 使い方:
#   bash infra/multiuser/handson.sh start  [人数]   # 既定 10 人
#   bash infra/multiuser/handson.sh urls   [人数]   # 参加者に配る接続手順を表示
#   bash infra/multiuser/handson.sh status [人数]   # 各サーバーのメモリ使用量
#   bash infra/multiuser/handson.sh stop   [人数]
#   bash infra/multiuser/handson.sh refresh [人数]  # 教材を配り直す（開催前のみ。参加者の編集は消える）
#
# 上限を変えるときは stop → 環境変数を付けて start（作業ファイルは残る。カーネルは再起動）
#   例（第2章）: HANDSON_RAM_GB=8 HANDSON_GPU_GB=14 bash infra/multiuser/handson.sh start
#
# 調整用の環境変数（既定値）:
#   HANDSON_RAM_GB=6  HANDSON_GPU_GB=5  HANDSON_CPU_PCT=400（=4コア）
#   HANDSON_GPU_SLOTS=2（重い学習を同時に走らせる本数）
#   HANDSON_BASE_PORT=8800（Web ページ = 8800、p01 = 8801 …）  HANDSON_WORK_ROOT=~/handson-work
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
VENV_BIN="${REPO_ROOT}/.venv/bin"

CMD="${1:-}"
N="${2:-10}"
BASE_PORT="${HANDSON_BASE_PORT:-8800}"
WORK_ROOT="${HANDSON_WORK_ROOT:-${HOME}/handson-work}"
RAM_GB="${HANDSON_RAM_GB:-6}"
GPU_GB="${HANDSON_GPU_GB:-5}"
CPU_PCT="${HANDSON_CPU_PCT:-400}"
GPU_SLOTS="${HANDSON_GPU_SLOTS:-2}"
HF_CACHE="${HF_HOME:-${HOME}/.cache/huggingface}"

GREEN='\033[0;32m'; AMBER='\033[0;33m'; RED='\033[0;31m'; RESET='\033[0m'
info() { echo -e "${GREEN}[INFO]${RESET}  $*"; }
warn() { echo -e "${AMBER}[WARN]${RESET}  $*"; }
error() { echo -e "${RED}[ERROR]${RESET} $*"; }

pid_of() { printf 'p%02d' "$1"; }
port_of() { echo $((BASE_PORT + $1)); }
unit_of() { echo "handson-$(pid_of "$1")"; }
WEB_PORT="${BASE_PORT}"
WEB_UNIT="handson-web"
WEB_ROOT="${WORK_ROOT}/.web"

# ── 教材のコピー ────────────────────────────────────────────────────────────
copy_materials() {
  # solutions/ は講師のみ参照（DESIGN.md 5.1）なので参加者には配らない
  # web/ は共通の Web サーバーで配信するので配らない（JupyterLab の中では正しく表示できない）
  tar -C "${REPO_ROOT}" \
      --exclude='*/solutions' --exclude='*/web' --exclude='.ipynb_checkpoints' --exclude='outputs' \
      -cf - chapter1 chapter2 chapter3 | tar -C "$1" -xf -
}

# ── 教材の Web ページを配信する静的サーバー（全員共通・読み取りのみ） ────────
start_web() {
  # 公開するのは chapter*/web と assets だけ（リポジトリの他のファイルは見せない）
  local c
  for c in chapter1 chapter2 chapter3; do
    mkdir -p "${WEB_ROOT}/${c}"
    ln -sfn "${REPO_ROOT}/${c}/web" "${WEB_ROOT}/${c}/web"
  done
  ln -sfn "${REPO_ROOT}/assets" "${WEB_ROOT}/assets"
  printf '%s\n' '<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=chapter1/web/index.html"><title>DGX ハンズオン</title><a href="chapter1/web/index.html">第1章へ</a>' \
    > "${WEB_ROOT}/index.html"
  if systemctl --user is-active --quiet "${WEB_UNIT}"; then
    warn "Web ページ: 起動済み (port ${WEB_PORT})"
    return
  fi
  systemd-run --user --quiet --collect --unit="${WEB_UNIT}" -p MemoryMax=256M \
    "${VENV_BIN}/python" -m http.server "${WEB_PORT}" --bind 127.0.0.1 --directory "${WEB_ROOT}"
  info "Web ページ: 起動 (port ${WEB_PORT})"
}

# ── 参加者ディレクトリの用意（既存の作業は上書きしない） ────────────────────
init_participant() {
  local dir="$1"
  if [ ! -d "${dir}" ]; then
    mkdir -p "${dir}"
    copy_materials "${dir}"
  fi
  # カーネル起動時に GPU メモリ上限と gpu_slot() を用意する IPython スタートアップ
  mkdir -p "${dir}/.ipython/profile_default/startup"
  cp "${SCRIPT_DIR}/ipython_startup.py" "${dir}/.ipython/profile_default/startup/00-handson.py"
  if [ ! -f "${dir}/.token" ]; then
    (umask 077; "${VENV_BIN}/python" -c 'import secrets; print(secrets.token_hex(16))' > "${dir}/.token")
  fi
}

start() {
  mkdir -p "${WORK_ROOT}"
  info "RAM上限 ${RAM_GB}GB / GPU上限 ${GPU_GB}GB / CPU ${CPU_PCT}% × ${N}人（学習の同時実行 ${GPU_SLOTS}本）"
  start_web
  for i in $(seq 1 "${N}"); do
    local p dir port unit
    p="$(pid_of "$i")"; dir="${WORK_ROOT}/${p}"; port="$(port_of "$i")"; unit="$(unit_of "$i")"
    if systemctl --user is-active --quiet "${unit}"; then
      warn "${p}: 起動済み (port ${port})"
      continue
    fi
    init_participant "${dir}"
    systemd-run --user --quiet --collect --unit="${unit}" \
      -p MemoryMax="${RAM_GB}G" -p MemorySwapMax=0 -p CPUQuota="${CPU_PCT}%" \
      --working-directory="${dir}" \
      --setenv=HANDSON_PARTICIPANT="${p}" \
      --setenv=HANDSON_GPU_GB="${GPU_GB}" \
      --setenv=HANDSON_GPU_SLOTS="${GPU_SLOTS}" \
      --setenv=HANDSON_WORK_ROOT="${WORK_ROOT}" \
      --setenv=HANDSON_DATA_DIR="${REPO_ROOT}/data" \
      --setenv=IPYTHONDIR="${dir}/.ipython" \
      --setenv=JUPYTER_RUNTIME_DIR="${dir}/.jupyter-runtime" \
      --setenv=HF_HOME="${HF_CACHE}" \
      --setenv=HF_HUB_OFFLINE=1 \
      --setenv=WANDB_MODE=offline \
      --setenv=MPLCONFIGDIR="${dir}/.matplotlib" \
      --setenv=PATH="${VENV_BIN}:${SCRIPT_DIR}:/usr/local/bin:/usr/bin:/bin" \
      "${VENV_BIN}/jupyter" lab \
        --no-browser --ip=127.0.0.1 --port="${port}" --ServerApp.port_retries=0 \
        --ServerApp.root_dir="${dir}" \
        --IdentityProvider.token="$(cat "${dir}/.token")" \
        --MappingKernelManager.cull_idle_timeout=1800 \
        --MappingKernelManager.cull_interval=300
    info "${p}: 起動 (port ${port})"
  done
  echo ""
  info "接続手順は: bash infra/multiuser/handson.sh urls ${N}"
}

stop() {
  for i in $(seq 1 "${N}"); do
    systemctl --user stop "$(unit_of "$i")" 2>/dev/null && info "$(pid_of "$i"): 停止" || true
  done
  systemctl --user stop "${WEB_UNIT}" 2>/dev/null && info "Web ページ: 停止" || true
}

status() {
  printf '%-5s %-6s %-9s %10s\n' ID PORT STATE RAM
  for i in $(seq 1 "${N}"); do
    local unit state mem
    unit="$(unit_of "$i")"
    state="$(systemctl --user is-active "${unit}" 2>/dev/null || true)"
    mem="$(systemctl --user show -p MemoryCurrent --value "${unit}" 2>/dev/null || true)"
    [[ "${mem}" =~ ^[0-9]+$ ]] && mem="$(awk -v b="${mem}" 'BEGIN{printf "%.1fGB", b/1e9}')" || mem="-"
    printf '%-5s %-6s %-9s %10s\n' "$(pid_of "$i")" "$(port_of "$i")" "${state:-inactive}" "${mem}"
  done
  printf '%-5s %-6s %-9s\n' web "${WEB_PORT}" "$(systemctl --user is-active "${WEB_UNIT}" 2>/dev/null || echo inactive)"
  echo ""
  info "GPU 使用中のプロセス（統合メモリのため、上の RAM とは別に計上）:"
  nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader 2>/dev/null \
    | while IFS=', ' read -r pid mem _; do
        local cwd
        cwd="$(readlink "/proc/${pid}/cwd" 2>/dev/null || echo '?')"
        echo "  pid ${pid}  ${mem} MiB  ${cwd#"${WORK_ROOT}/"}"
      done
}

refresh() {
  warn "${WORK_ROOT}/p01〜p$(printf '%02d' "${N}") の教材を配り直します。"
  warn "参加者が編集したノートブックや outputs/ は消えます（トークン＝配布済み URL はそのまま）。"
  read -rp "  続けますか？ [y/N]: " ans
  [[ "${ans}" =~ ^[Yy]$ ]] || { info "中止しました"; return; }
  for i in $(seq 1 "${N}"); do
    local dir
    dir="${WORK_ROOT}/$(pid_of "$i")"
    [ -d "${dir}" ] || continue
    rm -rf "${dir}/chapter1" "${dir}/chapter2" "${dir}/chapter3" "${dir}/assets" "${dir}/outputs"
    copy_materials "${dir}"
    info "$(pid_of "$i"): 配り直しました"
  done
  info "開いているノートブックは、ブラウザで開き直すと新しい内容になります"
}

urls() {
  local host
  host="$(hostname -I | awk '{print $1}')"
  echo "参加者に配布する接続手順（各自の手元PCで実行）"
  echo "================================================================"
  for i in $(seq 1 "${N}"); do
    local p port dir
    p="$(pid_of "$i")"; port="$(port_of "$i")"; dir="${WORK_ROOT}/${p}"
    [ -f "${dir}/.token" ] || { warn "${p}: 未初期化（start を先に実行）"; continue; }
    echo "[${p}]"
    echo "  ssh -N -L ${port}:localhost:${port} -L ${WEB_PORT}:localhost:${WEB_PORT} ${USER}@${host}"
    echo "  JupyterLab : http://localhost:${port}/lab?token=$(cat "${dir}/.token")"
    echo "  教材ページ : http://localhost:${WEB_PORT}/"
  done
}

case "${CMD}" in
  start) start ;;
  stop) stop ;;
  status) status ;;
  urls) urls ;;
  refresh) refresh ;;
  *) sed -n '2,36p' "$0"; exit 1 ;;
esac
