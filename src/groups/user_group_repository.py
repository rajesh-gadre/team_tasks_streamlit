import logging
from typing import Any, Dict, List
from src.database.firestore import get_client

logger = logging.getLogger(__name__)

class UserGroupRepository:
    def __init__(self):
        self.collection = 'UserGroups'
        self.db = get_client()

    def get_user_groups(self) -> List[Dict[str, Any]]:
        filters = [('status', '!=', 'deleted')]
        return self.db.query(self.collection, filters=filters, order_by='createdAt', direction='DESCENDING')

    def create_user_group(self, data: Dict[str, Any]) -> str:
        return self.db.create(self.collection, data)

    def update_user_group(self, doc_id: str, data: Dict[str, Any]) -> bool:
        return self.db.update(self.collection, doc_id, data)

    def get_user_group(self, doc_id: str) -> Dict[str, Any] | None:
        return self.db.read(self.collection, doc_id)

    def delete_user_group(self, doc_id: str) -> bool:
        return self.db.update(self.collection, doc_id, {'status': 'deleted'})

_repo: UserGroupRepository | None = None

def get_user_group_repository() -> UserGroupRepository:
    global _repo
    if _repo is None:
        _repo = UserGroupRepository()
    return _repo
