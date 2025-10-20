"""
Tests for questionnaire utilities.
"""
import pytest
from unittest.mock import Mock, patch
import sys

from src.utils.questionnaires import (
    get_user_preferences,
    choose_llm_model
)
from src.data.models import (
    InvestmentGoal, RiskProfile, InvestmentHorizon,
    Currency, StockExchange, PortfolioPreference,
    InvestmentKnowledge, IncomeLevel, InvestmentPurpose,
    LiquidityNeed, MarketDownturnReaction, InvestmentPriority,
    Benchmarks
)
from src.llm.models import AllModels, LLMModel, ModelProvider


# ============================================================================
# Get User Preferences Tests
# ============================================================================

def get_complete_mock_setup():
    """Get complete mock setup for questionnaire tests."""
    return {
        'select_side_effect': [
            InvestmentKnowledge.INTERMEDIATE,       # investment_knowledge
            IncomeLevel.FROM_60K_TO_100K,          # income_level  
            InvestmentGoal.WEALTH_BUILDING,        # goal
            InvestmentPurpose.GROW_WEALTH,         # investment_purpose
            InvestmentHorizon.LONG_TERM,           # investment_horizon
            LiquidityNeed.OVER_5_YEARS,            # liquidity_need
            MarketDownturnReaction.HOLD,           # market_downturn_reaction
            InvestmentPriority.GROWTH,             # investment_priority
            Currency.USD,                          # currency
            StockExchange.NYSE,                    # stock_exchange
            Benchmarks.ACWI                        # benchmark
        ],
        'text_side_effect': [
            "35",      # age
            "20.0",    # max_acceptable_loss
            "5000",    # other_investments
            "10000",   # initial_investment
            "500"      # monthly_contribution
        ],
        'confirm_return': True  # has_emergency_fund
    }

