import logging
from typing import Any, Dict, List
from src.database.firestore import get_client

logger = logging.getLogger(__name__)

class GroupRepository:
    def __init__(self):
        self.collection = 'Groups'
        self.db = get_client()

    def get_groups(self) -> List[Dict[str, Any]]:
        return self.db.query(self.collection, order_by='createdAt', direction='DESCENDING')

    def create_group(self, data: Dict[str, Any]) -> str:
        return self.db.create(self.collection, data)

    def update_group(self, group_id: str, data: Dict[str, Any]) -> bool:
        return self.db.update(self.collection, group_id, data)

_repo: GroupRepository | None = None

def get_group_repository() -> GroupRepository:
    global _repo
    if _repo is None:
        _repo = GroupRepository()
    return _repo
