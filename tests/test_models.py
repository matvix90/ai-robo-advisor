import pytest
from src.data.models import (
    Portfolio, Holding, Strategy, AssetAllocation, GeographicalDiversification,
      SectorDiversification, StockExchange, Region, Sector
)

def test_create_valid_portfolio():
    # Create test data
    strategy = Strategy(
        name="Test Strategy",
        description="Test strategy description",
        asset_allocation=AssetAllocation(
            stocks_percentage=60.0,
            bonds_percentage=40.0
        ),
        geographical_diversification=GeographicalDiversification(
            regions=[Region(region="North America", weight=100.0)]
        ),
        sector_diversification=SectorDiversification(
            sectors=[Sector(sector="Technology", weight=100.0)]
        ),
        stock_exchange=StockExchange.NYSE,
        risk_tolerance="Moderate",
        time_horizon="Long Term",
        expected_returns="7-9%"
    )
    
    holdings = [
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
            weight=40.0
        )
    ]

    portfolio = Portfolio(
        name="Test Portfolio",
        holdings=holdings,
        strategy=strategy
    )

    # Assert basic properties
    assert portfolio.name == "Test Portfolio"
    assert len(portfolio.holdings) == 2
    assert portfolio.strategy.name == "Test Strategy"
    assert sum(holding.weight for holding in portfolio.holdings) == 100.0