@pytest.mark.unit
class TestGetUserPreferences:
    """Tests for get_user_preferences function."""

    @patch('src.utils.questionnaires.questionary.text')
    @patch('src.utils.questionnaires.questionary.select')
    @patch('src.utils.questionnaires.questionary.confirm')
    def test_get_user_preferences_complete(self, mock_confirm, mock_select, mock_text):
        """Test getting complete user preferences."""
        # Get standard mock setup
        mock_setup = get_complete_mock_setup()
        
        mock_select.return_value.ask.side_effect = mock_setup['select_side_effect']
        mock_text.return_value.ask.side_effect = mock_setup['text_side_effect']
        mock_confirm.return_value.ask.return_value = mock_setup['confirm_return']
        
        result = get_user_preferences()
        
        # Check type using type() instead of isinstance for better compatibility
        assert type(result).__name__ == 'PortfolioPreference'
        assert result.goal == InvestmentGoal.WEALTH_BUILDING
        assert result.risk_profile.value  # Calculated risk profile
        assert result.investment_horizon == InvestmentHorizon.LONG_TERM
        assert result.currency == Currency.USD
        assert result.stock_exchange == StockExchange.NYSE
        assert result.initial_investment == 10000.0
        assert result.age == 35
        assert result.investment_knowledge == InvestmentKnowledge.INTERMEDIATE
        assert result.income_level == IncomeLevel.FROM_60K_TO_100K
        assert result.benchmark == Benchmarks.ACWI.value
    @patch('src.utils.questionnaires.questionary.select')
    def test_get_user_preferences_keyboard_interrupt(self, mock_select):
        """Test handling of keyboard interrupt."""
        mock_select.return_value.ask.return_value = None  # Simulates interrupt
        
        with pytest.raises(SystemExit):
            get_user_preferences()

    @patch('src.utils.questionnaires.questionary.text')
    @patch('src.utils.questionnaires.questionary.select')
    @patch('src.utils.questionnaires.questionary.confirm')
    def test_get_user_preferences_different_currency(self, mock_confirm, mock_select, mock_text):
        """Test getting preferences with different currency."""
        mock_select.return_value.ask.side_effect = [
            InvestmentKnowledge.BASIC,              # investment_knowledge
            IncomeLevel.FROM_100K_TO_150K,         # income_level
            InvestmentGoal.RETIREMENT,             # goal
            InvestmentPurpose.GENERATE_INCOME,     # investment_purpose
            InvestmentHorizon.VERY_LONG_TERM,      # investment_horizon
            LiquidityNeed.FROM_3_TO_5_YEARS,       # liquidity_need
            MarketDownturnReaction.HOLD,           # market_downturn_reaction
            InvestmentPriority.STABILITY,          # investment_priority
            Currency.EUR,                          # currency
            StockExchange.EURONEXT,                # stock_exchange
            Benchmarks.ACWI                        # benchmark
        ]
        mock_text.return_value.ask.side_effect = [
            "45",      # age
            "10.0",    # max_acceptable_loss
            "15000",   # other_investments
            "50000",   # initial_investment
            "1000"     # monthly_contribution
        ]
        mock_confirm.return_value.ask.return_value = True  # has_emergency_fund
        
        result = get_user_preferences()
        
        assert result.currency == Currency.EUR
        assert result.stock_exchange == StockExchange.EURONEXT
        assert result.initial_investment == 50000.0
    @patch('src.utils.questionnaires.questionary.text')
    @patch('src.utils.questionnaires.questionary.select')
    @patch('src.utils.questionnaires.questionary.confirm')
    def test_get_user_preferences_different_benchmark(self, mock_confirm, mock_select, mock_text):
        """Test getting preferences with different currency."""
        mock_select.return_value.ask.side_effect = [
            InvestmentKnowledge.BASIC,              # investment_knowledge
            IncomeLevel.FROM_100K_TO_150K,         # income_level
            InvestmentGoal.RETIREMENT,             # goal
            InvestmentPurpose.GENERATE_INCOME,     # investment_purpose
            InvestmentHorizon.VERY_LONG_TERM,      # investment_horizon
            LiquidityNeed.FROM_3_TO_5_YEARS,       # liquidity_need
            MarketDownturnReaction.HOLD,           # market_downturn_reaction
            InvestmentPriority.STABILITY,          # investment_priority
            Currency.EUR,                          # currency
            StockExchange.EURONEXT,                # stock_exchange
            Benchmarks.SPY                       # benchmark
        ]
        mock_text.return_value.ask.side_effect = [
            "45",      # age
            "10.0",    # max_acceptable_loss
            "15000",   # other_investments
            "50000",   # initial_investment
            "1000"     # monthly_contribution
        ]
        mock_confirm.return_value.ask.return_value = True  # has_emergency_fund
        
        result = get_user_preferences()
        
        assert result.benchmark == Benchmarks.SPY.value
        assert result.stock_exchange == StockExchange.EURONEXT
        assert result.initial_investment == 50000.0

    @patch('src.utils.questionnaires.questionary.text')
    @patch('src.utils.questionnaires.questionary.select')
    @patch('src.utils.questionnaires.questionary.confirm')
    def test_get_user_preferences_amount_with_commas(self, mock_confirm, mock_select, mock_text):
        """Test handling of investment amount with commas."""
        mock_setup = get_complete_mock_setup()
        mock_select.return_value.ask.side_effect = mock_setup['select_side_effect']
        # Test amount with commas as initial investment input
        mock_text.return_value.ask.side_effect = [
            "35",       # age
            "20.0",     # max_acceptable_loss
            "5000",     # other_investments
            "100,000.50",  # initial_investment (with commas)
            "500"       # monthly_contribution
        ]
        mock_confirm.return_value.ask.return_value = mock_setup['confirm_return']
        
        result = get_user_preferences()
        
        assert result.initial_investment == 100000.50

    @patch('src.utils.questionnaires.questionary.text')
    @patch('src.utils.questionnaires.questionary.select')
    @patch('src.utils.questionnaires.questionary.confirm')
    def test_get_user_preferences_amount_with_currency_symbols(self, mock_confirm, mock_select, mock_text):
        """Test handling of investment amount with currency symbols."""
        mock_setup = get_complete_mock_setup()
        mock_select.return_value.ask.side_effect = mock_setup['select_side_effect']
        # Test amount with currency symbols as initial investment input
        mock_text.return_value.ask.side_effect = [
            "35",       # age
            "20.0",     # max_acceptable_loss
            "5000",     # other_investments
            "$25,000",  # initial_investment (with currency symbol)
            "500"       # monthly_contribution
        ]
        mock_confirm.return_value.ask.return_value = mock_setup['confirm_return']
        
        result = get_user_preferences()
        
        assert result.initial_investment == 25000.0

    @patch('src.utils.questionnaires.questionary.select')
    def test_get_user_preferences_interrupt_on_risk_profile(self, mock_select):
        """Test interrupt on risk profile selection."""
        # Return goal, then None for risk profile
        mock_select.return_value.ask.side_effect = [
            InvestmentGoal.WEALTH_BUILDING,
            None  # Interrupt on risk profile
        ]
        
        with pytest.raises(SystemExit):
            get_user_preferences()

    @patch('src.utils.questionnaires.questionary.select')
    def test_get_user_preferences_interrupt_on_horizon(self, mock_select):
        """Test interrupt on investment horizon selection."""
        mock_select.return_value.ask.side_effect = [
            InvestmentGoal.WEALTH_BUILDING,
            RiskProfile.MODERATE,
            None  # Interrupt on horizon
        ]
        
        with pytest.raises(SystemExit):
            get_user_preferences()

    @patch('src.utils.questionnaires.questionary.select')
    def test_get_user_preferences_interrupt_on_currency(self, mock_select):
        """Test interrupt on currency selection."""
        mock_select.return_value.ask.side_effect = [
            InvestmentGoal.WEALTH_BUILDING,
            RiskProfile.MODERATE,
            InvestmentHorizon.LONG_TERM,
            None  # Interrupt on currency
        ]
        
        with pytest.raises(SystemExit):
            get_user_preferences()

    @patch('src.utils.questionnaires.questionary.select')
    def test_get_user_preferences_interrupt_on_exchange(self, mock_select):
        """Test interrupt on stock exchange selection."""
        mock_select.return_value.ask.side_effect = [
            InvestmentGoal.WEALTH_BUILDING,
            RiskProfile.MODERATE,
            InvestmentHorizon.LONG_TERM,
            Currency.USD,
            None  # Interrupt on exchange
        ]
        
        with pytest.raises(SystemExit):
            get_user_preferences()

    @patch('src.utils.questionnaires.questionary.select')
    @patch('src.utils.questionnaires.questionary.text')
    def test_get_user_preferences_interrupt_on_amount(self, mock_text, mock_select):
        """Test interrupt on investment amount input."""
        mock_select.return_value.ask.side_effect = [
            InvestmentGoal.WEALTH_BUILDING,
            RiskProfile.MODERATE,
            InvestmentHorizon.LONG_TERM,
            Currency.USD,
            StockExchange.NYSE
        ]
        mock_text.return_value.ask.return_value = None  # Interrupt on amount
        
        with pytest.raises(SystemExit):
            get_user_preferences()

    @patch('src.utils.questionnaires.questionary.confirm')
    @patch('src.utils.questionnaires.questionary.select')
    @patch('src.utils.questionnaires.questionary.text')
    def test_get_user_preferences_euro_symbol(self, mock_text, mock_select, mock_confirm):
        """Test handling of Euro currency symbol."""
        mock_setup = get_complete_mock_setup()
        # Use EUR currency in the select side effect
        mock_setup_euro = mock_setup.copy()
        mock_setup_euro['select_side_effect'] = mock_setup['select_side_effect'].copy()
        mock_setup_euro['select_side_effect'][8] = Currency.EUR  # Update currency to EUR
        
        mock_select.return_value.ask.side_effect = mock_setup_euro['select_side_effect']
        # Test amount with Euro symbol as initial investment input
        mock_text.return_value.ask.side_effect = [
            "35",       # age
            "20.0",     # max_acceptable_loss
            "5000",     # other_investments
            "€15,000",  # initial_investment (with Euro symbol)
            "500"       # monthly_contribution
        ]
        mock_confirm.return_value.ask.return_value = mock_setup['confirm_return']
        
        result = get_user_preferences()
        
        assert result.initial_investment == 15000.0

    @patch('src.utils.questionnaires.questionary.text')
    @patch('src.utils.questionnaires.questionary.select')
    @patch('src.utils.questionnaires.questionary.confirm')
    def test_get_user_preferences_pound_symbol(self, mock_confirm, mock_select, mock_text):
        """Test handling of Pound currency symbol."""
        mock_setup = get_complete_mock_setup()
        # Use GBP currency in the select side effect
        mock_setup_gbp = mock_setup.copy()
        mock_setup_gbp['select_side_effect'] = mock_setup['select_side_effect'].copy()
        mock_setup_gbp['select_side_effect'][8] = Currency.GBP  # Update currency to GBP
        
        mock_select.return_value.ask.side_effect = mock_setup_gbp['select_side_effect']
        # Test amount with Pound symbol as initial investment input
        mock_text.return_value.ask.side_effect = [
            "35",       # age
            "20.0",     # max_acceptable_loss
            "5000",     # other_investments
            "£20,000",  # initial_investment (with Pound symbol)
            "500"       # monthly_contribution
        ]
        mock_confirm.return_value.ask.return_value = mock_setup['confirm_return']
        
        result = get_user_preferences()
        
        assert result.initial_investment == 20000.0


