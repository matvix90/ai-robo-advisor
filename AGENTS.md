# Agent Guidelines

This document describes the agent architecture, conventions, and best practices for adding new agents to the AI Robo Advisor project.

## Overview

The AI Robo Advisor uses a **multi-agent system** powered by LangGraph, where specialized agents collaborate to provide comprehensive investment analysis. The system follows a clear separation of concerns:

```
Investment Agent → Portfolio Agent → Analyst Agents (Parallel) → Analysis Orchestrator
                                    ├─ Fees Agent
                                    ├─ Diversification Agent
                                    ├─ Alignment Agent
                                    └─ Performance Agent
```

### Key Principles
- **Function-based**: Agents are functions, not classes
- **State-driven**: All agents take and return `State`
- **LLM-powered**: Use structured LLM outputs for analysis
- **Parallel execution**: Analyst agents run concurrently
- **Standardized output**: All analysts return `AnalysisAgent` model

## Project Structure

```
src/
├── nodes/                         # All agents live here
│   ├── investment_agents/         # Investment strategy creation
│   │   ├── __init__.py
│   │   └── goal_based.py         # Creates investment strategy
│   ├── analyst_agents/            # Portfolio analysis specialists
│   │   ├── __init__.py
│   │   ├── fees.py               # TER analysis
│   │   ├── diversification.py    # Asset/geo/sector analysis
│   │   ├── alignment.py          # Risk/time alignment
│   │   ├── performance.py        # CAGR, Sharpe, drawdown
│   │   └── analysis_workflow.py  # Orchestrates all analysts
│   └── portfolios_agent.py       # Creates ETF portfolio
├── graph/
│   └── state.py                  # State definition
├── data/
│   └── models.py                 # Pydantic models
└── main.py                       # Main workflow
```

## Agent Types

### 1. Investment Agents
**Purpose**: Create investment strategies based on user preferences

**Location**: `src/nodes/investment_agents/`

**Example**: `goal_based.py`

### 2. Portfolio Agent
**Purpose**: Translate strategy into concrete ETF portfolio

**Location**: `src/nodes/portfolios_agent.py`

### 3. Analyst Agents
**Purpose**: Analyze portfolio across different dimensions

**Location**: `src/nodes/analyst_agents/`

**Current Analysts**:
- `fees.py` - Total Expense Ratio (TER) analysis
- `diversification.py` - Asset class, geography, sector analysis
- `alignment.py` - Risk tolerance and time horizon alignment
- `performance.py` - Returns, volatility, Sharpe ratio, alpha, beta

## Creating a New Analyst Agent

This section focuses on adding new analyst agents, which is the most common contribution.

### Step 1: Create Agent File

Create a new file in `src/nodes/analyst_agents/`:

```bash
touch src/nodes/analyst_agents/your_new_agent.py
```

### Step 2: Implement Agent Function

**Template Structure:**

```python
# src/nodes/analyst_agents/your_new_agent.py
from graph.state import State
from data.models import AnalysisAgent

def analyze_your_feature(state: State) -> State:
    """
    Analyze [specific aspect] of the portfolio.
    
    This function evaluates [what it analyzes] and provides
    recommendations based on [criteria].
    
    Args:
        state: Current workflow state containing portfolio data and metadata
        
    Returns:
        Updated state with analysis results in state['data']['analysis']['your_key']
    """
    # 1. Extract LLM and data from state
    llm = state["metadata"]["analyst_llm_agent"]
    portfolio = state["data"]["portfolio"]
    strategy = portfolio.strategy  # If needed
    
    # 2. Initialize analysis dictionary if needed
    if "analysis" not in state["data"]:
        state["data"]["analysis"] = {}
    
    # 3. Build analysis prompt
    prompt = f"""
    You are a financial data analyst AI specializing in [your analysis area].
    
    ## TASK
    Analyze the [specific aspect] of the provided portfolio and return 
    a structured analysis with recommendations.
    
    ## PORTFOLIO DATA
    {portfolio.holdings}
    
    ## STRATEGY DATA (if relevant)
    {strategy}
    
    ## ANALYSIS REQUIREMENTS
    
    ### 1. [First Analysis Step]
    - Describe what to analyze
    - Specify data sources or calculations needed
    
    ### 2. [Second Analysis Step]
    - More detailed analysis requirements
    
    ### 3. Status Determination
    - Set status key as "is_[your_metric]"
    - Set status value to `true` ONLY if [specific conditions met]
    - Set status value to `false` if [conditions not met]
    
    ### 4. Recommendation Generation
    - Provide specific recommendations if status is `false`
    - Focus on actionable improvements
    - Leave `advices` empty if no improvements needed
    
    ### 5. Reasoning Documentation
    - Explain your analysis methodology
    - Document any assumptions made
    - Provide context for recommendations
    
    ## OUTPUT FORMAT
    Return data structured according to the AnalysisAgent model:
    - `status`: Status object with key "is_[your_metric]" and boolean value
    - `reasoning`: Comprehensive explanation of findings
    - `advices`: List of specific recommendations (empty if none needed)
    """
    
    # 4. Get structured output from LLM
    response = llm.with_structured_output(AnalysisAgent).invoke(prompt)
    
    # 5. Optional: Print reasoning if flag is set
    if state["metadata"]["show_reasoning"]:
        print(response.reasoning)
    
    # 6. Store result in state
    state["data"]["analysis"]["your_key"] = response
    
    return state
```

### Step 3: Add to Analysis Workflow

Update `src/nodes/analyst_agents/analysis_workflow.py`:

