from data.models import PortfolioAgent
from graph.state import State


def create_portfolio(state: State) -> State:
    """
    Create a diversified ETF-based portfolio based on the provided investment strategy.
    """
    print("Creating portfolio based on investment strategy...\n")

    llm = state["metadata"]["portfolio_llm_agent"]
    strategy = state["data"]["investment"]["strategy"]
    analyst = state["data"]["investment"]["analyst"]

    # Get user preferences if available (for enhanced prompting)
    user_preferences = state["data"]["investment"].get("user_preferences")

    # Build enhanced investor profile section if user preferences are available
    investor_profile_section = ""
    enhanced_selection_criteria = ""
    enhanced_reasoning_requirements = ""
    enhanced_goal_section = ""
    enhanced_constraints = ""

    if user_preferences:
        investor_profile_section = f"""
        INVESTOR PROFILE:
        - Age: {user_preferences.age} years
        - Investment Knowledge: {user_preferences.investment_knowledge.value}
        - Income Level: {user_preferences.income_level.value}
        - Investment Goal: {user_preferences.goal.value}
        - Investment Purpose: {user_preferences.investment_purpose.value}
        - Investment Horizon: {user_preferences.investment_horizon.value}
        - Risk Profile: {user_preferences.risk_profile.value}
        - Investment Priority: {user_preferences.investment_priority.value}
        - Initial Investment: {user_preferences.initial_investment:,.2f} {user_preferences.currency.value}
        - Monthly Contribution: {user_preferences.monthly_contribution:,.2f} {user_preferences.currency.value}
        - Emergency Fund: {"Yes" if user_preferences.has_emergency_fund else "No"}
        - Liquidity Need: {user_preferences.liquidity_need.value}
        """

        enhanced_selection_criteria = f"""
            SELECTION CRITERIA FOR ETFs:
            - Match investor's knowledge level (simpler, broad-market ETFs for beginners: {user_preferences.investment_knowledge.value})
            - Consider liquidity needs (more liquid ETFs if liquidity_need is short-term: {user_preferences.liquidity_need.value})
            - Factor in monthly contribution amounts (ensure ETFs are affordable for DCA: {user_preferences.monthly_contribution:,.2f})
            - Align with investment purpose and priority ({user_preferences.investment_purpose.value}, {user_preferences.investment_priority.value})
            - Ensure low expense ratios for cost efficiency
            - Consider tax efficiency based on investment horizon ({user_preferences.investment_horizon.value})
        """

        enhanced_reasoning_requirements = f"""
            a) INVESTOR CONTEXT:
                - Explain how the investor's age ({user_preferences.age}) and life stage influence ETF selection
                - Discuss how investment knowledge level ({user_preferences.investment_knowledge.value}) affects portfolio complexity
                - Detail how liquidity needs ({user_preferences.liquidity_need.value}) shape the choice of liquid vs. less liquid ETFs
                - Explain how monthly contributions ({user_preferences.monthly_contribution:,.2f}) inform the selection (fractional shares, minimum investment)
            
            c) GOAL ACHIEVEMENT:
                - Explain how this portfolio helps achieve the primary goal ({user_preferences.goal.value})
                - Discuss how the portfolio supports the investment purpose ({user_preferences.investment_purpose.value})
                - Detail how the portfolio aligns with the investor's priority ({user_preferences.investment_priority.value})
            
            d) RISK MANAGEMENT:
                - Explain how the portfolio respects the risk profile ({user_preferences.risk_profile.value})
                - Discuss how emergency fund status ({"Yes" if user_preferences.has_emergency_fund else "No"}) influences risk-taking
                - Detail rebalancing considerations given the monthly contribution schedule
            
            e) PRACTICAL CONSIDERATIONS:
                - Address how the portfolio fits the initial investment amount ({user_preferences.initial_investment:,.2f})
                - Discuss ongoing contributions and dollar-cost averaging strategy
                - Explain liquidity considerations based on stated liquidity needs
        """

        enhanced_goal_section = f"""
                * The investor's age group ({user_preferences.age}) and life stage
                * Primary investment goal ({user_preferences.goal.value}) and purpose ({user_preferences.investment_purpose.value})
        """

        enhanced_constraints = f"""
        - **Knowledge-Appropriate**: 
            * For NONE/BASIC knowledge: Use only broad-market, well-known ETFs
            * For INTERMEDIATE: Can include sector-specific or regional ETFs
            * For ADVANCED/EXPERT: Can include specialized or tactical ETFs
            (Investor knowledge: {user_preferences.investment_knowledge.value})
        - **Liquidity-Appropriate**: 
            * If liquidity need is ANYTIME or WITHIN_1_YEAR: Focus on highly liquid ETFs
            * If liquidity need is OVER_5_YEARS: Can include less liquid but strategic ETFs
            (Investor liquidity need: {user_preferences.liquidity_need.value})
        - **Accessibility**: Ensure ETFs are accessible for monthly contribution of {user_preferences.monthly_contribution:,.2f}
        """
    else:
        enhanced_selection_criteria = """
            SELECTION CRITERIA FOR ETFs:
            - Align with investment strategy and portfolio objectives
            - Ensure low expense ratios for cost efficiency
            - Consider tax efficiency based on investment horizon
        """

        enhanced_reasoning_requirements = """
            a) STRATEGY ALIGNMENT:
                - Justify each specific ETF selection and how it achieves the target asset allocation
                - Explain how the ETF combination delivers geographical diversification per strategy
                - Detail how sector diversification targets are met through the selected ETFs
        """

        enhanced_goal_section = """
        """

    prompt = f"""You are an expert financial portfolio manager tasked with creating an ETF-based portfolio 
    that strictly adheres to a given investment strategy. Your investment style should emulate that of {analyst["name"]}.
{investor_profile_section}
        INVESTMENT STRATEGY TO IMPLEMENT:
        {strategy}

        PORTFOLIO CONSTRUCTION REQUIREMENTS:
        Based on the strategy above{"and investor profile" if user_preferences else ""}, construct a complete `PortfolioAgent` object containing the portfolio (`data`) and your `reasoning`.

        1. PORTFOLIO (`data`):
            - **Name**: A descriptive name for the portfolio that reflects:{enhanced_goal_section}
                * Risk profile and time horizon
                * The analyst's investment philosophy ({analyst["name"]})
            
            - **Holdings**: A list of 2 to 4 carefully selected ETFs. Each holding must include:
                - `symbol`: The correct ETF ticker symbol quoted on {strategy.stock_exchange.value}
                - `name`: The full name of the ETF
                - `isin`: The ISIN for the ETF (12 characters)
                - `asset_class`: The primary asset class (e.g., 'Stocks', 'Bonds', 'Real Estate', 'Commodities', 'Cash')
                - `weight`: The percentage of the portfolio allocated to this ETF
{enhanced_selection_criteria}
        2. REASONING (`reasoning`):
            Provide a comprehensive, step-by-step explanation for your portfolio construction:
{enhanced_reasoning_requirements}            
            b) STRATEGY ALIGNMENT:
                - Justify each specific ETF selection and how it achieves the target asset allocation
                - Explain how the ETF combination delivers geographical diversification per strategy
                - Detail how sector diversification targets are met through the selected ETFs
                - Show how the portfolio matches the strategy's risk tolerance and time horizon

        STRICT GUIDELINES & CONSTRAINTS:
        - **ETF Only**: The portfolio must consist exclusively of ETFs (no individual stocks, bonds, or other securities)
        - **Stock Exchange**: All selected ETFs must be traded on {strategy.stock_exchange.value}
        - **Accurate Allocation**: The combined weights of the ETFs must precisely match the asset, geographical, 
          and sector allocations defined in the strategy (within 2% tolerance)
        - **Weight Sum**: The sum of all holding weights must equal exactly 100%
        - **ETF Quality**: Choose well-established, highly liquid ETFs with:
            * High assets under management (AUM > $500M preferred)
            * Low expense ratios (TER < 0.5% preferred)
            * Good trading volume for easy entry/exit
            * Proven track record (at least 3 years of history preferred)
        - **Limited Holdings**: The portfolio must contain a maximum of 4 ETFs{enhanced_constraints}"""

    response = llm.with_structured_output(PortfolioAgent).invoke(prompt)

    if state["metadata"]["show_reasoning"]:
        print(response.reasoning)

    portfolio = response.portfolio
    portfolio.strategy = strategy

    state["data"]["portfolio"] = portfolio

    return state
