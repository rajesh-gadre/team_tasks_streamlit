import logging
from typing import Optional, Dict
from src.database.firestore import get_client

logger = logging.getLogger(__name__)

class UserRepository:
    def __init__(self):
        self.collection = 'users'
        self.db = get_client()

    def get_by_email(self, email: str) -> Optional[Dict[str, str]]:
        records = self.db.query(self.collection, filters=[('userEmail', '==', email)], limit=1)
        return records[0] if records else None

    def create_user(self, email: str, tz: str, name: str | None=None) -> Dict[str, str]:
        data = {'userEmail': email, 'userTZ': tz}
        if name:
            data['userName'] = name
        doc_id = self.db.create(self.collection, data)
        self.db.update(self.collection, doc_id, {'userId': doc_id})
        record = {'userId': doc_id, 'userEmail': email, 'userTZ': tz}
        if name:
            record['userName'] = name
        return record

    def get_users(self):
        return self.db.get_all(self.collection)

_repo: Optional[UserRepository] = None

def get_user_repository() -> UserRepository:
    global _repo
    if _repo is None:
        _repo = UserRepository()
    return _repo
