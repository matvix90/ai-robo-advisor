import numpy as np
import pandas as pd


def calculate_performance_metrics(
    price_series: pd.Series, risk_free_rate: float = 0.02
) -> dict:
    """
    Calculates absolute performance metrics for a given price series.

    Args:
        price_series (pd.Series): A pandas Series of prices, indexed by date.
        risk_free_rate (float): The annual risk-free rate.

    Returns:
        dict: A dictionary of performance metrics.
    """
    if price_series.empty or len(price_series) < 2:
        raise ValueError("Price series must contain at least 2 data points")

    # Validate price series contains only positive values
    if (price_series <= 0).any():
        raise ValueError("Price series must contain only positive values")

    # Cumulative Return
    cumulative_return = (price_series.iloc[-1] / price_series.iloc[0]) - 1

    # CAGR
    num_days = (price_series.index[-1] - price_series.index[0]).days
    if num_days <= 0:
        raise ValueError("Price series must span more than 0 days")

    cagr = (1 + cumulative_return) ** (365.0 / num_days) - 1

    # Daily Returns and Volatility
    daily_returns = price_series.pct_change().dropna()
    if daily_returns.empty:
        raise ValueError("Unable to calculate daily returns from price series")

    annualized_volatility = daily_returns.std() * np.sqrt(252)

    # Max Drawdown
    cum_returns = (1 + daily_returns).cumprod()
    peak = cum_returns.cummax()
    drawdown = (cum_returns - peak) / peak
    max_drawdown = drawdown.min()

    # Sharpe Ratio
    annualized_return = (1 + daily_returns.mean()) ** 252 - 1
    if annualized_volatility == 0:
        raise ValueError("Cannot calculate Sharpe ratio: volatility is zero")

    sharpe_ratio = (annualized_return - risk_free_rate) / annualized_volatility

    return {
        "Cumulative Return": round(cumulative_return, 4),
        "CAGR": round(cagr, 4),
        "Annualized Volatility": round(annualized_volatility, 4),
        "Max Drawdown": round(max_drawdown, 4),
        "Sharpe Ratio": round(sharpe_ratio, 4),
    }


def calculate_relative_metrics(
    asset_returns: pd.Series, benchmark_returns: pd.Series, risk_free_rate: float = 0.02
) -> dict:
    """
    Calculates Alpha and Beta relative to a benchmark.

    Args:
        asset_returns (pd.Series): Daily returns of the asset (ticker or portfolio).
        benchmark_returns (pd.Series): Daily returns of the benchmark.
        risk_free_rate (float): The annual risk-free rate.

    Returns:
        dict: A dictionary containing Alpha and Beta.
    """
    # Align returns and drop any non-overlapping dates
    df = pd.DataFrame({"asset": asset_returns, "benchmark": benchmark_returns}).dropna()
    if len(df) < 2:
        raise ValueError(
            "Insufficient overlapping data between asset and benchmark returns"
        )

    # Beta
    covariance = df["asset"].cov(df["benchmark"])
    benchmark_variance = df["benchmark"].var()
    if benchmark_variance == 0:
        raise ValueError("Cannot calculate Beta: benchmark variance is zero")

    beta = covariance / benchmark_variance

    # Alpha
    asset_annual_return = (1 + df["asset"].mean()) ** 252 - 1
    benchmark_annual_return = (1 + df["benchmark"].mean()) ** 252 - 1
    expected_return = risk_free_rate + beta * (benchmark_annual_return - risk_free_rate)
    alpha = asset_annual_return - expected_return

    return {
        "Alpha": round(alpha, 4),
        "Beta": round(beta, 4),
    }


