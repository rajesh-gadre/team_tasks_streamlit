"""
OpenAI integration module for the Task Management System.
Handles interactions with OpenAI API via Langchain.
"""
import os
import json
import logging
import datetime
from typing import Dict, Optional, Any, List

from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool

from src.tasks.task_service import task_service

from src.database.firestore import firestore_client
from src.database.models import AIChat
from src.ai.prompt_repository import prompt_repository

# Custom JSON encoder to handle Firestore timestamp objects
class FirestoreEncoder(json.JSONEncoder):
    def default(self, obj):
        # Check if object has isoformat method (datetime-like objects)
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        # Handle any other non-serializable objects
        try:
            return str(obj)
        except:
            return None

# Configure logging
logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for OpenAI API interactions."""
    
    def __init__(self):
        """Initialize OpenAI service with API key from environment variables."""
        self.api_key = os.environ.get('OPENAI_API_KEY')
        self.model = os.environ.get('OPENAI_MODEL', 'gpt-4.1-mini')
        
        if not self.api_key:
            logger.error("OpenAI API key not found in environment variables")
            raise ValueError("Missing OpenAI API key")
        
        # Initialize Firestore client for AI chats
        self.db = firestore_client
        self.collection = 'AI_chats'
    
    def process_chat(self, user_id: str, input_text: str) -> Dict[str, Any]:
        """
        Process a chat interaction with OpenAI.
        
        Args:
            user_id: User identifier
            input_text: User input text
            
        Returns:
            Dictionary with chat ID and response
        """
        try:
            # Create chat record in Firestore
            chat_data = {
                'user_id': user_id,
                'inputText': input_text
            }
            
            # Get the list of tasks for the user
            task_list = self._list_tasks(user_id)
            
            # Get system prompt from repository
            system_prompt = self._get_system_prompt()
            
            # Create chat record in Firestore
            chat_id = self.db.create(self.collection, chat_data)
            
            # Process with OpenAI
            response = self._call_openai(system_prompt, input_text, task_list)
            
            # Update chat record with response
            self.db.update(self.collection, chat_id, {'Response': response})
            
            logger.info(f"Chat processed for user {user_id}")
            return {
                'id': chat_id,
                'response': response
            }
        except Exception as e:
            logger.error(f"Error processing chat for user {user_id}: {str(e)}")
            raise
    
    # Define task tools
    def _list_tasks(self, user_id: str):
        """
        Lists all tasks for the current user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with active, completed, and deleted tasks
        """
        try:
            active_tasks = task_service.get_active_tasks(user_id)
            completed_tasks = task_service.get_completed_tasks(user_id)
            deleted_tasks = task_service.get_deleted_tasks(user_id)
            
            # Convert task objects to dictionaries
            active_tasks_dict = [task.to_dict() for task in active_tasks]
            completed_tasks_dict = [task.to_dict() for task in completed_tasks]
            deleted_tasks_dict = [task.to_dict() for task in deleted_tasks]
            
            return {
                "active": active_tasks_dict,
                "completed": completed_tasks_dict,
                "deleted": deleted_tasks_dict
            }
        except Exception as e:
            logger.error(f"Error listing tasks: {str(e)}")
            return {"error": str(e)}
    
    def _add_task(self, user_id: str, task_data_str: str):
        """
        Adds a new task for the current user.
        
        Args:
            user_id: User identifier
            task_data_str: JSON string with task data
            
        Returns:
            Dictionary with task ID and success status
        """
        try:
            # Parse task data from JSON string
            task_data = json.loads(task_data_str)
            
            # Validate required fields
            if "title" not in task_data:
                return {"error": "Task title is required"}
            
            # Create task
            task_id = task_service.create_task(
                user_id=user_id,
                title=task_data.get("title"),
                description=task_data.get("description", ""),
                notes=task_data.get("notes", ""),
                due_date=task_data.get("due_date")
            )
            
            return {"success": True, "task_id": task_id}
        except Exception as e:
            logger.error(f"Error adding task: {str(e)}")
            return {"error": str(e)}
    
    def _update_task(self, user_id: str, task_id: str, update_data_str: str):
        """
        Updates an existing task for the current user.
        
        Args:
            user_id: User identifier
            task_id: Task identifier
            update_data_str: JSON string with fields to update
            
        Returns:
            Dictionary with success status
        """
        try:
            # Parse update data from JSON string
            update_data = json.loads(update_data_str)
            
            # Update task
            task_service.update_task(user_id, task_id, update_data)
            
            return {"success": True}
        except Exception as e:
            logger.error(f"Error updating task: {str(e)}")
            return {"error": str(e)}
    
    def _get_system_prompt(self) -> str:
        """
        Get system prompt for OpenAI.
        
        Returns:
            System prompt text
        """
        DEFAULT_PROMPT = """You are an expert Task manager. Given the user input which includes user's current task-list, first understand the user's goal and figure out what changes need to be made to user's task list."""
        try:
            # Get prompt from repository
            prompt = prompt_repository.get_active_prompt("AI_Tasks")
            
            if prompt:
                return prompt.text
            else:
                # Fallback prompt if none found in repository
                logger.warning("No active AI_Tasks prompt found, using fallback")
                return DEFAULT_PROMPT
        except Exception as e:
            logger.error(f"Error getting system prompt: {str(e)}")
            # Fallback prompt in case of error
            return DEFAULT_PROMPT
    
    def _call_openai(self, system_prompt: str, user_input: str, task_list: Dict[str, Any]) -> str:
        """
        Call OpenAI API with system prompt, user input, and task list.
        
        Args:
            system_prompt: System prompt text
            user_input: User input text
            task_list: Dictionary containing active, completed, and deleted tasks
            
        Returns:
            OpenAI response text with structured output for task changes
        """
        try:
            # Define the schema for structured output
            task_changes_schema = {
                "type": "object",
                "properties": {
                    "new_tasks": {
                        "type": "array",
                        "description": "List of new tasks to add",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "description": "Task title (required)"},
                                "description": {"type": "string", "description": "Task description (optional)"},
                                "notes": {"type": "string", "description": "Additional notes (optional)"},
                                "due_date": {"type": "string", "description": "Due date in YYYY-MM-DD format (optional)"}
                            },
                            "required": ["title"]
                        }
                    },
                    "modified_tasks": {
                        "type": "array",
                        "description": "List of existing tasks to modify",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string", "description": "Task ID (required)"},
                                "title": {"type": "string", "description": "New task title (optional)"},
                                "description": {"type": "string", "description": "New task description (optional)"},
                                "notes": {"type": "string", "description": "New additional notes (optional)"},
                                "due_date": {"type": "string", "description": "New due date in YYYY-MM-DD format (optional)"}
                            },
                            "required": ["id"]
                        }
                    },
                    "summary": {"type": "string", "description": "A summary of the changes made to the task list"}
                },
                "required": ["new_tasks", "modified_tasks", "summary"]
            }
            
            # Initialize OpenAI client
            chat = ChatOpenAI(
                api_key=self.api_key,
                model=self.model,
                temperature=0.7
            )
            
            # Clean input (remove any special instructions)
            clean_input = user_input.strip()
            
            # Format task list for inclusion in the prompt
            active_tasks_str = json.dumps(task_list.get('active', []), indent=2, cls=FirestoreEncoder)
            completed_tasks_str = json.dumps(task_list.get('completed', []), indent=2, cls=FirestoreEncoder)
            
            # Create a comprehensive prompt with the task list
            full_prompt = f"{system_prompt}\n\nCurrent active tasks:\n{active_tasks_str}\n\nCompleted tasks:\n{completed_tasks_str}\n\nBased on the user's request, determine what changes need to be made to the task list."
            
            # Prepare messages
            messages = [
                SystemMessage(content=full_prompt),
                HumanMessage(content=clean_input)
            ]
            
            logger.info("Calling OpenAI with structured output schema")
            
            # Call OpenAI with structured output
            try:
                response = chat.with_structured_output(task_changes_schema).invoke(messages)
                
                # Process the structured response
                new_tasks = response.new_tasks
                modified_tasks = response.modified_tasks
                summary = response.summary
                
                # Log the structured response
                logger.info(f"Structured response: {json.dumps(response.__dict__, cls=FirestoreEncoder)}")
                
                # Apply the changes to the task list
                for new_task in new_tasks:
                    task_data_str = json.dumps(new_task, cls=FirestoreEncoder)
                    self._add_task(user_id, task_data_str)
                
                for modified_task in modified_tasks:
                    task_id = modified_task.pop('id')
                    update_data_str = json.dumps(modified_task, cls=FirestoreEncoder)
                    self._update_task(user_id, task_id, update_data_str)
                
                # Return the summary
                return summary
                
            except Exception as e:
                logger.error(f"Error with structured output: {str(e)}")
                # Fallback to regular chat completion
                response = chat.invoke(messages)
                return response.content
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            return f"I encountered an error while processing your request: {str(e)}"
            # Don't raise the exception to provide a better user experience

# Create an instance for use in the application
openai_service = OpenAIService()
