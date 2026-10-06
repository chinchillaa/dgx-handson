#!/usr/bin/env bash
# =============================================================================
# gpu_queue.sh  —  重い学習ジョブ（第2章 SFT/DPO）を同時 N 本までに制限して実行する
#
# 空きスロットができるまで待ってからコマンドを実行する。sudo 不要（flock のみ）。
#
# 使い方:
#   bash infra/multiuser/gpu_queue.sh python chapter2/scripts/train_sft.py
#   HANDSON_GPU_SLOTS=3 bash infra/multiuser/gpu_queue.sh python ...
#
# 待ち状況の確認:
#   ls ~/handson-work/.gpu-locks/
# =============================================================================

set -uo pipefail

SLOTS="${HANDSON_GPU_SLOTS:-2}"
LOCK_DIR="${HANDSON_WORK_ROOT:-${HOME}/handson-work}/.gpu-locks"
BUSY=75   # flock がロックを取れなかったときの終了コード

[ $# -gt 0 ] || { sed -n '2,14p' "$0"; exit 1; }
mkdir -p "${LOCK_DIR}"

waited=false
while true; do
  for i in $(seq 1 "${SLOTS}"); do
    flock -n -E "${BUSY}" "${LOCK_DIR}/slot${i}" "$@"
    rc=$?
    [ "${rc}" -ne "${BUSY}" ] && exit "${rc}"
  done
  ${waited} || echo "[gpu_queue] GPU スロット（${SLOTS}本）が埋まっています。空くまで待機します..."
  waited=true
  sleep 10
done
