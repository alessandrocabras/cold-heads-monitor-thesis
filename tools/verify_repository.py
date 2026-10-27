"""Offline integrity checks; use --model for the optional trusted-pickle check."""

import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys
import warnings


ROOT = Path(__file__).resolve().parents[1]


def check_sources():
    python_files = [*ROOT.glob('*.py'), *ROOT.joinpath('tools').glob('*.py')]
    for path in python_files:
        ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path.relative_to(ROOT)))

    notebooks = [*ROOT.joinpath('training_notebooks').glob('*.ipynb'),
                 *ROOT.joinpath('archive').rglob('*.ipynb')]
    for path in notebooks:
        notebook = json.loads(path.read_text(encoding='utf-8'))
        assert notebook['nbformat'] == 4, path
        for index, cell in enumerate(notebook['cells']):
            if cell['cell_type'] != 'code':
                continue
            assert not cell.get('outputs'), (path, index, 'stale output')
            assert cell.get('execution_count') is None, (path, index, 'stale count')
            if 'archive' not in path.relative_to(ROOT).parts:
                ast.parse(''.join(cell['source']), filename=f'{path.name}:cell{index}')
    print(f'PASS: syntax of {len(python_files)} Python files; {len(notebooks)} clean notebooks')


def check_integrity():
    entries = json.loads((ROOT / 'reports/artifact_hashes.json').read_text(encoding='utf-8'))
    for relative, expected in entries.items():
        path = ROOT / relative
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual == expected, f'Hash mismatch: {relative}'
    print(f'PASS: SHA-256 of {len(entries)} supplied artifacts')


def check_model():
    import joblib
    import numpy as np
    import sklearn
    from sklearn.exceptions import InconsistentVersionWarning
    from sklearn.pipeline import Pipeline

    if sklearn.__version__ != '1.6.1':
        raise RuntimeError('Install requirements.txt: supplied model requires scikit-learn 1.6.1.')
    with warnings.catch_warnings():
        warnings.simplefilter('error', InconsistentVersionWarning)
        model = joblib.load(ROOT / 'random_forest_model_candidate.pkl')
    assert isinstance(model, Pipeline)
    assert list(model.named_steps) == ['scaler', 'classifier']
    assert model.n_features_in_ == 128
    assert model.classes_.tolist() == [0, 1, 2]
    assert model.named_steps['scaler'].n_samples_seen_ == 93750
    assert model.named_steps['classifier'].n_estimators == 300
    prediction = model.predict(np.full((1, 128), 2.5))
    assert prediction.shape == (1,) and int(prediction[0]) in (0, 1, 2)
    print('PASS: supplied pipeline loads and predicts (interface check, not an accuracy test)')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', action='store_true', help='Load the trusted supplied model')
    args = parser.parse_args()
    check_sources()
    check_integrity()
    if args.model:
        check_model()


if __name__ == '__main__':
    sys.path.insert(0, str(ROOT))
    main()
