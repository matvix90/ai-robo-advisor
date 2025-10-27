# 🤖 GitHub Copilot Instructions — AI Robo Advisor

## 🧭 Project Overview

**AI Robo Advisor** is a Python-based intelligent financial assistant using **LangChain**, **LangGraph**, and multiple **LLM providers** to offer explainable investment insights and ETF portfolio analysis.

**Goal:** Create a modular, multi-agent architecture for AI-powered financial advisory agents that combine LLM reasoning with structured market data.

---

## 🏗️ Architecture

### Multi-Agent Pipeline
```
User Input (Questionnaire)
    ↓
Investment Agent (goal_based.py) — Creates investment strategy
    ↓
Portfolio Agent (portfolios_agent.py) — Generates ETF portfolio
    ↓
Analyst Agents (Parallel Execution)
    ├─ Fees Agent (analyze_ter)
    ├─ Diversification Agent (analyze_diversification) 
    ├─ Alignment Agent (analyze_alignment)
    └─ Performance Agent (analyze_performance)
    ↓
Analysis Orchestrator (is_approved) — Aggregates results
    ↓
Final Report & Recommendations
```

### Key Principles
- **State-Driven**: All agents take and return `State` (TypedDict with `data` and `metadata`)
- **Function-Based**: Agents are functions, not classes
- **LLM-Powered**: Use structured outputs via Pydantic models
- **Parallel Execution**: Analyst agents run concurrently
- **Modular**: Easy to add new agents (see [AGENTS.md](../AGENTS.md))

---

## 📁 Project Structure

| Directory/File | Description |
|----------------|-------------|
| `src/main.py` | Application entry point |
| `src/nodes/investment_agents/` | Investment strategy creation |
| `src/nodes/portfolios_agent.py` | ETF portfolio generation |
| `src/nodes/analyst_agents/` | Portfolio analysis specialists |
| `src/graph/state.py` | State definition for LangGraph |
| `src/data/models.py` | Pydantic models |
| `src/llm/` | LLM provider abstraction |
| `src/tools/` | External API integrations (Polygon.io) |
| `src/utils/` | Helper utilities |
| `tests/` | Unit and integration tests |

---

## 🧩 Coding Conventions

**Language:** Python ≥ 3.10  
**Formatting:** Black, PEP8  
**Typing:** Required  
**Docstrings:** Google-style  
**Testing:** pytest  

### File Naming
| Type | Pattern | Example |
|------|---------|---------|
| Modules | `snake_case.py` | `portfolios_agent.py` |
| Tests | `test_<module>.py` | `test_analyst_workflow.py` |
| Agents | `analyze_{feature}()` | `analyze_ter()` |

---

## 🔧 Core Patterns

### Agent Pattern
```python
from graph.state import State
from data.models import AnalysisAgent

def analyze_feature(state: State) -> State:
    """Analyze specific aspect of portfolio."""
    llm = state["metadata"]["analyst_llm_agent"]
    portfolio = state["data"]["portfolio"]
    
    if "analysis" not in state["data"]:
        state["data"]["analysis"] = {}
    
    prompt = f"Analyze {portfolio.holdings} for specific criteria..."
    response = llm.with_structured_output(AnalysisAgent).invoke(prompt)
    
    if state["metadata"]["show_reasoning"]:
        print(response.reasoning)
    
    state["data"]["analysis"]["feature"] = response
    return state
```

### State Structure
```python
state = {
    "data": {
        "portfolio": Portfolio,
        "benchmark": tuple,
        "analysis": {
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

### Pydantic Models
```python
from pydantic import BaseModel
from typing import Optional

class Status(BaseModel):
    key: str        # e.g., "is_cheaper"
    value: bool     # True if passes, False if fails

class AnalysisAgent(BaseModel):
    status: Status
    reasoning: str
    advices: Optional[list[str]]
```

---

## 🚀 Quick Setup

### Environment
```bash
git clone https://github.com/matvix90/ai-robo-advisor.git
cd ai-robo-advisor
python -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
```

### Environment Variables
```bash
# .env file
OPENAI_API_KEY="sk-..."
POLYGON_API_KEY="your_key"
```

### Run & Test
```bash
run-advisor                     # Normal mode
run-advisor --show-reasoning    # Debug mode
pytest --cov=src               # Run tests with coverage
```

---

## 🧪 Testing Requirements

### Essential Commands
```bash
pytest -v                      # All tests
pytest tests/test_nodes.py -v  # Specific file
pytest --cov=src --cov-report=term-missing  # Coverage
black src tests                # Format code
```

### Test Pattern
```python
def test_analyze_feature_passes(sample_state):
    """Test that feature analysis passes with valid data."""
    mock_response = AnalysisAgent(
        status=Status(key="is_feature", value=True),
        reasoning="Test reasoning",
        advices=[]
    )
    
    mock_llm = Mock()
    mock_llm.with_structured_output.return_value.invoke.return_value = mock_response
    sample_state["metadata"]["analyst_llm_agent"] = mock_llm
    
    result = analyze_feature(sample_state)
    
    assert "feature" in result["data"]["analysis"]
    assert result["data"]["analysis"]["feature"].status.value is True
```

---

## 🔐 Security Best Practices

### API Keys
- ✅ Store in `.env` file (never commit)
- ✅ Use `python-decouple` for loading
- ❌ Never hardcode in source

### Data Privacy
- ✅ Keep user data local
- ❌ Never log sensitive information
- ❌ Never share API keys

### Error Handling
```python
try:
    response = llm.invoke(prompt)
except Exception as e:
    logger.error(f"LLM error: {e}")
    return default_response
```

---

## 🎯 Copilot Guidance

### When Coding, Always:
1. **Write Clean Code** - Make it shorter, cleaner, and follow best practices
2. **Activate venv** - Always `source venv/bin/activate` before running src/ or tests/
3. **Follow Agent Pattern** - Functions taking/returning `State`
4. **Use Pydantic Models** - Validate all data structures
5. **Include Tests** - All new code needs tests
6. **Handle Errors** - Graceful failure handling
7. **Document Code** - Google-style docstrings
8. **Educational Focus** - This is not financial advice

### When Adding Features:
- Check alignment with multi-agent architecture
- Follow existing patterns (see [AGENTS.md](../AGENTS.md))
- Include comprehensive tests
- Update documentation

### When Debugging:
- Verify state key paths: `state["data"]["key"]` vs `state["metadata"]["key"]`
- Check LLM structured outputs match Pydantic models
- Ensure environment variables are loaded
- Validate all analyst agents return `AnalysisAgent` model

---

## 📚 Key Resources

- **[AGENTS.md](../AGENTS.md)** - Comprehensive agent development guide
- **[CONTRIBUTING.md](../CONTRIBUTING.md)** - Contribution workflow
- **[LangGraph Docs](https://docs.langchain.com/oss/python/langgraph)** - Framework documentation
- **[Polygon.io API](https://polygon.io/docs)** - Market data API

---

## ⚖️ Disclaimer

This project is for **educational and research purposes only**. It does not constitute financial advice. Always consult qualified financial professionals before making investment decisions.

---

**Maintained by:** [@matvix90](https://github.com/matvix90) | **License:** MIT | **Version:** 0.1.0