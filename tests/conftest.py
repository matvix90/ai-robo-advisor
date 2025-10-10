"""
Pytest configuration and shared fixtures for all tests.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock

from src.data.models import (
    Portfolio, Holding, Strategy, AssetAllocation, 
    GeographicalDiversification, SectorDiversification,
    StockExchange, Region, Sector, RiskProfile,
    InvestmentGoal, InvestmentHorizon, Currency,
    PortfolioPreference, InvestmentAgent, InvestmentKnowledge,
    IncomeLevel, InvestmentPurpose, LiquidityNeed,
    MarketDownturnReaction, InvestmentPriority
)


# ============================================================================
# Data Model Fixtures
# ============================================================================

@pytest.fixture
def sample_asset_allocation():
    """Sample asset allocation for testing."""
    return AssetAllocation(
        stocks_percentage=60.0,
        bonds_percentage=30.0,
        real_estate_percentage=5.0,
        commodities_percentage=3.0,
        cryptocurrency_percentage=0.0,
        cash_percentage=2.0
    )


@pytest.fixture
def sample_geographical_diversification():
    """Sample geographical diversification for testing."""
    return GeographicalDiversification(
        regions=[
            Region(region="North America", weight=50.0),
            Region(region="Europe", weight=30.0),
            Region(region="Asia", weight=20.0)
        ]
    )


@pytest.fixture
def sample_sector_diversification():
    """Sample sector diversification for testing."""
    return SectorDiversification(
        sectors=[
            Sector(sector="Technology", weight=30.0),
            Sector(sector="Healthcare", weight=20.0),
            Sector(sector="Financial", weight=25.0),
            Sector(sector="Consumer", weight=25.0)
        ]
    )


@pytest.fixture
def sample_strategy(sample_asset_allocation, sample_geographical_diversification, sample_sector_diversification):
    """Sample investment strategy for testing."""
    return Strategy(
        name="Balanced Growth Strategy",
        description="A balanced portfolio for long-term growth",
        asset_allocation=sample_asset_allocation,
        geographical_diversification=sample_geographical_diversification,
        sector_diversification=sample_sector_diversification,
        stock_exchange=StockExchange.NYSE,
        risk_tolerance="Moderate",
        time_horizon="Long Term (7-15 years)",
        expected_returns="7-9% annually"
    )


@pytest.fixture
def sample_holdings():
    """Sample portfolio holdings for testing."""
    return [
        Holding(
            symbol="VTI",
            name="Vanguard Total Stock Market ETF",
            isin="US9229087690",
            asset_class="Stocks",
            weight=60.0
        ),
        Holding(
            symbol="BND",
            name="Vanguard Total Bond Market ETF",
            isin="US9219378356",
            asset_class="Bonds",
            weight=30.0
        ),
        Holding(
            symbol="VNQ",
            name="Vanguard Real Estate ETF",
            isin="US9229085538",
            asset_class="Real Estate",
            weight=10.0
        )
    ]


@pytest.fixture
def sample_portfolio(sample_holdings, sample_strategy):
    """Sample portfolio for testing."""
    return Portfolio(
        name="Test Portfolio",
        holdings=sample_holdings,
        strategy=sample_strategy
    )


@pytest.fixture
def sample_portfolio_preference():
    """Sample portfolio preference for testing."""
    return PortfolioPreference(
        goal=InvestmentGoal.WEALTH_BUILDING,
        risk_profile=RiskProfile.MODERATE,
        investment_horizon=InvestmentHorizon.LONG_TERM,
        currency=Currency.USD,
        stock_exchange=StockExchange.NYSE,
        initial_investment=10000.0,
        # Enhanced fields - Personal Information
        age=35,
        investment_knowledge=InvestmentKnowledge.INTERMEDIATE,
        income_level=IncomeLevel.FROM_60K_TO_100K,
        # Enhanced fields - Investment Goals & Timeline
        investment_purpose=InvestmentPurpose.GROW_WEALTH,
        liquidity_need=LiquidityNeed.OVER_5_YEARS,
        # Enhanced fields - Financial Situation
        has_emergency_fund=True,
        other_investments=5000.0,
        monthly_contribution=500.0,
        # Enhanced fields - Risk Assessment
        max_acceptable_loss=20.0,
        market_downturn_reaction=MarketDownturnReaction.HOLD,
        investment_priority=InvestmentPriority.GROWTH
    )


@pytest.fixture
def sample_investment_agent(sample_strategy):
    """Sample investment agent for testing."""
    return InvestmentAgent(
        strategy=sample_strategy,
        reasoning="This is a test reasoning for the investment strategy."
    )


# ============================================================================
# State Fixtures
# ============================================================================

@pytest.fixture
def sample_state(sample_portfolio_preference):
    """Sample workflow state for testing."""
    return {
        'data': {
            'investment': {
                'analyst': None,
                'user_preferences': sample_portfolio_preference
            }
        },
        'metadata': {
            'show_reasoning': False,
            'investment_llm_agent': None,
            'portfolio_llm_agent': None,
            'analyst_llm_agent': None
        }
    }


@pytest.fixture
def sample_state_with_portfolio(sample_state, sample_portfolio):
    """Sample workflow state with portfolio for testing."""
    sample_state['data']['portfolio'] = sample_portfolio
    return sample_state


# ============================================================================
# Mock LLM Fixtures
# ============================================================================

@pytest.fixture
def mock_llm():
    """Mock LLM for testing."""
    mock = Mock()
    mock.with_structured_output = Mock(return_value=mock)
    mock.invoke = Mock()
    return mock


@pytest.fixture
def mock_llm_with_strategy_response(mock_llm, sample_investment_agent):
    """Mock LLM that returns investment agent response."""
    mock_llm.invoke.return_value = sample_investment_agent
    return mock_llm


# ============================================================================
# Data Generation Fixtures
# ============================================================================

@pytest.fixture
def sample_price_series():
    """Generate sample price series for testing metrics."""
    dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
    # Generate realistic price data with some volatility
    np.random.seed(42)
    returns = np.random.normal(0.0005, 0.01, len(dates))
    prices = 100 * (1 + returns).cumprod()
    return pd.Series(prices, index=dates)


@pytest.fixture
def sample_benchmark_series():
    """Generate sample benchmark price series for testing."""
    dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
    np.random.seed(24)
    returns = np.random.normal(0.0004, 0.008, len(dates))
    prices = 100 * (1 + returns).cumprod()
    return pd.Series(prices, index=dates)


@pytest.fixture
def sample_ohlcv_data():
    """Generate sample OHLCV data for polygon API testing."""
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    data = []
    price = 100.0
    
    for date in dates:
        daily_return = np.random.normal(0.0005, 0.01)
        close = price * (1 + daily_return)
        high = close * (1 + abs(np.random.normal(0, 0.005)))
        low = close * (1 - abs(np.random.normal(0, 0.005)))
        open_price = (high + low) / 2
        volume = np.random.randint(1000000, 10000000)
        
        data.append({
            'date': date.strftime('%Y-%m-%d %H:%M:%S'),
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close, 2),
            'volume': volume
        })
        
        price = close
    
    return data


@pytest.fixture
def sample_tickers_data(sample_ohlcv_data):
    """Generate sample tickers data dictionary."""
    return {
        'VTI': sample_ohlcv_data[:200],
        'BND': sample_ohlcv_data[:200],
        'VNQ': sample_ohlcv_data[:200]
    }


# ============================================================================
# Environment Fixtures
# ============================================================================

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-google-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("POLYGON_API_KEY", "test-polygon-key")


# ============================================================================
# Helper Functions
# ============================================================================

def create_mock_llm_response(model_class, **kwargs):
    """Helper to create mock LLM responses."""
    return model_class(**kwargs)
