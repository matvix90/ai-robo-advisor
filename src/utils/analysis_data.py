from tools.polygon_api import fetch_histories_concurrently, get_two_year_ago_date, get_today_date
from data.models import Portfolio
from typing import Tuple, Dict, List, Optional


class DataQualityWarning:
    """Represents a warning about data quality issues."""
    def __init__(self, message: str, missing_tickers: List[str] = None):
        self.message = message
        self.missing_tickers = missing_tickers or []


def all_data(
    portfolio: Portfolio, 
    benchmark_ticker: str,
    allow_partial: bool = True
) -> Tuple[Dict, Dict, Dict, Optional[DataQualityWarning]]:
    """ Fetch historical data for all portfolio tickers and the benchmark ticker concurrently.

    Args:
        portfolio (Portfolio): The portfolio containing holdings with symbols and weights.
        benchmark_ticker (str): The benchmark ticker symbol.
        allow_partial (bool): If True, returns partial data when some tickers fail.
                             If False, raises error if any ticker fails.

    Returns:
        tuple: A tuple containing four elements:
            - portfolio_data: A dictionary where keys are portfolio ticker symbols and values are their historical data.
            - benchmark_data: A dictionary containing the historical data for the benchmark ticker.
            - weights: A dictionary containing the weights of the portfolio tickers (normalized if partial data).
            - warning: DataQualityWarning object if there are issues, None otherwise.
    
    Raises:
        ValueError: If portfolio is invalid, has no holdings, or critical data fetching fails.
        TypeError: If portfolio is not a Portfolio instance.
    """
    
    # Validate inputs - check type name to avoid import path issues
    if not hasattr(portfolio, '__class__') or type(portfolio).__name__ != 'Portfolio':
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

    # Fetch all data concurrently with retry mechanism
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
        raise ValueError("No historical data was retrieved for any ticker")
    
    # Check benchmark data first - this is critical
    if benchmark_ticker not in all_histories:
        # Try common benchmark alternatives
        benchmark_alternatives = {
            'ACWI': ['SPY', 'VT'],
            'SPY': ['VOO', 'IVV'],
            'VT': ['ACWI', 'VTI'],
        }
        
        fallback_ticker = None
        if benchmark_ticker in benchmark_alternatives:
            for alt in benchmark_alternatives[benchmark_ticker]:
                if alt in all_histories:
                    fallback_ticker = alt
                    break
        
        if not fallback_ticker:
            raise ValueError(
                f"Failed to fetch data for benchmark ticker: {benchmark_ticker}. "
                f"Unable to proceed with analysis without benchmark data."
            )
        
        # Use fallback
        benchmark_data = all_histories.pop(fallback_ticker)
        warning_message = f"Using {fallback_ticker} as fallback for benchmark {benchmark_ticker}"
    else:
        benchmark_data = all_histories.pop(benchmark_ticker)
        warning_message = None

    # Check portfolio tickers
    missing_tickers = [ticker for ticker in portfolio_tickers if ticker not in all_histories]
    available_tickers = [ticker for ticker in portfolio_tickers if ticker in all_histories]
    
    if missing_tickers:
        if not allow_partial or not available_tickers:
            # If we don't allow partial data or have no available tickers at all
            raise ValueError(
                f"Failed to fetch data for portfolio tickers: {missing_tickers}. "
                f"Analysis cannot proceed without sufficient portfolio data."
            )
        
        # Adjust weights for available tickers only
        adjusted_weights = {ticker: weights[ticker] for ticker in available_tickers}
        
        # Normalize the weights to sum to the original total
        available_weight_sum = sum(adjusted_weights.values())
        if available_weight_sum <= 0:
            raise ValueError("Remaining portfolio tickers have zero or negative weights")
        
        # Create normalized weights
        scale_factor = total_weight / available_weight_sum
        weights = {ticker: weight * scale_factor for ticker, weight in adjusted_weights.items()}
        
        warning_message = (
            f"Partial data: missing {len(missing_tickers)} of {len(portfolio_tickers)} holdings "
            f"({', '.join(missing_tickers)}). Weights have been adjusted for remaining holdings."
        )

    # Validate that we have sufficient data for each ticker
    insufficient_data_tickers = []
    for ticker, data in all_histories.items():
        if not data or len(data) < 2:
            insufficient_data_tickers.append(ticker)
    
    if insufficient_data_tickers:
        if not allow_partial:
            raise ValueError(
                f"Insufficient data for tickers: {insufficient_data_tickers}. "
                f"Each ticker needs at least 2 data points."
            )
        
        # Remove tickers with insufficient data
        for ticker in insufficient_data_tickers:
            all_histories.pop(ticker, None)
            weights.pop(ticker, None)
        
        if not all_histories:
            raise ValueError("No tickers with sufficient data remain after validation")
        
        # Renormalize weights
        remaining_weight = sum(weights.values())
        if remaining_weight > 0:
            weights = {ticker: (weight / remaining_weight) * total_weight 
                      for ticker, weight in weights.items()}
        
        if warning_message:
            warning_message += f" Additionally, {len(insufficient_data_tickers)} ticker(s) had insufficient data."
        else:
            warning_message = f"Removed {len(insufficient_data_tickers)} ticker(s) with insufficient data."

    # Validate benchmark has sufficient data
    if not benchmark_data or len(benchmark_data) < 2:
        raise ValueError(
            f"Insufficient data for benchmark: need at least 2 data points, got {len(benchmark_data) if benchmark_data else 0}"
        )

    portfolio_data = all_histories
    
    # Create warning object if there were any issues
    data_warning = None
    if warning_message:
        all_missing = missing_tickers + insufficient_data_tickers
        data_warning = DataQualityWarning(warning_message, all_missing)

    return portfolio_data, benchmark_data, weights, data_warning