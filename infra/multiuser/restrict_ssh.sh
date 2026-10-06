#!/usr/bin/env bash
# =============================================================================
# restrict_ssh.sh  —  参加者用アカウント handson の SSH を制限する（運営者が sudo で実行）
#
# 使い方（運営者が自分の端末で。パスワードは Claude などに渡さないこと）:
#   sudo bash infra/multiuser/restrict_ssh.sh                          # トンネルの行き先だけ制限
#   sudo bash infra/multiuser/restrict_ssh.sh 10.1.3.219 10.1.3.221 …  # 接続元も貸与 VM に限定
#   sudo bash infra/multiuser/restrict_ssh.sh --remove                 # 制限を外す
#
# やること（/etc/ssh/sshd_config.d/50-handson.conf を作り直して sshd を再読み込み）:
#   1. handson の SSH トンネルの行き先を、JupyterLab と教材ページ（localhost:8800〜8810）だけにする
#      → DGX を踏み台にして社内の他の機器へトンネルを張れないようにする
#      X11・エージェント転送・リモート転送・tun も禁止する
#   2. 接続元を指定したとき: handson でログインできるのは、指定した IP と localhost
#      （運営者が ssh handson@localhost で操作するため）だけにする
#      それ以外からは認証方法をすべて無効にし、万一ログインできても何もできないようにする
#   3. localhost 以外から handson でログインしたら、シェルの代わりに welcome.sh を動かす
#      （ForceCommand）。接続元の貸与 VM から参加者番号を決めて、その人の URL を表示し、
#      トンネルを保ったまま待つ。参加者は DGX のシェルを使えなくなる
#      → 先に deploy.sh で /opt/handson/app に welcome.sh を配置しておくこと
#
# 影響するのは handson だけ。運営者（user01 など）の SSH は変わらない。
# 設定は sshd -t で検査し、さらに運営者の実効設定（sshd -T）が適用前と同じかを比べる。
# エラーや差分があれば元に戻してから終了する（sshd と運営者の SSH を壊さない）。
# =============================================================================

set -euo pipefail

HANDSON_USER="${HANDSON_USER:-handson}"
BASE_PORT="${HANDSON_BASE_PORT:-8800}"
CONF="/etc/ssh/sshd_config.d/50-handson.conf"
WELCOME="${HANDSON_OPT:-/opt/handson}/app/infra/multiuser/welcome.sh"

GREEN='\033[0;32m'; AMBER='\033[0;33m'; RED='\033[0;31m'; RESET='\033[0m'
info() { echo -e "${GREEN}[INFO]${RESET}  $*"; }
warn() { echo -e "${AMBER}[WARN]${RESET}  $*"; }
error() { echo -e "${RED}[ERROR]${RESET} $*"; }

if [ "$(id -u)" -ne 0 ]; then
  error "sudo で実行してください: sudo bash $0 [接続元IP ...]"
  exit 1
fi

reload_sshd() {
  systemctl reload ssh 2>/dev/null || systemctl restart ssh
}

if [ "${1:-}" = "--remove" ]; then
  rm -f "${CONF}"
  reload_sshd
  info "制限を外しました（${CONF} を削除）"
  exit 0
fi

if [ ! -f "${WELCOME}" ]; then
  error "${WELCOME} がありません。先に運営者のアカウントで bash infra/multiuser/deploy.sh を実行してください"
  exit 1
fi

for ip in "$@"; do
  [[ "${ip}" =~ ^[0-9]{1,3}(\.[0-9]{1,3}){3}$ ]] || { error "IPv4 アドレスではありません: ${ip}"; exit 1; }
done

# 転送を許す行き先: localhost / 127.0.0.1 の 8800（教材ページ）〜8810（p10）
PERMIT_OPEN=""
for port in $(seq "${BASE_PORT}" $((BASE_PORT + 10))); do
  PERMIT_OPEN+=" localhost:${port} 127.0.0.1:${port}"
done

OPERATOR="${SUDO_USER:-root}"
effective() {  # 指定ユーザー・接続元での sshd の実効設定
  sshd -T -C "user=$1,addr=$2,host=$2,laddr=127.0.0.1,lport=22" 2>/dev/null | sort
}
OPERATOR_BEFORE="$(effective "${OPERATOR}" 10.1.3.219)"

BACKUP=""
if [ -f "${CONF}" ]; then
  BACKUP="$(mktemp)"
  cp -p "${CONF}" "${BACKUP}"
fi

