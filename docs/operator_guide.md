# 開催側の手順書

DGX Spark 1台を、最大10人の参加者で同時に使うハンズオンの運営手順です。
方針とその理由は `design/DESIGN.md` 4章にあります。参加者に配る手順は `docs/participant_guide.md` です。

## 全体像

```
参加者 p01 ─ ssh -N -L 8801:… -L 8800:… user01@<DGX> ─┬▶ JupyterLab :8801 → ~/handson-work/p01/
                                                       └▶ 教材ページ :8800（全員共通）→ chapter*/web
参加者 p02 ─ ssh -N -L 8802:… -L 8800:… user01@<DGX> ─┬▶ JupyterLab :8802 → ~/handson-work/p02/
                                                       └▶ 教材ページ :8800
  ...（最大 p10）

全員で共有（運営者が用意）: ~/dgx-handson/.venv、~/.cache/huggingface（モデル）、~/dgx-handson/data（MNIST）
```

- 全員が同じアカウント `user01` で SSH します。sudo は不要です
- 参加者ごとの JupyterLab は運営者が起動します。参加者はサーバー上でコマンドを打ちません
- 参加者の JupyterLab はオフライン（`HF_HUB_OFFLINE=1`）で動きます。**事前にダウンロードしたモデルしか使えません**
- 教材の Web ページ（`chapter*/web`）は、JupyterLab とは別の静的サーバー（ポート 8800）で配信します。JupyterLab の中で HTML を開くとサンドボックス化され、数式（KaTeX）・レイアウト（Tailwind）・相対リンクが動かないためです。参加者のディレクトリには `web/` を配りません
- 教材ページは、参加者のブラウザが CDN（Tailwind・KaTeX・highlight.js・Google Fonts）を読み込めることが前提です

以下のコマンドは、すべて DGX 上で `~/dgx-handson` から実行します。

---

## 1. 事前準備（1回だけ）

### 1-1. 仮想環境

```bash
bash infra/setup.sh
```

`.venv` がすでにあれば飛ばされます。

### 1-2. モデル・データセットのダウンロード

Llama は HuggingFace でのアクセス申請が必要です。次の2つのページで申請し、承認されてから進めてください。

- https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct
- https://huggingface.co/meta-llama/Meta-Llama-3-8B

```bash
export HF_TOKEN=hf_xxxx      # 運営者のトークン。参加者には渡さない
bash infra/predownload.sh
```

- 必要な空き容量の目安は約 25GB です（大半は Llama-3-8B の約 16GB）
- ダウンロード済みのものは飛ばされるので、何度実行しても問題ありません
- 取得対象の一覧は `infra/required_assets.py` にあります。**教材で新しいモデルやデータセットを使うときは、ここに追加してから再実行してください**

### 1-3. 環境確認

```bash
.venv/bin/python infra/check_env.py
```

「4. モデル・データセット」がすべて ✓ になっていれば準備完了です。このチェックは、当日と同じオフラインの条件で読み込めるかを確認します。

---

## 2. 前日まで

### 2-1. リハーサル（強く推奨）

10人同時に動かしたときの本当のメモリ使用量は、実際に動かさないと分かりません。特に**第2章の上限値（RAM 8GB / GPU 14GB / 同時2本）は暫定値**です。

1. 手順 3 でサーバーを起動する
2. 数人がかりで複数のブラウザタブから、第1章・第2章のノートブックを同時に実行する
3. `bash infra/multiuser/handson.sh status` と `free -h` でメモリの余裕を確認する
4. 足りなければ手順 4-2 の上限値を調整し、`design/DESIGN.md` 4.3 の表も更新する

### 2-2. 参加者番号の割り当て

参加者ごとに `p01`〜`p10` を割り当て、名簿を作っておきます。

### 2-3. 接続情報の配布

サーバーを起動したあと（手順 3）、次のコマンドで参加者ごとの接続情報を表示できます。

```bash
bash infra/multiuser/handson.sh urls
```

```
[p01]
  ssh -N -L 8801:localhost:8801 -L 8800:localhost:8800 user01@10.1.3.220
  JupyterLab : http://localhost:8801/lab?token=xxxxxxxx
  教材ページ : http://localhost:8800/
```

- **各参加者には、自分の番号の行だけを個別に渡してください。** トークンを知っていれば、他人の JupyterLab を開けてしまいます
- 参加者手順書 `docs/participant_guide.md` もあわせて配布します
- `user01` の SSH パスワード（または鍵）の渡し方は別途決めてください。全員が同じ認証情報を使います
- トークンは、`~/handson-work` を消さない限り再起動しても変わりません。前日に配布して問題ありません

---

## 3. 当日の開始前

### 3-1. 残っているプロセスを確認する

```bash
nvidia-smi
bash infra/multiuser/handson.sh status
```

前回の開催や開発で残ったカーネルが GPU メモリを持ったままのことがあります。`handson-work/pNN` 以外の場所で動いているプロセスで、止めてよいものは止めてください。

