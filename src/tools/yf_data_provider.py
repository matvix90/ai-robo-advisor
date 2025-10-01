"""
src/tools/data_provider.py

Helper functions to fetch ETF metadata, prices and compute performance metrics
using yfinance. Designed to be imported by your analyst/investment agents.

Functions:
- is_european_ticker(ticker) -> bool
- get_etf_prices(ticker, period="5y") -> pd.Series (close prices)
- extract_ter_from_info(info) -> Optional[float]
- get_etf_data(ticker, period="5y") -> Dict[str, Any]
- compute_etf_metrics(prices, risk_free_rate=0.0, benchmark_prices=None) -> Dict[str, float]

Notes:
- Returns are annualized using ~252 trading days.
- Alpha/Beta computed vs provided benchmark_prices series if available.
"""
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
import logging

import pandas as pd
import numpy as np
import yfinance as yf

logger = logging.getLogger(__name__)

EUROPEAN_SUFFIXES = (
    ".L",  # London
    ".DE",  # XETRA (Germany)
    ".PA",  # Euronext Paris
    ".SW",  # SIX Swiss Exchange
    ".AS",  # Euronext Amsterdam
    ".MI",  # Borsa Italiana / Milan
    ".OL",  # Oslo
    ".BE",  # Euronext Brussels
    ".AT",  # Vienna
    ".FI",  # Helsinki
    ".HE",  # Helsinki alternative
    ".MC",  # Monaco / EURONEXT? (sometimes used)
    ".ST",  # Stockholm
)


def is_european_ticker(ticker: str) -> bool:
    """Rudimentary check whether a ticker looks like a European listing by suffix."""
    if not ticker:
        return False
    t = ticker.strip().upper()
    return any(t.endswith(suffix.upper()) for suffix in EUROPEAN_SUFFIXES)


def get_ticker_obj(ticker: str) -> yf.Ticker:
    """Return a yfinance Ticker object."""
    return yf.Ticker(ticker)


def get_etf_prices(ticker: str, period: str = "5y") -> Optional[pd.Series]:
    """
    Download historical close prices for ticker using yfinance.
    Returns a pandas Series of Close prices indexed by DatetimeIndex.
    If data cannot be retrieved, returns None.
    """
    try:
        tk = get_ticker_obj(ticker)
        hist = tk.history(period=period, auto_adjust=False)
        if hist is None or hist.empty:
            logger.warning("No historical data for %s (period=%s)", ticker, period)
            return None

        # Prefer 'Close' column; if not present, try first numeric column
        if "Close" in hist.columns:
            closes = hist["Close"].copy()
        else:
            # fallback: take the first numeric column
            numeric_cols = hist.select_dtypes(include="number").columns
            if len(numeric_cols) == 0:
                logger.warning("No numeric columns in history for %s", ticker)
                return None
            closes = hist[numeric_cols[0]].copy()

        closes.index = pd.to_datetime(closes.index)
        closes = closes.sort_index()
        return closes
    except Exception as e:
        logger.exception("Error fetching prices for %s: %s", ticker, e)
        return None


def extract_ter_from_info(info: Dict[str, Any]) -> Optional[float]:
    """
    Try common keys for TER/expense ratio in the yfinance info dict.
    Returns TER as decimal (e.g., 0.002 for 0.2%) or None if not found.
    """
    if not info:
        return None

    # Common keys observed in yfinance info payloads
    possible_keys = [
        "annualReportExpenseRatio",
        "expenseRatio",
        "fundExpenseRatio",
        "trailingAnnualExpenseRatio",
        "managementFee",  # sometimes present but not the TER
    ]
    for key in possible_keys:
        val = info.get(key)
        if val is None:
            continue
        try:
            # some values might already be decimal (0.002), others might be percent strings
            if isinstance(val, str):
                # strip percent if present
                v = val.strip().replace("%", "")
                v = float(v) / 100.0
            else:
                v = float(val)
            # sanity: reject unrealistic numbers > 1 (100%) unless original is percent string
            if 0 <= v <= 1:
                return v
            # if value looks like basis points or percent given as >1 (e.g., 0.2 given as 0.2 means 20%),
            # try to detect and correct common misformats:
            if v > 1 and v <= 100:
                # assume percent given without converting (e.g., 0.2 -> 20.0) -> treat as percent
                return v / 100.0
        except Exception:
            continue
    return None


