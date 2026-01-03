"""
LLM Router - Manages and switches between LLM providers.
Defaults to Ollama, allows manual switching to Gemini.
"""
import logging
from typing import Dict, Optional
from brain.llm_provider import LLMProvider

logger = logging.getLogger("AURA.LLMRouter")


class LLMRouter:
    """
    Routes LLM requests to the selected provider.
    Manages provider instances and switching.
    """
    
    def __init__(self, default_provider: str = "ollama"):
        self._providers: Dict[str, LLMProvider] = {}
        self._current_provider_name: str = default_provider
        self._initialized: bool = False
        
        # Register available providers
        self._register_providers()
        
        # Set default provider
        if default_provider in self._providers:
            self._current_provider_name = default_provider
            logger.info(f"LLMRouter initialized with default provider: {default_provider}")
        else:
            # Fallback to first available
            if self._providers:
                self._current_provider_name = list(self._providers.keys())[0]
                logger.warning(f"Default provider '{default_provider}' not available. Using: {self._current_provider_name}")
    
    def _register_providers(self) -> None:
        """
        Register all available LLM providers.
        Providers are lazily initialized on first use.
        """
        # Register Ollama (primary)
        try:
            from brain.ollama_client import OllamaClient
            ollama = OllamaClient()
            self._providers["ollama"] = ollama
            logger.info("Registered provider: ollama")
        except Exception as e:
            logger.warning(f"Failed to register Ollama provider: {e}")
        
        # Register Gemini (secondary)
        try:
            from brain.gemini_client import GeminiClient
            gemini = GeminiClient()
            self._providers["gemini"] = gemini
            logger.info("Registered provider: gemini")
        except Exception as e:
            logger.warning(f"Failed to register Gemini provider: {e}")
    
    @property
    def current_provider(self) -> Optional[LLMProvider]:
        """Get the current active provider instance."""
        return self._providers.get(self._current_provider_name)
    
    @property
    def current_provider_name(self) -> str:
        """Get the name of the current provider."""
        return self._current_provider_name
    
    def set_provider(self, provider_name: str) -> bool:
        """
        Switch to a different LLM provider.
        
        Args:
            provider_name: Name of the provider ('ollama', 'gemini')
            
        Returns:
            True if switch successful, False otherwise
        """
        provider_name = provider_name.lower()
        
        if provider_name not in self._providers:
            logger.error(f"Unknown provider: {provider_name}. Available: {list(self._providers.keys())}")
            return False
        
        self._current_provider_name = provider_name
        logger.info(f"Switched LLM provider to: {provider_name}")
        return True
    
    def get_available_providers(self) -> list:
        """Get list of available provider names."""
        return list(self._providers.keys())
    
    def get_provider_status(self) -> Dict[str, any]:
        """
        Get status of all registered providers.
        
        Returns:
            Dict with provider names as keys and status info as values
        """
        status = {}
        for name, provider in self._providers.items():
            try:
                healthy = provider.health_check()
                status[name] = {
                    "healthy": healthy,
                    "model": provider.model,
                    "current": name == self._current_provider_name
                }
            except Exception as e:
                status[name] = {
                    "healthy": False,
                    "error": str(e),
                    "current": name == self._current_provider_name
                }
        return status
    
    # =========================================================
    # Delegated LLMProvider methods
    # =========================================================
    
    def start_chat(self, history=None) -> None:
        """Delegate to current provider."""
        provider = self.current_provider
        if provider:
            provider.start_chat(history)
    
    def generate_response(self, prompt: str) -> str:
        """Delegate to current provider."""
        provider = self.current_provider
        if not provider:
            return '{"type": "ERROR", "message": "No LLM provider available"}'
        
        logger.debug(f"Generating response using provider: {self._current_provider_name}")
        return provider.generate_response(prompt)
    
    def health_check(self) -> bool:
        """Check health of current provider."""
        provider = self.current_provider
        if provider:
            return provider.health_check()
        return False
