"""
Simplified tests for analysis_data utility functions focusing on coverage.
"""
import pytest
from unittest.mock import patch

from src.utils.analysis_data import all_data
from src.data.models import Portfolio, Holding


# ============================================================================
# All Data Function Tests
# ============================================================================

@pytest.mark.unit
class TestAllDataValidation:
    """Tests for input validation in all_data function."""

    def test_all_data_invalid_portfolio_type(self):
        """Test error when portfolio is not Portfolio instance."""
        with pytest.raises(TypeError, match="portfolio must be a Portfolio instance"):
            all_data("not a portfolio", "ACWI")

    def test_all_data_empty_benchmark_ticker(self, sample_portfolio):
        """Test error when benchmark ticker is empty."""
        with pytest.raises(ValueError, match="benchmark_ticker must be a non-empty string"):
            all_data(sample_portfolio, "")

    def test_all_data_none_benchmark_ticker(self, sample_portfolio):
        """Test error when benchmark ticker is None."""
        with pytest.raises(ValueError, match="benchmark_ticker must be a non-empty string"):
            all_data(sample_portfolio, None)

    def test_all_data_portfolio_no_holdings(self, sample_strategy):
        """Test error when portfolio has no holdings."""
        empty_portfolio = Portfolio(
            name="Empty Portfolio",
            holdings=[],
            strategy=sample_strategy
        )
        
        with pytest.raises(ValueError, match="Portfolio must have holdings"):
            all_data(empty_portfolio, "ACWI")

    def test_all_data_holding_missing_symbol(self, sample_strategy):
        """Test error when holding has empty symbol."""
        holding = Holding(
            symbol="",  # Empty symbol
            name="Test ETF",
            isin="US1234567890",
            asset_class="Stocks",
            weight=100.0
        )
        
        portfolio = Portfolio(
            name="Bad Portfolio",
            holdings=[holding],
            strategy=sample_strategy
        )
        
        with pytest.raises(ValueError, match="Holding symbol cannot be empty"):
            all_data(portfolio, "ACWI")

    def test_all_data_zero_total_weight(self, sample_strategy):
        """Test error when portfolio weights sum to zero."""
        holding = Holding(
            symbol="VTI",
            name="Test ETF",
            isin="US1234567890",
            asset_class="Stocks",
            weight=0.0
        )
        
        portfolio = Portfolio(
            name="Zero Weight Portfolio",
            holdings=[holding],
            strategy=sample_strategy
        )
        
        with pytest.raises(ValueError, match="Portfolio weights must sum to a positive value"):
            all_data(portfolio, "ACWI")


