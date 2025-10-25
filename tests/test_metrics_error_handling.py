"""
Tests for enhanced error handling in metrics module.
"""
import pytest
from unittest.mock import patch
import pandas as pd
import numpy as np

from src.utils.metrics import analyze_portfolio, AnalysisWarning


def generate_sample_ohlcv(days=10, start_price=100):
    """Helper to generate sample OHLCV data."""
    dates = pd.date_range(start='2023-01-01', periods=days, freq='D')
    data = []
    price = start_price
    
    for date in dates:
        daily_return = np.random.normal(0.001, 0.01)
        close = price * (1 + daily_return)
        data.append({
            'date': date.strftime('%Y-%m-%d %H:%M:%S'),
            'open': round(close * 0.99, 2),
            'high': round(close * 1.01, 2),
            'low': round(close * 0.98, 2),
            'close': round(close, 2),
            'volume': 1000000
        })
        price = close
    
    return data


@pytest.mark.unit
class TestAnalyzePortfolioPartialData:
    """Tests for partial data handling in analyze_portfolio function."""

    def test_skip_ticker_with_no_data(self):
        """Test that tickers with no data are skipped when allow_partial=True."""
        tickers_data = {
            'AAPL': generate_sample_ohlcv(10, 150),
            'GOOGL': [],  # No data
            'MSFT': generate_sample_ohlcv(10, 250)
        }
        benchmark_data = generate_sample_ohlcv(10, 400)
        
        result, warning = analyze_portfolio(
            tickers_data, benchmark_data, allow_partial=True
        )
        
        assert 'AAPL' in result['tickers']
        assert 'MSFT' in result['tickers']
        assert 'GOOGL' not in result['tickers']
        assert warning is not None
        assert 'GOOGL' in warning.affected_tickers

    def test_skip_ticker_with_missing_close(self):
        """Test that tickers missing 'close' column are skipped."""
        tickers_data = {
            'AAPL': generate_sample_ohlcv(10, 150),
            'GOOGL': [{'date': '2023-01-01', 'open': 2800}, {'date': '2023-01-02', 'open': 2810}],  # No close
            'MSFT': generate_sample_ohlcv(10, 250)
        }
        benchmark_data = generate_sample_ohlcv(10, 400)
        
        result, warning = analyze_portfolio(
            tickers_data, benchmark_data, allow_partial=True
        )
        
        assert 'AAPL' in result['tickers']
        assert 'MSFT' in result['tickers']
        assert 'GOOGL' not in result['tickers']
        assert warning is not None

    def test_error_when_all_tickers_invalid_and_partial_not_allowed(self):
        """Test error when all tickers are invalid and allow_partial=False."""
        tickers_data = {
            'INVALID1': [],
            'INVALID2': []
        }
        benchmark_data = generate_sample_ohlcv(10, 400)
        
        with pytest.raises(ValueError):
            analyze_portfolio(tickers_data, benchmark_data, allow_partial=False)

    def test_error_when_all_tickers_invalid_even_with_partial(self):
        """Test error when all tickers are invalid even with allow_partial=True."""
        tickers_data = {
            'INVALID1': [],
            'INVALID2': []
        }
        benchmark_data = generate_sample_ohlcv(10, 400)
        
        with pytest.raises(ValueError, match="No valid ticker data could be processed"):
            analyze_portfolio(tickers_data, benchmark_data, allow_partial=True)

    def test_weights_adjusted_for_skipped_tickers(self):
        """Test that weights are properly adjusted when tickers are skipped."""
        tickers_data = {
            'AAPL': generate_sample_ohlcv(10, 150),
            'GOOGL': [],  # Will be skipped
            'MSFT': generate_sample_ohlcv(10, 250)
        }
        benchmark_data = generate_sample_ohlcv(10, 400)
        weights = {'AAPL': 40, 'GOOGL': 20, 'MSFT': 40}  # Total: 100
        
        result, warning = analyze_portfolio(
            tickers_data, benchmark_data, weights=weights, allow_partial=True
        )
        
        # Weights should be renormalized: AAPL: 40/(40+40)*100 = 50, MSFT: 40/(40+40)*100 = 50
        assert result['portfolio'] is not None
        assert warning is not None

    def test_failed_ticker_analysis_continues(self):
        """Test that analysis continues when individual ticker analysis fails."""
        tickers_data = {
            'AAPL': generate_sample_ohlcv(10, 150),
            'MSFT': generate_sample_ohlcv(10, 250)
        }
        benchmark_data = generate_sample_ohlcv(10, 400)
        
        result, warning = analyze_portfolio(
            tickers_data, benchmark_data, allow_partial=True
        )
        
        assert 'AAPL' in result['tickers']
        assert 'MSFT' in result['tickers']
        assert result['portfolio'] is not None

    def test_equal_weights_fallback_when_weights_invalid(self):
        """Test fallback to equal weights when provided weights are invalid."""
        tickers_data = {
            'AAPL': generate_sample_ohlcv(10, 150),
            'MSFT': generate_sample_ohlcv(10, 250)
        }
        benchmark_data = generate_sample_ohlcv(10, 400)
        weights = {'AAPL': 0, 'MSFT': 0}  # Invalid: sum to zero
        
        result, warning = analyze_portfolio(
            tickers_data, benchmark_data, weights=weights, allow_partial=True
        )
        
        assert result['portfolio'] is not None
        assert warning is not None
        assert 'equal weights' in warning.message.lower()

    def test_benchmark_error_stops_analysis(self):
        """Test that benchmark errors stop the entire analysis."""
        tickers_data = {
            'AAPL': generate_sample_ohlcv(10, 150)
        }
        benchmark_data = []  # Empty benchmark
        
        with pytest.raises(ValueError, match="benchmark_data cannot be empty"):
            analyze_portfolio(tickers_data, benchmark_data)

    def test_no_warning_when_all_successful(self):
        """Test that no warning is returned when all tickers succeed."""
        tickers_data = {
            'AAPL': generate_sample_ohlcv(10, 150),
            'MSFT': generate_sample_ohlcv(10, 250)
        }
        benchmark_data = generate_sample_ohlcv(10, 400)
        
        result, warning = analyze_portfolio(
            tickers_data, benchmark_data, allow_partial=True
        )
        
        assert result['portfolio'] is not None
        assert 'AAPL' in result['tickers']
        assert 'MSFT' in result['tickers']
        assert warning is None

    def test_empty_tickers_data_error(self):
        """Test error when tickers_data is empty."""
        benchmark_data = generate_sample_ohlcv(10, 400)
        
        with pytest.raises(ValueError, match="tickers_data cannot be empty"):
            analyze_portfolio({}, benchmark_data)

    def test_missing_benchmark_close_column(self):
        """Test error when benchmark data is missing close column."""
        tickers_data = {
            'AAPL': generate_sample_ohlcv(10, 150)
        }
        benchmark_data = [
            {'date': '2023-01-01', 'open': 400},  # No close
            {'date': '2023-01-02', 'open': 402}
        ]
        
        with pytest.raises(ValueError, match="Missing 'close' column in benchmark data"):
            analyze_portfolio(tickers_data, benchmark_data)

    def test_no_overlapping_data_error(self):
        """Test error when there's no overlapping data between assets and benchmark."""
        tickers_data = {
            'AAPL': [
                {'date': '2023-01-01 00:00:00', 'close': 150},
                {'date': '2023-01-02 00:00:00', 'close': 152}
            ]
        }
        benchmark_data = [
            {'date': '2024-01-01 00:00:00', 'close': 400},  # Different dates
            {'date': '2024-01-02 00:00:00', 'close': 402}
        ]
        
        with pytest.raises(ValueError):
            analyze_portfolio(tickers_data, benchmark_data)

    def test_partial_allowed_with_some_failures(self):
        """Test analysis continues with partial data when some tickers fail."""
        tickers_data = {
            'AAPL': generate_sample_ohlcv(10, 150),
            'INVALID': [],
            'MSFT': generate_sample_ohlcv(10, 250)
        }
        benchmark_data = generate_sample_ohlcv(10, 400)
        
        result, warning = analyze_portfolio(
            tickers_data, benchmark_data, allow_partial=True
        )
        
        assert len(result['tickers']) == 2
        assert result['portfolio'] is not None
        assert warning is not None
        assert len(warning.affected_tickers) == 1
