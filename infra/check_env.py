#!/usr/bin/env python
"""
check_env.py  —  DGX ハンズオン環境確認スクリプト（運営者が本番前に実行）

使い方:
    .venv/bin/python infra/check_env.py

確認項目:
    1. Python バージョン
    2. GPU 情報（GPU 名・メモリ・CUDA バージョン）
    3. 必須パッケージのバージョン
    4. モデル・データセットがオフラインで読み込めるか（当日は HF_HUB_OFFLINE=1）
    5. 参加者用 JupyterLab の起動条件（systemd --user・linger・空きポート）
    6. 動作確認（簡易テスト）
"""

import sys
import os
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
# /opt/handson/app から実行したときは、隣の hf_cache（deploy.sh が配置）を見る。
# huggingface_hub は import 時に HF_HOME を読むので、パッケージを import する前に設定する
if 'HF_HOME' not in os.environ and (REPO_ROOT.parent / 'hf_cache').is_dir():
    os.environ['HF_HOME'] = str(REPO_ROOT.parent / 'hf_cache')
# datasets は読むだけでもキャッシュにロックファイルを書く。共有キャッシュが読み取り専用のとき
# （参加者用アカウントで実行したとき）は、一時ディレクトリにコピーして確認する（handson.sh と同じ扱い）
_ds_cache = Path(os.environ.get('HF_HOME', Path.home() / '.cache' / 'huggingface')) / 'datasets'
if 'HF_DATASETS_CACHE' not in os.environ and _ds_cache.is_dir() and not os.access(_ds_cache, os.W_OK):
    import tempfile
    _tmp = Path(tempfile.mkdtemp(prefix='check_env_datasets_'))
    shutil.copytree(_ds_cache, _tmp, dirs_exist_ok=True, ignore=shutil.ignore_patterns('*.lock'))
    os.environ['HF_DATASETS_CACHE'] = str(_tmp)
    import atexit
    atexit.register(shutil.rmtree, _tmp, True)

# ── カラー出力 ──────────────────────────────────────────────────────────────
GREEN  = '\033[0;32m'
AMBER  = '\033[0;33m'
RED    = '\033[0;31m'
BOLD   = '\033[1m'
RESET  = '\033[0m'

def ok(msg):    print(f'{GREEN}  ✓  {RESET}{msg}')
def warn(msg):  print(f'{AMBER}  ⚠  {RESET}{msg}')
def fail(msg):  print(f'{RED}  ✗  {RESET}{msg}')
def section(title):
    print(f'\n{BOLD}{GREEN}── {title} {"─" * max(0, 44 - len(title))}{RESET}')

ISSUES = []  # 問題点を収集して最後にまとめて表示

# =============================================================================
# Section 1: Python バージョン
# =============================================================================
section('1. Python')

py_version = sys.version_info
py_str = f'{py_version.major}.{py_version.minor}.{py_version.micro}'
py_path = sys.executable

if py_version >= (3, 10):
    ok(f'Python {py_str}  ({py_path})')
else:
    fail(f'Python {py_str} — 3.10 以上が必要です')
    ISSUES.append('Python 3.10+ を使用してください')

# =============================================================================
# Section 2: GPU
# =============================================================================
section('2. GPU / CUDA')

try:
    import torch

    if torch.cuda.is_available():
        n_gpus = torch.cuda.device_count()
        ok(f'CUDA 利用可能  (torch.cuda.is_available() = True)')
        ok(f'GPU 台数: {n_gpus}')

        for i in range(n_gpus):
            name   = torch.cuda.get_device_name(i)
            mem_gb = torch.cuda.get_device_properties(i).total_memory / 1024**3
            ok(f'  GPU {i}: {name}  ({mem_gb:.1f} GB VRAM)')

        ok(f'CUDA バージョン: {torch.version.cuda}')
        ok(f'cuDNN バージョン: {torch.backends.cudnn.version()}')
    else:
        warn('CUDA が利用できません（CPU モードで動作します）')
        warn('ハンズオン③ の LLM 推論が遅くなります（CPU で約 1〜2 分/生成）')
        ISSUES.append('GPU が検出されませんでした。DGX 上で実行しているか確認してください。')

except ImportError:
    fail('PyTorch がインストールされていません')
    ISSUES.append('PyTorch をインストールしてください: bash infra/setup.sh')

