import logging
from typing import Dict, List, Any

from src.database.firestore import get_client
from src.database.models import AIEvalInput, EvalStatus

logger = logging.getLogger(__name__)

class EvalInputRepository:
    """Repository for AI evaluation input documents."""

    def __init__(self):
        self.collection = 'AI_Eval_Inputs'
        self.db = get_client()

    def get_latest_inputs(self, limit: int = 10) -> List[AIEvalInput]:
        docs = self.db.query(
            self.collection,
            order_by='createdAt',
            direction='DESCENDING',
            limit=limit,
        )
        return [AIEvalInput.from_dict(d) for d in docs]

    def create_from_chat(self, chat_data: Dict[str, Any], eval_prompt: str) -> str:
        data = {
            'user_id': chat_data.get('user_id'),
            'inputText': chat_data.get('inputText'),
            'Response': chat_data.get('Response'),
            'evalPrompt': eval_prompt,
            'status': EvalStatus.ACTIVE,
        }
        return self.db.create(self.collection, data)

    def update_status(self, doc_id: str, status: str) -> bool:
        return self.db.update(self.collection, doc_id, {'status': status})

    def update_input(self, doc_id: str, data: Dict[str, Any]) -> bool:
        return self.db.update(self.collection, doc_id, data)

_eval_repo: EvalInputRepository | None = None


def get_eval_input_repository() -> EvalInputRepository:
    global _eval_repo
    if _eval_repo is None:
        _eval_repo = EvalInputRepository()
    return _eval_repo