@pytest.mark.unit
class TestAllDataFetching:
    """Tests for data fetching in all_data function."""

    @patch('src.utils.analysis_data.get_two_year_ago_date')
    def test_all_data_date_range_error(self, mock_date, sample_portfolio):
        """Test error when date range retrieval fails."""
        mock_date.side_effect = Exception("Date error")
        
        with pytest.raises(ValueError, match="Failed to get date range"):
            all_data(sample_portfolio, "ACWI")

    @patch('src.utils.analysis_data.fetch_histories_concurrently')
    @patch('src.utils.analysis_data.get_two_year_ago_date')
    @patch('src.utils.analysis_data.get_today_date')
    def test_all_data_fetch_error(self, mock_today, mock_two_years_ago,
                                  mock_fetch, sample_portfolio):
        """Test error when data fetching fails."""
        mock_two_years_ago.return_value = '2023-01-01'
        mock_today.return_value = '2025-01-01'
        mock_fetch.side_effect = Exception("API error")
        
        with pytest.raises(ValueError, match="Failed to fetch historical data"):
            all_data(sample_portfolio, "ACWI")

    @patch('src.utils.analysis_data.fetch_histories_concurrently')
    @patch('src.utils.analysis_data.get_two_year_ago_date')
    @patch('src.utils.analysis_data.get_today_date')
    def test_all_data_no_data_retrieved(self, mock_today, mock_two_years_ago,
                                        mock_fetch, sample_portfolio):
        """Test error when no data is retrieved."""
        mock_two_years_ago.return_value = '2023-01-01'
        mock_today.return_value = '2025-01-01'
        mock_fetch.return_value = {}
        
        with pytest.raises(ValueError, match="No historical data was retrieved"):
            all_data(sample_portfolio, "ACWI")

    @patch('src.utils.analysis_data.fetch_histories_concurrently')
    @patch('src.utils.analysis_data.get_two_year_ago_date')
    @patch('src.utils.analysis_data.get_today_date')
    def test_all_data_missing_benchmark(self, mock_today, mock_two_years_ago,
                                       mock_fetch, sample_portfolio):
        """Test error when benchmark data is missing."""
        mock_two_years_ago.return_value = '2023-01-01'
        mock_today.return_value = '2025-01-01'
        mock_fetch.return_value = {
            'VTI': [{'date': '2023-01-01', 'close': 100}, {'date': '2023-01-02', 'close': 101}],
            'BND': [{'date': '2023-01-01', 'close': 80}, {'date': '2023-01-02', 'close': 81}],
        }
        
        with pytest.raises(ValueError, match="Failed to fetch data for benchmark ticker"):
            all_data(sample_portfolio, "ACWI")

    @patch('src.utils.analysis_data.fetch_histories_concurrently')
    @patch('src.utils.analysis_data.get_two_year_ago_date')
    @patch('src.utils.analysis_data.get_today_date')
    def test_all_data_missing_portfolio_tickers(self, mock_today, mock_two_years_ago,
                                                mock_fetch, sample_portfolio):
        """Test error when some portfolio ticker data is missing."""
        mock_two_years_ago.return_value = '2023-01-01'
        mock_today.return_value = '2025-01-01'
        mock_fetch.return_value = {
            'VTI': [{'date': '2023-01-01', 'close': 100}, {'date': '2023-01-02', 'close': 101}],
            'ACWI': [{'date': '2023-01-01', 'close': 95}, {'date': '2023-01-02', 'close': 96}]
            # Missing BND and VNQ
        }
        
        with pytest.raises(ValueError, match="Failed to fetch data for portfolio tickers"):
            all_data(sample_portfolio, "ACWI")

    @patch('src.utils.analysis_data.fetch_histories_concurrently')
    @patch('src.utils.analysis_data.get_two_year_ago_date')
    @patch('src.utils.analysis_data.get_today_date')
    def test_all_data_insufficient_data_points(self, mock_today, mock_two_years_ago,
                                               mock_fetch, sample_portfolio):
        """Test error when ticker has insufficient data points."""
        mock_two_years_ago.return_value = '2023-01-01'
        mock_today.return_value = '2025-01-01'
        mock_fetch.return_value = {
            'VTI': [{'date': '2023-01-01', 'close': 100}],  # Only 1 point
            'BND': [{'date': '2023-01-01', 'close': 80}, {'date': '2023-01-02', 'close': 81}],
            'VNQ': [{'date': '2023-01-01', 'close': 90}, {'date': '2023-01-02', 'close': 91}],
            'ACWI': [{'date': '2023-01-01', 'close': 95}, {'date': '2023-01-02', 'close': 96}]
        }
        
        with pytest.raises(ValueError, match="Insufficient data for ticker"):
            all_data(sample_portfolio, "ACWI")

    @patch('src.utils.analysis_data.fetch_histories_concurrently')
    @patch('src.utils.analysis_data.get_two_year_ago_date')
    @patch('src.utils.analysis_data.get_today_date')
    def test_all_data_success(self, mock_today, mock_two_years_ago, 
                              mock_fetch, sample_portfolio):
        """Test successful data fetching."""
        # Setup mocks
        mock_two_years_ago.return_value = '2023-01-01'
        mock_today.return_value = '2025-01-01'
        
        mock_data = {
            'VTI': [{'date': '2023-01-01', 'close': 100}, {'date': '2023-01-02', 'close': 101}],
            'BND': [{'date': '2023-01-01', 'close': 80}, {'date': '2023-01-02', 'close': 81}],
            'VNQ': [{'date': '2023-01-01', 'close': 90}, {'date': '2023-01-02', 'close': 91}],
            'ACWI': [{'date': '2023-01-01', 'close': 95}, {'date': '2023-01-02', 'close': 96}]
        }
        mock_fetch.return_value = mock_data
        
        # Execute
        portfolio_data, benchmark_data, weights = all_data(sample_portfolio, 'ACWI')
        
        # Verify
        assert 'VTI' in portfolio_data
        assert 'BND' in portfolio_data
        assert 'VNQ' in portfolio_data
        assert 'ACWI' not in portfolio_data  # Should be separated
        assert benchmark_data is not None
        assert len(benchmark_data) == 2
        assert weights['VTI'] == 60.0
        assert weights['BND'] == 30.0
        assert weights['VNQ'] == 10.0
