import logging
from typing import Optional, Dict
from src.database.firestore import get_client

logger = logging.getLogger(__name__)

class UserRoleRepository:
    def __init__(self):
        self.collection = 'user_roles'
        self.db = get_client()

    def get_by_user_id(self, user_id: str) -> Optional[Dict[str, str]]:
        records = self.db.query(self.collection, filters=[('userId', '==', user_id)], limit=1)
        return records[0] if records else None

    def create_role(self, user_id: str, role: str) -> Dict[str, str]:
        doc_id = self.db.create(self.collection, {'userId': user_id, 'role': role})
        return {'id': doc_id, 'userId': user_id, 'role': role}

_repo: Optional[UserRoleRepository] = None

def get_user_role_repository() -> UserRoleRepository:
    global _repo
    if _repo is None:
        _repo = UserRoleRepository()
    return _repo
