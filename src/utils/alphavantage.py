# src/utils/alphavantage.py
"""
Alpha Vantage helper utilities.

Usage:
    export ALPHAVANTAGE_API_KEY="your_key_here"

    from utils.alphavantage import (
        get_time_series_daily_adjusted,
        get_overview,
    )

    ts = get_time_series_daily_adjusted("CSPX.L", outputsize="full")
    ov = get_overview("CSPX.L")
"""

from __future__ import annotations
import os
import time
import json
import logging
from typing import Optional, Dict, Any
import requests
from pathlib import Path

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"
DEFAULT_CACHE_DIR = Path("data/alphavantage_cache")

# Basic exponential backoff settings for rate limiting / transient errors
_RETRY_STATUS = (429, 503)
_MAX_RETRIES = 5
_BASE_SLEEP = 1.0


def _ensure_cache_dir(cache_dir: Path | str | None) -> Path:
    if cache_dir is None:
        cache_dir = DEFAULT_CACHE_DIR
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def _write_cache(cache_path: Path, data: Dict[str, Any]) -> None:
    try:
        with cache_path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
    except Exception:
        logger.exception("Failed writing cache for %s", cache_path)


def _read_cache(cache_path: Path) -> Optional[Dict[str, Any]]:
    if not cache_path.exists():
        return None
    try:
        with cache_path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        logger.exception("Failed reading cache for %s", cache_path)
        return None


