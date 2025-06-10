from datetime import datetime
from typing import List, Tuple

from src.database.models import Task


def sort_tasks(tasks: List[Task], column: str, descending: bool = False) -> List[Task]:
    key_map = {
        'Title': lambda t: (t.title or '').lower(),
        'Due Date': lambda t: t.due_date or datetime.min,
        'Completed Date': lambda t: t.completion_date or datetime.min,
        'Deleted Date': lambda t: t.deletion_date or datetime.min,
    }
    key = key_map.get(column, lambda t: t.updated_at or t.created_at or datetime.min)
    return sorted(tasks, key=key, reverse=descending)


def sort_group_tasks(tasks: List[Tuple[str, Task]], column: str, descending: bool = False) -> List[Tuple[str, Task]]:
    key_map = {
        'Group': lambda r: (r[0] or '').lower(),
        'Title': lambda r: (r[1].title or '').lower(),
        'Due Date': lambda r: r[1].due_date or datetime.min,
        'Completed Date': lambda r: r[1].completion_date or datetime.min,
        'Deleted Date': lambda r: r[1].deletion_date or datetime.min,
    }
    key = key_map.get(column, lambda r: r[1].updated_at or r[1].created_at or datetime.min)
    return sorted(tasks, key=key, reverse=descending)
