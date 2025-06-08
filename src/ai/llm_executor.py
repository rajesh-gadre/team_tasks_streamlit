import streamlit as st
from contextlib import nullcontext
from typing import Any, Dict

class LlmExecutor:
    def __init__(self, service):
        self.service = service

    def execute(self, user_id: str, system_prompt: str, user_input: str, task_list: Dict[str, Any], chat_id: str):
        spinner = getattr(st, "spinner", None)
        if spinner is None:
            spinner = nullcontext
        with spinner("Processing your request..."):
            content1 = self.service._first_call(system_prompt, user_input, task_list)
            resp = self.service._second_call(content1)
            final_response = self.service._LlmService__third_call(user_id, resp)
        return final_response

