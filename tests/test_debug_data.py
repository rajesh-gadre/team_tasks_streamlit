import sys
from types import SimpleNamespace
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / 'src'))

from eval.debug_data import get_eval_inputs, get_eval_results


def test_get_eval_inputs(monkeypatch):
    client = SimpleNamespace(get_all=lambda c: ['i'])
    monkeypatch.setattr('eval.debug_data.get_client', lambda: client)
    result = get_eval_inputs()
    assert result == ['i']


def test_get_eval_results(monkeypatch):
    client = SimpleNamespace(get_all=lambda c: ['r'])
    monkeypatch.setattr('eval.debug_data.get_client', lambda: client)
    result = get_eval_results()
    assert result == ['r']
