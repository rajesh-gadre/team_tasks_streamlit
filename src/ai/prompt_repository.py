"""
Prompt repository module for the Task Management System.
Handles data access operations for AI prompts in Firestore.
"""
import logging
from typing import Dict, List, Optional, Any

from src.database.firestore import firestore_client
from src.database.models import AIPrompt, PromptStatus

# Configure logging
logger = logging.getLogger(__name__)

class PromptRepository:
    """Repository for AI prompt data access operations."""
    
    def __init__(self):
        """Initialize prompt repository with Firestore client."""
        self.collection = 'AI_prompts'
        self.db = firestore_client
    
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
            
            prompts_data = self.db.query(self.collection, filters=filters, limit=1)
            
            if not prompts_data:
                logger.warning(f"No active prompt found with name: {prompt_name}")
                return None
            
            return AIPrompt.from_dict(prompts_data[0])
        except Exception as e:
            logger.error(f"Error getting active prompt {prompt_name}: {str(e)}")
            raise
    
    def get_all_prompts(self) -> List[AIPrompt]:
        """
        Get all prompts.
        
        Returns:
            List of AIPrompt objects
        """
        try:
            prompts_data = self.db.query(self.collection)
            
            return [AIPrompt.from_dict(prompt_data) for prompt_data in prompts_data]
        except Exception as e:
            logger.error(f"Error getting all prompts: {str(e)}")
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
    
    def update_prompt(self, prompt_id: str, prompt_data: Dict[str, Any]) -> bool:
        """
        Update an existing prompt.
        
        Args:
            prompt_id: Prompt identifier
            prompt_data: Updated prompt data
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            # Update prompt in Firestore
            result = self.db.update(self.collection, prompt_id, prompt_data)
            
            logger.info(f"Prompt {prompt_id} updated")
            return result
        except Exception as e:
            logger.error(f"Error updating prompt {prompt_id}: {str(e)}")
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

# Create an instance for use in the application
prompt_repository = PromptRepository()