def get_holdings_and_weights(ticker: str) -> Tuple[Optional[pd.DataFrame], Optional[Dict[str, float]]]:
    """
    Attempt to fetch a holdings DataFrame and/or sector/geography weights.
    yfinance has inconsistent keys across ETFs — this tries a couple of approaches.
    Returns tuple (holdings_df_or_None, weights_dict_or_None)
    """
    tk = get_ticker_obj(ticker)
    holdings = None
    weights = None
    try:
        # fund_holdings is a DataFrame in some yfinance versions
        if hasattr(tk, "fund_holdings"):
            try:
                fh = tk.fund_holdings
                if isinstance(fh, pd.DataFrame) and not fh.empty:
                    holdings = fh
            except Exception:
                pass
        # some info keys may contain sectors or geography mappings
        info = {}
        try:
            info = tk.info or {}
        except Exception:
            info = {}
        # Try common keys for sector/geography breakdowns
        for k in ("sectorWeightings", "sector_weights", "fundSectorWeightings", "sectorWeights", "fund_geography"):
            w = info.get(k)
            if isinstance(w, dict) and w:
                weights = w
                break
        # if holdings is still None, try to fetch from .get_holdings() if available
        if holdings is None and hasattr(tk, "get_holdings"):
            try:
                raw = tk.get_holdings()
                if isinstance(raw, pd.DataFrame) and not raw.empty:
                    holdings = raw
            except Exception:
                pass
    except Exception:
        logger.exception("Error fetching holdings for %s", ticker)

    return holdings, weights


def get_etf_data(ticker: str, period: str = "5y") -> Dict[str, Any]:
    """
    High-level helper that returns structured ETF data for the given ticker.

    Returned dict example:
    {
        "ticker": "CSPX.L",
        "is_european": True,
        "name": "iShares ...",
        "currency": "GBP",
        "ter": 0.0012,  # None if unknown
        "info": { ... }  # full yfinance info dict (may be large)
        "prices": pd.Series([...]) or None,
        "holdings": pd.DataFrame or None,
        "sector_weights": dict or None,
        "fetched_at": datetime.utcnow()
    }
    """
    tk = get_ticker_obj(ticker)
    out: Dict[str, Any] = {"ticker": ticker, "is_european": is_european_ticker(ticker)}
    out["fetched_at"] = datetime.utcnow()
    try:
        info = tk.info or {}
    except Exception:
        logger.exception("Error getting info for %s", ticker)
        info = {}
    out["info"] = info

    # basic metadata
    out["name"] = info.get("longName") or info.get("shortName") or info.get("name")
    out["currency"] = info.get("currency")
    out["quoteType"] = info.get("quoteType")
    out["exchange"] = info.get("exchange")

    # TER (try multiple keys)
    out["ter"] = extract_ter_from_info(info)

    # historical prices
    prices = get_etf_prices(ticker, period=period)
    out["prices"] = prices

    # holdings / weights if available
    holdings, sector_weights = get_holdings_and_weights(ticker)
    out["holdings"] = holdings
    out["sector_weights"] = sector_weights

    return out


