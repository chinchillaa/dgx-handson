# 開催側の手順書

DGX Spark 1台を、最大10人の参加者で同時に使うハンズオンの運営手順です。
方針とその理由は `design/DESIGN.md` 4章にあります。参加者に配る手順は `docs/participant_guide.md` です。

## 全体像

```
参加者 p01 ─ ssh -N -L 8801:… -L 8800:… handson@<DGX> ─┬▶ JupyterLab :8801 → /home/handson/handson-work/p01/
                                                        └▶ 教材ページ :8800（全員共通）
参加者 p02 ─ ssh -N -L 8802:… -L 8800:… handson@<DGX> ─┬▶ JupyterLab :8802 → /home/handson/handson-work/p02/
                                                        └▶ 教材ページ :8800
  ...（最大 p10）
```

アカウントと置き場所は3つに分かれています。

| 場所 | 持ち主 | 中身 | 参加者から |
|---|---|---|---|
| `/home/user01/` | 運営者（`user01`） | リポジトリ `~/dgx-handson`、GitHub・Claude Code の認証情報、会話履歴 | **読めない** |
| `/opt/handson/` | 運営者（グループ `handson`） | 教材・infra・`.venv`・Python・モデル（`deploy.sh` が配置） | 読めるが、**書き換えられない** |
| `/home/handson/` | 参加者用アカウント `handson` | 参加者の作業ディレクトリ `handson-work/pNN/` | 読み書きできる（参加者どうしも） |

- 参加者は全員、同じ `handson` アカウントで SSH します。参加者ごとの区切りは JupyterLab で作ります
- 参加者の JupyterLab は運営者が起動します。参加者はサーバー上でコマンドを打ちません
- 参加者の JupyterLab はオフライン（`HF_HUB_OFFLINE=1`）で動きます。**事前にダウンロードしたモデルしか使えません**
- 教材の Web ページ（`chapter*/web`）は、JupyterLab とは別の静的サーバー（ポート 8800）で配信します。JupyterLab の中で HTML を開くとサンドボックス化され、数式（KaTeX）・レイアウト（Tailwind）・相対リンクが動かないためです。参加者のディレクトリには `web/` を配りません
- 教材ページは、参加者のブラウザが CDN（Tailwind・KaTeX・highlight.js・Google Fonts）を読み込めることが前提です

### コマンドの実行場所

この手順書では、コマンドを実行する場所を次のように書き分けます。

| 表記 | 意味 |
|---|---|
| **[user01]** | 運営者のアカウントで、リポジトリ `~/dgx-handson` から実行 |
| **[handson]** | 参加者用アカウントで実行。運営者は `user01` から `ssh handson@localhost` で入れます（鍵は登録済み。パスワード不要） |
| **[sudo]** | 運営者が自分の端末で `sudo` を付けて実行（パスワードを Claude などに渡さないこと） |

[handson] のコマンドは、次のように入ってから実行します。

```bash
ssh handson@localhost
cd /opt/handson/app
```

> `handson` のアカウントには、参加者も入ります。**`handson` で `gh auth login`・`hf auth login`・Claude Code へのログインをしないでください。** 認証情報が必要な作業は、すべて [user01] で行います。

---

## 1. 事前準備（1回だけ）

### 1-1. リポジトリの仮想環境 [user01]

```bash
bash infra/setup.sh
```

ここで作る `~/dgx-handson/.venv` が、参加者用の `.venv` の元になります（`deploy.sh` が同じバージョンを `/opt/handson` に作ります）。

### 1-2. 参加者用アカウント [sudo]

```bash
sudo bash infra/multiuser/setup_account.sh
```

途中で、参加者に配る `handson` の SSH パスワードを設定します。やることはスクリプトの冒頭に書いてあります（アカウント作成、`/opt/handson` の作成、`user01` をグループ `handson` に追加、linger の有効化、運営者の鍵の登録）。何度実行しても安全です。

### 1-3. 教材・仮想環境の配置 [user01]

```bash
bash infra/multiuser/deploy.sh
```

- 教材（`solutions/` を除く）・infra・MNIST を `/opt/handson/app` に同期します
- 初回は `/opt/handson/app/.venv` を作り、`~/.cache/huggingface` のモデルを `/opt/handson/hf_cache` にコピーします
- 最後に、所有グループと権限（`handson` は読むだけ）を直し、崩れていれば止まります

