"""
Agent Service - Singleton wrapper around CoreAgentController.
Manages LLM provider selection and agent lifecycle.
"""
from typing import Optional
import sys
import os
from pathlib import Path

# Load .env file before anything else
from dotenv import load_dotenv

# Find the project root (where .env is located)
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# Add parent directory to path for imports
sys.path.insert(0, str(project_root))

from core_controller import CoreAgentController, AgentResult
from brain.brain import Brain
from tools.executor import Executor
from perception.voice import VoiceEngine
from memory.memory_system import MemorySystem
from safety.safety import Safety


class AgentService:
    """
    Singleton service managing the agent lifecycle.
    Supports LLM provider switching between Ollama and Gemini.
    """
    _instance: Optional["AgentService"] = None
    _agent: Optional[CoreAgentController] = None
    _brain: Optional[Brain] = None
    _initialized: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @property
    def is_initialized(self) -> bool:
        return self._initialized
    
    def initialize(self, provider: str = "ollama") -> dict:
        """
        Initialize all agent components.
        
        Args:
            provider: LLM provider to use ('ollama' or 'gemini'). Default: 'ollama'
            
        Returns:
            Success status and message.
        """
        if self._initialized:
            return {"success": True, "message": "Already initialized"}
        
        try:
            # Initialize components with selected provider
            self._brain = Brain(default_provider=provider)
            executor = Executor()
            perception = VoiceEngine()
            memory = MemorySystem()
            safety = Safety()
            
            # Create controller
            self._agent = CoreAgentController(
                brain=self._brain,
                executor=executor,
                perception=perception,
                memory=memory,
                safety=safety
            )
            
            self._initialized = True
            provider_name = self._brain.get_provider_name()
            return {
                "success": True, 
                "message": f"AURA initialized with {provider_name.upper()} provider"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def set_llm_provider(self, provider: str) -> dict:
        """
        Switch to a different LLM provider.
        
        Args:
            provider: 'ollama' or 'gemini'
            
        Returns:
            Success status and current provider name.
        """
        if not self._initialized or self._brain is None:
            return {
                "success": False,
                "message": "Agent not initialized",
                "provider": None
            }
        
        success = self._brain.set_provider(provider)
        current = self._brain.get_provider_name()
        
        if success:
            return {
                "success": True,
                "message": f"Switched to {current.upper()} provider",
                "provider": current
            }
        else:
            return {
                "success": False,
                "message": f"Failed to switch. Unknown provider: {provider}",
                "provider": current
            }
    
    def get_llm_status(self) -> dict:
        """
        Get current LLM provider status.
        
        Returns:
            Provider name, health status, and available providers.
        """
        if not self._initialized or self._brain is None:
            return {
                "current_provider": None,
                "providers": {},
                "available": []
            }
        
        status = self._brain.get_provider_status()
        current = self._brain.get_provider_name()
        
        return {
            "current_provider": current,
            "providers": status,
            "available": list(status.keys())
        }
    
    def run(self, message: str) -> dict:
        """
        Run the agent with a user message.
        Returns the AgentResult as a dict.
        """
        if not self._initialized or self._agent is None:
            return {
                "success": False,
                "message": "Agent not initialized. Call /api/initialize first.",
                "trace": []
            }
        
        try:
            result: AgentResult = self._agent.run(message)
            
            # Convert trace to serializable format
            trace_data = []
            for step in result.trace.steps:
                trace_data.append({
                    "step_id": step.step_id,
                    "action": step.action,
                    "success": step.success,
                    "result": str(step.result) if step.result else None,
                    "observation": str(step.observation) if step.observation else None,
                    "error": step.error,
                    "timestamp": step.timestamp
                })
            
            return {
                "success": result.success,
                "message": result.message,
                "trace": trace_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "trace": []
            }
    
    def get_status(self) -> dict:
        """Get current system status including LLM provider."""
        llm_provider = None
        if self._brain:
            llm_provider = self._brain.get_provider_name()
            
        return {
            "initialized": self._initialized,
            "gpu": "NVIDIA RTX 3050" if self._initialized else "Not active",
            "llm_provider": llm_provider
        }


# Global instance
agent_service = AgentService()
