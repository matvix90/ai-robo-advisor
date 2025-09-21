from src.graph.state import State
from src.data.models import PortfolioAgent


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

    state["data"]['portfolio'] = portfolio

    return state