### 1-4. モデル・データセットのダウンロード [user01]

Llama は HuggingFace でのアクセス申請が必要です。次の2つのページで申請し、承認されてから進めてください。

- https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct
- https://huggingface.co/meta-llama/Meta-Llama-3-8B

```bash
HF_TOKEN=hf_xxxx bash infra/multiuser/deploy.sh --models
```

- `/opt/handson/hf_cache` に直接ダウンロードし、権限まで直します。`predownload.sh` を単体で実行すると権限が崩れるので、必ずこの形で実行してください
- 必要な空き容量の目安は約 25GB です（大半は Llama-3-8B の約 16GB）
- ダウンロード済みのものは飛ばされるので、何度実行しても問題ありません
- 取得対象の一覧は `infra/required_assets.py` にあります。**教材で新しいモデルやデータセットを使うときは、ここに追加してから再実行してください**
- トークンは `/opt/handson` にはコピーされません

### 1-5. 環境確認 [handson]

```bash
/opt/handson/app/.venv/bin/python /opt/handson/app/infra/check_env.py
```

参加者と同じアカウント・同じ条件（オフライン、読み取り専用のモデルキャッシュ）で読み込めるかを確認します。「4. モデル・データセット」がすべて ✓ になっていれば準備完了です。

---

## 2. 前日まで

### 2-1. リハーサル（強く推奨）

10人同時に動かしたときの本当のメモリ使用量は、実際に動かさないと分かりません。特に**第2章の上限値（RAM 8GB / GPU 14GB / 同時2本）は暫定値**です。

1. 手順 3 でサーバーを起動する
2. 数人がかりで複数のブラウザタブから、第1章・第2章のノートブックを同時に実行する
3. [handson] `bash infra/multiuser/handson.sh status` と `free -h` でメモリの余裕を確認する
4. 足りなければ手順 4-2 の上限値を調整し、`design/DESIGN.md` 4.3 の表も更新する

### 2-2. 参加者番号の割り当て

参加者ごとに `p01`〜`p10` を割り当て、名簿を作っておきます。

### 2-3. 接続情報の配布 [handson]

サーバーを起動したあと（手順 3）、次のコマンドで参加者ごとの接続情報を表示できます。

```bash
bash infra/multiuser/handson.sh urls
```

```
[p01]
  ssh -N -L 8801:localhost:8801 -L 8800:localhost:8800 handson@10.1.3.220
  JupyterLab : http://localhost:8801/lab?token=xxxxxxxx
  教材ページ : http://localhost:8800/
```

- **各参加者には、自分の番号の行だけを個別に渡してください。** トークンを知っていれば、他人の JupyterLab を開けてしまいます
- 参加者手順書 `docs/participant_guide.md` もあわせて配布します
- `handson` の SSH パスワード（手順 1-2 で設定したもの）の渡し方は別途決めてください。全員が同じパスワードを使います
- トークンは、`/home/handson/handson-work` を消さない限り再起動しても変わりません。前日に配布して問題ありません

### 2-4. 参加者から見えるもの・見えないもの

参加者の JupyterLab は `handson` として動きます。参加者は、Python の `open()` やターミナルで、**`handson` が読めるファイルはすべて読めます**。JupyterLab のファイル一覧で自分の `pNN` しか見えないのは、見た目だけです。

実機で、p01 のカーネルから確認済みです。

| 対象 | 参加者から | 理由 |
|---|---|---|
| 運営者のホーム（`/home/user01`。GitHub・Claude Code の認証情報、会話履歴、リポジトリ、`.git`） | **読めない** | ホームが `drwxr-x---` で、`handson` は `user01` グループに入っていない |
| 共有ディレクトリ（`/opt/handson`。`.venv`・スクリプト・モデル） | 読めるが、**書き換えられない** | 所有者が `user01` で、グループ `handson` には読み取り権限しかない |
| 解答（`solutions/`） | DGX 上では**読めない**（配置しない） | ただし公開リポジトリなので GitHub では見られる（下記） |
| 他の参加者の作業ディレクトリとトークン（`/home/handson/handson-work/pNN`） | **読める・書ける** | 同じ `handson` アカウントのため防げない。「自分の `pNN` 以外は触らない」を周知する |

注意点:

