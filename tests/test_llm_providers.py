import pytest
from llm.models import load_models, get_llm_model, ModelProvider

PROVIDER_ENV = {
    ModelProvider.ANTHROPIC: "ANTHROPIC_API_KEY",
    ModelProvider.GOOGLE: "GOOGLE_API_KEY",
    ModelProvider.OPENAI: "OPENAI_API_KEY",
    ModelProvider.GROQ: "GROQ_API_KEY",
}


def test_load_models_includes_all_providers():
    all_models = load_models()
    providers_in_models = {m.provider for m in all_models.models}
    for prov in PROVIDER_ENV.keys():
        assert prov in providers_in_models, f"{prov} missing from AVAILABLE_MODELS"


@pytest.mark.parametrize("provider,env_name", list(PROVIDER_ENV.items()))
def test_get_llm_model_requires_env_key(provider, env_name, monkeypatch):
    # ensure env not present
    monkeypatch.delenv(env_name, raising=False)
    with pytest.raises(ValueError) as exc:
        get_llm_model(provider, "dummy-model")
    assert env_name in str(exc.value)


@pytest.mark.parametrize("provider,env_name", list(PROVIDER_ENV.items()))
def test_get_llm_model_calls_init_chat_model(provider, env_name, monkeypatch):
    # provide fake key and stub init_chat_model
    monkeypatch.setenv(env_name, "fake-key")

    def fake_init_chat_model(model, api_key, **kwargs):
        return {"model": model, "api_key": api_key, "kwargs": kwargs}

    monkeypatch.setattr("llm.models.init_chat_model", fake_init_chat_model)

    model_name = "test-model-123"
    result = get_llm_model(provider, model_name)
    assert isinstance(result, dict)
    assert result["model"] == f"{provider.value}:{model_name}"
    assert result["api_key"] == "fake-key"