{
  echo "# 参加者用アカウント ${HANDSON_USER} の SSH 制限。infra/multiuser/restrict_ssh.sh が生成（手で編集しない）"
  echo "# 生成: $(date '+%F %T') / 実行者: ${SUDO_USER:-root}"
  echo ""
  # sshd は同じ項目なら「最初に現れた値」が勝つ。許可外の接続元の制限を先に書き、
  # 後ろの handson 全体の設定（AllowTcpForwarding local など）に上書きされないようにする
  if [ $# -gt 0 ]; then
    NOT_ALLOWED="*,!127.0.0.1,!::1"
    for ip in "$@"; do NOT_ALLOWED+=",!${ip}"; done
    echo "# 許可した接続元（$*）と localhost 以外からは、認証方法をすべて無効にする。"
    echo "# 万一ログインできても、シェルもトンネルも使えないようにする"
    echo "Match User ${HANDSON_USER} Address ${NOT_ALLOWED}"
    echo "    PasswordAuthentication no"
    echo "    KbdInteractiveAuthentication no"
    echo "    PubkeyAuthentication no"
    echo "    AllowTcpForwarding no"
    echo "    PermitOpen none"
    echo "    ForceCommand /bin/false"
    echo ""
  fi
  # 貸与 VM からのログインでは、シェルの代わりに参加者の URL を表示して待つ。
  # welcome.sh が何かで終わっても、sleep でトンネルを保つ（-N なしの接続はコマンドが終わると切れる）
  echo "# localhost 以外からのログインでは、シェルを開かずに参加者の URL を表示する"
  echo "Match User ${HANDSON_USER} Address *,!127.0.0.1,!::1"
  echo "    ForceCommand /bin/bash ${WELCOME}; exec /bin/sleep infinity"
  echo ""
  echo "Match User ${HANDSON_USER}"
  echo "    AllowTcpForwarding local"
  echo "    PermitOpen${PERMIT_OPEN}"
  echo "    X11Forwarding no"
  echo "    AllowAgentForwarding no"
  echo "    AllowStreamLocalForwarding no"
  echo "    PermitTunnel no"
  echo "    GatewayPorts no"
} > "${CONF}"
chmod 644 "${CONF}"

rollback() {
  error "$1。元に戻します"
  if [ -n "${BACKUP}" ]; then cp -p "${BACKUP}" "${CONF}"; else rm -f "${CONF}"; fi
  exit 1
}
sshd -t || rollback "sshd の設定検査でエラーになりました"
if [ "$(effective "${OPERATOR}" 10.1.3.219)" != "${OPERATOR_BEFORE}" ]; then
  diff <(echo "${OPERATOR_BEFORE}") <(effective "${OPERATOR}" 10.1.3.219) || true
  rollback "運営者（${OPERATOR}）の実効設定が変わりました（Match が handson 以外に効いています）"
fi
[ -n "${BACKUP}" ] && rm -f "${BACKUP}"
reload_sshd

info "1. ${HANDSON_USER} のトンネルの行き先: localhost:${BASE_PORT}〜$((BASE_PORT + 10)) のみ"
if [ $# -gt 0 ]; then
  info "2. ${HANDSON_USER} の接続元: $* と localhost のみ"
else
  warn "2. 接続元は制限していません（貸与 VM の IP が分かったら、引数に付けて再実行してください）"
fi
info "3. localhost 以外からのログイン: シェルの代わりに ${WELCOME} を実行"
echo ""
info "実効設定（sshd -T）:"
echo "  ${HANDSON_USER} @ localhost  : $(effective "${HANDSON_USER}" 127.0.0.1 | grep -E '^(allowtcpforwarding|passwordauthentication) ' | tr '\n' ' ')"
[ $# -gt 0 ] && echo "  ${HANDSON_USER} @ $1 : $(effective "${HANDSON_USER}" "$1" | grep -E '^(allowtcpforwarding|passwordauthentication|forcecommand) ' | tr '\n' ' ')"
echo "  ${HANDSON_USER} @ 192.0.2.1（許可外の例）: $(effective "${HANDSON_USER}" 192.0.2.1 | grep -E '^(allowtcpforwarding|passwordauthentication|forcecommand) ' | tr '\n' ' ')"
echo "  ${OPERATOR} @ 10.1.3.219  : $(effective "${OPERATOR}" 10.1.3.219 | grep -E '^(allowtcpforwarding|passwordauthentication|x11forwarding) ' | tr '\n' ' ')"
info "設定: ${CONF}（外すとき: sudo bash $0 --remove）"
