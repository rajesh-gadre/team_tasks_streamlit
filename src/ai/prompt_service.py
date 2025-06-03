import logging
from typing import List, Dict, Any
from src.ai.prompt_repository import prompt_repository
from src.database.models import AIPrompt

logger = logging.getLogger(__name__)

class PromptService:
    """Service layer for prompt operations."""

    def __init__(self):
        self.repository = prompt_repository

    def get_all_prompts(self) -> List[AIPrompt]:
        logger.info("Getting all prompts")
        return self.repository.get_all_prompts()

    def update_prompt(self, prompt_id: str, prompt_data: Dict[str, Any]) -> bool:
        logger.info(f"Updating prompt {prompt_id}")
        return self.repository.update_prompt(prompt_id, prompt_data)

prompt_service = PromptService()
