from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Callable
from decouple import config
import pytz
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FutureTimeout
import logging
import time
import random

logger = logging.getLogger(__name__)

# Configuration
DEFAULT_TIMEOUT = config("POLYGON_REQUEST_TIMEOUT", default=10, cast=int)
DEFAULT_MAX_RETRIES = config("POLYGON_MAX_RETRIES", default=3, cast=int)

# Polygon.io integration
try:
    from polygon import RESTClient
    POLYGON_API_KEY = config("POLYGON_API_KEY", default=None, cast=str)
    POLYGON_AVAILABLE = True

except Exception:
    POLYGON_AVAILABLE = False
    print("Polygon.io client not available. Ensure 'polygon' package is installed and POLYGON_API_KEY is set.")

LAST_RATE_LIMIT_HEADERS: Optional[Dict[str, Any]] = None


def get_last_rate_limit_headers() -> Optional[Dict[str, Any]]:
    """Return the most recently observed rate-limit headers (or None)."""
    return LAST_RATE_LIMIT_HEADERS


def _is_rate_limit_exception(exc: Exception) -> bool:
    """Best-effort detection for 429 / rate-limit exceptions.

    Some HTTP client exceptions expose a numeric status (e.g., `status`, `status_code`),
    others include the string '429' or 'rate limit' in their message. This helper
    tries a few heuristics so we can retry only on rate-limit responses.
    """
    for attr in ("status", "status_code", "statusCode", "code"):
        if hasattr(exc, attr):
            try:
                if int(getattr(exc, attr)) == 429:
                    return True
            except Exception:
                pass

    msg = str(exc).lower()
    if "429" in msg or "rate limit" in msg or "too many requests" in msg:
        return True

    return False


def _extract_headers_from_exception(exc: Exception) -> Optional[Dict[str, Any]]:
    """Try to extract response headers from exception objects returned by HTTP clients.

    Returns None if not available.
    """
    candidates = [
        getattr(exc, "response", None),
        getattr(exc, "res", None),
        getattr(exc, "http_resp", None),
        getattr(exc, "resp", None),
    ]
    for c in candidates:
        if c is None:
            continue
        headers = getattr(c, "headers", None)
        if headers:
            return dict(headers)
        try:
            if hasattr(c, "getheaders"):
                return dict(c.getheaders())
        except Exception:
            pass
            
    if hasattr(exc, "headers"):
        try:
            return dict(getattr(exc, "headers"))
        except Exception:
            pass

    return None


def _call_with_retries(
    func: Callable[[], Any],
    timeout: Optional[int] = None,
    max_retries: Optional[int] = None,
) -> Any:
    """Call a blocking function with per-call timeout and retry on rate-limit (429).

    Args:
        func: Zero-arg callable that performs the HTTP request.
        timeout: Per-request timeout in seconds (default uses DEFAULT_TIMEOUT).
        max_retries: Maximum number of retries on 429 (default DEFAULT_MAX_RETRIES).

    Returns:
        The function's successful return value.

    Raises:
        Exception: The last exception if all retries/timeouts are exhausted.
    """
    timeout = DEFAULT_TIMEOUT if timeout is None else timeout
    max_retries = DEFAULT_MAX_RETRIES if max_retries is None else max_retries

    attempt = 0
    backoff_base = 1.0
    last_exc: Optional[Exception] = None

    with ThreadPoolExecutor(max_workers=1) as executor:
        while attempt <= max_retries:
            attempt += 1
            future = executor.submit(func)
            try:
                result = future.result(timeout=timeout)
                return result
            except FutureTimeout:
                future.cancel()
                last_exc = TimeoutError(f"Polygon request timed out after {timeout}s on attempt {attempt}")
                logger.warning("Polygon request timed out (attempt %d/%d) after %ss", attempt, max_retries, timeout)
            except Exception as exc:
                last_exc = exc
                headers = _extract_headers_from_exception(exc)
                global LAST_RATE_LIMIT_HEADERS
                if headers:
                    LAST_RATE_LIMIT_HEADERS = headers
                    logger.info("Observed rate-limit headers: %s", headers)

                if _is_rate_limit_exception(exc) and attempt <= max_retries:
                    wait = backoff_base * (2 ** (attempt - 1)) + random.uniform(0, 0.5)
                    logger.warning(
                        "Rate limit detected on attempt %d/%d, backing off %.2fs before retrying",
                        attempt,
                        max_retries,
                        wait,
                    )
                    time.sleep(wait)
                    continue

                logger.exception("Polygon request failed on attempt %d: %s", attempt, exc)
                raise

        if last_exc:
            raise last_exc