```python
# 1. Import your new agent
from . import alignment, diversification, fees, performance, your_new_agent

def create_analyst_graph():
    """Creates and compiles the graph for portfolio analysis."""
    workflow = StateGraph(State)

    # 2. Add your node
    workflow.add_node("start", start)
    workflow.add_node("expense_ratio", fees.analyze_ter)
    workflow.add_node("diversification", diversification.analyze_diversification)
    workflow.add_node("alignment", alignment.analyze_alignment)
    workflow.add_node("performance", performance.analyze_performance)
    workflow.add_node("your_feature", your_new_agent.analyze_your_feature)  # ADD THIS
    workflow.add_node("analyst", is_approved)
    
    workflow.set_entry_point("start")

    # 3. Add edges (parallel execution from start)
    workflow.add_edge("start", "expense_ratio")
    workflow.add_edge("start", "diversification")
    workflow.add_edge("start", "alignment")
    workflow.add_edge("start", "performance")
    workflow.add_edge("start", "your_feature")  # ADD THIS
    
    # 4. Connect to analyst node
    workflow.add_edge("expense_ratio", "analyst")
    workflow.add_edge("diversification", "analyst")
    workflow.add_edge("alignment", "analyst")
    workflow.add_edge("performance", "analyst")
    workflow.add_edge("your_feature", "analyst")  # ADD THIS
    workflow.add_edge("analyst", END)

    app = workflow.compile()
    return app
```

### Step 4: Update Final Analysis Logic

If your agent should contribute to the approval score, update `is_approved()` function:

```python
def is_approved(state: State) -> State:
    llm = state["metadata"]["analyst_llm_agent"]
    response = state["data"]["analysis"]
    confidence = 0
    
    # Existing checks
    if response["expense_ratio"].status.value:
        confidence += 1
    if response["diversification"].status.value:
        confidence += 1
    if response["alignment"].status.value:
        confidence += 1
    if check_performance(state):
        confidence += 1
    # Add your check
    if response["your_key"].status.value:
        confidence += 1
    
    # Update threshold if needed (currently 2 out of 4)
    if confidence >= 2:  # Adjust threshold
        state["data"]["analysis"]["is_approved"] = True
    else:
        state["data"]["analysis"]["is_approved"] = False
    
    # Collect advice from your agent
    all_advices = []
    # ... existing advice collection ...
    if response["your_key"].advices:
        all_advices.extend(response["your_key"].advices)
    
    # Update the summary prompt to include your analysis
    prompt = f"""
    ...
    - Your Feature Analysis: {"PASSED" if response["your_key"].status.value else "FAILED"}
      Reasoning: {response["your_key"].reasoning}
    ...
    """
    
    # Rest of the function remains the same
```

### Step 5: Write Tests

Create test file: `tests/test_nodes/test_your_agent.py`

```python
import pytest
from unittest.mock import Mock
from src.nodes.analyst_agents.your_new_agent import analyze_your_feature
from src.data.models import AnalysisAgent, Status

@pytest.fixture
def mock_state(sample_state):
    """Create state with required data for your agent."""
    sample_state["data"]["portfolio"] = Mock()
    sample_state["data"]["portfolio"].holdings = [
        # Your test portfolio data
    ]
    return sample_state

@pytest.fixture
def mock_llm_response():
    """Mock LLM response for your agent."""
    mock_response = AnalysisAgent(
        status=Status(key="is_your_metric", value=True),
        reasoning="Test reasoning for your analysis",
        advices=[]
    )
    return mock_response

def test_analyze_your_feature_success(mock_state, mock_llm_response):
    """Test agent with valid portfolio that passes analysis."""
    # Setup
    mock_llm = Mock()
    mock_llm.with_structured_output.return_value.invoke.return_value = mock_llm_response
    mock_state["metadata"]["analyst_llm_agent"] = mock_llm
    
    # Execute
    result = analyze_your_feature(mock_state)
    
    # Assert
    assert "your_key" in result["data"]["analysis"]
    assert result["data"]["analysis"]["your_key"].status.value is True
    assert result["data"]["analysis"]["your_key"].reasoning == "Test reasoning for your analysis"
    mock_llm.with_structured_output.assert_called_once_with(AnalysisAgent)

def test_analyze_your_feature_failure(mock_state):
    """Test agent with portfolio that fails analysis."""
    # Setup mock to return failed status
    failed_response = AnalysisAgent(
        status=Status(key="is_your_metric", value=False),
        reasoning="Analysis failed due to X",
        advices=["Recommendation 1", "Recommendation 2"]
    )
    
    mock_llm = Mock()
    mock_llm.with_structured_output.return_value.invoke.return_value = failed_response
    mock_state["metadata"]["analyst_llm_agent"] = mock_llm
    
    # Execute
    result = analyze_your_feature(mock_state)
    
    # Assert
    assert result["data"]["analysis"]["your_key"].status.value is False
    assert len(result["data"]["analysis"]["your_key"].advices) == 2

def test_analyze_your_feature_show_reasoning(mock_state, mock_llm_response, capsys):
    """Test that reasoning is printed when flag is set."""
    # Setup
    mock_llm = Mock()
    mock_llm.with_structured_output.return_value.invoke.return_value = mock_llm_response
    mock_state["metadata"]["analyst_llm_agent"] = mock_llm
    mock_state["metadata"]["show_reasoning"] = True
    
    # Execute
    analyze_your_feature(mock_state)
    
    # Assert
    captured = capsys.readouterr()
    assert "Test reasoning" in captured.out
```

### Step 6: Run Tests

```bash
# Run your specific tests
pytest tests/test_nodes/test_your_agent.py -v

# Run all tests
pytest tests/ -v

# Check coverage
pytest tests/ --cov=src/nodes/analyst_agents --cov-report=term-missing
```

## Real-World Examples

### Example 1: Fees Agent (Simple Numeric Analysis)

```python
def analyze_ter(state: State) -> State:
    llm = state["metadata"]["analyst_llm_agent"]
    portfolio = state["data"]["portfolio"]
    
    if "analysis" not in state["data"]:
        state["data"]["analysis"] = {}
    
    prompt = f"""
    Analyze the Total Expense Ratio (TER) for each holding.
    
    Portfolio: {portfolio.holdings}
    
    Requirements:
    - Find official TER for each ETF
    - Express as decimal (0.25% = 0.0025)
    - Status is true ONLY if ALL TERs < 0.004 (0.4%)
    - Recommend alternatives if any TER ≥ 0.0045 (0.45%)
    """
    
    response = llm.with_structured_output(AnalysisAgent).invoke(prompt)
    
    if state["metadata"]["show_reasoning"]:
        print(response.reasoning)
    
    state["data"]["analysis"]["expense_ratio"] = response
    return state
```

### Example 2: Diversification Agent (Complex Multi-Dimensional)

