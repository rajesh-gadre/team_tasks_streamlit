import os
import logging
from typing import List, Optional
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from src.eval.eval_result_repository import get_eval_result_repository
from src.ai.prompt_repository import get_prompt_repository
from src.database.models import AIEvalInput, AIEvalResult
logger = logging.getLogger(__name__)

class EvalService:

    def __init__(self):
        self.repo = get_eval_result_repository()
        self.prompt_repo = get_prompt_repository()
        self.api_key = os.environ.get('OPENAI_API_KEY')
        self.model = os.environ.get('OPENAI_MODEL', 'gpt-4.1-mini')

    def run_evals(self, prompt_name: str, version: int, eval_inputs: List[AIEvalInput]) -> List[str]:
        prompt = self.prompt_repo.get_prompt_by_name_version(prompt_name, version)
        if not prompt:
            raise ValueError(f'Prompt {prompt_name} v{version} not found')
        chat = ChatOpenAI(api_key=self.api_key, model=self.model, temperature=0)
        result_ids = []
        for ev in eval_inputs:
            messages = [SystemMessage(content=prompt.text), HumanMessage(content=ev.input_text)]
            response = chat.invoke(messages)
            judge_msgs = [SystemMessage(content='Please evaluate this result as per the criteria provided'), SystemMessage(content=ev.eval_prompt or ''), HumanMessage(content=getattr(response, 'content', str(response)))]
            judge = chat.invoke(judge_msgs)
            result = AIEvalResult(eval_input_id=ev.id, prompt_name=prompt_name, prompt_version=version, result=getattr(response, 'content', str(response)), llm_judge_says=getattr(judge, 'content', str(judge)), input_text=ev.input_text)
            res_id = self.repo.create_result(result)
            result_ids.append(res_id)
        return result_ids
_eval_service: Optional[EvalService] = None

def get_eval_service() -> EvalService:
    global _eval_service
    if _eval_service is None:
        _eval_service = EvalService()
    return _eval_service