# =============================================================================
# Section 3: 必須パッケージ
# =============================================================================
section('3. パッケージバージョン')

REQUIRED_PACKAGES = [
    # (パッケージ名, 最低バージョン, 必須か, インポート名 or None)
    ('torch',               '2.0.0',  True,  None),
    ('torchvision',         '0.15.0', True,  None),
    ('transformers',        '4.35.0', True,  None),
    ('datasets',            '2.14.0', True,  None),
    ('numpy',               '1.24.0', True,  None),
    ('pandas',              '2.0.0',  True,  None),
    ('matplotlib',          '3.7.0',  True,  None),
    ('scikit-learn',        '1.3.0',  True,  'sklearn'),   # インポート名が異なる
    ('jupyter',             '1.0.0',  False, None),
    ('ipywidgets',          '8.0.0',  False, None),
    ('trl',                 '0.7.0',  True,  None),
    ('peft',                '0.6.0',  True,  None),
    ('langchain',           '0.1.0',  True,  None),
    ('chromadb',            '0.4.0',  True,  None),
    ('sentence_transformers','2.2.0', True,  None),
    ('wandb',               '0.16.0', False, None),
]

import importlib
import importlib.metadata

all_ok = True
for pkg_name, min_ver, required, import_alias in REQUIRED_PACKAGES:
    try:
        # インポート名とパッケージ名が異なるケースに対応
        import_name = import_alias if import_alias else pkg_name.replace('-', '_')
        mod = importlib.import_module(import_name)
        try:
            installed = importlib.metadata.version(pkg_name)
        except importlib.metadata.PackageNotFoundError:
            installed = getattr(mod, '__version__', '?')

        ok(f'{pkg_name:<28} {installed}')

    except ImportError:
        if required:
            fail(f'{pkg_name:<28} インストールされていません  ← 必須')
            ISSUES.append(f'{pkg_name} がインストールされていません')
            all_ok = False
        else:
            warn(f'{pkg_name:<28} インストールされていません  (推奨)')

if all_ok:
    ok('必須パッケージはすべてインストール済みです')

# =============================================================================
# Section 4: モデル・データセット（オフライン読み込み）
# =============================================================================
section('4. モデル・データセット')

sys.path.insert(0, str(Path(__file__).resolve().parent))
from required_assets import MODELS, DATASETS, cached_model_path  # noqa: E402

HF_HOME = os.environ.get('HF_HOME', str(Path.home() / '.cache' / 'huggingface'))
ok(f'HF_HOME: {HF_HOME}')

mnist_raw = REPO_ROOT / 'data' / 'MNIST' / 'raw'
if mnist_raw.exists() and any(mnist_raw.iterdir()):
    ok(f'{"MNIST":<40} {REPO_ROOT / "data"}')
else:
    fail(f'{"MNIST":<40} 未ダウンロード')
    ISSUES.append('MNIST がありません → bash infra/predownload.sh')

for repo_id, purpose, gated in MODELS:
    path = cached_model_path(repo_id)
    if path:
        size_gb = sum(f.stat().st_size for f in Path(path).rglob('*') if f.is_file()) / 1024**3
        ok(f'{repo_id:<40} {size_gb:5.1f} GB  （{purpose}）')
    else:
        fail(f'{repo_id:<40} 未ダウンロード  （{purpose}）')
        hint = '（HF のアクセス申請と HF_TOKEN が必要）' if gated else ''
        ISSUES.append(f'{repo_id} がありません → bash infra/predownload.sh {hint}')

os.environ['HF_HUB_OFFLINE'] = '1'  # 当日と同じ条件で読む
for name, split, purpose in DATASETS:
    try:
        from datasets import load_dataset
        n = len(load_dataset(name, split=split))
        ok(f'{name:<40} {n:,} 件  （{purpose}）')
    except Exception:
        fail(f'{name:<40} 未ダウンロード  （{purpose}）')
        ISSUES.append(f'{name} がありません → bash infra/predownload.sh')

total, used, free = shutil.disk_usage(Path.home())
if free / 1024**3 >= 30:
    ok(f'空き容量: {free / 1024**3:.0f} GB')
else:
    warn(f'空き容量: {free / 1024**3:.0f} GB — 参加者の学習出力（outputs/）で不足する可能性があります')

# =============================================================================
# Section 5: 参加者用 JupyterLab の起動条件
# =============================================================================
section('5. 参加者用 JupyterLab（infra/multiuser/handson.sh）')

