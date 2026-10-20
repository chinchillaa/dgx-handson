# テスト専用: dolly-15k-ja を偽の JSON に差し替える（DGX では使わない）
import datasets, glob, os
_orig = datasets.load_dataset
def _fake(path, *a, **k):
    if path == 'kunishou/databricks-dolly-15k-ja':
        f = glob.glob(os.environ['HF_HOME'] + '/hub/datasets--kunishou--databricks-dolly-15k-ja/snapshots/*/*.json')[0]
        return _orig('json', data_files=f, split=k.get('split', 'train'))
    return _orig(path, *a, **k)
datasets.load_dataset = _fake
