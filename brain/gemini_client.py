"""
Gemini LLM Client - Google's Gemini API provider.
Implements LLMProvider interface for consistent API.
"""
import os
import logging
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from brain.llm_provider import LLMProvider

logger = logging.getLogger("AURA.GeminiClient")


class GeminiClient(LLMProvider):
    """
    Wrapper for Google's Gemini API to serve as the agent's brain.
    Implements LLMProvider interface.
    """
    
    def __init__(self, model_name: str = "gemini-2.5-flash", api_key: Optional[str] = None):
        self._model_name = model_name
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            logger.warning("Google API Key not found. Gemini provider will not be available.")
            self._available = False
            self._model = None
            self.chat_session = None
            return
        
        self._available = True
        genai.configure(api_key=self.api_key)
        
        self._model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=genai.GenerationConfig(
                temperature=0.7,
                top_p=0.95,
                top_k=64,
                max_output_tokens=8192,
            )
        )
        self.chat_session = None
    
    @property
    def name(self) -> str:
        return "gemini"
    
    @property
    def model(self) -> str:
        return self._model_name

    def start_chat(self, history: Optional[List[Dict[str, str]]] = None) -> None:
        """
        Initializes a chat session with history.
        """
        if not self._available:
            return
            
        gemini_history = []
        if history:
            for msg in history:
                role = "user" if msg["role"] == "user" else "model"
                gemini_history.append({"role": role, "parts": [msg["content"]]})
        
        self.chat_session = self._model.start_chat(history=gemini_history)

    def generate_response(self, prompt: str) -> str:
        """
        Sends a prompt to the model and returns the text response.
        """
        if not self._available:
            return '{"type": "ERROR", "message": "Gemini API Key not configured"}'
            
        if not self.chat_session:
            self.start_chat()
            
        try:
            response = self.chat_session.send_message(prompt)
            return response.text
        except Exception as e:
            error_msg = f"Gemini API Error: {str(e)}"
            logger.error(error_msg)
            return f'{{"type": "ERROR", "message": "{error_msg}"}}'

    def health_check(self) -> bool:
        """
        Check if Gemini API is available and working.
        """
        if not self._available:
            return False
            
        try:
            # Try a simple generation to verify API works
            response = self._model.generate_content("Say 'ok'")
            return response.text is not None
        except Exception as e:
            logger.error(f"Gemini health check failed: {e}")
            return False

    def generate_content_oneshot(self, prompt: str, image_path: str = None) -> str:
        """
        One-off generation, useful for vision tasks.
        """
        if not self._available:
            return '{"type": "ERROR", "message": "Gemini API Key not configured"}'
            
        content = [prompt]
        if image_path:
            # In a real scenario, we'd load the image data here using PIL or similar
            pass 
        
        try:
            response = self._model.generate_content(content)
            return response.text
        except Exception as e:
            logger.error(f"Gemini oneshot generation failed: {e}")
            return f'{{"type": "ERROR", "message": "Gemini Error: {str(e)}"}}'