```python
def analyze_diversification(state: State) -> State:
    llm = state["metadata"]["analyst_llm_agent"]
    portfolio = state["data"]["portfolio"]
    strategy = portfolio.strategy
    
    if "analysis" not in state["data"]:
        state["data"]["analysis"] = {}
    
    prompt = f"""
    Analyze diversification across three dimensions:
    
    Portfolio: {portfolio.holdings}
    
    Target Strategy:
    - Asset Allocation: {strategy.asset_allocation}
    - Geography: {strategy.geographical_diversification}
    - Sectors: {strategy.sector_diversification}
    
    Requirements:
    - Compare actual vs target allocations
    - Status is true ONLY if ALL within ±5% of target
    - Provide rebalancing recommendations if needed
    """
    
    response = llm.with_structured_output(AnalysisAgent).invoke(prompt)
    
    if state["metadata"]["show_reasoning"]:
        print(response.reasoning)
    
    state["data"]["analysis"]["diversification"] = response
    return state
```

## Data Models Reference

### State Structure

```python
# State type definition
class State(TypedDict):
    data: Annotated[dict[str, any], merge_dicts]
    metadata: Annotated[dict[str, any], merge_dicts]

# Example state access in agent:
state = {
    "data": {
        "portfolio": Portfolio,           # Portfolio object with holdings
        "benchmark": tuple,               # (ticker, description)
        "analysis": {                     # Analysis results
            "expense_ratio": AnalysisAgent,
            "diversification": AnalysisAgent,
            "alignment": AnalysisAgent,
            "performance": AnalysisAgent,
            "is_approved": bool,
            "summary": AnalysisResponse
        }
    },
    "metadata": {
        "show_reasoning": bool,
        "investment_llm_agent": LLM,
        "portfolio_llm_agent": LLM,
        "analyst_llm_agent": LLM
    }
}
```

### AnalysisAgent Model

```python
class Status(BaseModel):
    key: str        # e.g., "is_cheaper", "is_diversified"
    value: bool     # True if passes, False if fails

class AnalysisAgent(BaseModel):
    status: Status                  # Pass/fail with key
    reasoning: str                  # Detailed explanation
    advices: Optional[list[str]]    # Recommendations (can be empty)

# Example usage:
response = AnalysisAgent(
    status=Status(key="is_cheaper", value=True),
    reasoning="All ETFs have TER below 0.4% threshold...",
    advices=[]  # Empty if no improvements needed
)
```

### AnalysisResponse Model (Final Summary)

```python
class AnalysisResponse(BaseModel):
    is_approved: bool              # Overall approval
    strengths: Optional[str]       # Portfolio strengths
    weeknesses: Optional[str]      # Areas of concern (note: typo in original)
    overall_assessment: Optional[str]  # Balanced evaluation
    advices: Optional[str]         # Consolidated recommendations
```

## Naming Conventions

### File Names
- Lowercase with underscores: `fees.py`, `tax_efficiency.py`
- Descriptive and specific: `esg_score.py` not `scoring.py`

### Function Names
- Pattern: `analyze_{feature}(state: State) -> State`
- Examples:
  - `analyze_ter(state)`
  - `analyze_diversification(state)`
  - `analyze_tax_efficiency(state)`

### Status Keys
- Pattern: `is_{metric}` (boolean)
- Examples:
  - `"is_cheaper"` - TER below threshold
  - `"is_diversified"` - Diversification adequate
  - `"is_aligned"` - Risk/time horizon match
  - `"is_tax_efficient"` - Tax optimization good

### Analysis Keys in State
- Use lowercase with underscores
- Match file name or feature
- Examples:
  - `state["data"]["analysis"]["expense_ratio"]`
  - `state["data"]["analysis"]["diversification"]`
  - `state["data"]["analysis"]["tax_efficiency"]`

## Prompt Engineering Best Practices

### Structure Your Prompts

```python
prompt = f"""
You are a [specific expert type] AI specializing in [domain].

## TASK
[Clear, one-sentence task description]

## INPUT DATA
{data_section}

## ANALYSIS REQUIREMENTS

### 1. [Step Name]
- Specific instruction
- Expected output format

### 2. [Step Name]
- More instructions
- Calculation details

### 3. Status Determination
- Set status key as "[your_key]"
- Set value to `true` ONLY if [precise conditions]
- Set value to `false` if [failure conditions]

### 4. Recommendations
- When to provide advice
- What kind of recommendations
- When to leave empty

### 5. Reasoning
- What to document
- What to explain

## OUTPUT FORMAT
Return data structured according to the AnalysisAgent model:
- `status`: Status object with key "[your_key]" and boolean value
- `reasoning`: Comprehensive explanation
- `advices`: List of recommendations (empty if none needed)
"""
```

### Prompt Tips

✅ **DO**:
- Be specific about thresholds and conditions
- Provide exact data formats (e.g., "0.25% = 0.0025")
- Include all relevant context (portfolio, strategy, benchmarks)
- Clearly state when to return empty advices
- Use consistent terminology

❌ **DON'T**:
- Use vague instructions like "analyze well"
- Mix different analysis aspects in one agent
- Forget to specify the status key name
- Leave output format ambiguous

## Security & Privacy

### API Keys
```python
# ✅ Good: Keys in environment variables
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

# ❌ Bad: Hardcoded keys
OPENAI_API_KEY = "sk-1234567890"  # NEVER!
```

### Sensitive Data
```python
# ✅ Good: Never log user portfolios
if state["metadata"]["show_reasoning"]:
    print(response.reasoning)  # Analysis only, no raw data

# ❌ Bad: Logging sensitive info
print(f"User portfolio: {state['data']['portfolio']}")  # NEVER!
```

### Input Validation
```python
def analyze_your_feature(state: State) -> State:
    # Validate required data exists
    if "portfolio" not in state["data"]:
        raise ValueError("Portfolio data missing from state")
    
    portfolio = state["data"]["portfolio"]
    
    # Validate portfolio has holdings
    if not portfolio.holdings:
        raise ValueError("Portfolio has no holdings")
    
    # Validate LLM is available
    if "analyst_llm_agent" not in state["metadata"]:
        raise ValueError("Analyst LLM agent not configured")
    
    # Your analysis logic...
```

