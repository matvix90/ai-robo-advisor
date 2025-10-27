# Agent Development Guide

Quick reference for adding new analyst agents to the AI Robo Advisor.

## Architecture Overview

Multi-agent pipeline powered by LangGraph:

```
Investment Agent → Portfolio Agent → Analyst Agents (Parallel) → Analysis Orchestrator
                                    ├─ Fees Agent
                                    ├─ Diversification Agent
                                    ├─ Alignment Agent
                                    └─ Performance Agent
```

### Core Principles
- **Function-based**: Agents are functions taking/returning `State`
- **LLM-powered**: Use structured outputs via Pydantic models
- **Parallel execution**: Analyst agents run concurrently
- **Standardized output**: All analysts return `AnalysisAgent` model

## Project Structure

```
src/nodes/analyst_agents/          # Portfolio analysis specialists
├── fees.py                       # TER analysis
├── diversification.py            # Asset/geo/sector analysis
├── alignment.py                  # Risk/time alignment
├── performance.py                # Performance metrics
└── analysis_workflow.py          # Orchestrates all analysts
```

## Quick Start: Adding New Analyst Agent

### 1. Activate Virtual Environment
```bash
source venv/bin/activate
```
**CRITICAL**: Always activate the virtual environment before any development work!

### 2. Create Agent File
```bash
touch src/nodes/analyst_agents/your_agent.py
```

### 3. Agent Template
```python
from graph.state import State
from data.models import AnalysisAgent

def analyze_your_feature(state: State) -> State:
    """Analyze specific portfolio aspect."""
    llm = state["metadata"]["analyst_llm_agent"]
    portfolio = state["data"]["portfolio"]
    
    # Initialize analysis dict
    if "analysis" not in state["data"]:
        state["data"]["analysis"] = {}
    
    prompt = f"""
    You are a financial analyst AI specializing in [your domain].
    
    ## TASK
    Analyze [specific aspect] of this portfolio: {portfolio.holdings}
    
    ## REQUIREMENTS
    - Set status key as "is_[your_metric]"
    - Set value to `true` ONLY if [conditions met]
    - Provide `advices` list if improvements needed (empty if none)
    - Include detailed `reasoning`
    """
    
    response = llm.with_structured_output(AnalysisAgent).invoke(prompt)
    
    if state["metadata"]["show_reasoning"]:
        print(response.reasoning)
    
    state["data"]["analysis"]["your_key"] = response
    return state
```

### 4. Update Workflow
Add to `src/nodes/analyst_agents/analysis_workflow.py`:

```python
# Import your agent
from . import your_agent

# Add to create_analyst_graph()
workflow.add_node("your_feature", your_agent.analyze_your_feature)
workflow.add_edge("start", "your_feature")
workflow.add_edge("your_feature", "analyst")
```

### 5. Write Tests
Create `tests/test_nodes/test_your_agent.py`:

```python
import pytest
from unittest.mock import Mock
from src.nodes.analyst_agents.your_agent import analyze_your_feature
from src.data.models import AnalysisAgent, Status

def test_analyze_success(sample_state):
    # Setup mock LLM
    mock_response = AnalysisAgent(
        status=Status(key="is_your_metric", value=True),
        reasoning="Test reasoning",
        advices=[]
    )
    
    mock_llm = Mock()
    mock_llm.with_structured_output.return_value.invoke.return_value = mock_response
    sample_state["metadata"]["analyst_llm_agent"] = mock_llm
    
    # Execute
    result = analyze_your_feature(sample_state)
    
    # Assert
    assert "your_key" in result["data"]["analysis"]
    assert result["data"]["analysis"]["your_key"].status.value is True
```

### 6. Test & Run
```bash
# Activate virtual environment first!
source venv/bin/activate

# Test your agent
pytest tests/test_nodes/test_your_agent.py -v

# Test full workflow
run-advisor --show-reasoning
```

## Data Models & State

### State Structure
```python
state = {
    "data": {
        "portfolio": Portfolio,           # Portfolio with holdings
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
        "analyst_llm_agent": LLM,
        # ... other LLM agents
    }
}
```

### AnalysisAgent Model
```python
class Status(BaseModel):
    key: str        # e.g., "is_cheaper", "is_diversified"
    value: bool     # True if passes, False if fails

class AnalysisAgent(BaseModel):
    status: Status
    reasoning: str
    advices: Optional[list[str]]  # Empty list if no improvements needed
```

## Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Files | `snake_case.py` | `tax_efficiency.py` |
| Functions | `analyze_{feature}()` | `analyze_ter()` |
| Status Keys | `is_{metric}` | `"is_tax_efficient"` |
| Analysis Keys | `snake_case` | `"tax_efficiency"` |