def _call_alpha_vantage(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Internal request wrapper that handles backoff and common error messages.
    """
    if not ALPHAVANTAGE_API_KEY:
        raise RuntimeError("ALPHAVANTAGE_API_KEY environment variable not set.")

    params = params.copy()
    params["apikey"] = ALPHAVANTAGE_API_KEY

    attempt = 0
    while attempt < _MAX_RETRIES:
        attempt += 1
        resp = requests.get(BASE_URL, params=params, timeout=30)
        # If service returns HTTP-level rate limiting, try again with backoff
        if resp.status_code in _RETRY_STATUS:
            sleep_for = _BASE_SLEEP * (2 ** (attempt - 1))
            logger.warning("AlphaVantage returned %s; backing off %ss (attempt %d)", resp.status_code, sleep_for, attempt)
            time.sleep(sleep_for)
            continue

        try:
            data = resp.json()
        except ValueError:
            resp.raise_for_status()
        
        # Alpha Vantage sometimes returns a "Note" when rate limited, or "Error Message"
        if isinstance(data, dict) and ("Note" in data or "Error Message" in data):
            # If a Rate Limit Note, exponential backoff and retry
            note = data.get("Note") or data.get("Error Message")
            logger.warning("AlphaVantage API returned Note/Error: %s", note)
            sleep_for = _BASE_SLEEP * (2 ** (attempt - 1))
            time.sleep(sleep_for)
            continue

        return data

    # If we've reached here, raise a helpful message
    raise RuntimeError("AlphaVantage API failed after retries; check logs or API key and rate limits.")


def get_time_series_daily_adjusted(
    symbol: str,
    outputsize: str = "compact",
    cache: bool = True,
    cache_dir: Optional[Path | str] = None,
    force: bool = False,
) -> Dict[str, Any]:
    """
    Fetch TIME_SERIES_DAILY_ADJUSTED for a symbol.

    Args:
        symbol: The symbol as you want to query it (e.g., "IVV", "CSPX.L", "CSSPX.MI", etc).
                NOTE: Alpha Vantage symbol formats for some exchanges vary. Use the exact
                symbol you expect the service to accept, or make your own mapping layer.
        outputsize: "compact" (last 100 days) or "full" (full history)
        cache: whether to cache the JSON response to disk
        cache_dir: directory to store cached responses
        force: if True, ignore cache and fetch fresh

    Returns:
        dict containing parsed "Time Series (Daily)" mapping dates -> OHLCV fields
        and other Alpha Vantage fields when available.

    Raises:
        RuntimeError if the API fails or no time series found.
    """
    cache_dir = _ensure_cache_dir(cache_dir)
    cache_path = cache_dir / f"{symbol.replace('/', '_')}_time_series.json"

    if cache and not force:
        cached = _read_cache(cache_path)
        if cached:
            return cached

    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": symbol,
        "outputsize": outputsize,
        "datatype": "json",
    }

    data = _call_alpha_vantage(params)

    # Standard key name in Alpha Vantage responses
    time_series_key = None
    for k in data.keys():
        if "Time Series" in k:
            time_series_key = k
            break

    if not time_series_key:
        # If no time series present, surface helpful debug info
        logger.error("AlphaVantage response for symbol=%s contained no 'Time Series' key: %s", symbol, data)
        raise RuntimeError(f"No time series data returned for symbol {symbol}. Response keys: {list(data.keys())}")

    result = {
        "symbol": symbol,
        "meta": data.get("Meta Data", {}),
        "time_series": data[time_series_key],
        "_raw": data
    }

    if cache:
        _write_cache(cache_path, result)

    return result


def get_overview(
    symbol: str,
    cache: bool = True,
    cache_dir: Optional[Path | str] = None,
    force: bool = False,
) -> Dict[str, Any]:
    """
    Fetch OVERVIEW data for a symbol (company / fund metadata).

    The "OVERVIEW" endpoint might include fields such as Description, Sector, Industry,
    MarketCapitalization (for stocks), and sometimes expense ratios or other fund-specific fields
    depending on ticker coverage.

    Args:
        symbol: symbol to fetch overview for
        cache: whether to cache results locally
        cache_dir: directory to store cached results
        force: ignore cache and fetch fresh

    Returns:
        dict with overview fields (raw Alpha Vantage JSON returned)

    Raises:
        RuntimeError if API fails or returns empty.
    """
    cache_dir = _ensure_cache_dir(cache_dir)
    cache_path = cache_dir / f"{symbol.replace('/', '_')}_overview.json"

    if cache and not force:
        cached = _read_cache(cache_path)
        if cached:
            return cached

    params = {
        "function": "OVERVIEW",
        "symbol": symbol,
        "datatype": "json",
    }

    data = _call_alpha_vantage(params)

    # The overview endpoint returns an empty dict for unknown symbols in some cases.
    if not data or (isinstance(data, dict) and not data.keys()):
        logger.error("AlphaVantage overview returned empty for %s: %s", symbol, data)
        raise RuntimeError(f"No overview data for symbol {symbol}")

    if cache:
        _write_cache(cache_path, data)

    return {"symbol": symbol, "overview": data, "_raw": data}


def batch_get_overview(
    symbols: list[str],
    sleep_between: float = 12.0,
    cache: bool = True,
    cache_dir: Optional[Path | str] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Convenience: fetch overview for a list of symbols with a sleep between calls to reduce hitting rate limits.
    Note: Free Alpha Vantage tier typically allows 5 calls/minute; set sleep_between accordingly.

    Returns a dict mapping symbol -> overview dict or error info.
    """
    out = {}
    for i, s in enumerate(symbols):
        try:
            out[s] = get_overview(s, cache=cache, cache_dir=cache_dir)
        except Exception as e:
            logger.exception("Failed to fetch overview for %s", s)
            out[s] = {"error": str(e)}
        # Sleep between calls to avoid throttling
        if i < len(symbols) - 1:
            time.sleep(sleep_between)
    return out


if __name__ == "__main__":
    # Quick manual test (only works if ALPHAVANTAGE_API_KEY is set)
    import pprint

    test_symbol = os.getenv("ALPHA_TEST_SYMBOL", "IVV")  # default to IVV
    print("Alpha Vantage helper test for:", test_symbol)
    try:
        ov = get_overview(test_symbol, cache=False)
        pprint.pprint(ov)
    except Exception as e:
        print("Overview fetch failed:", e)

    try:
        ts = get_time_series_daily_adjusted(test_symbol, outputsize="compact", cache=False)
        print("Time series days fetched:", len(ts["time_series"]))
        # Print most recent date sample
        first_date = next(iter(ts["time_series"].keys()))
        print("Most recent date:", first_date, "sample entry:", ts["time_series"][first_date])
    except Exception as e:
        print("Time series fetch failed:", e)
