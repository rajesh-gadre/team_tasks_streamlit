import logging
from typing import Dict, Any
from src.database.firestore import get_client
from src.database.models import AIEvalResult
logger = logging.getLogger(__name__)

class EvalResultRepository:

    def __init__(self):
        self.collection = 'Eval_Results'
        self.db = get_client()

    def create_result(self, result: AIEvalResult) -> str:
        data = result.to_dict()
        return self.db.create(self.collection, data)
_eval_result_repo: EvalResultRepository | None = None

def get_eval_result_repository() -> EvalResultRepository:
    global _eval_result_repo
    if _eval_result_repo is None:
        _eval_result_repo = EvalResultRepository()
    return _eval_result_repo