def _run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

r = _run(['systemd-run', '--user', '--scope', '-q', '-p', 'MemoryMax=1G', 'true'])
if r.returncode == 0:
    ok('systemd-run --user でメモリ上限（cgroup）をかけられます')
else:
    fail(f'systemd-run --user が使えません: {r.stderr.strip()[:120]}')
    ISSUES.append('systemd --user が使えないため handson.sh が動きません')

r = _run(['loginctl', 'show-user', os.environ.get('USER', ''), '-p', 'Linger', '--value'])
if r.stdout.strip() == 'yes':
    ok('linger 有効: SSH を全部切っても JupyterLab は止まりません')
else:
    warn('linger 無効: このアカウントの SSH 接続が全部切れると JupyterLab も止まります')
    warn('  運営者の SSH を1本つないだままにする（loginctl enable-linger が通れば不要）')

r = _run(['ss', '-ltnH'])
busy = sorted({int(l.split()[3].rsplit(':', 1)[1]) for l in r.stdout.splitlines() if l.split()[3].rsplit(':', 1)[1].isdigit()})
base = int(os.environ.get('HANDSON_BASE_PORT', '8800'))
taken = [p for p in range(base + 1, base + 11) if p in busy]
if not taken:
    ok(f'ポート {base + 1}〜{base + 10} は空いています')
else:
    warn(f'ポート使用中: {taken}（handson.sh 起動済みなら問題なし）')

# =============================================================================
# Section 6: 動作確認（簡易テスト）
# =============================================================================
section('6. 動作確認（簡易テスト）')

# NumPy
try:
    import numpy as np
    arr = np.array([1.0, 2.0, 3.0])
    assert arr.mean() == 2.0
    ok('NumPy: 基本演算 OK')
except Exception as e:
    fail(f'NumPy テスト失敗: {e}')
    ISSUES.append('NumPy が正常に動作しません')

# PyTorch テンソル演算
try:
    import torch
    x = torch.tensor([1.0, 2.0, 3.0])
    y = x * 2 + 1
    assert y.tolist() == [3.0, 5.0, 7.0]
    ok('PyTorch: テンソル演算 OK')
except Exception as e:
    fail(f'PyTorch テスト失敗: {e}')
    ISSUES.append('PyTorch が正常に動作しません')

# PyTorch GPU テスト
try:
    import torch
    if torch.cuda.is_available():
        x = torch.tensor([1.0]).cuda()
        y = x + 1
        assert y.item() == 2.0
        ok(f'PyTorch GPU: テンソル転送・演算 OK')
except Exception as e:
    warn(f'PyTorch GPU テスト失敗: {e}')

# Matplotlib 日本語フォント
try:
    import matplotlib
    matplotlib.use('Agg')  # GUIなし環境でも動作させる
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm

    jp_fonts = [f.name for f in fm.fontManager.ttflist
                if any(kw in f.name.lower() for kw in ['ipa', 'gothic', 'mincho', 'noto'])]
    if jp_fonts:
        ok(f'Matplotlib 日本語フォント: {jp_fonts[0]} など {len(jp_fonts)} 種類検出')
    else:
        warn('Matplotlib 日本語フォントが見つかりません。グラフの日本語が豆腐になる可能性があります。')
        warn('sudo apt-get install -y fonts-ipafont でインストールできます。')
except Exception as e:
    warn(f'Matplotlib チェック失敗: {e}')

# =============================================================================
# 最終サマリー
# =============================================================================
section('サマリー')

if not ISSUES:
    print(f'\n{BOLD}{GREEN}  すべてのチェックが通過しました。ハンズオンを開始できます！{RESET}')
    print(f'\n  参加者用 JupyterLab を起動するには:')
    print(f'    {GREEN}bash infra/multiuser/handson.sh start{RESET}\n')
else:
    print(f'\n{BOLD}{AMBER}  {len(ISSUES)} 件の問題が見つかりました:{RESET}')
    for i, issue in enumerate(ISSUES, 1):
        print(f'{AMBER}    {i}. {issue}{RESET}')
    print()
    print(f'  問題を解決するには:')
    print(f'    {GREEN}bash infra/setup.sh{RESET}         # 環境構築')
    print(f'    {GREEN}bash infra/predownload.sh{RESET}   # モデル・データダウンロード\n')
    sys.exit(1)
