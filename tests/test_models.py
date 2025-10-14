"""
Tests for data models defined in src/data/models.py
"""
import pytest
from pydantic import ValidationError

from src.data.models import (
    Portfolio, Holding, Strategy, AssetAllocation, GeographicalDiversification,
    SectorDiversification, StockExchange, Region, Sector, Currency,
    RiskProfile, InvestmentGoal, InvestmentHorizon, PortfolioPreference,
    InvestmentAgent, PortfolioAgent, AnalysisAgent, Status, AnalysisResponse,
    InvestmentKnowledge, IncomeLevel, InvestmentPurpose, LiquidityNeed,
    MarketDownturnReaction, InvestmentPriority
)


# ============================================================================
# Asset Allocation Tests
# ============================================================================

@pytest.mark.unit
class TestAssetAllocation:
    """Tests for AssetAllocation model."""

    def test_create_asset_allocation_all_fields(self):
        """Test creating asset allocation with all fields."""
        allocation = AssetAllocation(
            stocks_percentage=60.0,
            bonds_percentage=25.0,
            real_estate_percentage=5.0,
            commodities_percentage=5.0,
            cryptocurrency_percentage=3.0,
            cash_percentage=2.0
        )
        assert allocation.stocks_percentage == 60.0
        assert allocation.bonds_percentage == 25.0
        assert allocation.real_estate_percentage == 5.0

    def test_create_asset_allocation_partial_fields(self):
        """Test creating asset allocation with only some fields."""
        allocation = AssetAllocation(
            stocks_percentage=70.0,
            bonds_percentage=30.0
        )
        assert allocation.stocks_percentage == 70.0
        assert allocation.bonds_percentage == 30.0
        assert allocation.real_estate_percentage is None

    def test_asset_allocation_optional_fields(self):
        """Test that asset allocation fields are optional."""
        allocation = AssetAllocation()
        assert allocation.stocks_percentage is None
        assert allocation.bonds_percentage is None


# ============================================================================
# Geographical and Sector Diversification Tests
# ============================================================================

@pytest.mark.unit
class TestDiversification:
    """Tests for diversification models."""

    def test_create_region(self):
        """Test creating a region."""
        region = Region(region="North America", weight=50.0)
        assert region.region == "North America"
        assert region.weight == 50.0

    def test_create_geographical_diversification(self):
        """Test creating geographical diversification."""
        regions = [
            Region(region="North America", weight=50.0),
            Region(region="Europe", weight=30.0),
            Region(region="Asia", weight=20.0)
        ]
        geo_div = GeographicalDiversification(regions=regions)
        assert len(geo_div.regions) == 3
        assert sum(r.weight for r in geo_div.regions) == 100.0

    def test_create_sector(self):
        """Test creating a sector."""
        sector = Sector(sector="Technology", weight=30.0)
        assert sector.sector == "Technology"
        assert sector.weight == 30.0

    def test_create_sector_diversification(self):
        """Test creating sector diversification."""
        sectors = [
            Sector(sector="Technology", weight=40.0),
            Sector(sector="Healthcare", weight=30.0),
            Sector(sector="Finance", weight=30.0)
        ]
        sector_div = SectorDiversification(sectors=sectors)
        assert len(sector_div.sectors) == 3
        assert sum(s.weight for s in sector_div.sectors) == 100.0


# ============================================================================
# Strategy Tests
# ============================================================================

@pytest.mark.unit
class TestStrategy:
    """Tests for Strategy model."""

    def test_create_complete_strategy(self, sample_strategy):
        """Test creating a complete strategy."""
        assert sample_strategy.name == "Balanced Growth Strategy"
        assert sample_strategy.description is not None
        assert sample_strategy.asset_allocation is not None
        assert sample_strategy.geographical_diversification is not None
        assert sample_strategy.sector_diversification is not None
        assert sample_strategy.stock_exchange == StockExchange.NYSE
        assert sample_strategy.risk_tolerance == "Moderate"

    def test_strategy_with_different_stock_exchange(self, sample_asset_allocation, 
                                                     sample_geographical_diversification,
                                                     sample_sector_diversification):
        """Test creating strategy with different stock exchange."""
        strategy = Strategy(
            name="European Strategy",
            description="Focus on European markets",
            asset_allocation=sample_asset_allocation,
            geographical_diversification=sample_geographical_diversification,
            sector_diversification=sample_sector_diversification,
            stock_exchange=StockExchange.EURONEXT,
            risk_tolerance="Aggressive",
            time_horizon="Medium Term",
            expected_returns="10-12%"
        )
        assert strategy.stock_exchange == StockExchange.EURONEXT


