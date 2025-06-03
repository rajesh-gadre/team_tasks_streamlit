"""
Task service module for the Task Management System.
Implements business logic for task operations.
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from src.database.models import Task, TaskStatus
from src.tasks.task_repository import task_repository

logger = logging.getLogger(__name__)

class TaskService:
    """Service for task business logic."""
    
    def __init__(self):
        """Initialize task service with task repository."""
        self.repository = task_repository

    def get_all_tasks(self, user_id: str) -> List[Task]:
        logger.info(f"Getting all tasks for user {user_id}")
        return self.repository.get_all_tasks(user_id)
    
    def get_active_tasks(self, user_id: str) -> List[Task]:
        """
        Get active tasks for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of active Task objects
        """
        logger.info(f"Getting active tasks for user {user_id}")
        return self.repository.get_active_tasks(user_id)
    
    def get_completed_tasks(self, user_id: str) -> List[Task]:
        """
        Get completed tasks for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of completed Task objects
        """
        logger.info(f"Getting completed tasks for user {user_id}")
        return self.repository.get_completed_tasks(user_id)
    
    def get_deleted_tasks(self, user_id: str) -> List[Task]:
        """
        Get deleted tasks for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of deleted Task objects
        """
        logger.info(f"Getting deleted tasks for user {user_id}")
        return self.repository.get_deleted_tasks(user_id)
    
    def get_task(self, user_id: str, task_id: str) -> Optional[Task]:
        """
        Get a specific task by ID.
        
        Args:
            user_id: User identifier
            task_id: Task identifier
            
        Returns:
            Task object or None if not found
        """
        logger.info(f"Getting task {task_id} for user {user_id}")
        return self.repository.get_task(user_id, task_id)
    
    def create_task(self, user_id: str, task_data: Dict[str, Any]) -> str:
        """
        Create a new task.
        
        Args:
            user_id: User identifier
            task_data: Task data dictionary
            
        Returns:
            ID of the created task
        """
        logger.info(f"Creating task for user {user_id}")
        task = Task(
            user_id=user_id,
            title=task_data.get('title'),
            description=task_data.get('description'),
            due_date=task_data.get('due_date'),
            notes=task_data.get('notes')
        )
        task.updates = [{
            'timestamp': datetime.now(),
            'user': user_id,
            'updateText': 'Task created'
        }]
        return self.repository.create_task(task)
    
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
        logger.info(f"Updating task {task_id} for user {user_id}")
        db_task_data = {}
        if 'title' in task_data:
            db_task_data['title'] = task_data['title']
        if 'description' in task_data:
            db_task_data['description'] = task_data['description']
        if 'due_date' in task_data:
            db_task_data['dueDate'] = task_data['due_date']
        if 'notes' in task_data:
            db_task_data['notes'] = task_data['notes']
        return self.repository.update_task(user_id, task_id, db_task_data)
    
    def delete_task(self, user_id: str, task_id: str) -> bool:
        """
        Soft-delete a task.
        
        Args:
            user_id: User identifier
            task_id: Task identifier
            
        Returns:
            True if deletion was successful, False otherwise
        """
        logger.info(f"Deleting task {task_id} for user {user_id}")
        return self.repository.delete_task(user_id, task_id)
    
    def restore_task(self, user_id: str, task_id: str) -> bool:
        """
        Restore a deleted task.
        
        Args:
            user_id: User identifier
            task_id: Task identifier
            
        Returns:
            True if restoration was successful, False otherwise
        """
        logger.info(f"Restoring task {task_id} for user {user_id}")
        return self.repository.restore_task(user_id, task_id)
    
    def complete_task(self, user_id: str, task_id: str) -> bool:
        """
        Mark a task as completed.
        
        Args:
            user_id: User identifier
            task_id: Task identifier
            
        Returns:
            True if completion was successful, False otherwise
        """
        logger.info(f"Completing task {task_id} for user {user_id}")
        return self.repository.complete_task(user_id, task_id)

# Create an instance for use in the application
task_service = TaskService()
