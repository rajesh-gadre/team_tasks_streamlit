import logging
from typing import List, Dict, Any, Optional

from src.eval.eval_input_repository import get_eval_input_repository
from src.database.models import AIEvalInput, EvalStatus

logger = logging.getLogger(__name__)

class EvalInputService:
    def __init__(self):
        self.repository = get_eval_input_repository()

    def get_latest_inputs(self, count: int = 10) -> List[AIEvalInput]:
        return self.repository.get_latest_inputs(count)

    def add_from_chat(self, chat_data: Dict[str, Any], eval_prompt: str) -> str:
        return self.repository.create_from_chat(chat_data, eval_prompt)

    def update_status(self, doc_id: str, status: str) -> bool:
        return self.repository.update_status(doc_id, status)

_eval_service: Optional[EvalInputService] = None


def get_eval_input_service() -> EvalInputService:
    global _eval_service
    if _eval_service is None:
        _eval_service = EvalInputService()
    return _eval_service
