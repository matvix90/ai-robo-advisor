from enum import Enum

from decouple import config
from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import BaseModel

from .api import AVAILABLE_MODELS

# Import init_chat_model at module level for easier testing
try:
    from langchain.chat_models import init_chat_model
except ImportError:
    init_chat_model = None


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

    models: list[LLMModel]


def load_models(available_models: list[dict] = AVAILABLE_MODELS) -> AllModels:
    """Load and return all available LLM models."""
    models = [LLMModel(**model) for model in available_models]
    return AllModels(models=models)


def get_llm_model(
    provider: ModelProvider,
    model_name: str,
    api_key: str | None = None,
    temperature: float = 0.7,
    **kwargs,
) -> BaseChatModel:
    """Initialize and return the LLM model based on provider and model name.

    Args:
        provider: The LLM provider to use
        model_name: The specific model name
        api_key: Optional API key (will use env var if not provided)
        temperature: Model temperature (default: 0.7)
        **kwargs: Additional model parameters

    Returns:
        Initialized chat model instance

    Raises:
        ValueError: If API key is missing or provider is unsupported
        ImportError: If required provider package is not installed
    """
    if init_chat_model is None:
        raise ImportError(
            "langchain package is required. Install with: pip install langchain"
        )

    if provider == ModelProvider.ANTHROPIC:
        api_key = api_key or config("ANTHROPIC_API_KEY", default=None)
        if not api_key:
            raise ValueError("Missing ANTHROPIC_API_KEY in environment.")
        model = f"{provider.value}:{model_name}"
        return init_chat_model(
            model=model, api_key=api_key, temperature=temperature, **kwargs
        )

    elif provider == ModelProvider.GOOGLE:
        api_key = api_key or config("GOOGLE_API_KEY", default=None)
        if not api_key:
            raise ValueError("Missing GOOGLE_API_KEY in environment.")
        model = f"{provider.value}:{model_name}"
        return init_chat_model(
            model=model, api_key=api_key, temperature=temperature, **kwargs
        )

    elif provider == ModelProvider.OPENAI:
        api_key = api_key or config("OPENAI_API_KEY", default=None)
        if not api_key:
            raise ValueError("Missing OPENAI_API_KEY in environment.")
        model = f"{provider.value}:{model_name}"
        return init_chat_model(
            model=model, api_key=api_key, temperature=temperature, **kwargs
        )

    elif provider == ModelProvider.GROQ:
        api_key = api_key or config("GROQ_API_KEY", default=None)
        if not api_key:
            raise ValueError("Missing GROQ_API_KEY in environment.")

        try:
            # Direct import and use ChatGroq for better control
            from langchain_groq import ChatGroq

            print(f"✅ Using ChatGroq with model: {model_name}")
            return ChatGroq(
                groq_api_key=api_key,
                model_name=model_name,
                temperature=temperature,
                **kwargs,
            )
        except ImportError:
            # Fallback to init_chat_model if ChatGroq not available
            print("⚠️ Falling back to init_chat_model (langchain_groq not found)")
            model = f"{provider.value}:{model_name}"
            return init_chat_model(
                model=model, api_key=api_key, temperature=temperature, **kwargs
            )

    else:
        raise ValueError(f"Unsupported provider: {provider}")

