import logging
from typing import Any, Dict, List
from .user_group_repository import get_user_group_repository

logger = logging.getLogger(__name__)

class UserGroupService:
    def __init__(self):
        self.repo = get_user_group_repository()

    def get_user_groups(self) -> List[Dict[str, Any]]:
        return self.repo.get_user_groups()

    def create_user_group(self, data: Dict[str, Any]) -> str:
        return self.repo.create_user_group(data)

    def update_user_group(self, doc_id: str, data: Dict[str, Any]) -> bool:
        return self.repo.update_user_group(doc_id, data)

_service: UserGroupService | None = None

def get_user_group_service() -> UserGroupService:
    global _service
    if _service is None:
        _service = UserGroupService()
    return _service
