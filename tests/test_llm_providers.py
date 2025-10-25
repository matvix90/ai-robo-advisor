import pytest

from src.llm.models import ModelProvider, get_llm_model, load_models

PROVIDER_ENV = {
    ModelProvider.ANTHROPIC: "ANTHROPIC_API_KEY",
    ModelProvider.GOOGLE: "GOOGLE_API_KEY",
    ModelProvider.OPENAI: "OPENAI_API_KEY",
    ModelProvider.GROQ: "GROQ_API_KEY",
}


def test_load_models_includes_all_providers():
    all_models = load_models()
    providers_in_models = {m.provider for m in all_models.models}
    for prov in PROVIDER_ENV:
        assert prov in providers_in_models, f"{prov} missing from AVAILABLE_MODELS"


@pytest.mark.parametrize("provider,env_name", list(PROVIDER_ENV.items()))
def test_get_llm_model_requires_env_key(provider, env_name, monkeypatch):
    # ensure env not present by patching config to return None
    monkeypatch.delenv(env_name, raising=False)

    # Mock the config function to always return None for the specific env_name
    def mock_config(key, default=None):
        if key == env_name:
            return None
        return default

    monkeypatch.setattr("src.llm.models.config", mock_config)

    with pytest.raises(ValueError) as exc:
        get_llm_model(provider, "dummy-model")
    assert env_name in str(exc.value)


@pytest.mark.parametrize("provider,env_name", list(PROVIDER_ENV.items()))
def test_get_llm_model_calls_init_chat_model(provider, env_name, monkeypatch):
    # provide fake key and stub init_chat_model
    monkeypatch.setenv(env_name, "fake-key")

    def fake_init_chat_model(model, api_key, **kwargs):
        return {"model": model, "api_key": api_key, "kwargs": kwargs}

    monkeypatch.setattr("src.llm.models.init_chat_model", fake_init_chat_model)

    # For GROQ, we need to mock the ChatGroq import to force fallback to init_chat_model
    if provider == ModelProvider.GROQ:

        def mock_import(name, *args, **kwargs):
            if name == "langchain_groq":
                raise ImportError("Mocked import error for testing")
            return __import__(name, *args, **kwargs)

        import builtins

        original_import = builtins.__import__
        monkeypatch.setattr("builtins.__import__", mock_import)

    model_name = "test-model-123"
    result = get_llm_model(provider, model_name)
    assert isinstance(result, dict)
    assert result["model"] == f"{provider.value}:{model_name}"
    assert result["api_key"] == "fake-key"
