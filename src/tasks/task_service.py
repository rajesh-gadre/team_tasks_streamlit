import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from src.database.models import Task, TaskStatus
from src.tasks.task_repository import get_task_repository
logger = logging.getLogger(__name__)

class TaskService:

    def __init__(self):
        self.repository = get_task_repository()

    def get_all_tasks_for_user(self, user_id: str) -> List[Task]:
        logger.info(f'Getting all tasks for user {user_id}')
        return self.repository.get_all_tasks_for_user(user_id)

    def get_active_tasks(self, user_id: str) -> List[Task]:
        logger.info(f'Getting active tasks for user {user_id}')
        return self.repository.get_active_tasks(user_id)

    def get_completed_tasks(self, user_id: str) -> List[Task]:
        logger.info(f'Getting completed tasks for user {user_id}')
        return self.repository.get_completed_tasks(user_id)

    def get_deleted_tasks(self, user_id: str) -> List[Task]:
        logger.info(f'Getting deleted tasks for user {user_id}')
        return self.repository.get_deleted_tasks(user_id)

    def get_task(self, user_id: str, task_id: str) -> Optional[Task]:
        logger.info(f'Getting task {task_id} for user {user_id}')
        return self.repository.get_task(user_id, task_id)

    def get_all_tasks(self) -> List[Task]:
        logger.info(f'Getting all tasks for all users')
        return self.repository.get_all_tasks()

    def create_task(self, user_id: str, task_data: Dict[str, Any]) -> str:
        logger.info(f'Creating task for user {user_id}')
        due_date = task_data.get('due_date') or datetime.now() + timedelta(days=7)
        task = Task(user_id=user_id, title=task_data.get('title'), description=task_data.get('description'), due_date=due_date, notes=task_data.get('notes'), owner_id=task_data.get('owner_id', user_id), owner_email=task_data.get('owner_email'), owner_name=task_data.get('owner_name'))
        task.updates = [{'timestamp': datetime.now(), 'user': user_id, 'updateText': 'Task created'}]
        return self.repository.create_task(task)

    def update_task(self, user_id: str, task_id: str, task_data: Dict[str, Any]) -> bool:
        logger.info(f'Updating task {task_id} for user {user_id}')
        db_task_data = {}
        if 'title' in task_data:
            db_task_data['title'] = task_data['title']
        if 'description' in task_data:
            db_task_data['description'] = task_data['description']
        if 'due_date' in task_data:
            db_task_data['dueDate'] = task_data['due_date']
        if 'notes' in task_data:
            db_task_data['notes'] = task_data['notes']
        if 'status' in task_data:
            db_task_data['status'] = task_data['status']
        return self.repository.update_task(user_id, task_id, db_task_data)

    def delete_task(self, user_id: str, task_id: str) -> bool:
        logger.info(f'Deleting task {task_id} for user {user_id}')
        return self.repository.delete_task(user_id, task_id)

    def restore_task(self, user_id: str, task_id: str) -> bool:
        logger.info(f'Restoring task {task_id} for user {user_id}')
        return self.repository.restore_task(user_id, task_id)

    def complete_task(self, user_id: str, task_id: str) -> bool:
        logger.info(f'Completing task {task_id} for user {user_id}')
        return self.repository.complete_task(user_id, task_id)

    def assign_tasks(self, task_ids: List[str], new_user_id: str) -> bool:
        logger.info(f'Assigning tasks {task_ids} to user {new_user_id}')
        return self.repository.assign_tasks(task_ids, new_user_id)
_task_service: Optional[TaskService] = None

def get_task_service() -> TaskService:
    global _task_service
    if _task_service is None:
        _task_service = TaskService()
    return _task_service
