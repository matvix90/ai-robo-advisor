from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

import pytz
from decouple import config

# Polygon.io integration
try:
    from polygon import RESTClient

    POLYGON_API_KEY = config("POLYGON_API_KEY", default=None, cast=str)
    POLYGON_AVAILABLE = True

except ImportError:
    POLYGON_AVAILABLE = False
    print(
        "Polygon.io client not available. Ensure 'polygon' package is installed and POLYGON_API_KEY is set."
    )


def fetch_histories_concurrently(
    tickers: list[str], timespan: str, start_date: str, end_date: str
) -> dict[str, list[dict]]:
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

    histories = {}
    # Note: Polygon.io's free plan has a rate limit of 5 API calls per minute.
    # For larger portfolios on a free plan, you may need to add delays or
    # reduce the number of workers.
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_ticker = {
            executor.submit(
                get_stock_history, ticker, timespan, start_date, end_date
            ): ticker
            for ticker in tickers
        }

        for future in as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            try:
                result = future.result()
                if result:
                    histories[ticker] = result
            except Exception as exc:
                print(
                    f"Ticker {ticker} generated an exception during concurrent fetch: {exc}"
                )

    return histories


def get_stock_history(symbol, timespan, start_date, end_date):
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

    try:
        aggs = client.get_aggs(
            symbol, 1, timespan, start_date, end_date, sort="asc", adjusted=True
        )
        return history_to_dict(aggs)
    except Exception as e:
        print(f"Error fetching history for {symbol}: {e}")
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
        dt = dt.astimezone(
            pytz.timezone("US/Eastern")
        )  # Convert to US/Eastern timezone
        aggs.append(
            {
                "date": dt.strftime("%Y-%m-%d %H:%M:%S"),
                "open": item.open,
                "high": item.high,
                "low": item.low,
                "close": item.close,
                "volume": item.volume,
            }
        )

    return aggs


def get_today_date():
    """
    Get today's date in 'YYYY-MM-DD' format.

    Returns:
        str: Today's date
    """
    return datetime.now(pytz.timezone("US/Eastern")).strftime("%Y-%m-%d")


def get_one_year_ago_date():
    """
    Get the date one year ago from today in 'YYYY-MM-DD' format.

    Returns:
        str: Date one year ago
    """
    one_year_ago = datetime.now(pytz.timezone("US/Eastern")) - timedelta(days=365)
    return one_year_ago.strftime("%Y-%m-%d")


def get_two_year_ago_date():
    """
    Get the date two years ago from today in 'YYYY-MM-DD' format.

    Returns:
        str: Date two years ago
    """
    two_years_ago = datetime.now(pytz.timezone("US/Eastern")) - timedelta(days=730)
    return two_years_ago.strftime("%Y-%m-%d")