```bash
kill <PID>
```

### 3-2. SSH を1本つないだままにする

`user01` は linger（ログアウト後もサービスを残す設定）が無効です。そのため、**このアカウントの SSH 接続がすべて切れると、全員の JupyterLab が止まります。**

開催中は、運営者の SSH を1本つないだままにしてください（監視用のターミナルを兼ねると便利です）。

次のコマンドが権限エラーにならずに通れば、この心配はなくなります。

```bash
loginctl enable-linger
```

### 3-3. 起動する

```bash
bash infra/multiuser/handson.sh start       # 10人分（人数を変えるなら start 8 など）
bash infra/multiuser/handson.sh status
```

全員分と `web`（教材ページ）が `active` になっていれば完了です。

---

## 4. 開催中

### 4-1. 監視

```bash
bash infra/multiuser/handson.sh status      # 各参加者の RAM と、GPU を使っているプロセス
free -h                                     # 統合メモリ全体の空き
```

GB10 は CPU と GPU がメモリを共有しています。`status` の RAM 列には GPU に確保した分が含まれません。下の「GPU 使用中のプロセス」の一覧とあわせて見てください。

### 4-2. 章ごとに上限を切り替える

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
| 参加者のブラウザで何も開かない | ① `status` でその番号が `active` か確認 → ② 参加者の SSH トンネルが張られているか（`ssh -N -L ...` のウィンドウが開いたままか）→ ③ URL の番号とトークンが本人のものか |
| 教材ページが開かない | `status` で `web` が `active` か確認し、止まっていれば `start` を実行します（起動済みの JupyterLab には影響しません）。参加者の SSH コマンドに `-L 8800:localhost:8800` が入っているかも確認してください |
| 教材ページで数式が崩れる・リンクが開けない | JupyterLab の中で HTML を開いています。`http://localhost:8800/` から開くよう案内してください |
| 1人だけ調子が悪い（固まった・遅い） | `systemctl --user restart handson-pNN`（例: `handson-p03`）。上限もトークンも変わりません |
| 全員つながらなくなった | `user01` の SSH が全部切れて止まった可能性があります。`bash infra/multiuser/handson.sh start` で起動し直してください（作業ファイルと URL はそのまま） |
| 参加者のカーネルが勝手に落ちる | RAM 上限（cgroup）に当たった可能性があります。`journalctl --user -u handson-pNN -n 50` で確認し、必要なら上限を上げて再起動します |
| `OutOfMemoryError` が出る | GPU 上限に当たっています。参加者にはカーネルの再起動と batch size の縮小を案内します。全員が当たるようなら、上限値を見直してください |
| DGX 全体が重い・止まりそう | `free -h` と `status` で使いすぎている人を特定し、`systemctl --user restart handson-pNN` で再起動します |
| 順番待ちが進まない | `status` で学習中の人を確認します。放置されているなら、その人のカーネルを止めると枠が空きます |
| モデルが見つからないエラー（オフライン） | 事前ダウンロードが漏れています。`infra/required_assets.py` に追加して `predownload.sh` を実行してください |

---

## 6. 終了後

```bash
bash infra/multiuser/handson.sh stop
```

- 止めた時点で、参加者の URL は使えなくなります
- 参加者に成果物を持ち帰ってもらう場合は、止める前に JupyterLab からダウンロードしてもらってください
- 次回の開催で作業ディレクトリをまっさらにしたいときは `~/handson-work` を削除します。削除するとトークンも作り直されるので、URL を配り直す必要があります

```bash
rm -rf ~/handson-work
```

---

## 7. 教材を直したとき

| 変更の内容 | やること |
|---|---|
| Web ページの修正 | 何もしなくてよい（教材ページのサーバーはリポジトリの `chapter*/web` をそのまま配信しています）。開催中でも反映されます |
| ノートブックの修正（開催前） | `bash infra/multiuser/handson.sh refresh` で配り直す。URL は変わりません。参加者の編集は消えるので、**開催中は使わないでください** |
| 新しいモデル・データセットを使う | `infra/required_assets.py` に追加し、`bash infra/predownload.sh` を実行 |
| `infra/multiuser/ipython_startup.py` の修正 | `stop` してから `start` し直す（起動時にコピーされます） |

---

## 付録: 設定値の一覧

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
| `infra/multiuser/handson.sh` | JupyterLab と教材ページの起動・停止・状態表示・URL 発行・教材の配り直し |
| `infra/multiuser/ipython_startup.py` | カーネル起動時の GPU メモリ上限と `gpu_slot()` |
| `infra/multiuser/gpu_queue.sh` | スクリプトで学習するときの同時実行制御 |
| `infra/required_assets.py` | 事前ダウンロードするモデル・データセットの一覧 |
| `~/handson-work/pNN/.token` | 参加者のトークン（URL に含まれる） |