- **`handson` に秘密情報を置かない。** `handson` で GitHub・HuggingFace・Claude Code にログインすると、その認証情報は参加者全員から読めます
- **リポジトリ `chinchillaa/dgx-handson` は公開リポジトリです。** 解答とコミット履歴（作成者の名前とメールアドレス）は GitHub 上で誰でも見られます。解答を参加者から隠したい場合は、リポジトリの公開範囲や解答の置き場所を見直してください
- 参加者用アカウントを作れない環境では、付録 B の手順が必須です

---

## 3. 当日の開始前

### 3-1. 最新の教材を配置する [user01]

```bash
bash infra/multiuser/deploy.sh
```

### 3-2. 残っているプロセスを確認する

```bash
nvidia-smi
```

前回の開催や開発で残ったカーネルが GPU メモリを持ったままのことがあります。止めてよいものは、そのプロセスの持ち主のアカウントで `kill <PID>` します。

### 3-3. 起動する [handson]

```bash
bash infra/multiuser/handson.sh start       # 10人分（人数を変えるなら start 8 など）
bash infra/multiuser/handson.sh status
```

全員分と `web`（教材ページ）が `active` になっていれば完了です。`handson` は linger が有効なので、運営者が SSH を切っても JupyterLab は止まりません。

---

## 4. 開催中

### 4-1. 監視 [handson]

```bash
bash infra/multiuser/handson.sh status      # 各参加者の RAM と、GPU を使っているプロセス
free -h                                     # 統合メモリ全体の空き
```

GB10 は CPU と GPU がメモリを共有しています。`status` の RAM 列には GPU に確保した分が含まれません。下の「GPU 使用中のプロセス」の一覧とあわせて見てください。

### 4-2. 章ごとに上限を切り替える [handson]

上限は、サーバーの起動時に決まります。切り替えるときは、いったん止めて、環境変数を付けて起動し直します。

- 作業ファイルと URL は残ります
- **カーネルは再起動されます。** 休憩時間などに行い、参加者には「セルを上から実行し直してください」と伝えてください

```bash
bash infra/multiuser/handson.sh stop

# 第2章 SFT / DPO（Llama-3-8B QLoRA）
HANDSON_RAM_GB=8 HANDSON_GPU_GB=14 HANDSON_GPU_SLOTS=2 bash infra/multiuser/handson.sh start

# 第1章・第2章 RAG に戻す（既定値）
bash infra/multiuser/handson.sh start
```

| 場面 | RAM 上限 | GPU 上限 | 学習の同時実行 |
|---|---|---|---|
| 第1章 | 6GB（既定） | 5GB（既定） | ― |
| 第2章 SFT / DPO | 8GB | 14GB | 2本（既定） |
| 第2章 RAG / 評価 | 既定値。評価で 8B を読むなら SFT と同じ値 | | ― |

### 4-3. 第2章の学習の順番待ち

- ノートブックの学習セル（`with gpu_slot():`）と、ターミナルからの `gpu_queue.sh` は、同じ枠（既定2本）を使います
- 枠が埋まっていると、参加者の画面に「待機します」と表示され、空くと自動で始まります
- 誰が学習中かは、`status` の「GPU 使用中のプロセス」で確認できます（`pNN/...` が表示されます）
- 学習が終わるか、カーネルが止まると枠は自動で空きます

### 4-4. 放置カーネルの自動終了

30分使われていないカーネルは自動で終了します。参加者から「変数が消えた」と言われたら、これが原因です。セルを上から実行し直せば元に戻ります。

---

## 5. トラブル対応

