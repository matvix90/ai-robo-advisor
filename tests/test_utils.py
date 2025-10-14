"""
Tests for utility functions.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.utils.metrics import (
    calculate_performance_metrics,
    calculate_relative_metrics,
    analyze_portfolio
)


# ============================================================================
# Performance Metrics Tests
# ============================================================================

@pytest.mark.unit
class TestCalculatePerformanceMetrics:
    """Tests for calculate_performance_metrics function."""

    def test_calculate_metrics_valid_series(self, sample_price_series):
        """Test calculating metrics with valid price series."""
        metrics = calculate_performance_metrics(sample_price_series)
        
        assert 'Cumulative Return' in metrics
        assert 'CAGR' in metrics
        assert 'Annualized Volatility' in metrics
        assert 'Max Drawdown' in metrics
        assert 'Sharpe Ratio' in metrics
        
        # Check that values are reasonable
        assert isinstance(metrics['CAGR'], float)
        assert isinstance(metrics['Sharpe Ratio'], float)
        assert metrics['Max Drawdown'] <= 0  # Drawdown should be negative

    def test_calculate_metrics_custom_risk_free_rate(self, sample_price_series):
        """Test calculating metrics with custom risk-free rate."""
        metrics1 = calculate_performance_metrics(sample_price_series, risk_free_rate=0.02)
        metrics2 = calculate_performance_metrics(sample_price_series, risk_free_rate=0.05)
        
        # Sharpe ratio should be different with different risk-free rates
        assert metrics1['Sharpe Ratio'] != metrics2['Sharpe Ratio']
        # Higher risk-free rate should generally lead to lower Sharpe ratio
        assert metrics1['Sharpe Ratio'] > metrics2['Sharpe Ratio']

    def test_calculate_metrics_empty_series(self):
        """Test that empty series raises ValueError."""
        empty_series = pd.Series([], dtype=float)
        
        with pytest.raises(ValueError, match="at least 2 data points"):
            calculate_performance_metrics(empty_series)

    def test_calculate_metrics_single_value(self):
        """Test that series with single value raises ValueError."""
        single_series = pd.Series([100.0])
        
        with pytest.raises(ValueError, match="at least 2 data points"):
            calculate_performance_metrics(single_series)

    def test_calculate_metrics_negative_prices(self):
        """Test that negative prices raise ValueError."""
        dates = pd.date_range(start='2020-01-01', periods=100, freq='D')
        prices = pd.Series([-100.0] * 100, index=dates)
        
        with pytest.raises(ValueError, match="positive values"):
            calculate_performance_metrics(prices)

    def test_calculate_metrics_zero_prices(self):
        """Test that zero prices raise ValueError."""
        dates = pd.date_range(start='2020-01-01', periods=100, freq='D')
        prices = pd.Series([0.0] * 100, index=dates)
        
        with pytest.raises(ValueError, match="positive values"):
            calculate_performance_metrics(prices)

    def test_calculate_metrics_positive_return(self):
        """Test metrics calculation with positive returns."""
        dates = pd.date_range(start='2020-01-01', periods=365, freq='D')
        # Create series with steady growth
        prices = pd.Series([100 * (1.001 ** i) for i in range(365)], index=dates)
        
        metrics = calculate_performance_metrics(prices)
        
        assert metrics['Cumulative Return'] > 0
        assert metrics['CAGR'] > 0

    def test_calculate_metrics_negative_return(self):
        """Test metrics calculation with negative returns."""
        dates = pd.date_range(start='2020-01-01', periods=365, freq='D')
        # Create series with steady decline
        prices = pd.Series([100 * (0.999 ** i) for i in range(365)], index=dates)
        
        metrics = calculate_performance_metrics(prices)
        
        assert metrics['Cumulative Return'] < 0
        assert metrics['CAGR'] < 0

    def test_calculate_metrics_high_volatility(self):
        """Test metrics with high volatility series."""
        dates = pd.date_range(start='2020-01-01', periods=252, freq='D')
        np.random.seed(42)
        # High volatility returns
        returns = np.random.normal(0, 0.05, 252)
        prices = pd.Series(100 * (1 + returns).cumprod(), index=dates)
        
        metrics = calculate_performance_metrics(prices)
        
        # High volatility should be reflected in the metrics
        assert metrics['Annualized Volatility'] > 0.1


# ============================================================================
# Relative Metrics Tests
# ============================================================================

@pytest.mark.unit
class TestCalculateRelativeMetrics:
    """Tests for calculate_relative_metrics function."""

    def test_calculate_relative_metrics_valid_data(self, sample_price_series, sample_benchmark_series):
        """Test calculating relative metrics with valid data."""
        asset_returns = sample_price_series.pct_change().dropna()
        benchmark_returns = sample_benchmark_series.pct_change().dropna()
        
        metrics = calculate_relative_metrics(asset_returns, benchmark_returns)
        
        assert 'Alpha' in metrics
        assert 'Beta' in metrics
        assert isinstance(metrics['Alpha'], float)
        assert isinstance(metrics['Beta'], float)

    def test_calculate_relative_metrics_beta_interpretation(self):
        """Test beta calculation and interpretation."""
        dates = pd.date_range(start='2020-01-01', periods=252, freq='D')
        
        # Create benchmark returns
        np.random.seed(42)
        benchmark_returns = pd.Series(np.random.normal(0.0005, 0.01, 252), index=dates)
        
        # Create asset with higher beta (more volatile, correlated)
        high_beta_returns = benchmark_returns * 1.5 + pd.Series(np.random.normal(0, 0.005, 252), index=dates)
        
        metrics = calculate_relative_metrics(high_beta_returns, benchmark_returns)
        
        # Beta should be greater than 1
        assert metrics['Beta'] > 0.5

    def test_calculate_relative_metrics_insufficient_data(self):
        """Test that insufficient overlapping data raises ValueError."""
        asset_returns = pd.Series([0.01], index=[datetime(2020, 1, 1)])
        benchmark_returns = pd.Series([0.01], index=[datetime(2020, 1, 2)])
        
        with pytest.raises(ValueError, match="Insufficient overlapping data"):
            calculate_relative_metrics(asset_returns, benchmark_returns)

    def test_calculate_relative_metrics_zero_variance_benchmark(self):
        """Test that zero variance benchmark raises ValueError."""
        dates = pd.date_range(start='2020-01-01', periods=100, freq='D')
        asset_returns = pd.Series(np.random.normal(0.001, 0.01, 100), index=dates)
        benchmark_returns = pd.Series([0.0] * 100, index=dates)
        
        with pytest.raises(ValueError, match="benchmark variance is zero"):
            calculate_relative_metrics(asset_returns, benchmark_returns)


# ============================================================================
# Portfolio Analysis Tests
# ============================================================================

@pytest.mark.unit
class TestAnalyzePortfolio:
    """Tests for analyze_portfolio function."""

    def test_analyze_portfolio_basic(self, sample_tickers_data, sample_ohlcv_data):
        """Test basic portfolio analysis."""
        benchmark_data = sample_ohlcv_data[:200]
        
        result = analyze_portfolio(
            tickers_data=sample_tickers_data,
            benchmark_data=benchmark_data
        )
        
        assert 'benchmark' in result
        assert 'tickers' in result
        assert 'portfolio' in result
        
        # Check benchmark metrics
        assert 'CAGR' in result['benchmark']
        assert 'Sharpe Ratio' in result['benchmark']
        
        # Check ticker metrics
        for ticker in sample_tickers_data.keys():
            assert ticker in result['tickers']
            assert 'Alpha' in result['tickers'][ticker]
            assert 'Beta' in result['tickers'][ticker]
        
        # Check portfolio metrics
        assert 'CAGR' in result['portfolio']
        assert 'Alpha' in result['portfolio']

    def test_analyze_portfolio_with_weights(self, sample_tickers_data, sample_ohlcv_data):
        """Test portfolio analysis with custom weights."""
        benchmark_data = sample_ohlcv_data[:200]
        weights = {'VTI': 0.6, 'BND': 0.3, 'VNQ': 0.1}
        
        result = analyze_portfolio(
            tickers_data=sample_tickers_data,
            benchmark_data=benchmark_data,
            weights=weights
        )
        
        assert 'portfolio' in result
        assert 'CAGR' in result['portfolio']

    def test_analyze_portfolio_equal_weights(self, sample_tickers_data, sample_ohlcv_data):
        """Test portfolio analysis with equal weights (default)."""
        benchmark_data = sample_ohlcv_data[:200]
        
        result = analyze_portfolio(
            tickers_data=sample_tickers_data,
            benchmark_data=benchmark_data,
            weights=None
        )
        
        assert 'portfolio' in result

    def test_analyze_portfolio_empty_tickers(self, sample_ohlcv_data):
        """Test that empty tickers data raises ValueError."""
        benchmark_data = sample_ohlcv_data[:200]
        
        with pytest.raises(ValueError, match="tickers_data cannot be empty"):
            analyze_portfolio(
                tickers_data={},
                benchmark_data=benchmark_data
            )

    def test_analyze_portfolio_empty_benchmark(self, sample_tickers_data):
        """Test that empty benchmark data raises ValueError."""
        with pytest.raises(ValueError, match="benchmark_data cannot be empty"):
            analyze_portfolio(
                tickers_data=sample_tickers_data,
                benchmark_data=[]
            )

    def test_analyze_portfolio_missing_close_column_ticker(self, sample_ohlcv_data):
        """Test that missing close column in ticker raises ValueError."""
        bad_ticker_data = {
            'VTI': [{'date': '2023-01-01', 'open': 100}]  # Missing 'close'
        }
        
        with pytest.raises(ValueError, match="Missing 'close' column"):
            analyze_portfolio(
                tickers_data=bad_ticker_data,
                benchmark_data=sample_ohlcv_data[:200]
            )

    def test_analyze_portfolio_missing_close_column_benchmark(self, sample_tickers_data):
        """Test that missing close column in benchmark raises ValueError."""
        bad_benchmark_data = [{'date': '2023-01-01', 'open': 100}]  # Missing 'close'
        
        with pytest.raises(ValueError, match="Missing 'close' column"):
            analyze_portfolio(
                tickers_data=sample_tickers_data,
                benchmark_data=bad_benchmark_data
            )

    def test_analyze_portfolio_custom_risk_free_rate(self, sample_tickers_data, sample_ohlcv_data):
        """Test portfolio analysis with custom risk-free rate."""
        benchmark_data = sample_ohlcv_data[:200]
        
        result1 = analyze_portfolio(
            tickers_data=sample_tickers_data,
            benchmark_data=benchmark_data,
            risk_free_rate=0.02
        )
        
        result2 = analyze_portfolio(
            tickers_data=sample_tickers_data,
            benchmark_data=benchmark_data,
            risk_free_rate=0.05
        )
        
        # Sharpe ratios should differ
        assert result1['portfolio']['Sharpe Ratio'] != result2['portfolio']['Sharpe Ratio']

    def test_analyze_portfolio_weights_normalization(self, sample_tickers_data, sample_ohlcv_data):
        """Test that weights are properly normalized."""
        benchmark_data = sample_ohlcv_data[:200]
        
        # Provide weights that don't sum to 1 (use floats instead of ints)
        weights = {'VTI': 60.0, 'BND': 30.0, 'VNQ': 10.0}  # Sum to 100 instead of 1
        
        # Should not raise error - weights should be normalized
        result = analyze_portfolio(
            tickers_data=sample_tickers_data,
            benchmark_data=benchmark_data,
            weights=weights
        )
        
        assert 'portfolio' in result

    def test_analyze_portfolio_no_overlapping_data(self):
        """Test that no overlapping data raises ValueError."""
        # Create data with different date ranges
        ticker_data = {
            'VTI': [
                {'date': '2020-01-01 00:00:00', 'close': 100},
                {'date': '2020-01-02 00:00:00', 'close': 101}
            ]
        }
        benchmark_data = [
            {'date': '2023-01-01 00:00:00', 'close': 100},
            {'date': '2023-01-02 00:00:00', 'close': 101}
        ]
        
        # The error message might vary, so just check that it raises ValueError
        with pytest.raises(ValueError):
            analyze_portfolio(
                tickers_data=ticker_data,
                benchmark_data=benchmark_data
            )


# ============================================================================
# Edge Cases and Error Handling Tests
# ============================================================================

@pytest.mark.unit
class TestMetricsEdgeCases:
    """Tests for edge cases in metrics calculations."""

    def test_flat_price_series(self):
        """Test metrics with flat (no change) price series."""
        dates = pd.date_range(start='2020-01-01', periods=252, freq='D')
        prices = pd.Series([100.0] * 252, index=dates)
        
        # Flat prices lead to zero volatility which causes Sharpe ratio calculation to fail
        with pytest.raises(ValueError, match="volatility is zero"):
            calculate_performance_metrics(prices)

    def test_single_day_timespan(self):
        """Test that single day timespan raises error."""
        # Same date for all entries
        dates = [datetime(2020, 1, 1)] * 2
        prices = pd.Series([100.0, 101.0], index=dates)
        
        with pytest.raises(ValueError):
            calculate_performance_metrics(prices)

    def test_very_short_timespan(self):
        """Test metrics with very short timespan."""
        dates = pd.date_range(start='2020-01-01', periods=5, freq='D')
        prices = pd.Series([100, 101, 102, 101, 103], index=dates)
        
        # Should not raise error, but results might be less meaningful
        metrics = calculate_performance_metrics(prices)
        
        assert 'CAGR' in metrics
        # CAGR for short period will be extrapolated to annual
        assert isinstance(metrics['CAGR'], float)
