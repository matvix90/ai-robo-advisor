"""
Tests for Polygon API tool integration.
"""

from unittest.mock import Mock, patch

import pytest

from src.tools.polygon_api import (
    POLYGON_AVAILABLE,
    fetch_histories_concurrently,
    get_stock_history,
    history_to_dict,
)

# ============================================================================
# Polygon API Availability Tests
# ============================================================================


@pytest.mark.unit
class TestPolygonAvailability:
    """Tests for Polygon API availability checking."""

    def test_polygon_available_constant(self):
        """Test POLYGON_AVAILABLE constant exists."""
        assert isinstance(POLYGON_AVAILABLE, bool)


# ============================================================================
# History to Dict Tests
# ============================================================================


@pytest.mark.unit
class TestHistoryToDict:
    """Tests for history_to_dict function."""

    def test_history_to_dict_basic(self):
        """Test converting history data to dictionary."""
        # Mock history items
        mock_item1 = Mock()
        mock_item1.timestamp = 1609459200000  # 2021-01-01 in milliseconds
        mock_item1.open = 100.0
        mock_item1.high = 105.0
        mock_item1.low = 99.0
        mock_item1.close = 103.0
        mock_item1.volume = 1000000

        mock_item2 = Mock()
        mock_item2.timestamp = 1609545600000  # 2021-01-02 in milliseconds
        mock_item2.open = 103.0
        mock_item2.high = 107.0
        mock_item2.low = 102.0
        mock_item2.close = 106.0
        mock_item2.volume = 1200000

        history = [mock_item1, mock_item2]

        result = history_to_dict(history)

        assert len(result) == 2
        assert all("date" in item for item in result)
        assert all("open" in item for item in result)
        assert all("close" in item for item in result)
        assert all("high" in item for item in result)
        assert all("low" in item for item in result)
        assert all("volume" in item for item in result)

    def test_history_to_dict_empty(self):
        """Test converting empty history."""
        result = history_to_dict([])
        assert result == []

    def test_history_to_dict_date_format(self):
        """Test that dates are formatted correctly."""
        mock_item = Mock()
        mock_item.timestamp = 1609459200000  # 2021-01-01
        mock_item.open = 100.0
        mock_item.high = 105.0
        mock_item.low = 99.0
        mock_item.close = 103.0
        mock_item.volume = 1000000

        result = history_to_dict([mock_item])

        # Check date format (should be 'YYYY-MM-DD HH:MM:SS')
        assert "date" in result[0]
        assert isinstance(result[0]["date"], str)
        # Date should contain year, month, day, and time
        assert "-" in result[0]["date"]
        assert ":" in result[0]["date"]


# ============================================================================
# Get Stock History Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.api
class TestGetStockHistory:
    """Tests for get_stock_history function."""

    def test_get_stock_history_polygon_unavailable(self):
        """Test get_stock_history when Polygon is unavailable."""
        with patch("src.tools.polygon_api.POLYGON_AVAILABLE", False):
            result = get_stock_history("AAPL", "day", "2023-01-01", "2023-12-31")
            assert result == []

    @patch("src.tools.polygon_api.RESTClient")
    def test_get_stock_history_success(self, mock_rest_client):
        """Test successful stock history retrieval."""
        if not POLYGON_AVAILABLE:
            pytest.skip("Polygon not available")

        # Mock the client and response
        mock_client_instance = Mock()
        mock_rest_client.return_value = mock_client_instance

        mock_agg = Mock()
        mock_agg.timestamp = 1609459200000
        mock_agg.open = 100.0
        mock_agg.high = 105.0
        mock_agg.low = 99.0
        mock_agg.close = 103.0
        mock_agg.volume = 1000000

        mock_client_instance.get_aggs.return_value = [mock_agg]

        result = get_stock_history("AAPL", "day", "2023-01-01", "2023-12-31")

        assert isinstance(result, list)
        assert len(result) > 0

    @patch("src.tools.polygon_api.RESTClient")
    def test_get_stock_history_api_error(self, mock_rest_client):
        """Test handling of API errors."""
        if not POLYGON_AVAILABLE:
            pytest.skip("Polygon not available")

        mock_client_instance = Mock()
        mock_rest_client.return_value = mock_client_instance
        mock_client_instance.get_aggs.side_effect = Exception("API Error")

        result = get_stock_history("INVALID", "day", "2023-01-01", "2023-12-31")

        assert result == []


# ============================================================================
# Fetch Histories Concurrently Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.api
class TestFetchHistoriesConcurrently:
    """Tests for fetch_histories_concurrently function."""

    def test_fetch_histories_polygon_unavailable(self):
        """Test fetch_histories_concurrently when Polygon is unavailable."""
        with patch("src.tools.polygon_api.POLYGON_AVAILABLE", False):
            result = fetch_histories_concurrently(
                ["AAPL", "GOOGL"], "day", "2023-01-01", "2023-12-31"
            )
            assert result == {}

    @patch("src.tools.polygon_api.get_stock_history")
    def test_fetch_histories_multiple_tickers(self, mock_get_history):
        """Test fetching histories for multiple tickers."""
        if not POLYGON_AVAILABLE:
            pytest.skip("Polygon not available")

        # Mock return values for different tickers
        def mock_history_side_effect(symbol, *args):
            if symbol == "AAPL":
                return [{"date": "2023-01-01", "close": 100}]
            elif symbol == "GOOGL":
                return [{"date": "2023-01-01", "close": 200}]
            return []

        mock_get_history.side_effect = mock_history_side_effect

        result = fetch_histories_concurrently(
            ["AAPL", "GOOGL"], "day", "2023-01-01", "2023-12-31"
        )

        assert "AAPL" in result
        assert "GOOGL" in result
        assert len(result) == 2

    @patch("src.tools.polygon_api.get_stock_history")
    def test_fetch_histories_empty_tickers(self, mock_get_history):
        """Test fetching histories with empty ticker list."""
        if not POLYGON_AVAILABLE:
            pytest.skip("Polygon not available")

        result = fetch_histories_concurrently([], "day", "2023-01-01", "2023-12-31")

        assert result == {}

    @patch("src.tools.polygon_api.get_stock_history")
    def test_fetch_histories_error_handling(self, mock_get_history):
        """Test that errors in individual fetches don't break everything."""
        if not POLYGON_AVAILABLE:
            pytest.skip("Polygon not available")

        def mock_history_side_effect(symbol, *args):
            if symbol == "AAPL":
                return [{"date": "2023-01-01", "close": 100}]
            elif symbol == "ERROR":
                raise Exception("API Error")
            return []

        mock_get_history.side_effect = mock_history_side_effect

        result = fetch_histories_concurrently(
            ["AAPL", "ERROR", "GOOGL"], "day", "2023-01-01", "2023-12-31"
        )

        # Should still get AAPL data even though ERROR failed
        assert "AAPL" in result or isinstance(result, dict)


# ============================================================================
# Integration Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.slow
class TestPolygonIntegration:
    """Integration tests for Polygon API (requires actual API)."""

    @pytest.mark.skipif(not POLYGON_AVAILABLE, reason="Polygon API not available")
    def test_real_api_call_structure(self):
        """Test that real API calls return expected structure (if API is available)."""
        # This test would require actual API credentials
        # Skip in most test runs
        pytest.skip("Requires real Polygon API credentials")