| 症状 | 確認・対処 |
|---|---|
| 参加者のブラウザで何も開かない | ① [handson] `status` でその番号が `active` か確認 → ② 参加者の SSH トンネルが張られているか（`ssh -N -L ...` のウィンドウが開いたままか）→ ③ URL の番号とトークンが本人のものか |
| 参加者の SSH が `kex_exchange_identification: Connection closed by remote host` で切れる | DGX の sshd まで届いていない可能性が高いです。`/var/log/auth.log`（[user01] で読めます）にその時刻の記録がなければ、途中のネットワーク機器か IP の重複が原因です。ネットワーク管理者に確認してください |
| 教材ページが開かない | [handson] `status` で `web` が `active` か確認し、止まっていれば `start` を実行します（起動済みの JupyterLab には影響しません）。参加者の SSH コマンドに `-L 8800:localhost:8800` が入っているかも確認してください |
| 教材ページで数式が崩れる・リンクが開けない | JupyterLab の中で HTML を開いています。`http://localhost:8800/` から開くよう案内してください |
| 1人だけ調子が悪い（固まった・遅い） | [handson] `systemctl --user restart handson-pNN`（例: `handson-p03`）。上限もトークンも変わりません |
| 参加者のカーネルが勝手に落ちる | RAM 上限（cgroup）に当たった可能性があります。[handson] `journalctl --user -u handson-pNN -n 50` で確認し、必要なら上限を上げて再起動します |
| `OutOfMemoryError` が出る | GPU 上限に当たっています。参加者にはカーネルの再起動と batch size の縮小を案内します。全員が当たるようなら、上限値を見直してください |
| DGX 全体が重い・止まりそう | `free -h` と `status` で使いすぎている人を特定し、[handson] `systemctl --user restart handson-pNN` で再起動します |
| 順番待ちが進まない | `status` で学習中の人を確認します。放置されているなら、その人のカーネルを止めると枠が空きます |
| モデルが見つからないエラー（オフライン） | 事前ダウンロードが漏れています。`infra/required_assets.py` に追加し、[user01] `HF_TOKEN=... bash infra/multiuser/deploy.sh --models` を実行してください |
| `Permission denied: '/opt/handson/...'` | 参加者が共有ディレクトリに書こうとしています（想定どおりの拒否）。書き込みは自分の作業ディレクトリで行うよう案内してください。`.lock` ファイルで出る場合は、[user01] `deploy.sh` 後に [handson] `stop` → `start` し直してください |

---

## 6. 終了後 [handson]

```bash
bash infra/multiuser/handson.sh stop
```

- 止めた時点で、参加者の URL は使えなくなります
- 参加者に成果物を持ち帰ってもらう場合は、止める前に JupyterLab からダウンロードしてもらってください
- 次回の開催に向けて、`handson` のパスワードを変えておくと安全です（[sudo] `sudo passwd handson`）
- 作業ディレクトリをまっさらにしたいときは、`/home/handson/handson-work` を削除します。トークンも作り直されるので、URL を配り直す必要があります

```bash
rm -rf ~/handson-work
```

---

## 7. 教材を直したとき

教材はリポジトリ（`/home/user01/dgx-handson`）で直し、`deploy.sh` で `/opt/handson` に反映します。

| 変更の内容 | やること |
|---|---|
| Web ページの修正 | [user01] `deploy.sh` だけ。開催中でもすぐ反映されます |
| ノートブックの修正（開催前） | [user01] `deploy.sh` → [handson] `bash infra/multiuser/handson.sh refresh` で配り直す。URL は変わりません。参加者の編集は消えるので、**開催中は使わないでください** |
| 新しいモデル・データセットを使う | `infra/required_assets.py` に追加し、[user01] `HF_TOKEN=... bash infra/multiuser/deploy.sh --models` |
| `requirements.txt`・リポジトリの `.venv` の更新 | [user01] `bash infra/multiuser/deploy.sh --venv` → [handson] `stop` → `start` |
| `infra/multiuser/*` の修正 | [user01] `deploy.sh` → [handson] `stop` → `start` |

---

## 付録 A: 設定値の一覧

`handson.sh start` の前に環境変数で指定します。

| 変数 | 既定値 | 意味 |
|---|---|---|
| `HANDSON_RAM_GB` | 6 | 1人あたりの CPU メモリ上限（cgroup） |
| `HANDSON_GPU_GB` | 5 | 1人あたりの GPU メモリ上限（PyTorch） |
| `HANDSON_CPU_PCT` | 400 | 1人あたりの CPU 上限（100 = 1コア） |
| `HANDSON_GPU_SLOTS` | 2 | 重い学習を同時に走らせる本数 |
| `HANDSON_BASE_PORT` | 8800 | ポート番号の基準（教材ページ = 基準、p01 = 基準 + 1） |
| `HANDSON_WORK_ROOT` | `~/handson-work` | 参加者の作業ディレクトリの置き場所 |

