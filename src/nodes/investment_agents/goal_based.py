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

        USER PROFILE:
        - Age: {portfolio_preferences.age} years
        - Investment Knowledge: {portfolio_preferences.investment_knowledge.value}
        - Income Level: {portfolio_preferences.income_level.value}
        - Emergency Fund: {"Yes" if portfolio_preferences.has_emergency_fund else "No"}
        
        INVESTMENT GOALS & TIMELINE:
        - Primary Goal: {portfolio_preferences.goal.value}
        - Investment Purpose: {portfolio_preferences.investment_purpose.value}
        - Investment Horizon: {portfolio_preferences.investment_horizon.value}
        - Liquidity Need: {portfolio_preferences.liquidity_need.value}
        
        RISK ASSESSMENT:
        - Risk Profile: {portfolio_preferences.risk_profile.value}
        - Max Acceptable Loss: {portfolio_preferences.max_acceptable_loss}%
        - Market Downturn Reaction: {portfolio_preferences.market_downturn_reaction.value}
        - Investment Priority: {portfolio_preferences.investment_priority.value}
        
        FINANCIAL SITUATION:
        - Initial Investment: {portfolio_preferences.initial_investment:,.2f} {portfolio_preferences.currency.value}
        - Monthly Contribution: {portfolio_preferences.monthly_contribution:,.2f} {portfolio_preferences.currency.value}
        - Other Investments: {portfolio_preferences.other_investments:,.2f} {portfolio_preferences.currency.value}
        - Total Investable Assets: {portfolio_preferences.initial_investment + portfolio_preferences.other_investments:,.2f} {portfolio_preferences.currency.value}
        
        PREFERENCES:
        - Currency: {portfolio_preferences.currency.value}
        - Preferred Stock Exchange: {portfolio_preferences.stock_exchange.value}

        REQUIREMENTS:
        Create a complete InvestmentAgent object with a strategy and reasoning that considers ALL the user information above.

        1. STRATEGY: A complete Strategy object with:
            - STRATEGY NAME: A descriptive name reflecting the user's goals, age, risk profile, and investment purpose
            - DESCRIPTION: Detailed explanation of the investment approach considering:
                * User's age and investment knowledge level
                * Emergency fund status and overall financial stability
                * Investment purpose and liquidity needs
                * Risk tolerance and behavioral factors (market downturn reaction)
                * Monthly contributions for dollar-cost averaging strategy
            
            - ASSET ALLOCATION: Specific percentages for each asset class (must sum to 100%)
                * Stocks, Bonds, Real Estate, Commodities, Cryptocurrency, Cash
                * Consider age-based allocation (younger = more growth-oriented)
                * Factor in liquidity needs and investment horizon
                * Adjust based on emergency fund status and other investments
                * Account for income level and monthly contribution capacity
            
            - GEOGRAPHICAL DIVERSIFICATION: Regional allocation with specific weights
                * Consider home country bias based on stock exchange preference
                * Balance domestic and international exposure
                * Factor in investment knowledge level (simpler for beginners)
            
            - SECTOR DIVERSIFICATION: Sector allocation based on risk profile and goals
                * Align sector weights with investment purpose
                * Consider economic cycle positioning
                * Factor in user's priority (stability, income, balanced, growth)
            
            - STOCK EXCHANGE: Specify the stock exchange where the ETFs have to be quoted ({portfolio_preferences.stock_exchange.value})
            - RISK TOLERANCE: Align with user's stated risk profile ({portfolio_preferences.risk_profile.value})
            - TIME HORIZON: Match user's investment timeline ({portfolio_preferences.investment_horizon.value})
            - EXPECTED RETURNS: Realistic return expectations based on:
                * Asset allocation and risk level
                * Market conditions and historical data
                * User's age and investment horizon
                * Monthly contribution impact over time

        2. REASONING: Provide a comprehensive, step-by-step explanation for the generated strategy:
            - Explain how user's age influences the strategy
            - Justify how investment knowledge level affects portfolio complexity
            - Discuss how liquidity needs and emergency fund status shape asset allocation
            - Explain how market downturn reaction and max acceptable loss influence risk positioning
            - Detail how monthly contributions and investment horizon affect the strategy
            - Justify why this strategy aligns with their investment purpose and priority
            - Explain how income level and total investable assets inform the approach

        CRITICAL GUIDELINES:
        - The strategy must be tailored to achieve the investor's primary goal: {portfolio_preferences.goal.value}
        - Consider the user's age ({portfolio_preferences.age}) for appropriate risk-taking capacity
        - Match investment complexity to knowledge level ({portfolio_preferences.investment_knowledge.value})
        - Factor in liquidity needs ({portfolio_preferences.liquidity_need.value}) when allocating to less liquid assets
        - If no emergency fund, recommend a higher cash allocation for safety
        - Incorporate monthly contributions ({portfolio_preferences.monthly_contribution:,.2f}) into the long-term wealth-building plan
        - Consider the total investment context including other investments ({portfolio_preferences.other_investments:,.2f})
        - Ensure asset allocation reflects behavioral risk tolerance (max loss: {portfolio_preferences.max_acceptable_loss}%)
        - Align strategy with investment priority: {portfolio_preferences.investment_priority.value}
        - Ensure all percentages are realistic and sum to 100%"""

    analyst = {"name": "Self-Directed Investor", "description": "Investor who prefers to make their own investment decisions based on personal research and preferences."}

    response = llm.with_structured_output(InvestmentAgent).invoke(prompt)

    if state["metadata"]["show_reasoning"]:
        print(response.reasoning)

    state["data"]['investment']['strategy'] = response.strategy
    state["data"]['investment']['analyst'] = analyst

    return state