### Rate Limiting
```python
# Remember Polygon.io free tier limits:
# - 5 API calls per minute
# - Use caching for market data
# - Don't fetch same data multiple times

# ✅ Good: Cache in state
if "market_data_cache" not in state["data"]:
    state["data"]["market_data_cache"] = {}

# Check cache before API call
if symbol not in state["data"]["market_data_cache"]:
    data = fetch_from_polygon(symbol)
    state["data"]["market_data_cache"][symbol] = data
```

### Disclaimer Requirements

Every agent dealing with investment recommendations MUST include educational disclaimers:

```python
DISCLAIMER = """
⚠️ EDUCATIONAL PURPOSE ONLY
This analysis is for educational and research purposes only.
It does not constitute financial advice.
Consult a qualified financial advisor before making investment decisions.
"""

# Include in advices when providing recommendations
if needs_recommendations:
    advices = [
        "Consider rebalancing to reduce expense ratios",
        "Evaluate lower-cost ETF alternatives",
        DISCLAIMER
    ]
```

## Testing Guidelines

### Test Structure

Every agent must have:
1. **Unit tests** - Test agent function in isolation
2. **Integration tests** - Test within workflow
3. **Mock tests** - Test with mocked LLM responses

### Required Test Cases

```python
# 1. Test successful analysis (passing criteria)
def test_analyze_feature_passes(mock_state, mock_llm_success):
    result = analyze_feature(mock_state)
    assert result["data"]["analysis"]["feature"].status.value is True

# 2. Test failed analysis (not meeting criteria)
def test_analyze_feature_fails(mock_state, mock_llm_failure):
    result = analyze_feature(mock_state)
    assert result["data"]["analysis"]["feature"].status.value is False
    assert len(result["data"]["analysis"]["feature"].advices) > 0

# 3. Test edge cases
def test_analyze_feature_empty_portfolio(mock_state):
    mock_state["data"]["portfolio"].holdings = []
    with pytest.raises(ValueError, match="no holdings"):
        analyze_feature(mock_state)

# 4. Test show_reasoning flag
def test_analyze_feature_show_reasoning(mock_state, capsys):
    mock_state["metadata"]["show_reasoning"] = True
    analyze_feature(mock_state)
    captured = capsys.readouterr()
    assert len(captured.out) > 0

# 5. Test LLM invocation
def test_analyze_feature_llm_called(mock_state):
    mock_llm = Mock()
    mock_state["metadata"]["analyst_llm_agent"] = mock_llm
    analyze_feature(mock_state)
    mock_llm.with_structured_output.assert_called_once_with(AnalysisAgent)
```

### Using Fixtures

```python
# Reuse existing fixtures from conftest.py
def test_with_fixtures(sample_state, mock_llm):
    # sample_state and mock_llm are defined in tests/conftest.py
    result = analyze_feature(sample_state)
    assert result is not None
```

### Coverage Requirements

```bash
# Minimum 80% coverage for new agents
pytest tests/test_nodes/test_your_agent.py --cov=src/nodes/analyst_agents/your_agent --cov-fail-under=80

# Check what's not covered
pytest --cov=src/nodes/analyst_agents/your_agent --cov-report=term-missing
```

## Common Patterns & Pitfalls

### ✅ Good Patterns

**1. Clear Status Determination**
```python
# Good: Explicit threshold
if all(ter < 0.004 for ter in ters):
    status = Status(key="is_cheaper", value=True)
else:
    status = Status(key="is_cheaper", value=False)
```

**2. Conditional Advice**
```python
# Good: Empty list if no improvements needed
if status.value:
    advices = []  # No recommendations if passing
else:
    advices = ["Recommendation 1", "Recommendation 2"]
```

**3. Structured Reasoning**
```python
reasoning = f"""
Analysis Summary:
- Metric 1: {value1} (threshold: {threshold1})
- Metric 2: {value2} (threshold: {threshold2})

Conclusion:
{conclusion_text}

Methodology:
{methodology_description}
"""
```

### ❌ Common Pitfalls

**1. Modifying Wrong State Key**
```python
# ❌ Bad: Using wrong key
state["analysis"]["your_feature"] = response

# ✅ Good: Correct path
state["data"]["analysis"]["your_feature"] = response
```

**2. Forgetting to Return State**
```python
# ❌ Bad: Not returning state
def analyze_feature(state: State):
    # ... analysis ...
    state["data"]["analysis"]["feature"] = response
    # Missing return!

# ✅ Good: Always return state
def analyze_feature(state: State) -> State:
    # ... analysis ...
    state["data"]["analysis"]["feature"] = response
    return state
```

**3. Not Initializing Analysis Dict**
```python
# ❌ Bad: Assuming dict exists
state["data"]["analysis"]["feature"] = response  # KeyError!

# ✅ Good: Initialize first
if "analysis" not in state["data"]:
    state["data"]["analysis"] = {}
state["data"]["analysis"]["feature"] = response
```

**4. Incorrect Status Key Format**
```python
# ❌ Bad: Inconsistent naming
Status(key="cheaper", value=True)  # Missing "is_"
Status(key="IsCheaper", value=True)  # Wrong case

# ✅ Good: Consistent "is_" prefix, snake_case
Status(key="is_cheaper", value=True)
Status(key="is_tax_efficient", value=True)
```

**5. Ignoring Show Reasoning Flag**
```python
# ❌ Bad: Always printing or never printing
print(response.reasoning)  # Always prints

# ✅ Good: Respect the flag
if state["metadata"]["show_reasoning"]:
    print(response.reasoning)
```

## Advanced Topics

### Working with Market Data

If your agent needs market data:

```python
from tools.polygon_client import get_market_data

def analyze_with_market_data(state: State) -> State:
    portfolio = state["data"]["portfolio"]
    
    # Fetch market data for each holding
    market_data = {}
    for holding in portfolio.holdings:
        symbol = holding.symbol
        # Check cache first
        if symbol not in state.get("market_data_cache", {}):
            data = get_market_data(symbol)
            market_data[symbol] = data
        else:
            market_data[symbol] = state["market_data_cache"][symbol]
    
    # Use market data in analysis
    prompt = f"""
    Analyze with market data:
    Portfolio: {portfolio.holdings}
    Market Data: {market_data}
    ...
    """
    # Rest of analysis
```

