import sys
import importlib
from types import SimpleNamespace
from datetime import datetime
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.append(str(root / 'src'))

import src.utils.sort_utils as su


def test_sort_tasks():
    t1 = SimpleNamespace(title='B', due_date=datetime(2024,1,2), completion_date=None, deletion_date=None, updated_at=1, created_at=1)
    t2 = SimpleNamespace(title='A', due_date=datetime(2024,1,1), completion_date=None, deletion_date=None, updated_at=2, created_at=2)
    out = su.sort_tasks([t1, t2], 'Title', False)
    assert out[0] is t2
    out = su.sort_tasks([t1, t2], 'Due Date', True)
    assert out[0] is t1


def test_sort_group_tasks():
    t1 = SimpleNamespace(title='B', due_date=None, completion_date=datetime(2024,1,2), deletion_date=None, updated_at=1, created_at=1, user_id='u1')
    t2 = SimpleNamespace(title='A', due_date=None, completion_date=datetime(2024,1,1), deletion_date=None, updated_at=2, created_at=2, user_id='u2')
    g = [('G1', t1), ('G2', t2)]
    out = su.sort_group_tasks(g, 'Group', True)
    assert out[0][0] == 'G2'
