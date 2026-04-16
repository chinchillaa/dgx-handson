#!/usr/bin/env python
"""
check_env.py  —  DGX ハンズオン環境確認スクリプト

使い方:
    python infra/check_env.py

確認項目:
    1. Python バージョン
    2. GPU 情報（台数・VRAM・CUDA バージョン）
    3. 必須パッケージのバージョン
    4. 共有ストレージの存在・空き容量
    5. HuggingFace ログイン状態
    6. ダウンロード済みモデル・データセットの確認
"""

import sys
import os
import shutil
import subprocess
from pathlib import Path

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
# Section 4: 共有ストレージ
# =============================================================================
section('4. 共有ストレージ')

SHARED_ROOT = Path('/data/shared')

if SHARED_ROOT.exists():
    ok(f'共有ストレージ: {SHARED_ROOT}')

    # 空き容量
    total, used, free = shutil.disk_usage(SHARED_ROOT)
    free_gb  = free  / 1024**3
    total_gb = total / 1024**3
    used_pct = used / total * 100

    if free_gb >= 20:
        ok(f'空き容量: {free_gb:.1f} GB / {total_gb:.1f} GB  (使用率 {used_pct:.0f}%)')
    elif free_gb >= 5:
        warn(f'空き容量: {free_gb:.1f} GB / {total_gb:.1f} GB  (使用率 {used_pct:.0f}%)')
    else:
        fail(f'空き容量が少ない: {free_gb:.1f} GB — モデルダウンロードに支障が出る可能性があります')
        ISSUES.append(f'共有ストレージの空き容量が {free_gb:.1f} GB しかありません')

    # データセット確認
    datasets_dir = SHARED_ROOT / 'datasets'
    if datasets_dir.exists():
        ok(f'datasets/ ディレクトリ存在: {datasets_dir}')
        mnist_dir = datasets_dir / 'MNIST'
        if mnist_dir.exists():
            ok(f'MNIST データセット: ダウンロード済み')
        else:
            warn(f'MNIST データセット: 未ダウンロード → bash infra/predownload.sh を実行してください')
    else:
        warn(f'datasets/ ディレクトリなし → bash infra/predownload.sh を実行してください')

    # モデル確認
    models_dir = SHARED_ROOT / 'models'
    if models_dir.exists():
        ok(f'models/ ディレクトリ存在: {models_dir}')
        # Llama モデルの確認
        hub_dir = models_dir / 'hub'
        llama_exists = False
        if hub_dir.exists():
            for d in hub_dir.iterdir():
                if 'llama-3.2-1b' in d.name.lower() or 'llama-3_2-1b' in d.name.lower():
                    llama_exists = True
                    model_size = sum(
                        f.stat().st_size
                        for f in d.rglob('*') if f.is_file()
                    )
                    ok(f'Llama-3.2-1B: ダウンロード済み ({model_size / 1024**3:.1f} GB)')
                    break
        if not llama_exists:
            warn('Llama-3.2-1B: 未ダウンロード → bash infra/predownload.sh を実行してください')
    else:
        warn(f'models/ ディレクトリなし → bash infra/predownload.sh を実行してください')

else:
    warn(f'共有ストレージ ({SHARED_ROOT}) が見つかりません')
    warn('DGX 上では /data/shared/ が利用可能なはずです。管理者に確認してください。')
    warn('ローカル実行の場合は ~/.cache/huggingface と ./data が使用されます。')

# =============================================================================
# Section 5: HuggingFace ログイン状態
# =============================================================================
section('5. HuggingFace 認証')

hf_token = os.environ.get('HF_TOKEN', '')
if hf_token:
    ok(f'HF_TOKEN 環境変数が設定されています')
else:
    try:
        from huggingface_hub import whoami
        info = whoami()
        ok(f'HuggingFace ログイン済み: {info["name"]}')
    except Exception:
        warn('HuggingFace 未ログインです')
        warn('Llama モデルには認証が必要です:')
        print(f'{AMBER}       hf auth login{RESET}')
        print(f'{AMBER}       # または: export HF_TOKEN=hf_xxxx{RESET}')
        ISSUES.append('HuggingFace にログインしてください: huggingface-cli login')

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
    print(f'\n  Jupyter Lab を起動するには:')
    print(f'    {GREEN}source .venv/bin/activate && jupyter lab{RESET}\n')
else:
    print(f'\n{BOLD}{AMBER}  {len(ISSUES)} 件の問題が見つかりました:{RESET}')
    for i, issue in enumerate(ISSUES, 1):
        print(f'{AMBER}    {i}. {issue}{RESET}')
    print()
    print(f'  問題を解決するには:')
    print(f'    {GREEN}bash infra/setup.sh{RESET}         # 環境構築')
    print(f'    {GREEN}bash infra/predownload.sh{RESET}   # モデル・データダウンロード\n')
    sys.exit(1)