### Custom Analysis Models

If `AnalysisAgent` doesn't fit your needs, create a custom model:

```python
# In src/data/models.py
class DetailedAnalysisAgent(BaseModel):
    status: Status
    reasoning: str
    advices: Optional[list[str]]
    detailed_metrics: dict  # Your custom field
    confidence_score: float  # Your custom field

# In your agent
response = llm.with_structured_output(DetailedAnalysisAgent).invoke(prompt)
```

### Conditional Logic in Workflow

If your agent should only run under certain conditions:

```python
# In analysis_workflow.py
def should_run_tax_analysis(state: State) -> bool:
    """Only run tax analysis for US portfolios."""
    portfolio = state["data"]["portfolio"]
    return portfolio.currency == Currency.USD

# Add conditional edge
workflow.add_conditional_edges(
    "start",
    should_run_tax_analysis,
    {True: "tax_analysis", False: "skip_tax"}
)
```

## Debugging Tips

### Enable Reasoning Output

```bash
# Run with reasoning flag to see LLM outputs
run-advisor --show-reasoning
```

### Add Debug Prints

```python
def analyze_feature(state: State) -> State:
    # Debug: Check state structure
    print(f"DEBUG: Keys in state['data']: {state['data'].keys()}")
    print(f"DEBUG: Portfolio holdings count: {len(state['data']['portfolio'].holdings)}")
    
    # Your analysis...
    
    # Debug: Check response
    print(f"DEBUG: Status key: {response.status.key}")
    print(f"DEBUG: Status value: {response.status.value}")
    print(f"DEBUG: Advices count: {len(response.advices or [])}")
    
    return state
```

### Test in Isolation

```bash
# Test just your agent
pytest tests/test_nodes/test_your_agent.py::test_specific_case -v -s

# -s flag shows print statements
```

### Check LangGraph Flow

```python
# Visualize the graph
from langgraph.graph import StateGraph

def create_analyst_graph():
    workflow = StateGraph(State)
    # ... add nodes and edges ...
    
    # Save graph visualization
    app = workflow.compile()
    app.get_graph().draw_mermaid_png(output_file_path="graph.png")
    
    return app
```

## Contribution Checklist

Before submitting your new agent:

### Code Quality
- [ ] Agent function follows naming convention: `analyze_{feature}`
- [ ] Takes `State` parameter and returns `State`
- [ ] Initializes `state["data"]["analysis"]` dictionary
- [ ] Uses correct analysis key in state
- [ ] Respects `show_reasoning` flag
- [ ] Returns `AnalysisAgent` model with proper status key
- [ ] Handles empty advice case (empty list, not None)

### Integration
- [ ] Added to `analysis_workflow.py` imports
- [ ] Node added to workflow graph
- [ ] Edge from "start" to your node
- [ ] Edge from your node to "analyst"
- [ ] Updated `is_approved()` if contributing to score
- [ ] Updated final prompt in `is_approved()` to include your analysis

### Testing
- [ ] Created test file: `tests/test_nodes/test_your_agent.py`
- [ ] Test for successful analysis (status=True)
- [ ] Test for failed analysis (status=False)
- [ ] Test with empty portfolio
- [ ] Test show_reasoning flag
- [ ] Test LLM invocation
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Coverage ≥ 80%: `pytest --cov=src/nodes/analyst_agents/your_agent`

### Documentation
- [ ] Docstring in agent function
- [ ] Clear prompt structure
- [ ] Comments for complex logic
- [ ] Updated this AGENTS.md if adding new patterns

### Security
- [ ] No hardcoded API keys
- [ ] No logging of sensitive data
- [ ] Input validation for required fields
- [ ] Disclaimer included if providing investment advice

### Final Checks
- [ ] Run full test suite: `./run_tests.sh`
- [ ] Run linting if configured
- [ ] Test manually with `run-advisor --show-reasoning`
- [ ] Verify output in final analysis summary
- [ ] Check no breaking changes to existing agents

## Pull Request Template

When submitting your new agent, use this PR description:

```markdown
## 🤖 New Analyst Agent: [Agent Name]

### Description
Brief description of what this agent analyzes and why it's valuable.

### Type of Change
- [x] New analyst agent
- [ ] Enhancement to existing agent
- [ ] Bug fix
- [ ] Documentation

### Agent Details
- **File**: `src/nodes/analyst_agents/your_agent.py`
- **Function**: `analyze_your_feature()`
- **Status Key**: `is_your_metric`
- **Analysis Key**: `your_feature`

### What It Analyzes
- Key metric 1
- Key metric 2
- Key metric 3

### Status Criteria
Passes (status=True) when:
- Condition 1
- Condition 2

Fails (status=False) when:
- Failure condition 1
- Failure condition 2

### Example Output
```python
AnalysisAgent(
    status=Status(key="is_your_metric", value=True),
    reasoning="Analysis shows...",
    advices=[]
)
```

### Testing
- [ ] All tests pass
- [ ] Coverage ≥ 80%
- [ ] Manual testing completed

### Test Results
```bash
pytest tests/test_nodes/test_your_agent.py -v
# Paste output here
```

### Integration
- [ ] Added to `analysis_workflow.py`
- [ ] Updated `is_approved()` logic (if applicable)
- [ ] Tested in full workflow

### Checklist
- [ ] Code follows project conventions
- [ ] Docstrings added
- [ ] Tests written and passing
- [ ] No hardcoded secrets
- [ ] Handles edge cases
- [ ] Documentation updated

### Related Issues
Closes #[issue-number]
```

## Example: Complete New Agent Implementation

Here's a complete example of adding a **Tax Efficiency Agent**:

### 1. Create Agent File

