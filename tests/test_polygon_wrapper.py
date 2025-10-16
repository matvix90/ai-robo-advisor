"""Tests for the Polygon request wrapper behavior: retries, backoff, timeouts, and header propagation."""
import time
import pytest
from unittest.mock import patch, MagicMock

from src.tools import polygon_api


"""Tests for the Polygon request wrapper behavior: retries, backoff, timeouts, and header propagation."""
import time
import pytest
from unittest.mock import patch, MagicMock

from src.tools import polygon_api


class FakeRateLimitException(Exception):
    def __init__(self, message="429 Too Many Requests"):
        super().__init__(message)
        self.status = 429
        self.response = MagicMock()
        self.response.headers = {
            "x-rate-limit-limit": "5",
            "x-rate-limit-remaining": "0",
            "x-rate-limit-reset": "60",
        }


@pytest.mark.unit
def test_retry_on_429_and_capture_headers(monkeypatch):
    # Simulate the RESTClient.get_aggs raising a rate-limit on first call, then returning a list on second
    fake_client = MagicMock()

    call_count = {"n": 0}

    def side_effect(*args, **kwargs):
        call_count["n"] += 1
        if call_count["n"] == 1:
            raise FakeRateLimitException()
        return [MagicMock(timestamp=1609459200000, open=1, high=2, low=1, close=1.5, volume=1000)]

    fake_client.get_aggs.side_effect = side_effect

    with patch("src.tools.polygon_api.RESTClient", return_value=fake_client):
        # call get_stock_history which now uses the wrapper
        result = polygon_api.get_stock_history(
            "FAKE", "day", "2020-01-01", "2020-12-31", timeout=2, max_retries=2
        )

    assert isinstance(result, list)
    assert len(result) == 1

    headers = polygon_api.get_last_rate_limit_headers()
    assert headers is not None
    assert headers.get("x-rate-limit-remaining") == "0"


@pytest.mark.unit
def test_timeout_expires(monkeypatch):
    # Simulate a long-running get_aggs that exceeds timeout
    fake_client = MagicMock()

    def long_running(*args, **kwargs):
        time.sleep(2)
        return []

    fake_client.get_aggs.side_effect = long_running

    with patch("src.tools.polygon_api.RESTClient", return_value=fake_client):
        # Set timeout short so it triggers
        result = polygon_api.get_stock_history(
            "SLOW", "day", "2020-01-01", "2020-12-31", timeout=0.5, max_retries=0
        )

    assert result == []
