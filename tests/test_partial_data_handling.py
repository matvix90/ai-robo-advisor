"""
Tests for enhanced error handling in analysis_data module.
"""
import pytest
from unittest.mock import patch

from src.utils.analysis_data import all_data, DataQualityWarning
from src.data.models import Portfolio, Holding


@pytest.mark.unit
class TestAllDataPartialResults:
    """Tests for partial data handling in all_data function."""

    @patch('src.utils.analysis_data.fetch_histories_concurrently')
    @patch('src.utils.analysis_data.get_two_year_ago_date')
    @patch('src.utils.analysis_data.get_today_date')
    def test_partial_portfolio_data_allowed(self, mock_today, mock_two_years_ago,
                                           mock_fetch, sample_portfolio):
        """Test that partial portfolio data is accepted when allow_partial=True."""
        mock_two_years_ago.return_value = '2023-01-01'
        mock_today.return_value = '2025-01-01'
        
        # Only 2 out of 3 portfolio tickers succeed
        mock_fetch.return_value = {
            'VTI': [{'date': '2023-01-01', 'close': 100}, {'date': '2023-01-02', 'close': 101}],
            'BND': [{'date': '2023-01-01', 'close': 80}, {'date': '2023-01-02', 'close': 81}],
            # VNQ missing
            'ACWI': [{'date': '2023-01-01', 'close': 95}, {'date': '2023-01-02', 'close': 96}]
        }
        
        portfolio_data, benchmark_data, weights, warning = all_data(
            sample_portfolio, 'ACWI', allow_partial=True
        )
        
        assert 'VTI' in portfolio_data
        assert 'BND' in portfolio_data
        assert 'VNQ' not in portfolio_data
        assert warning is not None
        assert isinstance(warning, DataQualityWarning)
        assert 'VNQ' in warning.missing_tickers
        assert len(weights) == 2  # Only 2 tickers

    @patch('src.utils.analysis_data.fetch_histories_concurrently')
    @patch('src.utils.analysis_data.get_two_year_ago_date')
    @patch('src.utils.analysis_data.get_today_date')
    def test_partial_portfolio_data_rejected(self, mock_today, mock_two_years_ago,
                                            mock_fetch, sample_portfolio):
        """Test that partial portfolio data raises error when allow_partial=False."""
        mock_two_years_ago.return_value = '2023-01-01'
        mock_today.return_value = '2025-01-01'
        
        mock_fetch.return_value = {
            'VTI': [{'date': '2023-01-01', 'close': 100}, {'date': '2023-01-02', 'close': 101}],
            'ACWI': [{'date': '2023-01-01', 'close': 95}, {'date': '2023-01-02', 'close': 96}]
        }
        
        with pytest.raises(ValueError, match="Failed to fetch data for portfolio tickers"):
            all_data(sample_portfolio, 'ACWI', allow_partial=False)

    @patch('src.utils.analysis_data.fetch_histories_concurrently')
    @patch('src.utils.analysis_data.get_two_year_ago_date')
    @patch('src.utils.analysis_data.get_today_date')
    def test_weights_renormalized_for_partial_data(self, mock_today, mock_two_years_ago,
                                                   mock_fetch, sample_portfolio):
        """Test that weights are properly renormalized when some tickers are missing."""
        mock_two_years_ago.return_value = '2023-01-01'
        mock_today.return_value = '2025-01-01'
        
        # VTI: 60%, BND: 30%, VNQ: 10% - but VNQ is missing
        mock_fetch.return_value = {
            'VTI': [{'date': '2023-01-01', 'close': 100}, {'date': '2023-01-02', 'close': 101}],
            'BND': [{'date': '2023-01-01', 'close': 80}, {'date': '2023-01-02', 'close': 81}],
            'ACWI': [{'date': '2023-01-01', 'close': 95}, {'date': '2023-01-02', 'close': 96}]
        }
        
        _, _, weights, _ = all_data(sample_portfolio, 'ACWI', allow_partial=True)
        
        # Original total: 100, VNQ missing: 10, remaining: 90
        # Scale factor: 100/90 = 1.111...
        # VTI: 60 * 1.111 = 66.67, BND: 30 * 1.111 = 33.33
        assert abs(weights['VTI'] - 66.67) < 0.1
        assert abs(weights['BND'] - 33.33) < 0.1
        assert abs(sum(weights.values()) - 100.0) < 0.1

    @patch('src.utils.analysis_data.fetch_histories_concurrently')
    @patch('src.utils.analysis_data.get_two_year_ago_date')
    @patch('src.utils.analysis_data.get_today_date')
    def test_benchmark_fallback_to_alternative(self, mock_today, mock_two_years_ago,
                                               mock_fetch, sample_portfolio):
        """Test fallback to alternative benchmark when primary fails."""
        mock_two_years_ago.return_value = '2023-01-01'
        mock_today.return_value = '2025-01-01'
        
        # ACWI missing but SPY available
        mock_fetch.return_value = {
            'VTI': [{'date': '2023-01-01', 'close': 100}, {'date': '2023-01-02', 'close': 101}],
            'BND': [{'date': '2023-01-01', 'close': 80}, {'date': '2023-01-02', 'close': 81}],
            'VNQ': [{'date': '2023-01-01', 'close': 90}, {'date': '2023-01-02', 'close': 91}],
            'SPY': [{'date': '2023-01-01', 'close': 400}, {'date': '2023-01-02', 'close': 401}]
        }
        
        portfolio_data, benchmark_data, weights, warning = all_data(
            sample_portfolio, 'ACWI', allow_partial=True
        )
        
        assert benchmark_data is not None
        assert len(benchmark_data) == 2
        assert warning is not None
        assert 'SPY' in warning.message or 'fallback' in warning.message.lower()

    @patch('src.utils.analysis_data.fetch_histories_concurrently')
    @patch('src.utils.analysis_data.get_two_year_ago_date')
    @patch('src.utils.analysis_data.get_today_date')
    def test_benchmark_no_fallback_available(self, mock_today, mock_two_years_ago,
                                             mock_fetch, sample_portfolio):
        """Test error when benchmark has no available fallback."""
        mock_two_years_ago.return_value = '2023-01-01'
        mock_today.return_value = '2025-01-01'
        
        # Only portfolio tickers, no benchmark or alternatives
        mock_fetch.return_value = {
            'VTI': [{'date': '2023-01-01', 'close': 100}, {'date': '2023-01-02', 'close': 101}],
            'BND': [{'date': '2023-01-01', 'close': 80}, {'date': '2023-01-02', 'close': 81}],
            'VNQ': [{'date': '2023-01-01', 'close': 90}, {'date': '2023-01-02', 'close': 91}]
        }
        
        with pytest.raises(ValueError, match="Failed to fetch data for benchmark ticker"):
            all_data(sample_portfolio, 'ACWI')

    @patch('src.utils.analysis_data.fetch_histories_concurrently')
    @patch('src.utils.analysis_data.get_two_year_ago_date')
    @patch('src.utils.analysis_data.get_today_date')
    def test_insufficient_data_points_removed(self, mock_today, mock_two_years_ago,
                                              mock_fetch, sample_portfolio):
        """Test that tickers with insufficient data points are removed."""
        mock_two_years_ago.return_value = '2023-01-01'
        mock_today.return_value = '2025-01-01'
        
        mock_fetch.return_value = {
            'VTI': [{'date': '2023-01-01', 'close': 100}],  # Only 1 point
            'BND': [{'date': '2023-01-01', 'close': 80}, {'date': '2023-01-02', 'close': 81}],
            'VNQ': [{'date': '2023-01-01', 'close': 90}, {'date': '2023-01-02', 'close': 91}],
            'ACWI': [{'date': '2023-01-01', 'close': 95}, {'date': '2023-01-02', 'close': 96}]
        }
        
        portfolio_data, benchmark_data, weights, warning = all_data(
            sample_portfolio, 'ACWI', allow_partial=True
        )
        
        assert 'VTI' not in portfolio_data  # Removed due to insufficient data
        assert 'BND' in portfolio_data
        assert 'VNQ' in portfolio_data
        assert warning is not None
        assert 'insufficient data' in warning.message.lower()

    @patch('src.utils.analysis_data.fetch_histories_concurrently')
    @patch('src.utils.analysis_data.get_two_year_ago_date')
    @patch('src.utils.analysis_data.get_today_date')
    def test_all_portfolio_tickers_fail(self, mock_today, mock_two_years_ago,
                                        mock_fetch, sample_portfolio):
        """Test error when all portfolio tickers fail to fetch."""
        mock_two_years_ago.return_value = '2023-01-01'
        mock_today.return_value = '2025-01-01'
        
        # Only benchmark data
        mock_fetch.return_value = {
            'ACWI': [{'date': '2023-01-01', 'close': 95}, {'date': '2023-01-02', 'close': 96}]
        }
        
        with pytest.raises(ValueError, match="Failed to fetch data for portfolio tickers"):
            all_data(sample_portfolio, 'ACWI', allow_partial=True)

    @patch('src.utils.analysis_data.fetch_histories_concurrently')
    @patch('src.utils.analysis_data.get_two_year_ago_date')
    @patch('src.utils.analysis_data.get_today_date')
    def test_no_data_retrieved_at_all(self, mock_today, mock_two_years_ago,
                                      mock_fetch, sample_portfolio):
        """Test error when absolutely no data is retrieved."""
        mock_two_years_ago.return_value = '2023-01-01'
        mock_today.return_value = '2025-01-01'
        mock_fetch.return_value = {}
        
        with pytest.raises(ValueError, match="No historical data was retrieved"):
            all_data(sample_portfolio, 'ACWI')

    @patch('src.utils.analysis_data.fetch_histories_concurrently')
    @patch('src.utils.analysis_data.get_two_year_ago_date')
    @patch('src.utils.analysis_data.get_today_date')
    def test_successful_fetch_no_warning(self, mock_today, mock_two_years_ago,
                                        mock_fetch, sample_portfolio):
        """Test that no warning is returned when all data fetches successfully."""
        mock_two_years_ago.return_value = '2023-01-01'
        mock_today.return_value = '2025-01-01'
        
        mock_fetch.return_value = {
            'VTI': [{'date': '2023-01-01', 'close': 100}, {'date': '2023-01-02', 'close': 101}],
            'BND': [{'date': '2023-01-01', 'close': 80}, {'date': '2023-01-02', 'close': 81}],
            'VNQ': [{'date': '2023-01-01', 'close': 90}, {'date': '2023-01-02', 'close': 91}],
            'ACWI': [{'date': '2023-01-01', 'close': 95}, {'date': '2023-01-02', 'close': 96}]
        }
        
        portfolio_data, benchmark_data, weights, warning = all_data(
            sample_portfolio, 'ACWI', allow_partial=True
        )
        
        assert warning is None
        assert len(portfolio_data) == 3
        assert benchmark_data is not None
