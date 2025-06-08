import json
import logging
import traceback
from contextlib import nullcontext
from typing import Any, Dict

import streamlit as st
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from src.ai.llm_models import FirestoreEncoder, TaskChanges
from src.tasks.task_service import get_task_service

logger = logging.getLogger(__name__)

class LlmExecutor:
    def __init__(self, service):
        self.service = service

    def execute(self, user_id: str, system_prompt: str, user_input: str, task_list: Dict[str, Any], chat_id: str):
        spinner = getattr(st, "spinner", None)
        if spinner is None:
            spinner = nullcontext
        with spinner("Processing your request..."):
            content1 = self._first_call(system_prompt, user_input, task_list)
            resp = self._second_call(content1)
            final_response = self.__third_call(user_id, resp)
        return final_response

    def _first_call(self, system_prompt: str, user_input: str, task_list: Dict[str, Any]) -> str:
        try:
            chat = ChatOpenAI(
                api_key=self.service.api_key,
                model=self.service.model,
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
            logger.debug("\n\n\nCalling OpenAI with structured output schema PYDANTIC-H tool")
            response = chat.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"FIRST CALL:Error calling OpenAI API: {str(e)}")
            raise

    def _second_call(self, content1: str) -> TaskChanges:
        logger.debug(f"\n\n\nCalling second-call {content1}")
        logger.debug(f"Entering _second_call. Received content1:\n{content1}")
        system_prompt = "You are an AI assistant that processes a list of task descriptions and structures them into new and modified tasks. Strictly adhere to the provided Pydantic model for the output format. Ensure all required fields are present for each task. The input text is a list of proposed changes."
        try:
            chat = ChatOpenAI(
                api_key=self.service.api_key,
                model=self.service.model,
                temperature=0.2
            )
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=content1)
            ]
            response = chat.with_structured_output(TaskChanges).invoke(messages)
            logger.debug(f"Successfully structured output in _second_call: {response}")
            return response
        except Exception as e:
            detailed_error_message = f"Error Type: {type(e).__name__}\n"
            detailed_error_message += f"Error Args: {e.args}\n"
            if hasattr(e, 'response') and e.response is not None and hasattr(e.response, 'status_code'):
                detailed_error_message += f"API Response Status: {e.response.status_code}\n"
                detailed_error_message += f"API Response Headers: {e.response.headers}\n"
                try:
                    detailed_error_message += f"API Response JSON: {e.response.json()}\n"
                except ValueError:
                    detailed_error_message += f"API Response Text: {e.response.text}\n"
            logger.error(f"SECOND CALL: Error calling OpenAI API. Details:\n{detailed_error_message}\nContent1 that caused error (first 500 chars):\n{content1[:500]}\nTraceback:\n{traceback.format_exc()}")
            raise

    def __third_call(self, user_id: str, resp: TaskChanges) -> TaskChanges:
        logger.debug(f"\n\n\nCalling third-call {resp}")
        try:
            ts = get_task_service()
            for new_task in resp.new_tasks:
                task_data = getattr(new_task, 'model_dump', new_task.dict)(exclude_none=True)
                logger.debug(f"Creating task for {user_id}: {task_data}")
                ts.create_task(user_id, task_data)
            for mod_task in resp.modified_tasks:
                task_id = mod_task.id
                raw_data = getattr(mod_task, 'model_dump', mod_task.dict)(exclude={'id'})
                update_data = {k: v for k, v in raw_data.items() if v is not None}
                logger.debug(f"Updating task {task_id} for {user_id} with {update_data}")
                ts.update_task(user_id, task_id, update_data)
            return resp
        except Exception as e:
            logger.error(f"THIRD CALL: Error updating tasks - {str(e)}")
            return None