```python
# src/nodes/analyst_agents/tax_efficiency.py
from graph.state import State
from data.models import AnalysisAgent

def analyze_tax_efficiency(state: State) -> State:
    """
    Analyze the tax efficiency of the portfolio.
    
    Evaluates tax-loss harvesting opportunities, tax-advantaged
    account placement, and holding period optimization.
    
    Args:
        state: Current workflow state containing portfolio data and metadata
        
    Returns:
        Updated state with tax analysis in state['data']['analysis']['tax_efficiency']
    """
    # Extract from state
    llm = state["metadata"]["analyst_llm_agent"]
    portfolio = state["data"]["portfolio"]
    strategy = portfolio.strategy
    
    # Initialize analysis dictionary
    if "analysis" not in state["data"]:
        state["data"]["analysis"] = {}
    
    # Build prompt
    prompt = f"""
    You are a financial data analyst AI specializing in tax-efficient investing.
    
    ## TASK
    Analyze the tax efficiency of the provided portfolio and provide
    recommendations for optimization.
    
    ## PORTFOLIO DATA
    {portfolio.holdings}
    
    ## STRATEGY DATA
    Investment Horizon: {strategy.investment_horizon}
    Risk Profile: {strategy.risk_profile}
    
    ## ANALYSIS REQUIREMENTS
    
    ### 1. Asset Location Analysis
    - Evaluate if holdings are tax-efficient (ETFs vs mutual funds)
    - ETFs generally have lower capital gains distributions
    - Identify holdings with high tax-cost ratios
    
    ### 2. Turnover Rate Assessment
    - Analyze fund turnover rates (lower is better for taxes)
    - High turnover (>100%) triggers more taxable events
    - Look for index funds with low turnover (<10%)
    
    ### 3. Dividend Treatment
    - Check if dividends are qualified (lower tax rate)
    - International holdings may have foreign tax implications
    - REIT dividends are taxed as ordinary income
    
    ### 4. Tax Efficiency Status Determination
    - Set status key as "is_tax_efficient"
    - Set status value to `true` ONLY if ALL conditions met:
      * All holdings are ETFs (not mutual funds)
      * Average turnover rate < 50%
      * No high-yield dividend funds (>4% yield)
    - Set status value to `false` if ANY condition fails
    
    ### 5. Tax Optimization Recommendations
    - Provide specific recommendations if status is `false`
    - Suggest tax-loss harvesting opportunities
    - Recommend more tax-efficient alternatives
    - Leave `advices` empty if portfolio is already tax-efficient
    
    ### 6. Reasoning Documentation
    - Explain tax efficiency findings for each holding
    - Document turnover rates and tax implications
    - Provide context for optimization strategies
    
    ## OUTPUT FORMAT
    Return data structured according to the AnalysisAgent model:
    - `status`: Status object with key "is_tax_efficient" and boolean value
    - `reasoning`: Comprehensive explanation of tax implications
    - `advices`: List of tax optimization recommendations (empty if none needed)
    
    Note: Analysis assumes taxable account. Tax-advantaged accounts have different considerations.
    """
    
    # Get structured output
    response = llm.with_structured_output(AnalysisAgent).invoke(prompt)
    
    # Print reasoning if flag set
    if state["metadata"]["show_reasoning"]:
        print("\n" + "="*50)
        print("TAX EFFICIENCY ANALYSIS")
        print("="*50)
        print(response.reasoning)
        print("="*50 + "\n")
    
    # Store in state
    state["data"]["analysis"]["tax_efficiency"] = response
    
    return state
```

### 2. Update Analysis Workflow

```python
# src/nodes/analyst_agents/analysis_workflow.py
from langgraph.graph import StateGraph, END

from graph.state import State
from data.models import AnalysisResponse
from utils.check_performance import check_performance
from . import alignment, diversification, fees, performance, tax_efficiency  # ADD IMPORT

def start(state: State) -> State:
    """Initial state function."""
    print("Starting analysis workflow...\n")
    return state

def is_approved(state: State) -> State:
    llm = state["metadata"]["analyst_llm_agent"]
    response = state["data"]["analysis"]
    confidence = 0
    
    # Existing checks
    if response["expense_ratio"].status.value:
        confidence += 1
    if response["diversification"].status.value:
        confidence += 1
    if response["alignment"].status.value:
        confidence += 1
    if check_performance(state):
        confidence += 1
    # Add tax efficiency check
    if response["tax_efficiency"].status.value:
        confidence += 1
    
    # Update threshold from 2/4 to 3/5 for stricter approval
    if confidence >= 3:
        state["data"]["analysis"]["is_approved"] = True
    else:
        state["data"]["analysis"]["is_approved"] = False
    
    # Collect all advice
    all_advices = []
    if response["expense_ratio"].advices:
        all_advices.extend(response["expense_ratio"].advices)
    if response["diversification"].advices:
        all_advices.extend(response["diversification"].advices)
    if response["alignment"].advices:
        all_advices.extend(response["alignment"].advices)
    if response["performance"].advices:
        all_advices.extend(response["performance"].advices)
    if response["tax_efficiency"].advices:  # ADD THIS
        all_advices.extend(response["tax_efficiency"].advices)
    
    advice_summary = "\n".join([f"- {advice}" for advice in all_advices]) if all_advices else "No specific advice provided."
    
    # Update prompt to include tax efficiency
    prompt = f"""
    You are a senior financial portfolio analyst with expertise in comprehensive investment assessment.

    ANALYSIS RESULTS:
    - Expense Ratio: {"PASSED" if response["expense_ratio"].status.value else "FAILED"}
      Reasoning: {response["expense_ratio"].reasoning}
    
    - Diversification: {"PASSED" if response["diversification"].status.value else "FAILED"}
      Reasoning: {response["diversification"].reasoning}
    
    - Alignment: {"PASSED" if response["alignment"].status.value else "FAILED"}
      Reasoning: {response["alignment"].reasoning}
    
    - Performance: {"PASSED" if response["performance"].status.value else "FAILED"}
      Reasoning: {response["performance"].reasoning}
    
    - Tax Efficiency: {"PASSED" if response["tax_efficiency"].status.value else "FAILED"}
      Reasoning: {response["tax_efficiency"].reasoning}

    EXISTING ADVICE:
    {advice_summary}

    CONFIDENCE SCORE: {confidence}/5 criteria met
    APPROVAL STATUS: {"APPROVED" if confidence >= 3 else "REJECTED"}

    Provide comprehensive analysis with:
    1. STRENGTHS: Portfolio's strongest aspects
    2. WEAKNESSES: Areas of concern
    3. OVERALL ASSESSMENT: Balanced evaluation across all five dimensions
    4. ACTIONABLE ADVICE: Prioritized recommendations for optimization
    """
    
    analysis_response = llm.with_structured_output(AnalysisResponse).invoke(prompt)
    analysis_response.is_approved = state["data"]["analysis"]["is_approved"]
    state["data"]["analysis"]["summary"] = analysis_response

    return state


def create_analyst_graph():
    """Creates and compiles the graph for portfolio analysis."""
    workflow = StateGraph(State)

    # Add nodes
    workflow.add_node("start", start)
    workflow.add_node("expense_ratio", fees.analyze_ter)
    workflow.add_node("diversification", diversification.analyze_diversification)
    workflow.add_node("alignment", alignment.analyze_alignment)
    workflow.add_node("performance", performance.analyze_performance)
    workflow.add_node("tax_efficiency", tax_efficiency.analyze_tax_efficiency)  # ADD NODE
    workflow.add_node("analyst", is_approved)
    
    workflow.set_entry_point("start")

    # Add edges - all analysts run in parallel from start
    workflow.add_edge("start", "expense_ratio")
    workflow.add_edge("start", "diversification")
    workflow.add_edge("start", "alignment")
    workflow.add_edge("start", "performance")
    workflow.add_edge("start", "tax_efficiency")  # ADD EDGE
    
    # All converge to analyst
    workflow.add_edge("expense_ratio", "analyst")
    workflow.add_edge("diversification", "analyst")
    workflow.add_edge("alignment", "analyst")
    workflow.add_edge("performance", "analyst")
    workflow.add_edge("tax_efficiency", "analyst")  # ADD EDGE
    workflow.add_edge("analyst", END)

    app = workflow.compile()
    return app
```

