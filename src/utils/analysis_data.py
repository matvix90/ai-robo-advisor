from tools.polygon_api import fetch_histories_concurrently, get_two_year_ago_date, get_today_date
from data.models import Portfolio

def all_data(portfolio: Portfolio, benchmark_ticker: str) -> tuple[dict, dict, dict]:
    """ Fetch historical data for all portfolio tickers and the benchmark ticker concurrently.

    Args:
        portfolio (Portfolio): The portfolio containing holdings with symbols and weights.
        benchmark_ticker (str): The benchmark ticker symbol.

    Returns:
        tuple: A tuple containing three dictionaries:
            - portfolio_data: A dictionary where keys are portfolio ticker symbols and values are their historical data.
            - benchmark_data: A dictionary containing the historical data for the benchmark ticker.
            - weights: A dictionary containing the weights of the portfolio tickers.
    
    Raises:
        ValueError: If portfolio is invalid, has no holdings, or data fetching fails.
        TypeError: If portfolio is not a Portfolio instance.
    """
    
    # Validate inputs
    if not isinstance(portfolio, Portfolio):
        raise TypeError("portfolio must be a Portfolio instance")
    
    if not benchmark_ticker or not isinstance(benchmark_ticker, str):
        raise ValueError("benchmark_ticker must be a non-empty string")
    
    if not hasattr(portfolio, 'holdings') or not portfolio.holdings:
        raise ValueError("Portfolio must have holdings")

    # Extract tickers and weights from the portfolio
    portfolio_tickers = []
    weights = {}
    
    try:
        for holding in portfolio.holdings:
            if not hasattr(holding, 'symbol') or not hasattr(holding, 'weight'):
                raise ValueError("Each holding must have 'symbol' and 'weight' attributes")
            
            if not holding.symbol:
                raise ValueError("Holding symbol cannot be empty")
            
            portfolio_tickers.append(holding.symbol)
            weights[holding.symbol] = holding.weight
    except AttributeError as e:
        raise ValueError(f"Invalid portfolio holdings structure: {str(e)}")

    if not portfolio_tickers:
        raise ValueError("Portfolio contains no valid tickers")

    # Validate weights sum to a reasonable value
    total_weight = sum(weights.values())
    if total_weight <= 0:
        raise ValueError("Portfolio weights must sum to a positive value")

    # Combine all tickers for a single concurrent fetch
    all_tickers_to_fetch = portfolio_tickers + [benchmark_ticker]

    # Define date range and timespan
    try:
        start_date = get_two_year_ago_date()
        end_date = get_today_date()
    except Exception as e:
        raise ValueError(f"Failed to get date range: {str(e)}")
    
    timespan = 'day'

    # Fetch all data concurrently
    try:
        all_histories = fetch_histories_concurrently(
            tickers=all_tickers_to_fetch,
            timespan=timespan,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        raise ValueError(f"Failed to fetch historical data: {str(e)}")

    if not all_histories:
        raise ValueError("No historical data was retrieved")
    
    if benchmark_ticker not in all_histories:
        raise ValueError(f"Failed to fetch data for benchmark ticker: {benchmark_ticker}")

    # Check if we have data for all portfolio tickers
    missing_tickers = [ticker for ticker in portfolio_tickers if ticker not in all_histories]
    if missing_tickers:
        raise ValueError(f"Failed to fetch data for portfolio tickers: {missing_tickers}")

    # Validate that we have sufficient data
    for ticker, data in all_histories.items():
        if not data or len(data) < 2:
            raise ValueError(f"Insufficient data for ticker {ticker}: need at least 2 data points")

    # Separate the benchmark data from the portfolio data
    benchmark_data = all_histories.pop(benchmark_ticker)
    portfolio_data = all_histories  # The rest of the items are the portfolio

    return portfolio_data, benchmark_data, weights