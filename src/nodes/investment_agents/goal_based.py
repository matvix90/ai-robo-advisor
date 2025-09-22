from graph.state import State
from data.models import InvestmentAgent


# === Agents ===
def investment_strategy(state:State) -> State:
    """
    Collect user investment preferences through interactive questionnaire and 
    generate investment strategy based on user preferences.

    """
    print("Generating investment strategy based on user preferences...\n")
    
    llm = state["metadata"]["investment_llm_agent"]

    portfolio_preferences = state["data"]['investment']['user_preferences']

    prompt = f"""Create a comprehensive investment strategy based on the following user preferences:

        USER PREFERENCES:
        - Investment Goal: {portfolio_preferences.goal}
        - Risk Profile: {portfolio_preferences.risk_profile}
        - Investment Horizon: {portfolio_preferences.investment_horizon}
        - Currency: {portfolio_preferences.currency}
        - Preferred Stock Exchange: {portfolio_preferences.stock_exchange}
        - Initial Investment: {portfolio_preferences.initial_investment:,.2f}

        REQUIREMENTS:
        Create a complete InvestmentAgent object with a strategy and reasoning.

        1. STRATEGY: A complete Strategy object with:
            - STRATEGY NAME: A descriptive name reflecting the user's goals and risk profile
            - DESCRIPTION: Brief explanation of the investment approach
            - ASSET ALLOCATION: Specific percentages for each asset class (must sum to 100%)
                - Stocks, Bonds, Real Estate, Commodities, Cryptocurrency, Cash
            - GEOGRAPHICAL DIVERSIFICATION: Regional allocation with specific weights
            - SECTOR DIVERSIFICATION: Sector allocation based on risk profile and goals
            - STOCK EXCHANGE: Specify the stock exchange where the ETFs have to be quoted ({portfolio_preferences.stock_exchange})
            - RISK TOLERANCE: Align with user's stated risk profile ({portfolio_preferences.risk_profile})
            - TIME HORIZON: Match user's investment timeline ({portfolio_preferences.investment_horizon})
            - EXPECTED RETURNS: Realistic return expectations based on allocation and risk

        2. REASONING: Provide a step-by-step explanation for the generated strategy. 
        Justify the choices made for asset allocation, diversification, and other key parameters based on the user's preferences.

        GUIDELINES:
        - the strategy must be tailored to achieve the investor's goal: {portfolio_preferences.goal}
        - Consider the investment amount ({portfolio_preferences.initial_investment:,.2f} {portfolio_preferences.currency}) for practical allocation
        - Ensure all percentages are realistic and sum to 100%"""

    analyst = {"name": "Self-Directed Investor", "description": "Investor who prefers to make their own investment decisions based on personal research and preferences."}

    response = llm.with_structured_output(InvestmentAgent).invoke(prompt)

    if state["metadata"]["show_reasoning"]:
        print(response.reasoning)

    state["data"]['investment']['strategy'] = response.strategy
    state["data"]['investment']['analyst'] = analyst

    return state