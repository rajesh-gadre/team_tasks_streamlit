"""
Prompt repository module for the Task Management System.
Handles data access operations for AI prompts in Firestore.
"""
import logging
from typing import Dict, List, Optional, Any

from src.database.firestore import get_client
from src.database.models import AIPrompt, PromptStatus

# Configure logging
logger = logging.getLogger(__name__)

class PromptRepository:
    """Repository for AI prompt data access operations."""
    
    def __init__(self):
        """Initialize prompt repository with Firestore client."""
        self.collection = 'AI_prompts'
        self.db = get_client()
    
    def get_active_prompt(self, prompt_name: str) -> Optional[AIPrompt]:
        """
        Get an active prompt by name.
        
        Args:
            prompt_name: Name of the prompt
            
        Returns:
            AIPrompt object or None if not found
        """
        try:
            filters = [
                ('prompt_name', '==', prompt_name),
                ('status', '==', PromptStatus.ACTIVE)
            ]

            prompts_data = self.db.query(
                self.collection,
                filters=filters,
                order_by='version',
                direction='DESCENDING',
                limit=1
            )
            
            if not prompts_data:
                logger.warning(f"No active prompt found with name: {prompt_name}")
                return None
            
            return AIPrompt.from_dict(prompts_data[0])
        except Exception as e:
            logger.error(f"Error getting active prompt {prompt_name}: {str(e)}")
            raise
    
    def get_latest_prompts(self) -> List[AIPrompt]:
        """Get the latest version of each prompt."""
        try:
            prompts_data = self.db.query(
                self.collection,
                order_by='version',
                direction='DESCENDING'
            )

            latest = {}
            for data in prompts_data:
                name = data.get('prompt_name')
                if name and name not in latest:
                    latest[name] = AIPrompt.from_dict(data)
            return list(latest.values())
        except Exception as e:
            logger.error(f"Error getting latest prompts: {str(e)}")
            raise

    def get_all_prompts(self) -> List[AIPrompt]:
        """Return all prompts, all versions."""
        try:
            prompts_data = self.db.query(
                self.collection,
                order_by='prompt_name',
                direction='ASCENDING'
            )
            return [AIPrompt.from_dict(d) for d in prompts_data]
        except Exception as e:
            logger.error(f"Error getting all prompts: {str(e)}")
            raise

    def get_prompt_by_name_version(self, name: str, version: int) -> Optional[AIPrompt]:
        """Return a specific prompt version by name and version."""
        try:
            filters = [
                ('prompt_name', '==', name),
                ('version', '==', version)
            ]
            data = self.db.query(
                self.collection,
                filters=filters,
                limit=1
            )
            if not data:
                return None
            return AIPrompt.from_dict(data[0])
        except Exception as e:
            logger.error(f"Error getting prompt {name} v{version}: {str(e)}")
            raise
    
    def create_prompt(self, prompt: AIPrompt) -> str:
        """
        Create a new prompt.
        
        Args:
            prompt: AIPrompt object to create
            
        Returns:
            ID of the created prompt
        """
        try:
            # Validate prompt data
            prompt.validate()
            
            # Convert to dictionary
            prompt_data = prompt.to_dict()
            
            # Create prompt in Firestore
            prompt_id = self.db.create(self.collection, prompt_data)
            
            logger.info(f"Prompt created with ID: {prompt_id}")
            return prompt_id
        except Exception as e:
            logger.error(f"Error creating prompt: {str(e)}")
            raise
    
    def create_prompt_version(self, prompt_id: str, prompt_data: Dict[str, Any]) -> str:
        """Create a new version of the given prompt."""
        try:
            original = self.db.read(self.collection, prompt_id)
            if not original:
                raise ValueError(f"Prompt {prompt_id} not found")

            version = original.get('version', 1) + 1
            new_prompt = AIPrompt(
                prompt_name=original.get('prompt_name'),
                text=prompt_data.get('text', original.get('text')),
                status=PromptStatus.INACTIVE,
                version=version
            )
            new_prompt.validate()
            return self.create_prompt(new_prompt)
        except Exception as e:
            logger.error(f"Error creating new version for {prompt_id}: {str(e)}")
            raise

    def set_active_version(self, prompt_name: str, version: int) -> bool:
        """Set the given version as active and others inactive."""
        try:
            prompts = self.db.query(
                self.collection,
                filters=[('prompt_name', '==', prompt_name)]
            )
            if not prompts:
                raise ValueError(f"Prompt {prompt_name} not found")

            found = False
            for p in prompts:
                status = PromptStatus.ACTIVE if p.get('version') == version else PromptStatus.INACTIVE
                if p.get('version') == version:
                    found = True
                self.db.update(self.collection, p['id'], {'status': status})
            return found
        except Exception as e:
            logger.error(f"Error setting active version {prompt_name} v{version}: {str(e)}")
            raise
    
    def delete_prompt(self, prompt_id: str) -> bool:
        """
        Delete a prompt.
        
        Args:
            prompt_id: Prompt identifier
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            # Delete prompt from Firestore
            result = self.db.delete(self.collection, prompt_id)
            
            logger.info(f"Prompt {prompt_id} deleted")
            return result
        except Exception as e:
            logger.error(f"Error deleting prompt {prompt_id}: {str(e)}")
            raise

_prompt_repository: Optional[PromptRepository] = None


def get_prompt_repository() -> PromptRepository:
    """Return the PromptRepository singleton."""
    global _prompt_repository
    if _prompt_repository is None:
        _prompt_repository = PromptRepository()
    return _prompt_repository