def compute_etf_metrics(
    prices: pd.Series,
    risk_free_rate: float = 0.0,
    benchmark_prices: Optional[pd.Series] = None,
) -> Dict[str, Optional[float]]:
    """
    Compute performance metrics from a series of close prices.

    Inputs:
    - prices: pd.Series of close prices (DatetimeIndex, sorted ascending)
    - risk_free_rate: annual risk-free rate as decimal (e.g., 0.01 for 1%)
    - benchmark_prices: optional pd.Series of benchmark close prices to compute alpha & beta

    Returns a dict containing:
    - cagr, annual_volatility, sharpe, max_drawdown, alpha_annual, beta
    """
    if prices is None or prices.empty:
        return {
            "cagr": None,
            "annual_volatility": None,
            "sharpe": None,
            "max_drawdown": None,
            "alpha_annual": None,
            "beta": None,
        }

    # Ensure it's a Series
    if isinstance(prices, pd.DataFrame):
        if "Close" in prices.columns:
            series = prices["Close"].copy()
        else:
            series = prices.iloc[:, 0].copy()
    else:
        series = prices.copy()

    series = series.dropna().sort_index()
    if series.empty or len(series) < 2:
        logger.warning("Not enough price data to compute metrics.")
        return {
            "cagr": None,
            "annual_volatility": None,
            "sharpe": None,
            "max_drawdown": None,
            "alpha_annual": None,
            "beta": None,
        }

    # Years between first and last date (accurate calendar years)
    days = (series.index[-1] - series.index[0]).days
    years = days / 365.25 if days > 0 else 0.0

    # CAGR
    try:
        if years > 0:
            cagr = (series.iloc[-1] / series.iloc[0]) ** (1.0 / years) - 1.0
        else:
            cagr = None
    except Exception:
        cagr = None

    # Daily returns
    daily_returns = series.pct_change().dropna()
    if daily_returns.empty:
        return {
            "cagr": cagr,
            "annual_volatility": None,
            "sharpe": None,
            "max_drawdown": None,
            "alpha_annual": None,
            "beta": None,
        }

    trading_days = 252.0

    # Annualized volatility
    annual_volatility = float(daily_returns.std(ddof=0) * np.sqrt(trading_days))

    # Sharpe ratio (annualized) using excess return over risk-free
    rf_daily = risk_free_rate / trading_days
    excess_mean_daily = daily_returns.mean() - rf_daily
    try:
        sharpe = float((excess_mean_daily / daily_returns.std(ddof=0)) * np.sqrt(trading_days))
    except Exception:
        sharpe = None

    # Max Drawdown
    roll_max = series.cummax()
    drawdown = (series - roll_max) / roll_max
    max_drawdown = float(drawdown.min())

    # Alpha/Beta vs benchmark if provided
    alpha_annual = None
    beta = None
    if benchmark_prices is not None:
        # Align returns
        if isinstance(benchmark_prices, pd.DataFrame):
            if "Close" in benchmark_prices.columns:
                bench_series = benchmark_prices["Close"].copy()
            else:
                bench_series = benchmark_prices.iloc[:, 0].copy()
        else:
            bench_series = benchmark_prices.copy()
        bench_series = bench_series.dropna().sort_index()
        # Compute daily returns
        bench_daily = bench_series.pct_change().dropna()
        merged = pd.concat([daily_returns, bench_daily], axis=1, join="inner").dropna()
        if merged.shape[0] >= 2:
            y = merged.iloc[:, 0].values  # asset returns
            x = merged.iloc[:, 1].values  # benchmark returns
            # subtract rf_daily from both (excess returns)
            x_excess = x - rf_daily
            y_excess = y - rf_daily
            # Regression y_excess = alpha_daily + beta * x_excess
            try:
                beta_slope, alpha_intercept = np.polyfit(x_excess, y_excess, 1)
                beta = float(beta_slope)
                alpha_annual = float(alpha_intercept * trading_days)
            except Exception:
                beta = None
                alpha_annual = None

    return {
        "cagr": float(cagr) if cagr is not None else None,
        "annual_volatility": float(annual_volatility) if annual_volatility is not None else None,
        "sharpe": float(sharpe) if sharpe is not None else None,
        "max_drawdown": float(max_drawdown) if max_drawdown is not None else None,
        "alpha_annual": float(alpha_annual) if alpha_annual is not None else None,
        "beta": float(beta) if beta is not None else None,
    }


# Small usage example (for quick local manual testing):
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ticker = "CSPX.L"  # example London-listed UCITS ETF
    print("Is European:", is_european_ticker(ticker))
    data = get_etf_data(ticker)
    print("Name:", data.get("name"))
    print("Currency:", data.get("currency"))
    print("TER:", data.get("ter"))
    prices = data.get("prices")
    if prices is not None:
        metrics = compute_etf_metrics(prices)
        print("Metrics:", metrics)
    else:
        print("No prices returned.")
