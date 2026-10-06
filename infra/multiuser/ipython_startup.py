# handson.sh が各参加者の IPYTHONDIR に配置する。カーネル起動時に1回だけ実行される。
#
# 1. GPU メモリ上限
#    GB10 は CPU と GPU がメモリを共有しており、cgroup の MemoryMax は GPU 確保分を
#    数えない（実測）。そのため PyTorch のアロケータ側で GPU メモリに上限をかける。
#    上限を超えると torch.OutOfMemoryError になり、他の参加者のカーネルは巻き込まない。
#
# 2. gpu_slot()
#    重い学習（第2章 SFT/DPO）の同時実行数を HANDSON_GPU_SLOTS 本に制限する。
#    gpu_queue.sh と同じロックファイルを使うので、ノートブックとスクリプトで枠を共有する。
#    カーネルが落ちるとファイル記述子が閉じ、ロックは自動で解放される。
#        with gpu_slot():
#            trainer.train()
import contextlib
import fcntl
import os
import time

_gpu_gb = float(os.environ.get("HANDSON_GPU_GB", "0") or 0)
if _gpu_gb > 0:
    try:
        import torch

        if torch.cuda.is_available():
            _total = torch.cuda.get_device_properties(0).total_memory
            torch.cuda.set_per_process_memory_fraction(min(1.0, _gpu_gb * 1024**3 / _total))
            print(f"[handson] {os.environ.get('HANDSON_PARTICIPANT', '')}: GPU メモリ上限 {_gpu_gb:g} GB")
    except Exception as e:  # 上限設定の失敗でカーネル起動を止めない
        print(f"[handson] GPU メモリ上限の設定に失敗: {e}")


@contextlib.contextmanager
def gpu_slot():
    slots = int(os.environ.get("HANDSON_GPU_SLOTS", "2"))
    lock_dir = os.path.join(
        os.environ.get("HANDSON_WORK_ROOT", os.path.expanduser("~/handson-work")), ".gpu-locks"
    )
    os.makedirs(lock_dir, exist_ok=True)
    waited = False
    while True:
        for i in range(1, slots + 1):
            f = open(os.path.join(lock_dir, f"slot{i}"), "a")
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                f.close()
                continue
            print(f"[handson] GPU スロット {i}/{slots} を確保しました。学習を開始します。")
            try:
                yield
            finally:
                f.close()
            return
        if not waited:
            print(f"[handson] GPU スロット（{slots}本）が埋まっています。空くまで待機します...（■ で中断可）")
            waited = True
        time.sleep(10)
