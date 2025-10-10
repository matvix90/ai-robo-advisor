from langchain.chat_models import init_chat_model
from pydantic import BaseModel
from enum import Enum
from typing import Any, List
from decouple import config

from .api import AVAILABLE_MODELS


class ModelProvider(str, Enum):
    """Enum for supported LLM providers"""
    ANTHROPIC = "anthropic"
    GOOGLE = "google_genai"
    OPENAI = "openai"
    GROQ = "groq"


class LLMModel(BaseModel):
    """Base class for LLM models"""
    provider: ModelProvider
    model_name: str
    display: str


class AllModels(BaseModel):
    """Class to hold all supported models"""
    models: List[LLMModel]


def load_models(available_models=AVAILABLE_MODELS) -> AllModels:
    """Load and return all available LLM models."""
    models = [LLMModel(**model) for model in available_models]
    return AllModels(models=models)


def get_llm_model(provider: ModelProvider, model_name: str, api_key: str | None = None, **kwargs) -> Any:
    """Initialize and return the LLM model based on provider and model name.

    Notes:
    - For GROQ we instantiate langchain_groq.ChatGroq directly (pass exact model id).
    - For other providers we rely on init_chat_model and use provider.value prefix.
    """
    # Resolve API key if not provided
    if provider == ModelProvider.ANTHROPIC:
        api_key = api_key or config("ANTHROPIC_API_KEY", default=None)
        if not api_key:
            raise ValueError("Missing ANTHROPIC_API_KEY in environment.")
        model = f"{provider.value}:{model_name}"
        return init_chat_model(model=model, api_key=api_key, **kwargs)

    if provider == ModelProvider.GOOGLE:
        api_key = api_key or config("GOOGLE_API_KEY", default=None)
        if not api_key:
            raise ValueError("Missing GOOGLE_API_KEY in environment.")
        model = f"{provider.value}:{model_name}"
        return init_chat_model(model=model, api_key=api_key, **kwargs)

    if provider == ModelProvider.OPENAI:
        api_key = api_key or config("OPENAI_API_KEY", default=None)
        if not api_key:
            raise ValueError("Missing OPENAI_API_KEY in environment.")
        model = f"{provider.value}:{model_name}"
        return init_chat_model(model=model, api_key=api_key, **kwargs)

    if provider == ModelProvider.GROQ:
       api_key = api_key or config("GROQ_API_KEY", default=None)
       if not api_key:
            raise ValueError("Missing GROQ_API_KEY in environment.")

    try:
        # ✅ Directly import and use ChatGroq (the same way as temp.py)
        from langchain_groq import ChatGroq
        print(f"✅ Using ChatGroq with model: {model_name}")
        return ChatGroq(
            groq_api_key=api_key,
            model_name=model_name,
            temperature=0.7,
        )
    except ImportError:
        # fallback to init_chat_model if ChatGroq not available
        print("⚠️ Falling back to init_chat_model (ChatGroq not found)")
        model = f"{provider.value}:{model_name}"
        return init_chat_model(model=model, api_key=api_key, **kwargs)

    raise ValueError(f"Unsupported provider: {provider}")
