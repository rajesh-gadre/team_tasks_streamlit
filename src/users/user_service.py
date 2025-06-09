import logging
from typing import Dict
from .user_repository import get_user_repository
from .user_role_service import get_user_role_service

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        self.repo = get_user_repository()
        self.role_service = get_user_role_service()

    def login(self, email: str, name: str | None=None) -> Dict[str, str]:
        record = self.repo.get_by_email(email)
        if not record:
            record = self.repo.create_user(email, 'America/Los_Angeles', name)
        self.role_service.ensure_default_role(record['userId'])
        return record

    def get_users(self):
        return self.repo.get_users()

    def update_timezone(self, user_id: str, tz: str) -> bool:
        return self.repo.update_user_timezone(user_id, tz)

_service: UserService | None = None

def get_user_service() -> UserService:
    global _service
    if _service is None:
        _service = UserService()
    return _service