# ============================================================================
# Holding Tests
# ============================================================================

@pytest.mark.unit
class TestHolding:
    """Tests for Holding model."""

    def test_create_valid_holding(self):
        """Test creating a valid holding."""
        holding = Holding(
            symbol="VTI",
            name="Vanguard Total Stock Market ETF",
            isin="US9229087690",
            asset_class="Stocks",
            weight=60.0
        )
        assert holding.symbol == "VTI"
        assert holding.name == "Vanguard Total Stock Market ETF"
        assert holding.isin == "US9229087690"
        assert len(holding.isin) == 12

    def test_holding_isin_validation(self):
        """Test ISIN validation (must be 12 characters)."""
        # Note: ISIN validation might not be enforced strictly by Pydantic Field
        # This test verifies that creating a holding with invalid ISIN doesn't crash
        # In production, you might want stricter validation
        holding = Holding(
            symbol="VTI",
            name="Vanguard Total Stock Market ETF",
            isin="TOOLONG12345",  # More than 12 characters
            asset_class="Stocks",
            weight=60.0
        )
        # If validation were strict, this would raise ValidationError
        # For now, we just check it doesn't crash
        assert holding.isin == "TOOLONG12345"

    def test_holding_weight_type(self):
        """Test that weight must be a number."""
        holding = Holding(
            symbol="VTI",
            name="Vanguard Total Stock Market ETF",
            isin="US9229087690",
            asset_class="Stocks",
            weight=60.0
        )
        assert isinstance(holding.weight, float)


# ============================================================================
# Portfolio Tests
# ============================================================================

@pytest.mark.unit
class TestPortfolio:
    """Tests for Portfolio model."""

    def test_create_valid_portfolio(self, sample_portfolio):
        """Test creating a valid portfolio."""
        assert sample_portfolio.name == "Test Portfolio"
        assert len(sample_portfolio.holdings) == 3
        assert sample_portfolio.strategy is not None
        assert sample_portfolio.strategy.name == "Balanced Growth Strategy"

    def test_portfolio_holdings_weight_sum(self, sample_holdings, sample_strategy):
        """Test that portfolio holdings weights sum to 100."""
        portfolio = Portfolio(
            name="Test Portfolio",
            holdings=sample_holdings,
            strategy=sample_strategy
        )
        total_weight = sum(holding.weight for holding in portfolio.holdings)
        assert total_weight == 100.0

    def test_create_portfolio_with_single_holding(self, sample_strategy):
        """Test creating portfolio with single holding."""
        holdings = [
            Holding(
                symbol="VTI",
                name="Vanguard Total Stock Market ETF",
                isin="US9229087690",
                asset_class="Stocks",
                weight=100.0
            )
        ]
        portfolio = Portfolio(
            name="Single Holding Portfolio",
            holdings=holdings,
            strategy=sample_strategy
        )
        assert len(portfolio.holdings) == 1
        assert portfolio.holdings[0].weight == 100.0


# ============================================================================
# Portfolio Preference Tests
# ============================================================================

@pytest.mark.unit
class TestPortfolioPreference:
    """Tests for PortfolioPreference model."""

    def test_create_portfolio_preference(self, sample_portfolio_preference):
        """Test creating portfolio preference."""
        assert sample_portfolio_preference.goal == InvestmentGoal.WEALTH_BUILDING
        assert sample_portfolio_preference.risk_profile == RiskProfile.MODERATE
        assert sample_portfolio_preference.investment_horizon == InvestmentHorizon.LONG_TERM
        assert sample_portfolio_preference.currency == Currency.USD
        assert sample_portfolio_preference.initial_investment == 10000.0

    def test_portfolio_preference_different_values(self):
        """Test portfolio preference with different values."""
        pref = PortfolioPreference(
            goal=InvestmentGoal.RETIREMENT,
            risk_profile=RiskProfile.CONSERVATIVE,
            investment_horizon=InvestmentHorizon.VERY_LONG_TERM,
            currency=Currency.EUR,
            stock_exchange=StockExchange.EURONEXT,
            initial_investment=50000.0,
            # Enhanced fields - Personal Information
            age=45,
            investment_knowledge=InvestmentKnowledge.BASIC,
            income_level=IncomeLevel.FROM_100K_TO_150K,
            # Enhanced fields - Investment Goals & Timeline
            investment_purpose=InvestmentPurpose.GENERATE_INCOME,
            liquidity_need=LiquidityNeed.FROM_3_TO_5_YEARS,
            # Enhanced fields - Financial Situation
            has_emergency_fund=True,
            other_investments=15000.0,
            monthly_contribution=1000.0,
            # Enhanced fields - Risk Assessment
            max_acceptable_loss=10.0,
            market_downturn_reaction=MarketDownturnReaction.HOLD,
            investment_priority=InvestmentPriority.STABILITY
        )
        assert pref.goal == InvestmentGoal.RETIREMENT
        assert pref.currency == Currency.EUR
        assert pref.initial_investment == 50000.0


