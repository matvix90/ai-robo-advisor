# from graph.state import State
# from data.models import PortfolioAgent


# def create_portfolio(state:State) -> State:
#     """
#     Create a diversified ETF-based portfolio based on the provided investment strategy.
#     """
#     print("Creating portfolio based on investment strategy...\n")

#     llm = state["metadata"]["portfolio_llm_agent"]
#     strategy = state["data"]['investment']['strategy']
#     analyst = state["data"]['investment']['analyst']

#     prompt = f"""You are an expert financial portfolio manager tasked with creating an ETF-based portfolio 
#     that strictly adheres to a given investment strategy. Your investment style should emulate that of {analyst["name"]}.

#         INVESTMENT STRATEGY TO IMPLEMENT:
#         {strategy}

#         PORTFOLIO CONSTRUCTION REQUIREMENTS:
#         Based on the strategy above, construct a complete `PortfolioAgent` object containing the portfolio (`data`) and your `reasoning`.

#         1. PORTFOLIO (`data`):
#             - **Name**: A descriptive name for the portfolio that reflects the strategy and the analyst's style.
#             - **Holdings**: A list of 2 to 4 ETFs. Each holding must include:
#                 - `symbol`: The correct ETF ticker symbol quoted on the {strategy.stock_exchange}.
#                 - `name`: The full name of the ETF.
#                 - `isin`: The ISIN for the ETF.
#                 - `asset_class`: The primary asset class of the ETF (e.g., 'Stocks', 'Bonds').
#                 - `weight`: The percentage of the portfolio allocated to this ETF.

#         2. REASONING (`reasoning`):
#             - Provide a clear, step-by-step explanation for your portfolio construction.
#             - Justify the selection of each specific ETF, 
#             explaining how it helps achieve the target asset allocation, geographical, and sector diversification.
#             - Explain how the chosen ETFs align with the strategy's risk tolerance, time horizon, 
#             and the investment philosophy of {analyst["name"]}.

#         STRICT GUIDELINES & CONSTRAINTS:
#         - **ETF Only**: The portfolio must consist exclusively of ETFs.
#         - **Stock Exchange**: All selected ETFs must be traded on the {strategy.stock_exchange}.
#         - **Accurate Allocation**: The combined weights of the ETFs must precisely match the asset, geographical, 
#         and sector allocations defined in the strategy.
#         - **Weight Sum**: The sum of all holding weights must equal exactly 100%.
#         - **ETF Quality**: Choose well-established, highly liquid ETFs with low expense ratios.
#         - **Limited Holdings**: The portfolio must contain a maximum of 4 ETFs."""

#     response = llm.with_structured_output(PortfolioAgent).invoke(prompt)

#     if state["metadata"]["show_reasoning"]:
#         print(response.reasoning)

#     portfolio = response.portfolio
#     portfolio.strategy = strategy

#     state["data"]['portfolio'] = portfolio

#     return state


from typing import Any, Dict, List, Optional
import logging

from graph.state import State
from data.models import PortfolioAgent
from tools.yf_data_provider import get_etf_data, is_european_ticker

logger = logging.getLogger(__name__)


# Map common exchange identifiers (strategy.stock_exchange) -> ticker suffix used on Yahoo
EXCHANGE_TO_SUFFIX = {
    "LSE": ".L",
    "LONDON": ".L",
    "XETRA": ".DE",
    "DE": ".DE",
    "EURONEXT": ".PA",  # default to Paris listing suffix; Euronext uses many country suffixes
    "PARIS": ".PA",
    "SIX": ".SW",
    "SWISS": ".SW",
    "AMSTERDAM": ".AS",
    "MILAN": ".MI",
    "MI": ".MI",
    "OSLO": ".OL",
    "BRUSSELS": ".BE",
    "VIENNA": ".AT",
    "HELSINKI": ".HE",
    "STOCKHOLM": ".ST",
}


def _get_field(obj: Any, name: str) -> Any:
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj.get(name)
    return getattr(obj, name, None)


def _set_field(obj: Any, name: str, value: Any) -> None:
    if isinstance(obj, dict):
        obj[name] = value
    else:
        try:
            setattr(obj, name, value)
        except Exception:
            # last resort for frozen objects: ignore
            pass