# ============================================================================
# Choose LLM Model Tests
# ============================================================================

@pytest.mark.unit
class TestChooseLLMModel:
    """Tests for choose_llm_model function."""

    @patch('src.utils.questionnaires.questionary.select')
    def test_choose_llm_model_basic(self, mock_select):
        """Test choosing an LLM model."""
        models = AllModels(models=[
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
        ])
        
        # Mock returns: first for provider selection, second for model selection
        mock_select.return_value.ask.side_effect = [
            ModelProvider.ANTHROPIC,  # Provider selection
            models.models[0]  # Model selection
        ]
        
        result = choose_llm_model(models, agent="investment_agent")
        
        assert type(result).__name__ == 'LLMModel'
        assert result.provider == ModelProvider.ANTHROPIC

    @patch('src.utils.questionnaires.questionary.select')
    def test_choose_llm_model_different_agent(self, mock_select):
        """Test choosing model for different agent types."""
        models = AllModels(models=[
            LLMModel(
                provider=ModelProvider.ANTHROPIC,
                model_name="claude-3-5-sonnet-latest",
                display="Claude 3.5 Sonnet"
            )
        ])
        
        # Mock returns for each call (provider + model for each agent)
        mock_select.return_value.ask.side_effect = [
            ModelProvider.ANTHROPIC, models.models[0],  # investment_agent
            ModelProvider.ANTHROPIC, models.models[0],  # portfolio_agent
            ModelProvider.ANTHROPIC, models.models[0],  # analyst_agent
        ]
        
        # Should work for different agent names
        result1 = choose_llm_model(models, agent="investment_agent")
        result2 = choose_llm_model(models, agent="portfolio_agent")
        result3 = choose_llm_model(models, agent="analyst_agent")
        
        assert all(type(r).__name__ == 'LLMModel' for r in [result1, result2, result3])

    @patch('src.utils.questionnaires.questionary.select')
    def test_choose_llm_model_keyboard_interrupt_on_provider(self, mock_select):
        """Test handling of keyboard interrupt during provider selection."""
        models = AllModels(models=[
            LLMModel(
                provider=ModelProvider.ANTHROPIC,
                model_name="claude-3-5-sonnet-latest",
                display="Claude 3.5 Sonnet"
            )
        ])
        
        mock_select.return_value.ask.return_value = None  # Interrupt on provider
        
        with pytest.raises(SystemExit):
            choose_llm_model(models, agent="investment_agent")

    @patch('src.utils.questionnaires.questionary.select')
    def test_choose_llm_model_keyboard_interrupt_on_model(self, mock_select):
        """Test handling of keyboard interrupt during model selection."""
        models = AllModels(models=[
            LLMModel(
                provider=ModelProvider.ANTHROPIC,
                model_name="claude-3-5-sonnet-latest",
                display="Claude 3.5 Sonnet"
            )
        ])
        
        # Provider selected, then interrupt on model
        mock_select.return_value.ask.side_effect = [
            ModelProvider.ANTHROPIC,  # Provider selection succeeds
            None  # Interrupt on model selection
        ]
        
        with pytest.raises(SystemExit):
            choose_llm_model(models, agent="portfolio_agent")

    @patch('src.utils.questionnaires.questionary.select')
    def test_choose_llm_model_openai_provider(self, mock_select):
        """Test choosing OpenAI model."""
        models = AllModels(models=[
            LLMModel(
                provider=ModelProvider.OPENAI,
                model_name="gpt-4o",
                display="GPT-4o"
            )
        ])
        
        mock_select.return_value.ask.side_effect = [
            ModelProvider.OPENAI,
            models.models[0]
        ]
        
        result = choose_llm_model(models, agent="analyst_agent")
        
        assert result.provider == ModelProvider.OPENAI
        assert result.model_name == "gpt-4o"

    @patch('src.utils.questionnaires.questionary.select')
    def test_choose_llm_model_filters_by_provider(self, mock_select):
        """Test that model choices are filtered by selected provider."""
        models = AllModels(models=[
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
        ])
        
        # Select ANTHROPIC provider
        mock_select.return_value.ask.side_effect = [
            ModelProvider.ANTHROPIC,
            models.models[0]
        ]
        
        result = choose_llm_model(models, agent="investment_agent")
        
        # Should get the ANTHROPIC model, not OPENAI
        assert result.provider == ModelProvider.ANTHROPIC

    @patch('src.utils.questionnaires.questionary.select')
    def test_choose_llm_model_unknown_agent(self, mock_select):
        """Test choosing model with unknown agent type (no specific note)."""
        models = AllModels(models=[
            LLMModel(
                provider=ModelProvider.ANTHROPIC,
                model_name="claude-3-5-sonnet-latest",
                display="Claude 3.5 Sonnet"
            )
        ])
        
        mock_select.return_value.ask.side_effect = [
            ModelProvider.ANTHROPIC,
            models.models[0]
        ]
        
        # Use an agent name that's not one of the three special cases
        result = choose_llm_model(models, agent="unknown_agent")
        
        assert result.provider == ModelProvider.ANTHROPIC


