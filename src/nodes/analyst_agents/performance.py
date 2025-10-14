from graph.state import State
from data.models import AnalysisAgent
from utils.metrics import analyze_portfolio
from utils.analysis_data import all_data


def analyze_performance(state:State) -> State:
  
    llm = state["metadata"]["analyst_llm_agent"]
    portfolio = state["data"]['portfolio']
    strategy = portfolio.strategy

    if state["data"].get("benchmark") is None:
        state["data"]["benchmark"] = "ACWI"
        
    benchmark_ticker = state["data"]["benchmark"]

    # Initialize the analysis dictionary if it doesn't exist
    if 'analysis' not in state['data']:
        state['data']['analysis'] = {}

    portfolio_data, benchmark_data, weights = all_data(portfolio, benchmark_ticker)

    metrics = analyze_portfolio(
        tickers_data=portfolio_data,
        benchmark_data=benchmark_data,
        weights=weights
    )

    portfolio_metric = metrics["portfolio"]
    benchmark_metric = metrics["benchmark"]

    prompt = f"""
    You are a financial data analyst AI specializing in portfolio performance analysis. 
    
    ## TASK
    Analyze the provided portfolio's historical performance compared to relevant benchmarks and the defined investment strategy. 
    Provide a structured analysis with performance improvement recommendations.
    
    ## PORTFOLIO DATA
    {portfolio.holdings}

    ### PORTFOLIO METRICS:
    CAGR: {portfolio_metric['CAGR']}
    Annualized Volatility: {portfolio_metric['Annualized Volatility']}
    Sharpe Ratio: {portfolio_metric['Sharpe Ratio']}
    Max Drawdown: {portfolio_metric['Max Drawdown']}
    Alpha: {portfolio_metric['Alpha']}
    Beta: {portfolio_metric['Beta']}

    ## BENCHMARK DATA (ACWI ETF)

    ### BENCHMARK METRICS (ACWI ETF):
    CAGR: {benchmark_metric['CAGR']}
    Annualized Volatility: {benchmark_metric['Annualized Volatility']}
    Sharpe Ratio: {benchmark_metric['Sharpe Ratio']}
    Max Drawdown: {benchmark_metric['Max Drawdown']}

    ## STRATEGY DATA
    ### EXPECTED RETURNS
    {strategy.expected_returns}
  
    ## ANALYSIS REQUIREMENTS
  
    ### 1. Performance Metrics Comparison
    - Compare the portfolio's performance metrics (CAGR, Sharpe Ratio, etc.) against the benchmark metrics.
    - Identify areas where the portfolio outperforms or underperforms the benchmark.

    ### 2. Alignment with Strategy Expectations
    - Assess whether the portfolio's performance aligns with the strategy's expected returns.
    - Identify any significant deviations from the expected performance and their potential causes.

    ### 3. Performance Status Determination
    - Set status key as "is_performing"
    - Set status value to `true` ONLY if:
      * The portfolio meets or exceeds the benchmark performance in key metrics (CAGR, Sharpe Ratio).
      * The portfolio's performance is consistent with the strategy's expected returns.
    - Set status value to `false` if ANY of the above conditions are not met

    ### 4. Performance Improvement Advice Generation
    - Provide specific recommendations for improving performance if status is `false`
    - Suggest concrete actions, such as rebalancing, changing holdings, or adjusting strategy parameters to enhance performance.
    - Leave `advices` empty if the portfolio is already performing well (status `true`)

    ### 5. Reasoning Documentation
    - Document the reasoning behind the performance status and any recommendations made.
    - Include references to specific data points or analysis results that support the conclusions.

    ## OUTPUT FORMAT
    Return data structured according to the Analysis model:
    - `status`: Status object with key "is_performing" and boolean value
    - `reasoning`: Comprehensive explanation of findings and methodology
    - `advices`: List of specific recommendations (empty if none needed)
    """

    response = llm.with_structured_output(AnalysisAgent).invoke(prompt)

    if state["metadata"]['show_reasoning']:
        print(response.reasoning)
    
    state["data"]['analysis']['performance'] = response

    return state