def _parse_weight(raw: Any) -> Optional[float]:
    """
    Normalize weight into percentage number (0..100).
    Accepts strings like '40%', decimals like 0.4 or 40, or numeric types.
    Returns None if can't parse.
    """
    if raw is None:
        return None
    try:
        if isinstance(raw, str):
            s = raw.strip()
            if s.endswith("%"):
                return float(s[:-1])
            f = float(s)
            if 0 < f <= 1:
                return f * 100.0
            return f
        if isinstance(raw, (int, float)):
            f = float(raw)
            if 0 < f <= 1:
                return f * 100.0
            return f
    except Exception:
        return None
    return None


def _normalize_weights(holdings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ensure weights sum to exactly 100. If some weights missing, distribute equally.
    Round to 2 decimals and adjust last to make sum exactly 100.
    """
    parsed = []
    for h in holdings:
        w = _parse_weight(h.get("weight"))
        parsed.append(w)

    # count known weights
    known_indices = [i for i, w in enumerate(parsed) if w is not None]
    unknown_indices = [i for i, w in enumerate(parsed) if w is None]

    if not holdings:
        return holdings

    if not known_indices:
        # Give equal weights
        equal = round(100.0 / len(holdings), 2)
        for i, h in enumerate(holdings):
            h["weight"] = equal
        # adjust last
        total = equal * len(holdings)
        diff = round(100.0 - total, 2)
        holdings[-1]["weight"] = round(holdings[-1]["weight"] + diff, 2)
        return holdings

    total_known = sum(parsed[i] for i in known_indices)
    # If some unknown, allocate remaining equally among unknowns
    remaining = max(0.0, 100.0 - total_known)
    if unknown_indices:
        per_unknown = remaining / len(unknown_indices)
        for i in unknown_indices:
            holdings[i]["weight"] = round(per_unknown, 2)
    else:
        # All known — scale proportionally if not exactly 100
        if abs(total_known - 100.0) > 1e-6:
            scale = 100.0 / total_known
            for i in known_indices:
                holdings[i]["weight"] = round(parsed[i] * scale, 2)

    # Final adjustment to ensure sum exactly 100
    total = sum(_parse_weight(h["weight"]) for h in holdings)
    total = round(total, 2)
    diff = round(100.0 - total, 2)
    if abs(diff) >= 0.01:
        # apply diff to the largest-weight holding
        max_idx = max(range(len(holdings)), key=lambda i: _parse_weight(holdings[i]["weight"]) or 0)
        holdings[max_idx]["weight"] = round((_parse_weight(holdings[max_idx]["weight"]) or 0) + diff, 2)

    # Ensure weights are numeric floats
    for h in holdings:
        h["weight"] = float(_parse_weight(h["weight"]) if _parse_weight(h["weight"]) is not None else 0.0)

    return holdings


def create_portfolio(state: State) -> State:
    """
    Create a diversified ETF-based portfolio based on the provided investment strategy.
    Uses the LLM to construct a candidate portfolio, then validates and enriches holdings
    using tools.data_provider (yfinance) for European ETF support.
    """
    print("Creating portfolio based on investment strategy...\n")

    llm = state["metadata"]["portfolio_llm_agent"]
    strategy = state["data"]["investment"]["strategy"]
    analyst = state["data"]["investment"]["analyst"]

    # Build LLM prompt (keeps your original instructions)
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

    # Ask the LLM for a structured PortfolioAgent output
    response = llm.with_structured_output(PortfolioAgent).invoke(prompt)

    if state["metadata"].get("show_reasoning"):
        print(response.reasoning)

    portfolio = response.portfolio
    # Attach strategy for downstream agents
    try:
        portfolio.strategy = strategy
    except Exception:
        # If portfolio is dict-like
        if isinstance(portfolio, dict):
            portfolio["strategy"] = strategy

    # Validate & enrich holdings using data_provider
    raw_holdings = _get_field(portfolio, "holdings") or []
    enriched_holdings: List[Dict[str, Any]] = []
    validation_details = []
    all_valid = True

    # Determine expected suffix from strategy.stock_exchange if possible
    exchange_key = (getattr(strategy, "stock_exchange", None) or "").strip().upper()
    expected_suffix = EXCHANGE_TO_SUFFIX.get(exchange_key)

    for raw in raw_holdings:
        # Support holdings as dicts or simple objects
        symbol = _get_field(raw, "symbol") or _get_field(raw, "ticker")
        name = _get_field(raw, "name")
        isin = _get_field(raw, "isin")
        asset_class = _get_field(raw, "asset_class") or _get_field(raw, "assetClass")
        weight = _parse_weight(_get_field(raw, "weight"))

        hold_report = {"symbol": symbol, "issues": []}

        etf_data = None
        if symbol:
            try:
                etf_data = get_etf_data(symbol)
            except Exception as e:
                logger.exception("Error fetching ETF data for %s: %s", symbol, e)
                hold_report["issues"].append("failed_to_fetch_data")

        # If LLM provided no symbol but provided name, we cannot reliably resolve — mark issue
        if not symbol:
            hold_report["issues"].append("missing_symbol")
            all_valid = False

        # If we have etf_data, prefer issuer data to fill missing fields
        resolved_name = name or (etf_data.get("name") if etf_data else None)
        resolved_isin = isin or (etf_data.get("info", {}).get("isin") if etf_data else None)
        resolved_asset_class = asset_class or (etf_data.get("quoteType") if etf_data else None)
        resolved_exchange = etf_data.get("exchange") if etf_data else None
        resolved_currency = etf_data.get("currency") if etf_data else None
        resolved_ter = etf_data.get("ter") if etf_data else None

        # Validate exchange / suffix when known
        if expected_suffix and symbol:
            if not str(symbol).upper().endswith(expected_suffix):
                # If etf_data present, check if exchange string matches the expected key (loose)
                if etf_data and resolved_exchange:
                    if exchange_key not in str(resolved_exchange).upper() and expected_suffix not in str(symbol).upper():
                        hold_report["issues"].append(f"expected_exchange_suffix_{expected_suffix}_mismatch")
                        all_valid = False
                else:
                    hold_report["issues"].append(f"ticker_suffix_mismatch_expected_{expected_suffix}")
                    all_valid = False

        # Check if symbol corresponds to a European listing when strategy requested European exchange
        if exchange_key and exchange_key in ("LSE", "LONDON", "XETRA", "DE", "EURONEXT", "PARIS", "SIX", "SWISS"):
            if symbol and not is_european_ticker(symbol):
                # If data suggests it's European but symbol not suffixed, still accept but warn
                hold_report["issues"].append("symbol_may_not_be_exchange_specific")
                # Do not fail hard; just warn

        enriched = {
            "symbol": symbol,
            "name": resolved_name,
            "isin": resolved_isin,
            "asset_class": resolved_asset_class,
            "weight": weight,
            "exchange": resolved_exchange,
            "currency": resolved_currency,
            "ter": round(resolved_ter, 6) if isinstance(resolved_ter, (int, float)) else None,
        }

        enriched_holdings.append(enriched)
        validation_details.append(hold_report)

    # Normalize weights so they sum to exactly 100%
    enriched_holdings = _normalize_weights(enriched_holdings)

    # Recompute validation details with parsed weights
    for i, h in enumerate(enriched_holdings):
        validation_details[i]["weight"] = h.get("weight")
        if h.get("weight") is None:
            validation_details[i]["issues"].append("weight_missing_or_unparseable")
            all_valid = False

    # Save enriched holdings back into portfolio object/dict
    try:
        setattr(portfolio, "holdings", enriched_holdings)
    except Exception:
        if isinstance(portfolio, dict):
            portfolio["holdings"] = enriched_holdings

    # Attach a small validation report to state for transparency
    state["data"]["portfolio_validation"] = {
        "all_holdings_valid": all_valid,
        "details": validation_details,
        "expected_exchange_suffix": expected_suffix,
    }

    # Persist portfolio in state (overwrite)
    state["data"]["portfolio"] = portfolio

    return state
