#!/usr/bin/env bash
# =============================================================================
# setup_account.sh  —  参加者用アカウントを作る（運営者が sudo で1回だけ実行）
#
# 使い方（運営者が自分の端末で。パスワードは Claude などに渡さないこと）:
#   sudo bash infra/multiuser/setup_account.sh
#
# 目的:
#   参加者の JupyterLab を運営者（sudo を実行した人）とは別のアカウントで動かし、
#   運営者のホーム（GitHub・Claude Code の認証情報、会話履歴、リポジトリ）を
#   参加者から読めなくする。参加者10人は全員この1アカウントを使う。
#
# やること（何度実行しても安全。すでにあるものは作り直さない）:
#   1. 参加者用アカウント handson を作り、SSH 用のパスワードを設定する
#   2. /opt/handson を作る（所有者: 運営者 / グループ: handson / 2750）
#      → 運営者は書ける。handson は読むだけ（教材や .venv を書き換えられない）
#      運営者をグループ handson に加える。Linux は「所有グループに属さないユーザーが権限を
#      変えると setgid を外す」ため、属していないと deploy.sh の配置でグループが崩れる。
#      （運営者が /home/handson を読めるようになるだけで、参加者側の権限は増えない）
#      すでに配置済みのファイルは、グループ handson と setgid を付け直す
#   3. handson の linger を有効にする（SSH が全部切れても JupyterLab が止まらない）
#   4. 運営者の SSH 公開鍵を handson に登録する（運営者が ssh handson@localhost で操作するため）
#   5. 運営者のホームが他のユーザーから読めないことを確認する
#
# やらないこと: パッケージのインストール、sshd・ファイアウォールの設定変更、sudo 権限の付与
# =============================================================================

set -euo pipefail

HANDSON_USER="${HANDSON_USER:-handson}"
HANDSON_OPT="${HANDSON_OPT:-/opt/handson}"
OPERATOR="${SUDO_USER:-}"

GREEN='\033[0;32m'; AMBER='\033[0;33m'; RED='\033[0;31m'; RESET='\033[0m'
info() { echo -e "${GREEN}[INFO]${RESET}  $*"; }
warn() { echo -e "${AMBER}[WARN]${RESET}  $*"; }
error() { echo -e "${RED}[ERROR]${RESET} $*"; }

if [ "$(id -u)" -ne 0 ] || [ -z "${OPERATOR}" ] || [ "${OPERATOR}" = "root" ]; then
  error "運営者のアカウントから sudo で実行してください: sudo bash $0"
  exit 1
fi
OPERATOR_HOME="$(getent passwd "${OPERATOR}" | cut -d: -f6)"
info "運営者: ${OPERATOR}（${OPERATOR_HOME}） / 参加者用アカウント: ${HANDSON_USER} / 共有ディレクトリ: ${HANDSON_OPT}"

# ── 1. 参加者用アカウント ────────────────────────────────────────────────────
if id "${HANDSON_USER}" &>/dev/null; then
  warn "1. ${HANDSON_USER} はすでにあります（パスワードは変更しません。変える場合: sudo passwd ${HANDSON_USER}）"
else
  useradd --create-home --shell /bin/bash --user-group "${HANDSON_USER}"
  info "1. ${HANDSON_USER} を作成しました。参加者に配る SSH のパスワードを設定してください"
  passwd "${HANDSON_USER}"
fi
HANDSON_HOME="$(getent passwd "${HANDSON_USER}" | cut -d: -f6)"
chmod 750 "${HANDSON_HOME}"

# ── 2. 共有ディレクトリ ──────────────────────────────────────────────────────
mkdir -p "${HANDSON_OPT}"
chown "${OPERATOR}:${HANDSON_USER}" "${HANDSON_OPT}"
chmod 2750 "${HANDSON_OPT}"
usermod -aG "${HANDSON_USER}" "${OPERATOR}"
chgrp -hR "${HANDSON_USER}" "${HANDSON_OPT}"
find "${HANDSON_OPT}" -type d -exec chmod g+s {} +
chmod -R g+rX,g-w,o-rwx "${HANDSON_OPT}"
info "2. ${HANDSON_OPT}: $(stat -c '%A %U:%G' "${HANDSON_OPT}")（${OPERATOR} をグループ ${HANDSON_USER} に追加）"

# ── 3. linger ─────────────────────────────────────────────────────────────────
loginctl enable-linger "${HANDSON_USER}"
info "3. linger: $(loginctl show-user "${HANDSON_USER}" -p Linger --value 2>/dev/null || echo '?')"

# ── 4. 運営者の鍵を登録 ──────────────────────────────────────────────────────
KEY="${OPERATOR_HOME}/.ssh/id_ed25519"
if [ ! -f "${KEY}.pub" ]; then
  sudo -u "${OPERATOR}" mkdir -p "${OPERATOR_HOME}/.ssh"
  sudo -u "${OPERATOR}" chmod 700 "${OPERATOR_HOME}/.ssh"
  sudo -u "${OPERATOR}" ssh-keygen -q -t ed25519 -N '' -C "${OPERATOR}@$(hostname)-handson-admin" -f "${KEY}"
  info "4. 運営者の鍵を作成しました: ${KEY}"
fi
install -d -m 700 -o "${HANDSON_USER}" -g "${HANDSON_USER}" "${HANDSON_HOME}/.ssh"
AUTH="${HANDSON_HOME}/.ssh/authorized_keys"
touch "${AUTH}"
grep -qxF "$(cat "${KEY}.pub")" "${AUTH}" || cat "${KEY}.pub" >> "${AUTH}"
chown "${HANDSON_USER}:${HANDSON_USER}" "${AUTH}"
chmod 600 "${AUTH}"
info "4. 運営者の公開鍵を ${AUTH} に登録しました（ssh ${HANDSON_USER}@localhost で入れます）"

# ── 5. 運営者のホームの権限 ──────────────────────────────────────────────────
MODE="$(stat -c '%a' "${OPERATOR_HOME}")"
if [ $((8#${MODE} & 8#007)) -ne 0 ]; then
  warn "5. ${OPERATOR_HOME} が他のユーザーから読めます（${MODE}）。chmod 750 ${OPERATOR_HOME} を推奨します"
else
  info "5. ${OPERATOR_HOME} は他のユーザーから読めません（${MODE}）"
fi

echo ""
info "完了。次は sudo なしで: bash infra/multiuser/deploy.sh"
