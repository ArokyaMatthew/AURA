"""
Brain - Decision-making component for AURA agent.
Uses LLMRouter to select between Ollama (primary) and Gemini (manual).
"""
import json
import logging
from typing import Optional
from brain.llm_router import LLMRouter
from brain.prompt import SYSTEM_PROMPT

# =========================================================
# LOGGING CONFIGURATION
# =========================================================

# Create logger for Brain module
logger = logging.getLogger("AURA.Brain")
logger.setLevel(logging.DEBUG)

# Prevent duplicate handlers if module is reloaded
if not logger.handlers:
    # Console handler - shows everything in terminal
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_format = logging.Formatter(
        '\n%(asctime)s | %(levelname)s | %(name)s\n%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler - persistent log file
    file_handler = logging.FileHandler('aura_brain_debug.log', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)


class Brain:
    """
    Decision-making component.
    Uses LLMRouter to switch between Ollama (default) and Gemini.
    """

    def __init__(self, default_provider: str = "ollama"):
        # Initialize LLM Router with provider selection
        self.llm = LLMRouter(default_provider=default_provider)
        logger.info(f"Brain initialized with LLM provider: {self.llm.current_provider_name}")

    def set_provider(self, provider_name: str) -> bool:
        """
        Switch to a different LLM provider.
        
        Args:
            provider_name: 'ollama' or 'gemini'
            
        Returns:
            True if switch successful
        """
        success = self.llm.set_provider(provider_name)
        if success:
            logger.info(f"Brain switched to provider: {provider_name}")
        return success
    
    def get_provider_name(self) -> str:
        """Get current provider name."""
        return self.llm.current_provider_name
    
    def get_provider_status(self) -> dict:
        """Get status of all providers."""
        return self.llm.get_provider_status()

    def next_action(
        self,
        goal: str,
        memory_context: str,
        last_observation,
        last_error,
        step_state,
    ) -> dict:
        """
        Decide the next action or STOP.
        """

        prompt = f"""
{SYSTEM_PROMPT}

USER GOAL:
{goal}

RELEVANT MEMORY:
{memory_context}

LAST OBSERVATION:
{last_observation}

LAST ERROR:
{last_error}

CURRENT STEP:
{step_state.step_count}

Respond with JSON only.
"""

        raw_output = self.llm.generate_response(prompt)
        
        # Log full raw output with visual separator
        provider_name = self.llm.current_provider_name.upper()
        logger.debug(
            f"{'='*60}\n"
            f"{provider_name} RAW OUTPUT:\n"
            f"{'='*60}\n"
            f"{raw_output}\n"
            f"{'='*60}"
        )
        
        # --- Clean Markdown Fencing ---
        clean_output = self._clean_json(raw_output)
        
        # --- Strict JSON enforcement ---
        try:
            action = json.loads(clean_output)
            # Log parsed action with pretty formatting
            logger.debug(
                f"{'='*60}\n"
                f"PARSED ACTION (Pretty JSON):\n"
                f"{'='*60}\n"
                f"{json.dumps(action, indent=2, ensure_ascii=False)}\n"
                f"{'='*60}"
            )
        except json.JSONDecodeError as e:
            logger.error(f"JSON Parse Error: {e}\nRaw output was:\n{raw_output}")
            # Emergency fallback (safe stop)
            return {
                "type": "STOP",
                "message": f"Stopped due to invalid model output: {raw_output}"
            }

        # --- Minimal validation ---
        if "type" not in action:
            return {
                "type": "STOP",
                "message": "Stopped due to malformed action (missing 'type')."
            }

        return action

    def _clean_json(self, text: str) -> str:
        """
        Removes markdown code fences if present.
        """
        text = text.strip()
        # Remove ```json and ``` or just ```
        if text.startswith("```"):
            # Find the first newline
            first_newline = text.find("\n")
            if first_newline != -1:
                text = text[first_newline+1:]
            # Remove trailing ```
            if text.endswith("```"):
                text = text[:-3]
        return text.strip()
