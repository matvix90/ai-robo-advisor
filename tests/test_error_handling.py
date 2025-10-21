"""
Tests for data fetching error handling and retry mechanisms.
"""
import pytest
from unittest.mock import patch, Mock
import time

from src.tools.polygon_api import (
    get_stock_history_with_retry, 
    fetch_histories_concurrently,
    MAX_RETRIES
)


@pytest.mark.unit
class TestRetryMechanism:
    """Tests for retry logic in polygon_api."""

    @patch('src.tools.polygon_api.get_stock_history')
    @patch('src.tools.polygon_api.time.sleep')
    def test_retry_on_exception(self, mock_sleep, mock_get_history):
        """Test that retry mechanism attempts up to MAX_RETRIES times on exception."""
        mock_get_history.side_effect = Exception("API Error")
        
        result = get_stock_history_with_retry("AAPL", "day", "2023-01-01", "2024-01-01")
        
        assert result == []
        assert mock_get_history.call_count == MAX_RETRIES
        assert mock_sleep.call_count == MAX_RETRIES - 1

    @patch('src.tools.polygon_api.get_stock_history')
    @patch('src.tools.polygon_api.time.sleep')
    def test_retry_on_empty_result(self, mock_sleep, mock_get_history):
        """Test that retry mechanism attempts again on empty result."""
        mock_get_history.return_value = []
        
        result = get_stock_history_with_retry("INVALID", "day", "2023-01-01", "2024-01-01")
        
        assert result == []
        assert mock_get_history.call_count == MAX_RETRIES

    @patch('src.tools.polygon_api.get_stock_history')
    @patch('src.tools.polygon_api.time.sleep')
    def test_retry_success_on_second_attempt(self, mock_sleep, mock_get_history):
        """Test that retry returns data when second attempt succeeds."""
        expected_data = [{'date': '2023-01-01', 'close': 100}]
        mock_get_history.side_effect = [[], expected_data]
        
        result = get_stock_history_with_retry("AAPL", "day", "2023-01-01", "2024-01-01")
        
        assert result == expected_data
        assert mock_get_history.call_count == 2
        assert mock_sleep.call_count == 1

    @patch('src.tools.polygon_api.get_stock_history')
    def test_retry_success_on_first_attempt(self, mock_get_history):
        """Test that no retry happens when first attempt succeeds."""
        expected_data = [{'date': '2023-01-01', 'close': 100}]
        mock_get_history.return_value = expected_data
        
        result = get_stock_history_with_retry("AAPL", "day", "2023-01-01", "2024-01-01")
        
        assert result == expected_data
        assert mock_get_history.call_count == 1

    @patch('src.tools.polygon_api.get_stock_history')
    @patch('src.tools.polygon_api.time.sleep')
    def test_exponential_backoff(self, mock_sleep, mock_get_history):
        """Test that retry delays follow exponential backoff pattern."""
        mock_get_history.side_effect = Exception("API Error")
        
        get_stock_history_with_retry("AAPL", "day", "2023-01-01", "2024-01-01")
        
        # Verify exponential backoff: 1s, 2s
        sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
        assert sleep_calls[0] == 1
        assert sleep_calls[1] == 2

    @patch('src.tools.polygon_api.get_stock_history_with_retry')
    def test_concurrent_fetch_partial_success(self, mock_retry):
        """Test that concurrent fetch returns available data even when some fail."""
        def side_effect(ticker, *args):
            if ticker in ['AAPL', 'GOOGL']:
                return [{'date': '2023-01-01', 'close': 100}]
            return []
        
        mock_retry.side_effect = side_effect
        
        result = fetch_histories_concurrently(
            ['AAPL', 'GOOGL', 'INVALID1', 'INVALID2'],
            'day', '2023-01-01', '2024-01-01'
        )
        
        assert len(result) == 2
        assert 'AAPL' in result
        assert 'GOOGL' in result
        assert 'INVALID1' not in result
        assert 'INVALID2' not in result

    @patch('src.tools.polygon_api.get_stock_history_with_retry')
    def test_concurrent_fetch_all_fail(self, mock_retry):
        """Test that concurrent fetch returns empty dict when all fail."""
        mock_retry.return_value = []
        
        result = fetch_histories_concurrently(
            ['INVALID1', 'INVALID2'],
            'day', '2023-01-01', '2024-01-01'
        )
        
        assert result == {}

    @patch('src.tools.polygon_api.get_stock_history_with_retry')
    def test_concurrent_fetch_with_exception(self, mock_retry):
        """Test that exceptions in concurrent fetch don't crash the process."""
        def side_effect(ticker, *args):
            if ticker == 'AAPL':
                return [{'date': '2023-01-01', 'close': 100}]
            raise Exception("Network error")
        
        mock_retry.side_effect = side_effect
        
        result = fetch_histories_concurrently(
            ['AAPL', 'GOOGL'],
            'day', '2023-01-01', '2024-01-01'
        )
        
        assert len(result) == 1
        assert 'AAPL' in result


@pytest.mark.unit
class TestNetworkErrorScenarios:
    """Tests for network and API error scenarios."""

    @patch('src.tools.polygon_api.POLYGON_AVAILABLE', False)
    def test_polygon_unavailable(self):
        """Test behavior when Polygon API is not available."""
        result = fetch_histories_concurrently(
            ['AAPL'], 'day', '2023-01-01', '2024-01-01'
        )
        assert result == {}

    @patch('src.tools.polygon_api.get_stock_history')
    @patch('src.tools.polygon_api.time.sleep')
    def test_rate_limit_scenario(self, mock_sleep, mock_get_history):
        """Test handling of API rate limiting."""
        # Simulate rate limit error then success
        mock_get_history.side_effect = [
            Exception("Rate limit exceeded"),
            [{'date': '2023-01-01', 'close': 100}]
        ]
        
        result = get_stock_history_with_retry("AAPL", "day", "2023-01-01", "2024-01-01")
        
        assert result == [{'date': '2023-01-01', 'close': 100}]
        assert mock_get_history.call_count == 2

    @patch('src.tools.polygon_api.get_stock_history')
    @patch('src.tools.polygon_api.time.sleep')
    def test_network_timeout(self, mock_sleep, mock_get_history):
        """Test handling of network timeout errors."""
        mock_get_history.side_effect = TimeoutError("Request timeout")
        
        result = get_stock_history_with_retry("AAPL", "day", "2023-01-01", "2024-01-01")
        
        assert result == []
        assert mock_get_history.call_count == MAX_RETRIES