### 3. Create Tests

```python
# tests/test_nodes/test_tax_efficiency.py
import pytest
from unittest.mock import Mock
from src.nodes.analyst_agents.tax_efficiency import analyze_tax_efficiency
from src.data.models import AnalysisAgent, Status, Portfolio, Strategy, Holding

@pytest.fixture
def tax_efficient_portfolio():
    """Portfolio with good tax efficiency."""
    return Portfolio(
        holdings=[
            Holding(symbol="VTI", name="Vanguard Total Stock Market ETF", 
                   allocation=60, type="ETF"),
            Holding(symbol="BND", name="Vanguard Total Bond Market ETF", 
                   allocation=40, type="ETF")
        ],
        strategy=Strategy(
            investment_horizon="Long Term (7-15 years)",
            risk_profile="Moderate"
        )
    )

@pytest.fixture
def tax_inefficient_portfolio():
    """Portfolio with poor tax efficiency."""
    return Portfolio(
        holdings=[
            Holding(symbol="VWINX", name="Vanguard Wellesley Income Fund", 
                   allocation=50, type="Mutual Fund"),  # Mutual fund = less efficient
            Holding(symbol="VYM", name="Vanguard High Dividend Yield ETF", 
                   allocation=50, type="ETF", dividend_yield=4.5)  # High yield
        ],
        strategy=Strategy(
            investment_horizon="Long Term (7-15 years)",
            risk_profile="Moderate"
        )
    )

@pytest.fixture
def mock_state_tax_efficient(sample_state, tax_efficient_portfolio):
    """State with tax-efficient portfolio."""
    sample_state["data"]["portfolio"] = tax_efficient_portfolio
    return sample_state

@pytest.fixture
def mock_state_tax_inefficient(sample_state, tax_inefficient_portfolio):
    """State with tax-inefficient portfolio."""
    sample_state["data"]["portfolio"] = tax_inefficient_portfolio
    return sample_state

class TestTaxEfficiencyAgent:
    
    def test_tax_efficient_portfolio_passes(self, mock_state_tax_efficient):
        """Test that tax-efficient portfolio passes analysis."""
        # Setup mock LLM
        mock_response = AnalysisAgent(
            status=Status(key="is_tax_efficient", value=True),
            reasoning="All holdings are ETFs with low turnover and reasonable yields.",
            advices=[]
        )
        
        mock_llm = Mock()
        mock_llm.with_structured_output.return_value.invoke.return_value = mock_response
        mock_state_tax_efficient["metadata"]["analyst_llm_agent"] = mock_llm
        
        # Execute
        result = analyze_tax_efficiency(mock_state_tax_efficient)
        
        # Assert
        assert "tax_efficiency" in result["data"]["analysis"]
        assert result["data"]["analysis"]["tax_efficiency"].status.key == "is_tax_efficient"
        assert result["data"]["analysis"]["tax_efficiency"].status.value is True
        assert result["data"]["analysis"]["tax_efficiency"].advices == []
    
    def test_tax_inefficient_portfolio_fails(self, mock_state_tax_inefficient):
        """Test that tax-inefficient portfolio fails analysis."""
        mock_response = AnalysisAgent(
            status=Status(key="is_tax_efficient", value=False),
            reasoning="Portfolio contains mutual funds and high-yield holdings with tax inefficiencies.",
            advices=[
                "Replace VWINX mutual fund with equivalent ETF (e.g., VWELX or custom mix of VTI/BND)",
                "Consider lower-yield alternatives to VYM if in taxable account",
                "Review turnover rates - high turnover triggers more taxable events"
            ]
        )
        
        mock_llm = Mock()
        mock_llm.with_structured_output.return_value.invoke.return_value = mock_response
        mock_state_tax_inefficient["metadata"]["analyst_llm_agent"] = mock_llm
        
        # Execute
        result = analyze_tax_efficiency(mock_state_tax_inefficient)
        
        # Assert
        assert result["data"]["analysis"]["tax_efficiency"].status.value is False
        assert len(result["data"]["analysis"]["tax_efficiency"].advices) == 3
        assert "mutual fund" in result["data"]["analysis"]["tax_efficiency"].advices[0].lower()
    
    def test_agent_initializes_analysis_dict(self, mock_state_tax_efficient):
        """Test that agent initializes analysis dictionary if not present."""
        # Remove analysis dict
        if "analysis" in mock_state_tax_efficient["data"]:
            del mock_state_tax_efficient["data"]["analysis"]
        
        mock_response = AnalysisAgent(
            status=Status(key="is_tax_efficient", value=True),
            reasoning="Test",
            advices=[]
        )
        
        mock_llm = Mock()
        mock_llm.with_structured_output.return_value.invoke.return_value = mock_response
        mock_state_tax_efficient["metadata"]["analyst_llm_agent"] = mock_llm
        
        # Execute
        result = analyze_tax_efficiency(mock_state_tax_efficient)
        
        # Assert dict was created
        assert "analysis" in result["data"]
        assert "tax_efficiency" in result["data"]["analysis"]
    
    def test_show_reasoning_flag(self, mock_state_tax_efficient, capsys):
        """Test that reasoning is printed when flag is set."""
        mock_response = AnalysisAgent(
            status=Status(key="is_tax_efficient", value=True),
            reasoning="Detailed tax efficiency reasoning here",
            advices=[]
        )
        
        mock_llm = Mock()
        mock_llm.with_structured_output.return_value.invoke.return_value = mock_response
        mock_state_tax_efficient["metadata"]["analyst_llm_agent"] = mock_llm
        mock_state_tax_efficient["metadata"]["show_reasoning"] = True
        
        # Execute
        analyze_tax_efficiency(mock_state_tax_efficient)
        
        # Assert
        captured = capsys.readouterr()
        assert "TAX EFFICIENCY ANALYSIS" in captured.out
        assert "Detailed tax efficiency reasoning" in captured.out
    
    def test_llm_invocation(self, mock_state_tax_efficient):
        """Test that LLM is invoked with correct parameters."""
        mock_response = AnalysisAgent(
            status=Status(key="is_tax_efficient", value=True),
            reasoning="Test",
            advices=[]
        )
        
        mock_llm = Mock()
        mock_llm.with_structured_output.return_value.invoke.return_value = mock_response
        mock_state_tax_efficient["metadata"]["analyst_llm_agent"] = mock_llm
        
        # Execute
        analyze_tax_efficiency(mock_state_tax_efficient)
        
        # Assert
        mock_llm.with_structured_output.assert_called_once_with(AnalysisAgent)
        assert mock_llm.with_structured_output.return_value.invoke.called
```

