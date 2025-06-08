import logging
from typing import List, Dict, Any, Optional
from src.ai.prompt_repository import get_prompt_repository
from src.database.models import AIPrompt
logger = logging.getLogger(__name__)

class PromptService:

    def __init__(self):
        self.repository = get_prompt_repository()

    def get_all_prompts(self) -> List[AIPrompt]:
        logger.info('Getting all prompts')
        return self.repository.get_all_prompts()

    def update_prompt(self, prompt_id: str, prompt_data: Dict[str, Any]) -> bool:
        logger.info(f'Creating new version for prompt {prompt_id}')
        self.repository.create_prompt_version(prompt_id, prompt_data)
        return True

    def set_active_version(self, prompt_name: str, version: int) -> bool:
        logger.info(f'Setting {prompt_name} v{version} as active')
        return self.repository.set_active_version(prompt_name, version)
_prompt_service: Optional[PromptService] = None

def get_prompt_service() -> PromptService:
    global _prompt_service
    if _prompt_service is None:
        _prompt_service = PromptService()
    return _prompt_service
