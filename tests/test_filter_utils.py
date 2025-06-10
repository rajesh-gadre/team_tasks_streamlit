import sys
from types import SimpleNamespace
from pathlib import Path
root = Path(__file__).resolve().parents[1]
sys.path.append(str(root / 'src'))

from utils.filter_utils import filter_tasks_by_tags


def test_filter_tasks_by_tags():
    t1 = SimpleNamespace(tags=['work', 'urgent'])
    t2 = SimpleNamespace(tags=['home'])
    out = filter_tasks_by_tags([t1, t2], 'work')
    assert out == [t1]
    out = filter_tasks_by_tags([t1, t2], '')
    assert out == [t1, t2]
