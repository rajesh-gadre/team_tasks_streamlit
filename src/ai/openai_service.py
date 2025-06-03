"""OpenAI service module for the Task Management System."""
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
from pydantic import BaseModel

class FirestoreEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        try:
            return str(obj)
        except:
            return None

logger = logging.getLogger(__name__)

class NewTask(BaseModel):
    title: str
    description: Optional[str] = None
    notes: Optional[str] = None
    due_date: Optional[str] = None

class ModifiedTask(BaseModel):
    id: str
    title: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    due_date: Optional[str] = None
    status: Optional[str] = None


class TaskChanges(BaseModel):
    new_tasks: List[NewTask]
    modified_tasks: List[ModifiedTask]
    summary: str


class OpenAIService:
    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY')
        self.model = os.environ.get('OPENAI_MODEL', 'gpt-4.1-mini')
        if not self.api_key:
            logger.error("OpenAI API key not found in environment variables")
            raise ValueError("Missing OpenAI API key")
        self.db = firestore_client
        self.collection = 'AI_chats'
    
    def process_chat(self, user_id: str, input_text: str) -> Dict[str, Any]:
        try:
            chat_data = {
                'user_id': user_id,
                'inputText': input_text
            }
            task_list = self._list_tasks(user_id)
            system_prompt = self._get_system_prompt()
            chat_id = self.db.create(self.collection, chat_data)
            response = self._call_openai(system_prompt, input_text, task_list)
            self.db.update(self.collection, chat_id, {'Response': response})
            logger.info(f"Chat processed for user {user_id}")
            return {
                'id': chat_id,
                'response': response
            }
        except Exception as e:
            logger.error(f"Error processing chat for user {user_id}: {str(e)}")
            raise
    
    def _list_tasks(self, user_id: str):
        try:
            active_tasks = task_service.get_active_tasks(user_id)
            completed_tasks = task_service.get_completed_tasks(user_id)
            deleted_tasks = task_service.get_deleted_tasks(user_id)
            logger.info(f"Listing tasks for user {user_id}: Active:{active_tasks}, Completed:{completed_tasks}, Deleted:{deleted_tasks}")
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
        try:
            task_data = json.loads(task_data_str)
            if "title" not in task_data:
                return {"error": "Task title is required"}
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
        try:
            update_data = json.loads(update_data_str)
            task_service.update_task(user_id, task_id, update_data)
            return {"success": True}
        except Exception as e:
            logger.error(f"Error updating task: {str(e)}")
            return {"error": str(e)}
    
    def _get_system_prompt(self) -> str:
        DEFAULT_PROMPT = """You are an expert Task manager. Given the user input which includes user's current task-list, first understand the user's goal and figure out what changes need to be made to user's task list."""
        try:
            prompt = prompt_repository.get_active_prompt("AI_Tasks")
            if prompt:
                return prompt.text
            else:
                logger.warning("No active AI_Tasks prompt found, using fallback")
                return DEFAULT_PROMPT
        except Exception as e:
            logger.error(f"Error getting system prompt: {str(e)}")
            return DEFAULT_PROMPT

    def _first_call(self, system_prompt: str, user_input: str, task_list: Dict[str, Any]) -> str:
        try:
            chat = ChatOpenAI(
                api_key=self.api_key,
                model=self.model,
                temperature=0.7
            )
            clean_input = user_input.strip()
            active_tasks_str = json.dumps(task_list.get('active', []), indent=2, cls=FirestoreEncoder)
            completed_tasks_str = json.dumps(task_list.get('completed', []), indent=2, cls=FirestoreEncoder)
            full_prompt = f"""{system_prompt}\n\nCurrent active tasks:\n{active_tasks_str}
            Completed tasks:\n{completed_tasks_str}
            Based on the user's request, determine what changes need to be made to the task list.
            List each change separately.
            """
            messages = [
                SystemMessage(content=full_prompt),
                HumanMessage(content=clean_input)
            ]
            logger.info(f"\n\n\nCalling OpenAI with structured output schema PYDANTIC-H tool")
            response = chat.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise

    def _second_call(self, content1: str) -> str:
        logger.info(f"\n\n\nCalling second-call {content1}")
        return "TO-DO TO_DO XXX"
        
    def _call_openai(self, system_prompt: str, user_input: str, task_list: Dict[str, Any]) -> str:
        content1=self._first_call(system_prompt, user_input, task_list)
        content2=self._second_call(content1)
        logger.info(f"\n\n\nOpenAI response: {content2}")  
        return content2
    
    def _call_openai_old(self, system_prompt: str, user_input: str, task_list: Dict[str, Any]) -> str:
        try:
            chat = ChatOpenAI(
                api_key=self.api_key,
                model=self.model,
                temperature=0.7
            )
            clean_input = user_input.strip()
            active_tasks_str = json.dumps(task_list.get('active', []), indent=2, cls=FirestoreEncoder)
            completed_tasks_str = json.dumps(task_list.get('completed', []), indent=2, cls=FirestoreEncoder)
            full_prompt = f"""{system_prompt}\n\nCurrent active tasks:\n{active_tasks_str}
            Completed tasks:\n{completed_tasks_str}
            Based on the user's request, determine what changes need to be made to the task list.
            """
            messages = [
                SystemMessage(content=full_prompt),
                HumanMessage(content=clean_input)
            ]
            logger.info(f"\n\n\nCalling OpenAI with structured output schema PYDANTIC-H tool")
            try:
                # Use LangChain's structured output parsing
                response = chat.with_structured_output(TaskChanges).invoke(messages)

                # Convert response (TaskChanges) to dict for easier handling
                new_tasks = response.new_tasks
                modified_tasks = response.modified_tasks
                summary = response.summary

                logger.info(f"Response completed")
                logger.info(f"Response: {response}")
                logger.info(f"Structured response: {response}")

                for new_task in new_tasks:
                    task_data_str = json.dumps(new_task, cls=FirestoreEncoder)
                    self._add_task(user_id, task_data_str)
                for modified_task in modified_tasks:
                    task_id = modified_task.pop('id')
                    update_data_str = json.dumps(modified_task, cls=FirestoreEncoder)
                    self._update_task(user_id, task_id, update_data_str)
                return summary
            except Exception as e:
                logger.error(f"Error with structured output: {str(e)}")
                #response = chat.invoke(messages)
                #return response.content
                return None
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            return f"I encountered an error while processing your request: {str(e)}"

# Create an instance for use in the application
openai_service = OpenAIService()