# ============================================================================
# Choose Provider Tests
# ============================================================================

@pytest.mark.unit
class TestChooseProvider:
    """Tests for choose_provider function."""

    @patch('src.utils.questionnaires.questionary.select')
    def test_choose_provider_anthropic(self, mock_select):
        """Test selecting Anthropic provider."""
        from src.utils.questionnaires import choose_provider
        
        mock_select.return_value.ask.return_value = ModelProvider.ANTHROPIC
        
        result = choose_provider()
        
        assert result == ModelProvider.ANTHROPIC

    @patch('src.utils.questionnaires.questionary.select')
    def test_choose_provider_openai(self, mock_select):
        """Test selecting OpenAI provider."""
        from src.utils.questionnaires import choose_provider
        
        mock_select.return_value.ask.return_value = ModelProvider.OPENAI
        
        result = choose_provider()
        
        assert result == ModelProvider.OPENAI

    @patch('src.utils.questionnaires.questionary.select')
    def test_choose_provider_interrupt(self, mock_select):
        """Test handling interrupt during provider selection."""
        from src.utils.questionnaires import choose_provider
        
        mock_select.return_value.ask.return_value = None
        
        with pytest.raises(SystemExit):
            choose_provider()

    @patch('src.utils.questionnaires.questionary.select')
    def test_choose_provider_all_providers(self, mock_select):
        """Test that all providers can be selected."""
        from src.utils.questionnaires import choose_provider
        
        # Test each provider
        for provider in ModelProvider:
            mock_select.return_value.ask.return_value = provider
            result = choose_provider()
            assert result == provider


