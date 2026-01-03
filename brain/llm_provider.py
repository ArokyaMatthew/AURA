"""
Abstract base class for LLM providers.
All LLM clients (Ollama, Gemini, etc.) must implement this interface.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class LLMProvider(ABC):
    """
    Abstract interface for LLM providers.
    Ensures consistent API across different LLM backends.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider name (e.g., 'ollama', 'gemini')."""
        pass
    
    @property
    @abstractmethod
    def model(self) -> str:
        """Return the current model name."""
        pass
    
    @abstractmethod
    def start_chat(self, history: Optional[List[Dict[str, str]]] = None) -> None:
        """
        Initialize a chat session with optional history.
        
        Args:
            history: List of message dicts with 'role' and 'content' keys
        """
        pass
    
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """
        Generate a response for the given prompt.
        
        Args:
            prompt: The input prompt/message
            
        Returns:
            The generated text response
        """
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """
        Check if the provider is available and working.
        
        Returns:
            True if healthy, False otherwise
        """
        pass