| ファイル | 役割 |
|---|---|
| `infra/multiuser/setup_account.sh` | 参加者用アカウントと `/opt/handson` の作成（sudo で1回だけ） |
| `infra/multiuser/deploy.sh` | 教材・`.venv`・モデルを `/opt/handson` に配置（sudo 不要） |
| `infra/multiuser/handson.sh` | JupyterLab と教材ページの起動・停止・状態表示・URL 発行・教材の配り直し（`handson` で実行） |
| `infra/multiuser/ipython_startup.py` | カーネル起動時の GPU メモリ上限と `gpu_slot()` |
| `infra/multiuser/gpu_queue.sh` | スクリプトで学習するときの同時実行制御 |
| `infra/required_assets.py` | 事前ダウンロードするモデル・データセットの一覧 |
| `/home/handson/handson-work/pNN/.token` | 参加者のトークン（URL に含まれる） |
| `/home/handson/handson-work/pNN/.hf_datasets` | 参加者ごとのデータセットのキャッシュ（datasets は読むだけでもロックファイルを書くため、共有キャッシュからコピーしたもの） |

---

## 付録 B: 参加者用アカウントを作れない環境での注意

sudo が使えず、管理者にも参加者用アカウントを作ってもらえない場合は、参加者の JupyterLab を運営者のアカウントで動かすことになります（`/opt/handson` を使わず、リポジトリから `bash infra/multiuser/handson.sh start` で起動）。このとき、**参加者は運営者のホーム以下をすべて読めます。** 次の手順を**開催の直前**（参加者に URL を配る前、または SSH の接続を受け付ける前）に必ず行ってください。ログインが切れるので、運営作業（PR の作成、Claude Code での作業）は先に済ませておきます。

| 読まれるファイル | 中身 | 漏れると |
|---|---|---|
| `~/.config/gh/hosts.yml` | GitHub CLI のトークン | 運営者の GitHub アカウントとして、非公開を含むリポジトリの読み書き・プッシュができる |
| `~/.claude/.credentials.json` | Claude Code のログイン情報 | 運営者のアカウントで Claude Code を使われる |
| `~/.claude/projects/`・`~/.claude/history.jsonl` | Claude Code の会話履歴 | 会話に出てきたメールアドレス・参加者のトークン・社内の IP アドレスなどが読まれる |
| `~/.cache/huggingface/token` | HuggingFace のトークン（`hf auth login` を使った場合） | 運営者が申請した gated モデルを他で使われる |
| `~/.bash_history` | コマンド履歴 | `export HF_TOKEN=hf_...` などを打っていれば、トークンが読まれる |

1. **GitHub CLI からログアウトする**
   ```bash
   gh auth logout
   ```
   開催中にプッシュや PR 作成が必要になったら、DGX ではなく手元の PC から行います。

2. **Claude Code からログアウトし、会話履歴を DGX から外す**
   - Claude Code の中で `/logout` を実行する
   - 会話履歴を残したい場合は、手元の PC にコピーしてから消す
     ```bash
     # 手元の PC で（必要な場合のみ）
     scp -r <運営者>@<DGX>:~/.claude/projects ./claude-projects-backup
     ```
     ```bash
     # DGX で
     rm -rf ~/.claude/projects ~/.claude/history.jsonl
     ```

3. **HuggingFace のトークンを残さない**
   - `hf auth login` は使わず、`HF_TOKEN=... bash infra/predownload.sh` のように、そのときだけ渡す
   - 誤って `hf auth login` した場合は `hf auth logout` を実行する
   - コマンド履歴にトークンが残っていないか確認し、残っていれば履歴を消す
     ```bash
     grep -c 'hf_' ~/.bash_history      # 0 なら問題なし
     history -c && : > ~/.bash_history  # 残っていた場合
     ```

4. **残っていないか確認する**
   ```bash
   ls ~/.config/gh/hosts.yml ~/.claude/.credentials.json ~/.cache/huggingface/token \
      ~/.claude/history.jsonl 2>&1 | grep -v 'No such file'
   ```
   何も表示されなければ完了です。

5. **SSH を1本つないだままにする**: 運営者のアカウントで linger が無効なら、そのアカウントの SSH 接続がすべて切れると、全員の JupyterLab が止まります

6. **開催後にトークンを無効にする**（開催前にログアウトしていても、念のため行う）
   - GitHub: Settings → Applications → Authorized OAuth Apps → GitHub CLI → Revoke（その後、必要なら `gh auth login` し直す）
   - HuggingFace: Settings → Access Tokens で、使ったトークンを削除
