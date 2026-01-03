"""
REST API Routes - Includes LLM provider switching endpoints.
"""
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.agent_service import agent_service


router = APIRouter()


# =========================================================
# Request/Response Models
# =========================================================

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    success: bool
    message: str
    trace: list


class InitRequest(BaseModel):
    provider: Optional[str] = "ollama"


class InitResponse(BaseModel):
    success: bool
    message: str


class StatusResponse(BaseModel):
    initialized: bool
    gpu: str
    llm_provider: Optional[str] = None


class SetProviderRequest(BaseModel):
    provider: str


class SetProviderResponse(BaseModel):
    success: bool
    message: str
    provider: Optional[str] = None


class LLMStatusResponse(BaseModel):
    current_provider: Optional[str] = None
    providers: Dict[str, Any] = {}
    available: List[str] = []


# =========================================================
# Agent Lifecycle Endpoints
# =========================================================

@router.post("/initialize", response_model=InitResponse)
async def initialize_agent(request: InitRequest = None):
    """
    Initialize the AURA agent system.
    
    Args:
        provider: LLM provider to use ('ollama' or 'gemini'). Default: 'ollama'
    """
    provider = "ollama"
    if request and request.provider:
        provider = request.provider
        
    result = agent_service.initialize(provider=provider)
    return InitResponse(**result)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the agent and get a response."""
    if not agent_service.is_initialized:
        raise HTTPException(
            status_code=400,
            detail="Agent not initialized. Call /api/initialize first."
        )
    
    result = agent_service.run(request.message)
    return ChatResponse(**result)


@router.get("/status", response_model=StatusResponse)
async def get_status():
    """Get the current system status including LLM provider."""
    result = agent_service.get_status()
    return StatusResponse(**result)


# =========================================================
# LLM Provider Endpoints
# =========================================================

@router.post("/llm/provider", response_model=SetProviderResponse)
async def set_llm_provider(request: SetProviderRequest):
    """
    Switch LLM provider.
    
    Args:
        provider: 'ollama' or 'gemini'
    """
    if not agent_service.is_initialized:
        raise HTTPException(
            status_code=400,
            detail="Agent not initialized. Call /api/initialize first."
        )
    
    result = agent_service.set_llm_provider(request.provider)
    return SetProviderResponse(**result)


@router.get("/llm/status", response_model=LLMStatusResponse)
async def get_llm_status():
    """Get current LLM provider status and available providers."""
    result = agent_service.get_llm_status()
    return LLMStatusResponse(**result)
