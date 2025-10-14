from graph.state import State
from data.models import AnalysisAgent


def analyze_diversification(state:State) -> State:
  
    llm = state["metadata"]["analyst_llm_agent"]
    portfolio = state["data"]['portfolio']
    strategy = portfolio.strategy

    # Initialize the analysis dictionary if it doesn't exist
    if 'analysis' not in state['data']:
        state['data']['analysis'] = {}

    prompt = f"""
    You are a financial data analyst AI specializing in portfolio diversification analysis. 
    
    ## TASK
    Analyze the provided portfolio's diversification comparing with strategy across asset classes, 
    geographical regions, and sectors. Provide a structured analysis with diversification improvement recommendations.
    
    ## PORTFOLIO DATA
    {portfolio.holdings}
    
    ## STRATEGY DATA
    ### ASSET ALLOCATION
    {strategy.asset_allocation}
    ### GEOGRAPHICAL DIVERSIFICATION
    {strategy.geographical_diversification}
    ### SECTOR DIVERSIFICATION
    {strategy.sector_diversification}
    
    ## ANALYSIS REQUIREMENTS
    
    ### 1. Asset Class Diversification Analysis
    - Analyze the asset class allocation of the portfolio holdings
    - Compare actual allocations to the target allocations defined in the strategy
    - Identify over- or under-weighted asset classes based on the strategy
    
    ### 2. Geographical Diversification Analysis
    - Determine the geographical distribution of holdings based on their primary market exposure
    - Compare actual geographical weights to the target weights defined in the strategy
    - Identify over- or under-weighted regions based on the strategy
    
    ### 3. Sector Diversification Analysis
    - Analyze the sector allocation of equity holdings
    - Compare actual sector weights to the target weights defined in the strategy
    - Identify over- or under-weighted sectors based on the strategy
    
    ### 4. Diversification Status Determination
    - Set status key as "is_diversified"
    - Set status value to `true` ONLY if:
        * All asset classes are within ±5% of target strategy allocations
        * All geographical regions are within ±5% of target strategy weights
        * All sectors are within ±5% of target strategy weights
    - Set status value to `false` if ANY of the above conditions are not met

    ### 5. Diversification Improvement Advice Generation
    - Provide specific recommendations for improving diversification if status is `false`
    - Focus on areas where the portfolio is over- or under-weighted compared to the strategy
    - Suggest concrete actions, such as rebalancing or adding new holdings, to achieve better alignment with the strategy
    - Leave `advices` empty if the portfolio is already well-diversified (status `true`)

    ### 6. Reasoning Documentation
    - Document the rationale behind the diversification analysis and status determination
    - Explain any assumptions made during the analysis
    - Provide context for the recommendations given
    
    ## OUTPUT FORMAT
    Return data structured according to the Analysis model:
    - `status`: Status object with key "is_diversified" and boolean value
    - `reasoning`: Comprehensive explanation of findings and methodology
    - `advices`: List of specific recommendations (empty if none needed)
    """

    response = llm.with_structured_output(AnalysisAgent).invoke(prompt)

    if state["metadata"]['show_reasoning']:
        print(response.reasoning)
    
    state["data"]['analysis']['diversification'] = response

    return state