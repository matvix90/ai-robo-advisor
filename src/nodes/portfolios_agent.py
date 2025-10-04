from graph.state import State
from data.models import PortfolioAgent
from typing import Dict, Any
import logging
from utils.alphavantage import get_time_series_daily_adjusted, get_overview

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

def create_portfolio(state:State) -> State:
    """
    Create a diversified ETF-based portfolio based on the provided investment strategy.
    """
    print("Creating portfolio based on investment strategy...\n")

    llm = state["metadata"]["portfolio_llm_agent"]
    strategy = state["data"]['investment']['strategy']
    analyst = state["data"]['investment']['analyst']

    prompt = f"""You are an expert financial portfolio manager tasked with creating an ETF-based portfolio 
    that strictly adheres to a given investment strategy. Your investment style should emulate that of {analyst["name"]}.

        INVESTMENT STRATEGY TO IMPLEMENT:
        {strategy}

        PORTFOLIO CONSTRUCTION REQUIREMENTS:
        Based on the strategy above, construct a complete `PortfolioAgent` object containing the portfolio (`data`) and your `reasoning`.

        1. PORTFOLIO (`data`):
            - **Name**: A descriptive name for the portfolio that reflects the strategy and the analyst's style.
            - **Holdings**: A list of 2 to 4 ETFs. Each holding must include:
                - `symbol`: The correct ETF ticker symbol quoted on the {strategy.stock_exchange}.
                - `name`: The full name of the ETF.
                - `isin`: The ISIN for the ETF.
                - `asset_class`: The primary asset class of the ETF (e.g., 'Stocks', 'Bonds').
                - `weight`: The percentage of the portfolio allocated to this ETF.

        2. REASONING (`reasoning`):
            - Provide a clear, step-by-step explanation for your portfolio construction.
            - Justify the selection of each specific ETF, 
            explaining how it helps achieve the target asset allocation, geographical, and sector diversification.
            - Explain how the chosen ETFs align with the strategy's risk tolerance, time horizon, 
            and the investment philosophy of {analyst["name"]}.

        STRICT GUIDELINES & CONSTRAINTS:
        - **ETF Only**: The portfolio must consist exclusively of ETFs.
        - **Stock Exchange**: All selected ETFs must be traded on the {strategy.stock_exchange}.
        - **Accurate Allocation**: The combined weights of the ETFs must precisely match the asset, geographical, 
        and sector allocations defined in the strategy.
        - **Weight Sum**: The sum of all holding weights must equal exactly 100%.
        - **ETF Quality**: Choose well-established, highly liquid ETFs with low expense ratios.
        - **Limited Holdings**: The portfolio must contain a maximum of 4 ETFs."""

    response = llm.with_structured_output(PortfolioAgent).invoke(prompt)

    if state["metadata"]["show_reasoning"]:
        print(response.reasoning)

    portfolio = response.portfolio
    portfolio.strategy = strategy

 # Initialize market_data container
    portfolio.market_data = {}  # type: Dict[str, Dict[str, Any]]

    # Try to fetch overview + time series for each holding's symbol
    holdings = getattr(portfolio, "holdings", []) or []
    for h in holdings:
        symbol = h.get("symbol")
        if not symbol:
            continue
        try:
            # Attempt to fetch overview and time series. Use compact by default (faster).
            overview = get_overview(symbol, cache=True)
            ts = get_time_series_daily_adjusted(symbol, outputsize="compact", cache=True)
            portfolio.market_data[symbol] = {
                "overview": overview.get("overview") if isinstance(overview, dict) else overview,
                "time_series": ts.get("time_series") if isinstance(ts, dict) else ts,
                "_raw_overview": overview.get("_raw") if isinstance(overview, dict) else overview,
                "_raw_time_series": ts.get("_raw") if isinstance(ts, dict) else ts,
            }
            # Also attach quick fields onto the holding for convenience
            # (non-destructive; only if keys not present)
            if "name" not in h and overview and isinstance(overview, dict):
                # overview may be the structure returned by the helper
                ov = overview.get("overview") if "overview" in overview else overview
                if isinstance(ov, dict):
                    h.setdefault("name", ov.get("Name") or ov.get("name"))
            # try to extract ISIN if available in overview
            if "isin" not in h and overview and isinstance(overview, dict):
                ov = overview.get("overview") if "overview" in overview else overview
                if isinstance(ov, dict):
                    h.setdefault("isin", ov.get("ISIN"))
        except Exception as e:
            logger.exception("Failed to fetch market data for %s: %s", symbol, e)
            portfolio.market_data[symbol] = {"error": str(e)}

    state["data"]['portfolio'] = portfolio

    return state