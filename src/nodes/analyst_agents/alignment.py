from data.models import AnalysisAgent
from graph.state import State


def analyze_alignment(state: State) -> State:
    llm = state["metadata"]["analyst_llm_agent"]
    portfolio = state["data"]["portfolio"]
    strategy = portfolio.strategy

    # Initialize the analysis dictionary if it doesn't exist
    if "analysis" not in state["data"]:
        state["data"]["analysis"] = {}

    prompt = f"""
    You are a financial data analyst AI specializing in portfolio alignment analysis. 
    
    ## TASK
    Analyze the provided portfolio's alignment with the user's investment preferences and the defined investment strategy. 
    Provide a structured analysis with alignment improvement recommendations.
    
    ## PORTFOLIO DATA
    {portfolio.holdings}
    
    ## STRATEGY DATA
    ### RISK TOLERANCE
    {strategy.risk_tolerance}
    ### TIME HORIZON
    {strategy.time_horizon}
    ### EXPECTED RETURNS
    {strategy.expected_returns}
    
    ## ANALYSIS REQUIREMENTS
    
    ### 1. User Preferences Alignment Analysis
    - Assess how well the portfolio aligns with the strategy's stated investment preferences (e.g., risk tolerance, investment horizon)
    - Identify any areas where the portfolio may not fully reflect the strategy's preferences
    
    ### 2. Alignment Status Determination
    - Set status key as "is_aligned"
    - Set status value to `true` ONLY if:
        * The portfolio adequately reflects the strategy's investment preferences
    - Set status value to `false` if ANY of the above conditions are not met

    ### 3. Alignment Improvement Advice Generation
    - Provide specific recommendations for improving alignment if status is `false`
    - Suggest concrete actions, such as rebalancing or adding new holdings, to better align the portfolio with the strategy and user preferences
    - Leave `advices` empty if the portfolio is already well-aligned (status `true`)

    ### 4. Reasoning Documentation
    - Document the rationale behind the alignment analysis and status determination
    - Explain any assumptions made during the analysis
    - Provide context for the recommendations given

    ## OUTPUT FORMAT
    Return data structured according to the Analysis model:
    - `status`: Status object with key "is_aligned" and boolean value
    - `reasoning`: Comprehensive explanation of findings and methodology
    - `advices`: List of specific recommendations (empty if none needed)
    """

    response = llm.with_structured_output(AnalysisAgent).invoke(prompt)

    if state["metadata"]["show_reasoning"]:
        print(response.reasoning)

    state["data"]["analysis"]["alignment"] = response

    return state
