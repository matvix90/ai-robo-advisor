# 🤖 GitHub Copilot Instructions — AI Robo Advisor

## 🧭 Project Overview

**AI Robo Advisor** is a Python-based intelligent financial assistant that uses **LangChain**, **LangGraph**, and multiple **Large Language Model (LLM)** providers to offer explainable investment insights, portfolio suggestions, and conversational market analysis.

The project’s goal is to create a modular, extendable architecture for building **AI-powered financial advisory agents** that combine reasoning from LLMs with structured market data.

---

---

## Architecture
The application follows a **modular, layered design**:

- **Frontend / Interface Layer** – Conversational UI or CLI for user input and report display.  
- **Core Logic Layer** – Handles financial computations, portfolio simulation, and recommendation strategies.  
- **AI Layer** – LangGraph agent network for intent detection, query routing, and contextual response generation.  
- **Data Layer** – Integrations with external financial APIs (Alpha Vantage, Yahoo Finance, Polygon.io) for live and historical data.  
- **Storage Layer** – SQLite / PostgreSQL for caching and portfolio persistence.

Copilot should keep modules loosely coupled and easily testable.

---

## Key Components
| Directory | Description |
|------------|--------------|
| `src/main.py` | Application entry point – initializes agents, pipelines, and I/O interface. |
| `src/agents/` | LangGraph agent nodes handling user intents (risk, allocation, summary). |
| `src/core/` | Core financial logic and computational models. |
| `src/services/` | API connectors for market data and user portfolio information. |
| `src/utils/` | Logging, error handling, and helper utilities. |
| `tests/` | Unit and integration tests. |


---

## 🧩 Coding Conventions

**Language:** Python ≥ 3.10  
**Formatting:** PEP8, Black, and isort  
**Typing:** Required (use `typing.Optional`, `typing.List`, etc.)  
**Docstrings:** Google-style, concise, and action-oriented  
**Testing:** pytest with descriptive, lowercase test names

---


## Common Patterns
- **Pipeline Pattern** – For chaining computations: data → analysis → recommendation.  
- **Factory Pattern** – For dynamically creating strategy or agent instances.  
- **Observer Pattern** – For streaming live market updates.  
- **Repository Pattern** – For abstracting data access from business logic.

Copilot should prefer these patterns when suggesting architecture-level code.

---


## File Naming Conventions
| File Type | Naming Rule | Example |
|------------|--------------|----------|
| Python Modules | `snake_case.py` | `portfolio_optimizer.py` |
| Test Files | `test_<module>.py` | `test_portfolio_optimizer.py` |
| Config | `config.yaml` | |
| Jupyter Notebooks | `<topic>_analysis.ipynb` | `risk_analysis.ipynb` |
| Scripts | `<action>_script.py` | `fetch_data_script.py` |

---

## 🧰 Project Structure Reference

```
src/
├── llm/
│   ├── models.py          # LLM provider abstraction (OpenAI, Groq, etc.)
│   ├── api.py             # Provider availability and model metadata
│   └── __init__.py
├── agents/                # Core advisor and dialogue logic
├── data/                  # Financial data ingestion and processing
├── utils/                 # Helpers and reusable functions
tests/
├── test_llm.py            # Unit tests for model initialization
```

The **`get_llm_model()`** function is central — it dynamically initializes LLMs using API keys, temperature, and provider type.


---

## 💡 Example Patterns Copilot Should Follow

### Model Initialization
```python
from src.llm.models import get_llm_model, ModelProvider

model = get_llm_model(
    provider=ModelProvider.OPENAI,
    model_name="gpt-4o-mini",
    temperature=0.7
)
```

### Pydantic Model Example
```python
from pydantic import BaseModel

class FinancialQuery(BaseModel):
    symbol: str
    query: str
```

### API Key Pattern
```python
from decouple import config

OPENAI_API_KEY = config("OPENAI_API_KEY", default=None)
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY in environment")
```

### Test Example
```python
def test_model_loading():
    from src.llm.models import load_models
    models = load_models()
    assert len(models.models) > 0
```


---

## Key Dependencies
- **Core:** `python >= 3.10`, `langgraph`, `pandas`, `numpy`, `scikit-learn`
- **APIs:** `requests`, `alpha_vantage`, `yfinance`, `polygon-api-client`
- **AI:** `transformers`, `sentence-transformers`, `openai`
- **Visualization:** `plotly`, `matplotlib`, `streamlit`
- **Testing:** `pytest`, `coverage`


---

   
## Environment Setup

# Clone repository
```bash
git clone https://github.com/matvix90/ai-robo-advisor.git
cd ai-robo-advisor
```
# Create and activate virtual environment
```
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```
# Install dependencies
```
pip install -r requirements.txt  # or: poetry install
```
# Set environment variables
```
export ALPHA_VANTAGE_KEY="your_api_key_here"
```
# Run all tests
```
pytest -v
```
# Run tests with coverage
```
pytest --cov=src
```
# Run a single module test
```
pytest tests/test_portfolio_optimizer.py
```
All new code should pass unit tests before submission.

---

## Testing Commands

Use the following commands before committing or pushing new code:


# 1. Run all tests
```
pytest -v
```
# 2. Run tests with coverage report
```
pytest --cov=src --cov-report=term-missing
```
# 3. Run tests for a single module
```
pytest tests/test_portfolio_optimizer.py -v
```
# 4. Check code style with flake8
```
flake8 src tests
```
# 5. Auto-format code with Black
```
black src tests
```
# 6. Static type checking
```
mypy src
```
# 7. Run all quality checks together
```
pytest --cov=src && flake8 src && mypy src
```

All commits should pass these checks before opening a pull request.