def fetch_histories_concurrently(
    tickers: List[str],
    timespan: str,
    start_date: str,
    end_date: str,
) -> Dict[str, List[Dict]]:
    """
    Fetches historical data for multiple tickers concurrently.

    Args:
        tickers (List[str]): A list of stock ticker symbols (portfolio + benchmark).
        timespan (str): The size of the time window (e.g., 'day', 'hour').
        start_date (str): The start date for the history (YYYY-MM-DD).
        end_date (str): The end date for the history (YYYY-MM-DD).

    Returns:
        Dict[str, List[Dict]]: A dictionary mapping each ticker to its historical data.
    """
    if not POLYGON_AVAILABLE:
        return {}

    histories: Dict[str, List[Dict]] = {}
    # Note: Polygon.io's free plan has a rate limit of 5 API calls per minute.
    # We keep a small pool; callers can reduce workers or set higher plan limits.
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_ticker = {
            executor.submit(get_stock_history, ticker, timespan, start_date, end_date): ticker
            for ticker in tickers
        }

        for future in as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            try:
                result = future.result()
                if result:
                    histories[ticker] = result
            except Exception as exc:
                logger.exception("Ticker %s generated an exception during concurrent fetch: %s", ticker, exc)

    return histories

def get_stock_history(symbol, timespan, start_date, end_date, timeout: Optional[int] = None, max_retries: Optional[int] = None):
    """
    Fetch historical stock prices.
    
    Args:
        symbol: Stock symbol
        start_date: Start date for history
        end_date: End date for history
        
    Returns:
        list: List of historical prices
    """
    if not POLYGON_AVAILABLE:
        return []
    client = RESTClient(POLYGON_API_KEY)

    def _call():
        """
        Keep the interaction with the polygon client inside the callable so
        the wrapper can enforce timeouts and retries around it.
        
        """
        return client.get_aggs(symbol, 1, timespan, start_date, end_date, sort='asc', adjusted=True)

    try:
        aggs = _call_with_retries(_call, timeout=timeout, max_retries=max_retries)
        return history_to_dict(aggs)
    except Exception as e:
        logger.exception("Error fetching history for %s: %s", symbol, e)
        return []

def history_to_dict(history: list) -> list[dict]:
    """
    Convert historical data to a dictionary format.
    
    Args:
        history: List of historical prices

    Returns:
        dict: Dictionary with date as key and price as value
    """
    aggs = []
    for item in history:
        timestamp = item.timestamp / 1000  # Convert milliseconds to seconds
        dt = datetime.fromtimestamp(timestamp, pytz.UTC)  # Create UTC datetime
        dt = dt.astimezone(pytz.timezone('US/Eastern'))  # Convert to US/Eastern timezone
        aggs.append({
            'date': dt.strftime('%Y-%m-%d %H:%M:%S'),
            'open': item.open,
            'high': item.high,
            'low': item.low,
            'close': item.close,
            'volume': item.volume
        })

    return aggs

def get_today_date():
    """
    Get today's date in 'YYYY-MM-DD' format.
    
    Returns:
        str: Today's date
    """
    return datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d')

def get_one_year_ago_date():
    """
    Get the date one year ago from today in 'YYYY-MM-DD' format.
    
    Returns:
        str: Date one year ago
    """
    one_year_ago = datetime.now(pytz.timezone('US/Eastern')) - timedelta(days=365)
    return one_year_ago.strftime('%Y-%m-%d')

def get_two_year_ago_date():
    """
    Get the date two years ago from today in 'YYYY-MM-DD' format.
    
    Returns:
        str: Date two years ago
    """
    two_years_ago = datetime.now(pytz.timezone('US/Eastern')) - timedelta(days=730)
    return two_years_ago.strftime('%Y-%m-%d')
