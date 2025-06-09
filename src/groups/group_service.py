import logging
from typing import Any, Dict, List
from .group_repository import get_group_repository

logger = logging.getLogger(__name__)

class GroupService:
    def __init__(self):
        self.repo = get_group_repository()

    def get_groups(self) -> List[Dict[str, Any]]:
        return self.repo.get_groups()

    def create_group(self, name: str) -> str:
        return self.repo.create_group({'groupName': name})

    def update_group(self, group_id: str, name: str) -> bool:
        return self.repo.update_group(group_id, {'groupName': name})

_service: GroupService | None = None

def get_group_service() -> GroupService:
    global _service
    if _service is None:
        _service = GroupService()
    return _service
