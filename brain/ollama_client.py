"""
Ollama LLM Client - Primary local LLM provider.
Uses Ollama API to run local models like qwen2.5:7b.
"""
import requests
import json
import logging
from typing import List, Dict, Optional
from brain.llm_provider import LLMProvider

logger = logging.getLogger("AURA.OllamaClient")


class OllamaClient(LLMProvider):
    """
    Ollama API client for local LLM inference.
    Default model: qwen2.5:7b
    """
    
    def __init__(
        self,
        model_name: str = "qwen2.5:7b",
        base_url: str = "http://localhost:11434"
    ):
        self._model_name = model_name
        self._base_url = base_url
        self._chat_history: List[Dict[str, str]] = []
        
        # Generation parameters
        self._options = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 64,
            "num_predict": 8192,
        }
    
    @property
    def name(self) -> str:
        return "ollama"
    
    @property
    def model(self) -> str:
        return self._model_name
    
    def start_chat(self, history: Optional[List[Dict[str, str]]] = None) -> None:
        """
        Initialize or reset chat history.
        """
        self._chat_history = []
        if history:
            for msg in history:
                role = "user" if msg["role"] == "user" else "assistant"
                self._chat_history.append({
                    "role": role,
                    "content": msg["content"]
                })
    
    def generate_response(self, prompt: str) -> str:
        """
        Send a prompt to Ollama and get a response.
        Uses the chat API for conversation continuity.
        """
        # Add user message to history
        self._chat_history.append({
            "role": "user",
            "content": prompt
        })
        
        try:
            response = requests.post(
                f"{self._base_url}/api/chat",
                json={
                    "model": self._model_name,
                    "messages": self._chat_history,
                    "stream": False,
                    "options": self._options
                },
                timeout=120  # 2 minute timeout for long responses
            )
            response.raise_for_status()
            
            result = response.json()
            assistant_message = result.get("message", {}).get("content", "")
            
            # Add assistant response to history
            self._chat_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return assistant_message
            
        except requests.exceptions.ConnectionError:
            error_msg = "Ollama is not running. Please start Ollama service."
            logger.error(error_msg)
            return f'{{"type": "ERROR", "message": "{error_msg}"}}'
            
        except requests.exceptions.Timeout:
            error_msg = "Ollama request timed out. The model may be overloaded."
            logger.error(error_msg)
            return f'{{"type": "ERROR", "message": "{error_msg}"}}'
            
        except Exception as e:
            error_msg = f"Ollama API Error: {str(e)}"
            logger.error(error_msg)
            return f'{{"type": "ERROR", "message": "{error_msg}"}}'
    
    def health_check(self) -> bool:
        """
        Check if Ollama is running and the model is available.
        """
        try:
            # Check if Ollama is running
            response = requests.get(
                f"{self._base_url}/api/tags",
                timeout=5
            )
            response.raise_for_status()
            
            # Check if our model is available
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            
            # Check if model exists (with or without :latest tag)
            model_found = any(
                self._model_name in name or name.startswith(self._model_name.split(":")[0])
                for name in model_names
            )
            
            if not model_found:
                logger.warning(f"Model {self._model_name} not found. Available: {model_names}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
    
    def generate_content_oneshot(self, prompt: str, image_path: str = None) -> str:
        """
        One-off generation without chat history.
        Useful for standalone queries.
        """
        try:
            response = requests.post(
                f"{self._base_url}/api/generate",
                json={
                    "model": self._model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": self._options
                },
                timeout=120
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
            
        except Exception as e:
            logger.error(f"Ollama generate error: {e}")
            return f'{{"type": "ERROR", "message": "Ollama Error: {str(e)}"}}'
