#!/bin/bash
# 偽のモデル（ランダム重み）でノートブックを最後まで実行し、現行のライブラリで動くかを確かめる。
# Hugging Face に接続できない環境（クラウドの作業環境など）向け。DGX では使わない。
#
# 使い方（リポジトリのルートで）:
#   bash infra/dev/run_nb.sh setup                         # 検証用の venv と偽のモデルを作る（初回だけ。数分）
#   bash infra/dev/run_nb.sh chapter2/notebooks/ch2_03_rag.ipynb ...   # 実行して .dev/out に保存
#   bash infra/dev/run_nb.sh test                          # agent_kit の単体テスト
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
DEV="${DEV_DIR:-${REPO}/.dev}"
PY="${DEV}/venv/bin/python"
export HF_HOME="${DEV}/fake_hf" HF_HUB_OFFLINE=1 TRANSFORMERS_VERBOSITY=error MPLBACKEND=Agg ANONYMIZED_TELEMETRY=False

case "${1:-}" in
  setup)
    uv venv -q -p 3.11 "${DEV}/venv"
    VIRTUAL_ENV="${DEV}/venv" uv pip install -q -r "${REPO}/requirements.txt" nbconvert ipykernel
    "${PY}" "${REPO}/infra/dev/build_fake_cache.py" "${HF_HOME}"
    "${PY}" "${REPO}/infra/dev/build_fake_qwen.py" "${HF_HOME}"
    mkdir -p "${DEV}/ipython/profile_default/startup"
    cp "${REPO}/infra/dev/ipython_fake_dolly.py" "${DEV}/ipython/profile_default/startup/00-fake.py"
    echo "準備ができました: ${DEV}"
    ;;
  test)
    "${PY}" "${REPO}/infra/dev/test_agent_kit.py"
    ;;
  ""|-h|--help)
    sed -n 2,9p "$0"
    ;;
  *)
    mkdir -p "${DEV}/out"
    for nb in "$@"; do
      nb="$(cd "$(dirname "${nb}")" && pwd)/$(basename "${nb}")"
      (cd "$(dirname "${nb}")" && IPYTHONDIR="${DEV}/ipython" "${DEV}/venv/bin/jupyter" nbconvert --to notebook --execute \
        --ExecutePreprocessor.timeout=900 --output-dir "${DEV}/out" --output "$(basename "${nb}" .ipynb)" "$(basename "${nb}")")
    done
    # ノートブックが書き出した学習結果・作業ファイルを消す（偽のモデルの出力なので残さない）
    rm -rf "${REPO}/chapter2/outputs" "${REPO}/chapter3/workspace"
    ;;
esac