## Best Practices

### ✅ DO
- Activate virtual environment first: `source venv/bin/activate`
- Write clean, concise code with type hints and clear variable names
- Follow best practices: Use f-strings, list comprehensions, and Pythonic patterns
- Validate inputs and handle errors gracefully
- Respect `show_reasoning` flag
- Write comprehensive tests (80%+ coverage)
- Include educational disclaimers for investment advice

### ❌ DON'T
- Hardcode API keys or sensitive data
- Log user portfolio data
- Mix different analysis aspects in one agent
- Forget to return state from agent functions
- Skip error handling or input validation

## Examples

### Simple Numeric Analysis (Fees Agent)
```python
def analyze_ter(state: State) -> State:
    llm = state["metadata"]["analyst_llm_agent"]
    portfolio = state["data"]["portfolio"]
    
    if "analysis" not in state["data"]:
        state["data"]["analysis"] = {}
    
    prompt = f"""
    Analyze Total Expense Ratio for: {portfolio.holdings}
    
    - Find TER for each ETF (as decimal: 0.25% = 0.0025)
    - Status true ONLY if ALL TERs < 0.004 (0.4%)
    - Recommend alternatives if TER ≥ 0.0045 (0.45%)
    """
    
    response = llm.with_structured_output(AnalysisAgent).invoke(prompt)
    
    if state["metadata"]["show_reasoning"]:
        print(response.reasoning)
    
    state["data"]["analysis"]["expense_ratio"] = response
    return state
```

## Testing Guidelines

### Required Tests
- ✅ Success case (status=True)
- ✅ Failure case (status=False) 
- ✅ Empty portfolio edge case
- ✅ Show reasoning flag
- ✅ LLM invocation verification

### Test Commands
```bash
# Activate virtual environment first!
source venv/bin/activate

# Test specific agent
pytest tests/test_nodes/test_your_agent.py -v

# Check coverage
pytest --cov=src/nodes/analyst_agents/your_agent --cov-fail-under=80

# Run all tests
pytest tests/ -v
```

## Security Guidelines

### Environment Variables
```python
# ✅ Store secrets in .env
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("POLYGON_API_KEY")

# ❌ Never hardcode
API_KEY = "sk-1234567890"  # NEVER!
```

### Input Validation
```python
def analyze_feature(state: State) -> State:
    if "portfolio" not in state["data"]:
        raise ValueError("Portfolio data missing")
    
    if not state["data"]["portfolio"].holdings:
        raise ValueError("Portfolio has no holdings")
    
    # Your analysis...
```

### Educational Disclaimer
```python
DISCLAIMER = """
⚠️ EDUCATIONAL PURPOSE ONLY
This analysis is for educational purposes only.
Not financial advice. Consult qualified professionals.
"""
```

## Contribution Checklist

### Code Quality
- [ ] Function named `analyze_{feature}(state: State) -> State`
- [ ] Initializes `state["data"]["analysis"]` if needed
- [ ] Returns `AnalysisAgent` with proper status key
- [ ] Respects `show_reasoning` flag
- [ ] Clean code with type hints and docstrings

### Integration
- [ ] Added to `analysis_workflow.py` imports
- [ ] Node and edges added to workflow graph
- [ ] Updated `is_approved()` if contributing to score

### Testing
- [ ] Test file: `tests/test_nodes/test_your_agent.py`
- [ ] Tests for success, failure, edge cases
- [ ] Coverage ≥ 80%
- [ ] All tests pass

### Documentation
- [ ] Clear docstring and comments
- [ ] Updated AGENTS.md if needed

### Security
- [ ] No hardcoded secrets
- [ ] Input validation
- [ ] Educational disclaimer for investment advice

## Quick Reference

### Development Commands
```bash
# Activate virtual environment first!
source venv/bin/activate

# Create agent
touch src/nodes/analyst_agents/your_agent.py

# Test agent
pytest tests/test_nodes/test_your_agent.py -v

# Check coverage
pytest --cov=src/nodes/analyst_agents/your_agent --cov-fail-under=80

# Run full workflow
run-advisor --show-reasoning
```

### Resources
- [LangGraph Docs](https://docs.langchain.com/oss/python/langgraph/overview)
- [CONTRIBUTING.md](CONTRIBUTING.md) - General guidelines
- [README.md](README.md) - Project overview
- [Polygon.io API](https://polygon.io/docs) - Market data

---

**Educational Disclaimer**: This project is for educational and research purposes only. It does not constitute financial advice. Always consult qualified financial professionals before making investment decisions.