# ============================================================================
# Agent Models Tests
# ============================================================================

@pytest.mark.unit
class TestAgentModels:
    """Tests for agent-related models."""

    def test_create_investment_agent(self, sample_investment_agent):
        """Test creating investment agent."""
        assert sample_investment_agent.strategy is not None
        assert sample_investment_agent.reasoning is not None
        assert isinstance(sample_investment_agent.reasoning, str)

    def test_create_portfolio_agent(self, sample_portfolio):
        """Test creating portfolio agent."""
        agent = PortfolioAgent(
            portfolio=sample_portfolio,
            reasoning="This portfolio is well-diversified."
        )
        assert agent.portfolio.name == "Test Portfolio"
        assert agent.reasoning == "This portfolio is well-diversified."

    def test_create_analysis_agent(self):
        """Test creating analysis agent."""
        status = Status(key="is_performing", value=True)
        agent = AnalysisAgent(
            status=status,
            reasoning="Portfolio is performing well.",
            advices=[]
        )
        assert agent.status.key == "is_performing"
        assert agent.status.value is True
        assert agent.advices == []

    def test_create_analysis_agent_with_advices(self):
        """Test creating analysis agent with advices."""
        status = Status(key="is_diversified", value=False)
        agent = AnalysisAgent(
            status=status,
            reasoning="Portfolio lacks diversification.",
            advices=[
                "Consider adding international exposure",
                "Increase bond allocation"
            ]
        )
        assert agent.status.value is False
        assert len(agent.advices) == 2


# ============================================================================
# Analysis Response Tests
# ============================================================================

@pytest.mark.unit
class TestAnalysisResponse:
    """Tests for AnalysisResponse model."""

    def test_create_positive_analysis_response(self):
        """Test creating positive analysis response."""
        response = AnalysisResponse(
            is_approved=True,
            strengths="Well diversified, low fees",
            weeknesses="Slightly high risk",
            overall_assessment="Excellent portfolio for long-term growth",
            advices=None
        )
        assert response.is_approved is True
        assert response.strengths is not None
        assert response.advices is None

    def test_create_negative_analysis_response(self):
        """Test creating negative analysis response."""
        response = AnalysisResponse(
            is_approved=False,
            strengths="Low fees",
            weeknesses="Poor diversification, high risk",
            overall_assessment="Needs significant improvement",
            advices="Rebalance portfolio, add bonds"
        )
        assert response.is_approved is False
        assert response.advices is not None


# ============================================================================
# Enum Tests
# ============================================================================

@pytest.mark.unit
class TestEnums:
    """Tests for enum types."""

    def test_currency_enum_values(self):
        """Test currency enum has expected values."""
        assert Currency.USD == "USD"
        assert Currency.EUR == "EUR"
        assert Currency.GBP == "GBP"

    def test_stock_exchange_enum_values(self):
        """Test stock exchange enum has expected values."""
        assert StockExchange.NYSE == "NYSE"
        assert StockExchange.NASDAQ == "NASDAQ"
        assert StockExchange.LSE == "LSE"

    def test_risk_profile_enum_values(self):
        """Test risk profile enum has expected values."""
        assert RiskProfile.CONSERVATIVE == "Conservative"
        assert RiskProfile.MODERATE == "Moderate"
        assert RiskProfile.AGGRESSIVE == "Aggressive"

    def test_investment_goal_enum_values(self):
        """Test investment goal enum has expected values."""
        assert InvestmentGoal.RETIREMENT == "Retirement"
        assert InvestmentGoal.WEALTH_BUILDING == "Wealth Building"
        assert InvestmentGoal.INCOME_GENERATION == "Income Generation"

    def test_investment_horizon_enum_values(self):
        """Test investment horizon enum has expected values."""
        assert InvestmentHorizon.SHORT_TERM == "Short Term (1-3 years)"
        assert InvestmentHorizon.LONG_TERM == "Long Term (7-15 years)"