def analyze_portfolio(
    tickers_data: dict,
    benchmark_data: list,
    weights: dict = None,
    risk_free_rate: float = 0.02,
) -> dict:
    """
    Performs a comprehensive analysis of a portfolio against a benchmark.

    Args:
        tickers_data (dict): {ticker: list of OHLCV dicts}.
        benchmark_data (list): List of OHLCV dicts for the benchmark.
        weights (dict, optional): {ticker: weight}. Defaults to equal weights.
        risk_free_rate (float, optional): Annual risk-free rate.

    Returns:
        dict: A nested dictionary with metrics for tickers, the portfolio, and the benchmark.
    """
    if not tickers_data:
        raise ValueError("tickers_data cannot be empty")

    if not benchmark_data:
        raise ValueError("benchmark_data cannot be empty")

    # 1. Prepare DataFrames
    all_prices = {}
    try:
        for ticker, data in tickers_data.items():
            if not data:
                raise ValueError(f"No data provided for ticker: {ticker}")

            df = pd.DataFrame(data).set_index(
                pd.to_datetime(pd.DataFrame(data)["date"])
            )
            if "close" not in df.columns:
                raise ValueError(f"Missing 'close' column for ticker: {ticker}")

            all_prices[ticker] = df["close"]

        benchmark_df = pd.DataFrame(benchmark_data).set_index(
            pd.to_datetime(pd.DataFrame(benchmark_data)["date"])
        )
        if "close" not in benchmark_df.columns:
            raise ValueError("Missing 'close' column in benchmark data")

        all_prices["benchmark"] = benchmark_df["close"]
    except (KeyError, ValueError) as e:
        raise ValueError(f"Error processing input data: {e!s}")

    # Align all prices, forward-fill missing values, then drop any remaining NaNs
    prices_df = pd.DataFrame(all_prices).ffill().dropna()

    if prices_df.empty:
        raise ValueError("No overlapping data found for the given assets and benchmark")

    benchmark_prices = prices_df["benchmark"]
    ticker_prices = prices_df.drop(columns=["benchmark"])

    # 2. Calculate Returns
    returns_df = prices_df.pct_change().dropna()
    if returns_df.empty:
        raise ValueError("Unable to calculate returns from price data")

    benchmark_returns = returns_df["benchmark"]
    ticker_returns = returns_df.drop(columns=["benchmark"])

    # 3. Analyze Benchmark
    analysis_results = {
        "benchmark": calculate_performance_metrics(benchmark_prices, risk_free_rate)
    }

    # 4. Analyze Individual Tickers
    analysis_results["tickers"] = {}
    for ticker in ticker_prices.columns:
        try:
            perf_metrics = calculate_performance_metrics(
                ticker_prices[ticker], risk_free_rate
            )
            rel_metrics = calculate_relative_metrics(
                ticker_returns[ticker], benchmark_returns, risk_free_rate
            )
            analysis_results["tickers"][ticker] = {**perf_metrics, **rel_metrics}
        except ValueError as e:
            raise ValueError(f"Error analyzing ticker {ticker}: {e!s}")

    # 5. Analyze Portfolio
    # Normalize weights
    if weights is None:
        num_tickers = len(ticker_prices.columns)
        weights_array = np.array([1 / num_tickers] * num_tickers)
    else:
        weights_array = np.array([weights.get(t, 0) for t in ticker_prices.columns])
        if weights_array.sum() == 0:
            raise ValueError("Portfolio weights sum to zero")
        weights_array /= weights_array.sum()  # Ensure they sum to 1

    portfolio_returns = ticker_returns.dot(weights_array)

    # Create a synthetic price series for the portfolio to calculate metrics
    portfolio_prices = (
        1 + portfolio_returns
    ).cumprod() * 100  # Start at 100 for simplicity

    try:
        portfolio_perf_metrics = calculate_performance_metrics(
            portfolio_prices, risk_free_rate
        )
        portfolio_rel_metrics = calculate_relative_metrics(
            portfolio_returns, benchmark_returns, risk_free_rate
        )
        analysis_results["portfolio"] = {
            **portfolio_perf_metrics,
            **portfolio_rel_metrics,
        }
    except ValueError as e:
        raise ValueError(f"Error analyzing portfolio: {e!s}")

    return analysis_results