# ============================================================================
# Validation Tests
# ============================================================================

@pytest.mark.unit
class TestValidationFunctions:
    """Tests for input validation functions."""

    def test_validate_investment_amount_valid(self):
        """Test validation of valid investment amounts."""
        from src.utils.questionnaires import validate_investment_amount
        
        # Valid amounts
        assert validate_investment_amount("10000") is True
        assert validate_investment_amount("1000.50") is True
        assert validate_investment_amount("100") is True
        assert validate_investment_amount("100000") is True

    def test_validate_investment_amount_with_symbols(self):
        """Test validation with currency symbols and commas."""
        from src.utils.questionnaires import validate_investment_amount
        
        # Valid amounts with symbols
        assert validate_investment_amount("$10,000") is True
        assert validate_investment_amount("€5,000.50") is True
        assert validate_investment_amount("£25,000") is True
        assert validate_investment_amount("10,000.50") is True

    def test_validate_investment_amount_empty(self):
        """Test validation of empty input."""
        from src.utils.questionnaires import validate_investment_amount
        
        result = validate_investment_amount("")
        assert result == "Please enter an investment amount"
        
        result = validate_investment_amount("   ")
        assert result == "Please enter an investment amount"

    def test_validate_investment_amount_zero_or_negative(self):
        """Test validation of zero or negative amounts."""
        from src.utils.questionnaires import validate_investment_amount
        
        result = validate_investment_amount("0")
        assert result == "Investment amount must be greater than 0"
        
        result = validate_investment_amount("-1000")
        assert result == "Investment amount must be greater than 0"
        
        result = validate_investment_amount("-100")
        assert result == "Investment amount must be greater than 0"

    def test_validate_investment_amount_below_minimum(self):
        """Test validation of amounts below minimum."""
        from src.utils.questionnaires import validate_investment_amount
        
        result = validate_investment_amount("50")
        assert result == "Minimum investment amount is 100"
        
        result = validate_investment_amount("99")
        assert result == "Minimum investment amount is 100"
        
        result = validate_investment_amount("99.99")
        assert result == "Minimum investment amount is 100"

    def test_validate_investment_amount_invalid_format(self):
        """Test validation of invalid number formats."""
        from src.utils.questionnaires import validate_investment_amount
        
        result = validate_investment_amount("abc")
        assert result == "Please enter a valid number (e.g., 10000, $5,000, 1000.50)"
        
        result = validate_investment_amount("10k")
        assert result == "Please enter a valid number (e.g., 10000, $5,000, 1000.50)"
        
        result = validate_investment_amount("not a number")
        assert result == "Please enter a valid number (e.g., 10000, $5,000, 1000.50)"


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.integration
class TestQuestionnaireIntegration:
    """Integration tests for questionnaire flow."""

    @patch('src.utils.questionnaires.questionary.text')
    @patch('src.utils.questionnaires.questionary.select')
    @patch('src.utils.questionnaires.questionary.confirm')
    def test_complete_questionnaire_flow(self, mock_confirm, mock_select, mock_text):
        """Test complete questionnaire flow from start to finish."""
        # Setup mocks for all questions using our helper
        mock_setup = get_complete_mock_setup()
        
        mock_select.return_value.ask.side_effect = mock_setup['select_side_effect']
        mock_text.return_value.ask.side_effect = mock_setup['text_side_effect']
        mock_confirm.return_value.ask.return_value = mock_setup['confirm_return']
        
        preferences = get_user_preferences()
        
        # Verify the complete flow produced valid preferences
        assert type(preferences).__name__ == 'PortfolioPreference'
        assert preferences.goal is not None
        assert preferences.risk_profile is not None
        assert preferences.investment_horizon is not None
        assert preferences.currency is not None
        assert preferences.stock_exchange is not None
        assert preferences.initial_investment > 0
        assert preferences.age > 0
        assert preferences.investment_knowledge is not None
        assert preferences.income_level is not None
