"""
OpenAI integration module for the Task Management System.
Handles interactions with OpenAI API via Langchain.
"""
import os
import logging
from typing import Dict, Optional, Any

from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.database.firestore import firestore_client
from src.database.models import AIChat
from src.ai.prompt_repository import prompt_repository

# Configure logging
logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for OpenAI API interactions."""
    
    def __init__(self):
        """Initialize OpenAI service with API key from environment variables."""
        self.api_key = os.environ.get('OPENAI_API_KEY')
        self.model = os.environ.get('OPENAI_MODEL', 'gpt-4.1-mini')
        
        if not self.api_key:
            logger.error("OpenAI API key not found in environment variables")
            raise ValueError("Missing OpenAI API key")
        
        # Initialize Firestore client for AI chats
        self.db = firestore_client
        self.collection = 'AI_chats'
    
    def process_chat(self, user_id: str, input_text: str) -> Dict[str, Any]:
        """
        Process a chat interaction with OpenAI.
        
        Args:
            user_id: User identifier
            input_text: User input text
            
        Returns:
            Dictionary with chat ID and response
        """
        try:
            # Create chat record in Firestore
            chat_data = {
                'user_id': user_id,
                'inputText': input_text
            }
            
            chat_id = self.db.create(self.collection, chat_data)
            
            # Get system prompt from repository
            system_prompt = self._get_system_prompt()
            
            # Process with OpenAI
            response = self._call_openai(system_prompt, input_text)
            
            # Update chat record with response
            self.db.update(self.collection, chat_id, {'Response': response})
            
            logger.info(f"Chat processed for user {user_id}")
            return {
                'id': chat_id,
                'response': response
            }
        except Exception as e:
            logger.error(f"Error processing chat for user {user_id}: {str(e)}")
            raise
    
    def _get_system_prompt(self) -> str:
        """
        Get system prompt for OpenAI.
        
        Returns:
            System prompt text
        """
        try:
            # Get prompt from repository
            prompt = prompt_repository.get_active_prompt("AI_Tasks")
            
            if prompt:
                return prompt.text
            else:
                # Fallback prompt if none found in repository
                logger.warning("No active AI_Tasks prompt found, using fallback")
                return """You are an AI assistant for a task management system. 
                You can help users manage their tasks, provide suggestions, 
                and answer questions about task management best practices."""
        except Exception as e:
            logger.error(f"Error getting system prompt: {str(e)}")
            # Fallback prompt in case of error
            return """You are an AI assistant for a task management system. 
            You can help users manage their tasks, provide suggestions, 
            and answer questions about task management best practices."""
    
    def _call_openai(self, system_prompt: str, user_input: str) -> str:
        """
        Call OpenAI API with system prompt and user input.
        
        Args:
            system_prompt: System prompt text
            user_input: User input text
            
        Returns:
            OpenAI response text
        """
        try:
            # Initialize ChatOpenAI with API key and model from environment variables
            chat = ChatOpenAI(
                model=self.model,
                openai_api_key=self.api_key,
                temperature=0.7
            )
            
            # Create messages
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_input)
            ]
            
            # Get response
            response = chat(messages)
            
            return response.content
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise

# Create an instance for use in the application
openai_service = OpenAIService()
