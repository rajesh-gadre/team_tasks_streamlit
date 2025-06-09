import logging
from typing import Dict
from .user_role_repository import get_user_role_repository

logger = logging.getLogger(__name__)

class UserRoleService:
    def __init__(self):
        self.repo = get_user_role_repository()

    def ensure_default_role(self, user_id: str) -> Dict[str, str]:
        record = self.repo.get_by_user_id(user_id)
        if record:
            return record
        return self.repo.create_role(user_id, 'regular')

_service: UserRoleService | None = None

def get_user_role_service() -> UserRoleService:
    global _service
    if _service is None:
        _service = UserRoleService()
    return _service
