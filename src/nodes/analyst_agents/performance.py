from src.graph.state import State
from src.data.models import AnalysisAgent, Status, Benchmarks
from src.utils.metrics import analyze_portfolio
from src.utils.analysis_data import all_data


def analyze_performance(state: State) -> State:
  
    llm = state["metadata"]["analyst_llm_agent"]
    portfolio = state["data"]['portfolio']
    strategy = portfolio.strategy

    if state["data"].get("benchmark") is None:
        state["data"]["benchmark"] = Benchmarks.ACWI.value
        
    benchmark = state["data"]["benchmark"]

    # benchmark is now a tuple (ticker, description)
    benchmark_ticker = benchmark[0]
    benchmark_description = benchmark[1]

    # Initialize the analysis dictionary if it doesn't exist
    if 'analysis' not in state['data']:
        state['data']['analysis'] = {}

    # Fetch data with error handling
    try:
        portfolio_data, benchmark_data, weights, data_warning = all_data(
            portfolio, 
            benchmark_ticker,
            allow_partial=True
        )
        
        # Check if we got data quality warnings
        if data_warning:
            warning_context = f"\n\nDATA QUALITY WARNING: {data_warning.message}"
            if data_warning.missing_tickers:
                warning_context += f"\nMissing/problematic tickers: {', '.join(data_warning.missing_tickers)}"
        else:
            warning_context = ""
            
    except ValueError as e:
        # Critical data fetching error - cannot proceed with analysis
        error_message = str(e)
        
        # Create a failed analysis response
        state['data']['analysis']['performance'] = AnalysisAgent(
            status=Status(key="is_performing", value=False),
            reasoning=(
                f"Unable to complete performance analysis due to data availability issues.\n\n"
                f"Error: {error_message}\n\n"
                f"This typically occurs when:\n"
                f"- Stock ticker symbols are invalid or delisted\n"
                f"- Financial data provider is temporarily unavailable\n"
                f"- Network connectivity issues prevent data download\n"
                f"- API rate limits have been exceeded\n\n"
                f"Please verify that all portfolio holdings have valid ticker symbols and try again. "
                f"If the problem persists, consider using alternative benchmark tickers or checking "
                f"your data provider connection."
            ),
            advices=[
                "Verify all portfolio ticker symbols are valid and currently trading",
                "Check your internet connection and financial data API status",
                "Consider reducing the number of holdings if hitting rate limits",
                "Try again after a few minutes if experiencing temporary connectivity issues"
            ]
        )
        return state
    
    # Analyze portfolio with error handling
    try:
        metrics, analysis_warning = analyze_portfolio(
            tickers_data=portfolio_data,
            benchmark_data=benchmark_data,
            weights=weights,
            allow_partial=True
        )
        
        # Add analysis warnings to context if present
        if analysis_warning:
            warning_context += f"\n\nANALYSIS WARNING: {analysis_warning.message}"
            if analysis_warning.affected_tickers:
                warning_context += f"\nAffected tickers: {', '.join(analysis_warning.affected_tickers)}"
                
    except ValueError as e:
        # Analysis failed even with partial data
        error_message = str(e)
        
        state['data']['analysis']['performance'] = AnalysisAgent(
            status=Status(key="is_performing", value=False),
            reasoning=(
                f"Performance analysis could not be completed due to data quality issues.\n\n"
                f"Error: {error_message}\n\n"
                f"The available data was insufficient to calculate reliable performance metrics. "
                f"This may indicate that most or all portfolio holdings have data issues."
            ),
            advices=[
                "Review portfolio holdings for invalid or delisted securities",
                "Ensure holdings have sufficient trading history (at least 2 years recommended)",
                "Consider replacing problematic holdings with more liquid alternatives",
                "Verify that benchmark ticker is valid and has available historical data"
            ]
        )
        return state

    portfolio_metric = metrics["portfolio"]
    benchmark_metric = metrics["benchmark"]

    # Build holdings context - only include available tickers
    holdings_context = []
    for holding in portfolio.holdings:
        if holding.symbol in portfolio_data:
            holdings_context.append(holding)
    
    prompt = f"""
    You are a financial data analyst AI specializing in portfolio performance analysis. 
    
    ## TASK
    Analyze the provided portfolio's historical performance compared to relevant benchmarks and the defined investment strategy. 
    Provide a structured analysis with performance improvement recommendations.
    {warning_context}
    
    ## PORTFOLIO DATA
    {holdings_context}

    ### PORTFOLIO METRICS:
    CAGR: {portfolio_metric['CAGR']}
    Annualized Volatility: {portfolio_metric['Annualized Volatility']}
    Sharpe Ratio: {portfolio_metric['Sharpe Ratio']}
    Max Drawdown: {portfolio_metric['Max Drawdown']}
    Alpha: {portfolio_metric['Alpha']}
    Beta: {portfolio_metric['Beta']}

    ## BENCHMARK DATA: 
    ### Benchmark being used - ({benchmark_ticker})
    {benchmark_description}

    ### BENCHMARK METRICS for ({benchmark_ticker}):
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
    - If there were data quality warnings, acknowledge them and note any limitations in the analysis.

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
    - If data quality issues were present, include recommendations about reviewing affected holdings.
    - Leave `advices` empty if the portfolio is already performing well (status `true`)

    ### 5. Reasoning Documentation
    - Document the reasoning behind the performance status and any recommendations made.
    - Include references to specific data points or analysis results that support the conclusions.
    - Mention any data quality issues and how they may have affected the analysis.

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
