"""
Task repository module for the Task Management System.
Handles data access operations for tasks in Firestore.
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from src.database.firestore import get_client
from src.database.models import Task, TaskStatus

logger = logging.getLogger(__name__)

class TaskRepository:
    """Repository for task data access operations."""
    
    def __init__(self):
        """Initialize task repository with Firestore client."""
        self.collection = 'tasks'
        self.db = get_client()

    def get_all_tasks(self) -> List[Task]:
        try:
            tasks_data = self.db.query(self.collection, order_by='updatedAt', direction='DESCENDING')
            return [Task.from_dict(task_data) for task_data in tasks_data]
        except Exception as e:
            logger.error(f"Error getting all tasks: {str(e)}")
            raise
    
    def get_active_tasks(self, user_id: str) -> List[Task]:
        """
        Get active tasks for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of active Task objects
        """
        try:
            filters = [
                ('userId', '==', user_id),
                ('status', '==', TaskStatus.ACTIVE)
            ]
            tasks_data = self.db.query(self.collection, filters=filters, order_by='updatedAt', direction='DESCENDING')
            return [Task.from_dict(task_data) for task_data in tasks_data]
        except Exception as e:
            logger.error(f"Error getting active tasks for user {user_id}: {str(e)}")
            raise
    
    def get_completed_tasks(self, user_id: str) -> List[Task]:
        """
        Get completed tasks for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of completed Task objects
        """
        try:
            filters = [
                ('status', '==', TaskStatus.COMPLETED),
                ('userId', '==', user_id)
            ]
            tasks_data = self.db.query(self.collection, filters=filters, order_by='updatedAt', direction='DESCENDING')
            return [Task.from_dict(task_data) for task_data in tasks_data]
        except Exception as e:
            logger.error(f"Error getting completed tasks for user {user_id}: {str(e)}")
            raise
    
    def get_deleted_tasks(self, user_id: str) -> List[Task]:
        """
        Get deleted tasks for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of deleted Task objects
        """
        try:
            filters = [
                ('userId', '==', user_id),
                ('status', '==', TaskStatus.DELETED)
            ]
            tasks_data = self.db.query(self.collection, filters=filters, order_by='updatedAt', direction='DESCENDING')
            return [Task.from_dict(task_data) for task_data in tasks_data]
        except Exception as e:
            logger.error(f"Error getting deleted tasks for user {user_id}: {str(e)}")
            raise
    
    def get_task(self, user_id: str, task_id: str) -> Optional[Task]:
        """
        Get a specific task by ID.
        
        Args:
            user_id: User identifier
            task_id: Task identifier
            
        Returns:
            Task object or None if not found
        """
        try:
            task_data = self.db.read(self.collection, task_id)
            if not task_data:
                logger.warning(f"Task {task_id} not found")
                return None
            if task_data.get('userId') != user_id:
                logger.warning(f"Task {task_id} does not belong to user {user_id}")
                return None
            return Task.from_dict(task_data)
        except Exception as e:
            logger.error(f"Error getting task {task_id} for user {user_id}: {str(e)}")
            raise
    
    def create_task(self, task: Task) -> str:
        """
        Create a new task.
        
        Args:
            task: Task object to create
            
        Returns:
            ID of the created task
        """
        try:
            task_data = task.to_dict()
            if 'createdAt' not in task_data:
                task_data['createdAt'] = datetime.now()
            task_id = self.db.create(self.collection, task_data)
            logger.info(f"Task created with ID: {task_id}")
            return task_id
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            raise
    
    def update_task(self, user_id: str, task_id: str, task_data: Dict[str, Any]) -> bool:
        """
        Update an existing task.
        
        Args:
            user_id: User identifier
            task_id: Task identifier
            task_data: Updated task data
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            existing_task = self.get_task(user_id, task_id)
            if not existing_task:
                logger.warning(f"Task {task_id} not found or does not belong to user {user_id}")
                return False
            task_data['updatedAt'] = datetime.now()
            result = self.db.update(self.collection, task_id, task_data)
            logger.info(f"Task {task_id} updated")
            return result
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {str(e)}")
            raise
    
    def delete_task(self, user_id: str, task_id: str) -> bool:
        """
        Soft-delete a task by setting its status to DELETED.
        
        Args:
            user_id: User identifier
            task_id: Task identifier
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            existing_task = self.get_task(user_id, task_id)
            if not existing_task:
                logger.warning(f"Task {task_id} not found or does not belong to user {user_id}")
                return False
            update_data = {
                'status': TaskStatus.DELETED,
                'deletionDate': datetime.now()
            }
            if not existing_task.updates:
                existing_task.updates = []
            update_entry = {
                'timestamp': datetime.now(),
                'user': user_id,
                'updateText': 'Task deleted'
            }
            update_data['updates'] = existing_task.updates + [update_entry]
            result = self.db.update(self.collection, task_id, update_data)
            logger.info(f"Task {task_id} soft-deleted")
            return result
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {str(e)}")
            raise
    
    def restore_task(self, user_id: str, task_id: str) -> bool:
        """
        Restore a deleted task by setting its status to ACTIVE.
        
        Args:
            user_id: User identifier
            task_id: Task identifier
            
        Returns:
            True if restoration was successful, False otherwise
        """
        try:
            existing_task = self.get_task(user_id, task_id)
            if not existing_task:
                logger.warning(f"Task {task_id} not found or does not belong to user {user_id}")
                return False
            if existing_task.status != TaskStatus.DELETED:
                logger.warning(f"Task {task_id} is not deleted, cannot restore")
                return False
            update_data = {
                'status': TaskStatus.ACTIVE,
                'deletionDate': None
            }
            if not existing_task.updates:
                existing_task.updates = []
            update_entry = {
                'timestamp': datetime.now(),
                'user': user_id,
                'updateText': 'Task restored'
            }
            update_data['updates'] = existing_task.updates + [update_entry]
            result = self.db.update(self.collection, task_id, update_data)
            logger.info(f"Task {task_id} restored")
            return result
        except Exception as e:
            logger.error(f"Error restoring task {task_id}: {str(e)}")
            raise
    
    def complete_task(self, user_id: str, task_id: str) -> bool:
        """
        Mark a task as completed.
        
        Args:
            user_id: User identifier
            task_id: Task identifier
            
        Returns:
            True if completion was successful, False otherwise
        """
        try:
            existing_task = self.get_task(user_id, task_id)
            if not existing_task:
                logger.warning(f"Task {task_id} not found or does not belong to user {user_id}")
                return False
            if existing_task.status != TaskStatus.ACTIVE:
                logger.warning(f"Task {task_id} is not active, cannot complete")
                return False
            update_data = {
                'status': TaskStatus.COMPLETED,
                'completionDate': datetime.now()
            }
            if not existing_task.updates:
                existing_task.updates = []
            update_entry = {
                'timestamp': datetime.now(),
                'user': user_id,
                'updateText': 'Task completed'
            }
            update_data['updates'] = existing_task.updates + [update_entry]
            result = self.db.update(self.collection, task_id, update_data)
            logger.info(f"Task {task_id} marked as completed")
            return result
        except Exception as e:
            logger.error(f"Error completing task {task_id}: {str(e)}")
            raise
_task_repository: Optional[TaskRepository] = None


def get_task_repository() -> TaskRepository:
    """Return the TaskRepository singleton."""
    global _task_repository
    if _task_repository is None:
        _task_repository = TaskRepository()
    return _task_repository
