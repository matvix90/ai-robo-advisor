from langchain.chat_models import init_chat_model

from pydantic import BaseModel
from enum import Enum

from .api import AVAILABLE_MODELS

from decouple import config


class ModelProvider(str, Enum):
    """Enum for supported LLM providers"""

    ANTHROPIC = "anthropic"
    GOOGLE = "google_genai"
    OPENAI = "openai"

class LLMModel(BaseModel):
    """Base class for LLM models"""

    provider: ModelProvider
    model_name: str
    display: str

class AllModels(BaseModel):
    """Class to hold all supported models"""

    models: list[LLMModel]

def load_models(available_models=AVAILABLE_MODELS) -> AllModels:
    models = [LLMModel(**model) for model in available_models]
    return AllModels(models=models)

def get_llm_model(provider: ModelProvider, model_name: str, api_key=None) -> str:
    if provider == ModelProvider.ANTHROPIC:
        api_key = config("ANTHROPIC_API_KEY", default=None)
        if not api_key:
            raise ValueError("Missing ANTHROPIC_API_KEY in environment.")
        model = f"{provider}:{model_name}"
        return init_chat_model(model=model, api_key=api_key)
    elif provider == ModelProvider.GOOGLE:
        api_key = config("GOOGLE_API_KEY", default=None)
        if not api_key:
            raise ValueError("Missing GOOGLE_API_KEY in environment.")
        model = f"{provider}:{model_name}"
        return init_chat_model(model=model, api_key=api_key)
    elif provider == ModelProvider.OPENAI:
        api_key = config("OPENAI_API_KEY", default=None)
        if not api_key:
            raise ValueError("Missing OPENAI_API_KEY in environment.")
        model = f"{provider}:{model_name}"
        return init_chat_model(model=model, api_key=api_key)