### 4. Run Tests

```bash
# Run specific tests
pytest tests/test_nodes/test_tax_efficiency.py -v

# Run with coverage
pytest tests/test_nodes/test_tax_efficiency.py --cov=src/nodes/analyst_agents/tax_efficiency --cov-report=term-missing

# Run all tests
pytest tests/ -v
```

### 5. Manual Testing

```bash
# Test the full workflow
run-advisor --show-reasoning
```

## Resources

### LangGraph Documentation
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [StateGraph Guide](https://langchain-ai.github.io/langgraph/reference/graphs/)
- [State Management](https://langchain-ai.github.io/langgraph/how-tos/state-reducers/)

### Financial Analysis
- [Investopedia](https://www.investopedia.com/) - Financial concepts and metrics
- [CFA Institute](https://www.cfainstitute.org/) - Professional standards
- [Morningstar](https://www.morningstar.com/) - Fund analysis methodologies

### Project Resources
- [Contributing Guide](CONTRIBUTING.md) - General contribution guidelines
- [Docker Setup](docs/DOCKER.md) - Development environment setup
- [README](README.md) - Project overview and quick start
- [Security Policy](SECURITY.md) - Security guidelines

### API Documentation
- [Polygon.io API](https://polygon.io/docs) - Market data API
- [OpenAI API](https://platform.openai.com/docs) - LLM integration
- [LangChain](https://python.langchain.com/docs/get_started/introduction) - LLM framework

## Getting Help

### Common Questions

**Q: How do I test my agent without running the full workflow?**
```bash
# Use pytest with your specific test file
pytest tests/test_nodes/test_your_agent.py -v -s
```

**Q: My agent isn't being called in the workflow. What's wrong?**
- Check that you imported it in `analysis_workflow.py`
- Verify you added the node: `workflow.add_node("your_node", your_agent.analyze_your_feature)`
- Confirm edges are set: `workflow.add_edge("start", "your_node")` and `workflow.add_edge("your_node", "analyst")`

**Q: How do I access portfolio data in my agent?**
```python
portfolio = state["data"]["portfolio"]
holdings = portfolio.holdings  # List of Holding objects
strategy = portfolio.strategy  # Strategy object
```

**Q: Should I create a new model or use AnalysisAgent?**
- Use `AnalysisAgent` for most cases (90% of agents)
- Create custom model only if you need additional structured fields beyond status/reasoning/advices

**Q: How do I handle missing data?**
```python
# Check if data exists
if "portfolio" not in state["data"]:
    raise ValueError("Portfolio data required")

# Check portfolio has holdings
if not state["data"]["portfolio"].holdings:
    return {
        "status": Status(key="is_your_metric", value=False),
        "reasoning": "Cannot analyze empty portfolio",
        "advices": ["Add holdings to portfolio"]
    }
```

### Support Channels

- **GitHub Issues**: Report bugs or request features
- **GitHub Discussions**: Ask questions, share ideas
- **Pull Requests**: Suggest improvements to this guide
- **Tag Maintainers**: @matvix90 for guidance on complex agents

## Conclusion

You now have everything you need to create new analyst agents for the AI Robo Advisor! 

### Quick Start Checklist

To add a new agent:
1. ✅ Create `src/nodes/analyst_agents/your_agent.py`
2. ✅ Implement `analyze_your_feature(state: State) -> State`
3. ✅ Import and add to `analysis_workflow.py`
4. ✅ Update `is_approved()` if needed
5. ✅ Write tests in `tests/test_nodes/test_your_agent.py`
6. ✅ Run tests: `pytest tests/ -v`
7. ✅ Manual test: `run-advisor --show-reasoning`
8. ✅ Submit pull request

### Remember

- **Educational Purpose**: This is a learning project, not financial advice
- **Security First**: Never commit API keys or sensitive data
- **Test Thoroughly**: 80%+ coverage required
- **Document Well**: Clear docstrings and comments
- **Ask Questions**: Community is here to help!

---

**Happy Coding! 🚀**

*This guide is maintained by the AI Robo Advisor community. Contributions and improvements welcome!*

**Disclaimer**: This project is for educational and research purposes only. It does not constitute financial advice. Always consult qualified financial professionals before making investment decisions.