from graph.state import State
from data.models import AnalysisAgent


def analyze_ter(state:State) -> State:
  
    llm = state["metadata"]["analyst_llm_agent"]
    portfolio = state["data"]['portfolio']

    # Initialize the analysis dictionary if it doesn't exist
    if 'analysis' not in state['data']:
        state['data']['analysis'] = {}

    prompt = f"""
    You are a financial data analyst AI specializing in ETF and mutual fund expense analysis.

    ## TASK
    Analyze the Total Expense Ratio (TER) for each holding in the provided portfolio and return a structured analysis with cost-efficiency recommendations.

    ## PORTFOLIO DATA
    {portfolio.holdings}

    ## ANALYSIS REQUIREMENTS

    ### 1. TER Research & Data Collection
    - Find the official Total Expense Ratio (TER) for each holding using the symbol, name, and ISIN provided
    - Use the most recent and accurate TER data available
    - If TER data is unavailable or uncertain, set the value to `null`

    ### 2. TER Value Formatting
    - Express TER as a decimal value (e.g., 0.25% = 0.0025, 1.5% = 0.015)
    - Ensure precision to at least 4 decimal places where possible
    - Use `null` (not 0) for unknown/unavailable TER values

    ### 3. Cost Efficiency Status Determination
    - Set status key as "is_cheaper"
    - Set status value to `true` ONLY if ALL holdings have TER < 0.004 (0.4%)
    - Set status value to `false` if ANY holding has:
      * TER ≥ 0.004 (0.4%), OR
      * Unknown/null TER value

    ### 4. Investment Advice Generation
    - Provide specific alternative fund recommendations if ANY holding has TER ≥ 0.0045 (0.45%)
    - For each high-cost holding, suggest:
      * Specific lower-cost alternative funds with similar exposure
      * The alternative fund's TER and symbol
      * Brief rationale for the recommendation
    - Leave `advices` empty if all TERs are below 0.45% threshold

    ### 5. Reasoning Documentation
    - Explain your TER findings for each holding
    - Justify the status determination
    - Provide context for any advice given
    - Mention any limitations or assumptions made

    ## OUTPUT FORMAT
    Return data structured according to the Analysis model:
    - `status`: Status object with key "is_cheaper" and boolean value
    - `reasoning`: Comprehensive explanation of findings and methodology
    - `advices`: List of specific recommendations (empty if none needed)

  """

    response = llm.with_structured_output(AnalysisAgent).invoke(prompt)

    if state["metadata"]['show_reasoning']:
        print(response.reasoning)

    state["data"]['analysis']['expense_ratio'] = response

    return state