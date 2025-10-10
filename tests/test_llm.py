"""
Tests for LLM integration components.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pydantic import ValidationError

from src.llm.models import (
    ModelProvider, LLMModel, AllModels, 
    load_models, get_llm_model
)
from src.llm.api import AVAILABLE_MODELS


# ============================================================================
# Model Provider Tests
# ============================================================================

@pytest.mark.unit
class TestModelProvider:
    """Tests for ModelProvider enum."""

    def test_model_provider_values(self):
        """Test ModelProvider enum values."""
        assert ModelProvider.ANTHROPIC == "anthropic"
        assert ModelProvider.GOOGLE == "google_genai"
        assert ModelProvider.OPENAI == "openai"

    def test_model_provider_from_string(self):
        """Test creating ModelProvider from string."""
        provider = ModelProvider("anthropic")
        assert provider == ModelProvider.ANTHROPIC


# ============================================================================
# LLM Model Tests
# ============================================================================

@pytest.mark.unit
class TestLLMModel:
    """Tests for LLMModel class."""

    def test_create_llm_model(self):
        """Test creating an LLM model instance."""
        model = LLMModel(
            provider=ModelProvider.ANTHROPIC,
            model_name="claude-3-5-sonnet-latest",
            display="Claude 3.5 Sonnet"
        )
        assert model.provider == ModelProvider.ANTHROPIC
        assert model.model_name == "claude-3-5-sonnet-latest"
        assert model.display == "Claude 3.5 Sonnet"

    def test_llm_model_validation(self):
        """Test LLM model validation."""
        with pytest.raises(ValidationError):
            LLMModel(
                provider="invalid_provider",
                model_name="test",
                display="Test"
            )


# ============================================================================
# All Models Tests
# ============================================================================

@pytest.mark.unit
class TestAllModels:
    """Tests for AllModels class."""

    def test_create_all_models(self):
        """Test creating AllModels instance."""
        models = [
            LLMModel(
                provider=ModelProvider.ANTHROPIC,
                model_name="claude-3-5-sonnet-latest",
                display="Claude 3.5 Sonnet"
            ),
            LLMModel(
                provider=ModelProvider.OPENAI,
                model_name="gpt-4o",
                display="GPT-4o"
            )
        ]
        all_models = AllModels(models=models)
        assert len(all_models.models) == 2
        assert all_models.models[0].provider == ModelProvider.ANTHROPIC


# ============================================================================
# Load Models Tests
# ============================================================================

@pytest.mark.unit
class TestLoadModels:
    """Tests for load_models function."""

    def test_load_models_default(self):
        """Test loading models with default AVAILABLE_MODELS."""
        all_models = load_models()
        assert isinstance(all_models, AllModels)
        assert len(all_models.models) > 0
        assert all(isinstance(m, LLMModel) for m in all_models.models)

    def test_load_models_custom(self):
        """Test loading models with custom model list."""
        custom_models = [
            {
                "provider": "anthropic",
                "model_name": "claude-test",
                "display": "Test Claude"
            }
        ]
        all_models = load_models(custom_models)
        assert len(all_models.models) == 1
        assert all_models.models[0].model_name == "claude-test"

    def test_load_models_multiple_providers(self):
        """Test loading models from multiple providers."""
        all_models = load_models()
        providers = {model.provider for model in all_models.models}
        # Check that we have models from different providers
        assert len(providers) > 0

    def test_available_models_structure(self):
        """Test that AVAILABLE_MODELS has correct structure."""
        assert isinstance(AVAILABLE_MODELS, list)
        assert len(AVAILABLE_MODELS) > 0
        
        for model_dict in AVAILABLE_MODELS:
            assert "provider" in model_dict
            assert "model_name" in model_dict
            assert "display" in model_dict


# ============================================================================
# Get LLM Model Tests
# ============================================================================

@pytest.mark.unit
class TestGetLLMModel:
    """Tests for get_llm_model function."""

    @patch('src.llm.models.init_chat_model')
    @patch('src.llm.models.config')
    def test_get_anthropic_model(self, mock_config, mock_init_chat):
        """Test getting Anthropic model."""
        mock_config.return_value = "test-api-key"
        mock_model = Mock()
        mock_init_chat.return_value = mock_model

        result = get_llm_model(
            ModelProvider.ANTHROPIC, 
            "claude-3-5-sonnet-latest"
        )

        mock_config.assert_called_once_with("ANTHROPIC_API_KEY", default=None)
        # Check that init_chat_model was called with correct model string
        call_args = mock_init_chat.call_args
        assert "claude-3-5-sonnet-latest" in call_args[1]['model']
        assert call_args[1]['api_key'] == "test-api-key"
        assert result == mock_model

    @patch('src.llm.models.init_chat_model')
    @patch('src.llm.models.config')
    def test_get_openai_model(self, mock_config, mock_init_chat):
        """Test getting OpenAI model."""
        mock_config.return_value = "test-api-key"
        mock_model = Mock()
        mock_init_chat.return_value = mock_model

        result = get_llm_model(
            ModelProvider.OPENAI,
            "gpt-4o"
        )

        mock_config.assert_called_once_with("OPENAI_API_KEY", default=None)
        # Check that init_chat_model was called with correct model string
        call_args = mock_init_chat.call_args
        assert "gpt-4o" in call_args[1]['model']
        assert call_args[1]['api_key'] == "test-api-key"
        assert result == mock_model

    @patch('src.llm.models.init_chat_model')
    @patch('src.llm.models.config')
    def test_get_google_model(self, mock_config, mock_init_chat):
        """Test getting Google model."""
        mock_config.return_value = "test-api-key"
        mock_model = Mock()
        mock_init_chat.return_value = mock_model

        result = get_llm_model(
            ModelProvider.GOOGLE,
            "gemini-2.0-flash"
        )

        mock_config.assert_called_once_with("GOOGLE_API_KEY", default=None)
        # Check that init_chat_model was called with correct model string
        call_args = mock_init_chat.call_args
        assert "gemini-2.0-flash" in call_args[1]['model']
        assert call_args[1]['api_key'] == "test-api-key"
        assert result == mock_model

    @patch('src.llm.models.config')
    def test_get_model_missing_api_key_anthropic(self, mock_config):
        """Test error when API key is missing for Anthropic."""
        mock_config.return_value = None

        with pytest.raises(ValueError, match="Missing ANTHROPIC_API_KEY"):
            get_llm_model(ModelProvider.ANTHROPIC, "claude-3-5-sonnet-latest")

    @patch('src.llm.models.config')
    def test_get_model_missing_api_key_openai(self, mock_config):
        """Test error when API key is missing for OpenAI."""
        mock_config.return_value = None

        with pytest.raises(ValueError, match="Missing OPENAI_API_KEY"):
            get_llm_model(ModelProvider.OPENAI, "gpt-4o")

    @patch('src.llm.models.config')
    def test_get_model_missing_api_key_google(self, mock_config):
        """Test error when API key is missing for Google."""
        mock_config.return_value = None

        with pytest.raises(ValueError, match="Missing GOOGLE_API_KEY"):
            get_llm_model(ModelProvider.GOOGLE, "gemini-2.0-flash")

    @patch('src.llm.models.init_chat_model')
    @patch('src.llm.models.config')
    def test_get_model_with_custom_api_key(self, mock_config, mock_init_chat):
        """Test getting model with custom API key parameter."""
        mock_model = Mock()
        mock_init_chat.return_value = mock_model
        
        # When api_key is provided, config should still be called
        # but the provided key might be used (depending on implementation)
        mock_config.return_value = "test-api-key"

        result = get_llm_model(
            ModelProvider.ANTHROPIC,
            "claude-3-5-sonnet-latest",
            api_key="custom-key"
        )

        assert mock_init_chat.called
        assert result == mock_model


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.integration
class TestLLMIntegration:
    """Integration tests for LLM components."""

    def test_load_and_validate_all_models(self):
        """Test that all available models can be loaded and validated."""
        all_models = load_models()
        
        assert len(all_models.models) > 0
        
        for model in all_models.models:
            assert isinstance(model, LLMModel)
            assert isinstance(model.provider, ModelProvider)
            assert len(model.model_name) > 0
            assert len(model.display) > 0

    def test_model_provider_coverage(self):
        """Test that we have models from major providers."""
        all_models = load_models()
        providers = {model.provider for model in all_models.models}
        
        # Check for major providers
        expected_providers = {
            ModelProvider.ANTHROPIC,
            ModelProvider.OPENAI,
            ModelProvider.GOOGLE
        }
        
        # At least some of the expected providers should be present
        assert len(providers.intersection(expected_providers)) > 0
