from typing import Iterable, List, Tuple
from src.database.models import Task


def filter_tasks_by_tags(tasks: Iterable[Task] | Iterable[Tuple[str, Task]], query: str) -> List:
    tags = [t.strip().lower() for t in query.split(',') if t.strip()]
    if not tags:
        return list(tasks)
    results = []
    for item in tasks:
        task = item[1] if isinstance(item, tuple) else item
        task_tags = [tag.lower() for tag in getattr(task, 'tags', [])]
        if all(tag in task_tags for tag in tags):
            results.append(item)
    return results
