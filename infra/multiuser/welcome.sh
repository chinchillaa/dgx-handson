#!/usr/bin/env bash
# =============================================================================
# welcome.sh  —  参加者が SSH でログインしたときに、その人の URL を表示する
#
# 参加者が直接実行するものではない。restrict_ssh.sh が sshd の ForceCommand に設定し、
# 貸与 VM から handson でログインしたときに sshd が実行する（/opt/handson/app から）。
#   1. 接続元の IP（貸与 VM）から参加者番号を決める（VM_IPS の並び = p01, p02, …）
#   2. その参加者の JupyterLab の URL（トークン付き）と教材ページの URL を表示する
#   3. そのまま待ち続けて SSH トンネルを保つ（Ctrl+C で終了）
#
# シェルは開かない（参加者が DGX のコマンドを打てないようにする）。
# 運営者の ssh handson@localhost には適用されない（restrict_ssh.sh が localhost を除外）。
#
# 表示の確認（[handson] で。接続元を偽って p01 の表示を見る）:
#   SSH_CLIENT="10.1.3.221 0 22" bash /opt/handson/app/infra/multiuser/welcome.sh
#
# 補足: SSH_CLIENT は handson の ~/.bashrc で書き換えられるが、参加者は JupyterLab の
# ターミナルから他の人の .token をもともと読める（同じアカウントのため）ので、新たな穴にはならない。
# =============================================================================

# 貸与 VM の IP。1号機〜10号機 = p01〜p10（docs/operator_guide.md 2-2 の表と合わせる）
VM_IPS=(10.1.3.221 10.1.3.222 10.1.3.223 10.1.3.224 10.1.3.225
        10.1.3.226 10.1.3.227 10.1.3.228 10.1.3.229 10.1.3.230)

BASE_PORT="${HANDSON_BASE_PORT:-8800}"
WORK_ROOT="${HANDSON_WORK_ROOT:-${HOME}/handson-work}"

# トンネルを保つ。表示で何が起きても、ここに来れば接続は切れない
wait_forever() {
  echo ""
  echo "  このウィンドウは、ハンズオンの間ずっと開いたままにしてください。"
  echo "  （閉じるとブラウザから JupyterLab が見えなくなります。終了は Ctrl+C）"
  exec sleep infinity
}

client_ip="${SSH_CLIENT%% *}"
num=""
for i in "${!VM_IPS[@]}"; do
  if [ "${VM_IPS[$i]}" = "${client_ip}" ]; then num=$((i + 1)); break; fi
done

echo ""
echo "================================================================"
echo "  DGX ハンズオン: 接続に成功しました"
echo "================================================================"

if [ -z "${num}" ]; then
  echo ""
  echo "  この VM（${client_ip:-不明}）は参加者用の VM として登録されていません。"
  echo "  JupyterLab の URL は運営から受け取ってください。"
  echo ""
  echo "  Web page   : http://localhost:${BASE_PORT}/"
  wait_forever
fi

p="$(printf 'p%02d' "${num}")"
port=$((BASE_PORT + num))
token="$(cat "${WORK_ROOT}/${p}/.token" 2>/dev/null)"

echo ""
echo "  あなたの参加者番号: ${p}"
echo ""
if [ -z "${token}" ]; then
  echo "  JupyterLab の準備がまだできていません。講師に声をかけてください。"
else
  echo "  次の2つの URL を、この VM のブラウザで開いてください。"
  echo ""
  echo "  JupyterLab : http://localhost:${port}/lab?token=${token}"
  echo "  Web page   : http://localhost:${BASE_PORT}/"
  if ! (exec 3<>"/dev/tcp/127.0.0.1/${port}") 2>/dev/null; then
    echo ""
    echo "  ※ JupyterLab がまだ起動していません。講師に声をかけてください。"
  fi
  echo ""
  echo "  URL は自分専用です。他の人には教えないでください。"
fi
echo ""
echo "  ※ SSH コマンドは -L ${port}:localhost:${port} -L ${BASE_PORT}:localhost:${BASE_PORT} です"
echo "    （-L の左側の番号を変えた人は、URL の番号もその番号にしてください）"
wait_forever
