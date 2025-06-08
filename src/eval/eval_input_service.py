import logging
from typing import List, Dict, Any, Optional

from src.eval.eval_input_repository import get_eval_input_repository
from src.database.models import AIEvalInput, EvalStatus
from src.database.firestore import get_client

logger = logging.getLogger(__name__)

class EvalInputService:
    def __init__(self):
        self.repository = get_eval_input_repository()

    def get_latest_inputs(self, count: int = 10) -> List[AIEvalInput]:
        return self.repository.get_latest_inputs(count)

    def add_from_chat(self, chat_data: Dict[str, Any], eval_prompt: str) -> str:
        doc_id = self.repository.create_from_chat(chat_data, eval_prompt)
        cid = chat_data.get('id')
        if cid:
            get_client().delete('AI_chats', cid)
        return doc_id

    def update_status(self, doc_id: str, status: str) -> bool:
        return self.repository.update_status(doc_id, status)

    def update_input(self, doc_id: str, data: Dict[str, Any]) -> bool:
        return self.repository.update_input(doc_id, data)

_eval_service: Optional[EvalInputService] = None


def get_eval_input_service() -> EvalInputService:
    global _eval_service
    if _eval_service is None:
        _eval_service = EvalInputService()
    return _eval_service
