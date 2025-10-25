from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from decouple import config
import pytz
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

try:
    from polygon import RESTClient
    POLYGON_API_KEY = config("POLYGON_API_KEY", default=None, cast=str) 
    POLYGON_AVAILABLE = True

except ImportError:
    POLYGON_AVAILABLE = False
    print("Polygon.io client not available. Ensure 'polygon' package is installed and POLYGON_API_KEY is set.")

MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 1  
RETRY_BACKOFF_FACTOR = 2


def fetch_histories_concurrently(
    tickers: List[str],
    timespan: str,
    start_date: str,
    end_date: str
) -> Dict[str, List[Dict]]:
    """
    Fetches historical data for multiple tickers concurrently with retry logic.

    Args:
        tickers (List[str]): A list of stock ticker symbols (portfolio + benchmark).
        timespan (str): The size of the time window (e.g., 'day', 'hour').
        start_date (str): The start date for the history (YYYY-MM-DD).
        end_date (str): The end date for the history (YYYY-MM-DD).

    Returns:
        Dict[str, List[Dict]]: A dictionary mapping each ticker to its historical data.
            Only includes tickers with successfully fetched data.
    """
    if not POLYGON_AVAILABLE:
        return {}

    histories = {}
    failed_tickers = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_ticker = {
            executor.submit(get_stock_history_with_retry, ticker, timespan, start_date, end_date): ticker
            for ticker in tickers
        }

        for future in as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            try:
                result = future.result()
                if result:
                    histories[ticker] = result
                else:
                    failed_tickers.append(ticker)
            except Exception as exc:
                failed_tickers.append(ticker)

    return histories


def get_stock_history_with_retry(
    symbol: str, 
    timespan: str, 
    start_date: str, 
    end_date: str,
    max_retries: int = MAX_RETRIES
) -> List[Dict]:
    """
    Fetch historical stock prices with retry logic and exponential backoff.
    
    Args:
        symbol: Stock symbol
        timespan: The size of the time window (e.g., 'day', 'hour')
        start_date: Start date for history (YYYY-MM-DD)
        end_date: End date for history (YYYY-MM-DD)
        max_retries: Maximum number of retry attempts
        
    Returns:
        list: List of historical prices, empty list if all retries fail
    """
    if not POLYGON_AVAILABLE:
        return []
    
    for attempt in range(max_retries):
        try:
            result = get_stock_history(symbol, timespan, start_date, end_date)
            if result:
                return result
            
            # If empty result and not last attempt, retry
            if attempt < max_retries - 1:
                delay = INITIAL_RETRY_DELAY * (RETRY_BACKOFF_FACTOR ** attempt)
                time.sleep(delay)
                
        except Exception as e:
            if attempt < max_retries - 1:
                delay = INITIAL_RETRY_DELAY * (RETRY_BACKOFF_FACTOR ** attempt)
                time.sleep(delay)
            else:
                # Last attempt failed
                return []
    
    return []


def get_stock_history(symbol, timespan, start_date, end_date):
    """
    Fetch historical stock prices.
    
    Args:
        symbol: Stock symbol
        start_date: Start date for history
        end_date: End date for history
        
    Returns:
        list: List of historical prices, empty list on error
    """
    if not POLYGON_AVAILABLE:
        return []
    
    client = RESTClient(POLYGON_API_KEY)

    try:
        aggs = client.get_aggs(symbol, 1, timespan, start_date, end_date, sort='asc', adjusted=True)
        return history_to_dict(aggs)
    except Exception:
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
