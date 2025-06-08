import logging
from typing import Dict
from .user_repository import get_user_repository

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        self.repo = get_user_repository()

    def login(self, email: str) -> Dict[str, str]:
        record = self.repo.get_by_email(email)
        if record:
            return record
        return self.repo.create_user(email, 'America/Los_Angeles')

_service: UserService | None = None

def get_user_service() -> UserService:
    global _service
    if _service is None:
        _service = UserService()
    return _service
