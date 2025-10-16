# 🤖 GitHub Copilot Instructions — AI Robo Advisor

## 🧭 Project Overview

**AI Robo Advisor** is a Python-based intelligent financial assistant that uses **LangChain**, **LangGraph**, and multiple **Large Language Model (LLM)** providers to offer explainable investment insights, portfolio suggestions, and conversational market analysis.

The project’s goal is to create a modular, extendable architecture for building **AI-powered financial advisory agents** that combine reasoning from LLMs with structured market data.

Core design principles:
- Modular design across `src/` with clean separation of concerns
- Consistent typing and data validation via **Pydantic**
- Secure environment configuration via **python-decouple**
- Multi-provider LLM integration for flexibility and benchmarking
- Emphasis on financial transparency, explainability, and reproducibility

---

## ⚙️ Frameworks and Dependencies

Primary frameworks and libraries:

| Purpose | Libraries |
|----------|------------|
| LLM & Agents | `langchain`, `langgraph`, `langchain-core`, `langchain-groq` |
| Configuration | `python-decouple` |
| Validation | `pydantic` |
| Testing | `pytest` |
| Data & Utilities | `pandas`, `requests`, `json`, `typing` |
| Environment | `.env` configuration for API keys (OpenAI, Groq, Anthropic, Google) |

**LLM Providers supported:**
- `OpenAI`
- `Anthropic`
- `Groq`
- `Google GenAI`

Copilot should **not introduce new dependencies** unless explicitly required.  
If suggesting a new library, it must integrate smoothly with existing LangChain abstractions.

---

## 🧩 Coding Conventions

**Language:** Python ≥ 3.10  
**Formatting:** PEP8, Black, and isort  
**Typing:** Required (use `typing.Optional`, `typing.List`, etc.)  
**Docstrings:** Google-style, concise, and action-oriented  
**Testing:** pytest with descriptive, lowercase test names

### Naming Conventions

| Element | Convention | Example |
|----------|-------------|----------|
| Classes | PascalCase | `FinancialAgent`, `LLMModel` |
| Functions | snake_case | `get_llm_model()`, `load_models()` |
| Constants | UPPER_CASE | `AVAILABLE_MODELS`, `DEFAULT_TEMPERATURE` |
| Files | lowercase_underscore | `models.py`, `data_loader.py` |
| Branches | feature-based | `feat/new-provider`, `fix/config-bug` |

---

## 🧠 Domain-Specific Context (Finance & AI)

GitHub Copilot should interpret key project terms as follows:

| Concept | Meaning |
|----------|----------|
| **Advisor** | AI agent providing portfolio or market advice |
| **Client** | End user or investor interacting with the system |
| **Asset / Security** | Stocks, ETFs, bonds, or funds analyzed |
| **Portfolio** | Collection of assets managed or analyzed |
| **Risk / Reward** | Trade-offs used in optimization logic |
| **Temperature** | Creativity control in LLM-based responses |

Copilot suggestions should:
- Keep all **financial reasoning explainable**
- Avoid generating unverified investment advice
- Use **structured data flow** (input → processing → model → output)
- Handle exceptions gracefully when querying APIs

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

## 🧾 Best Practices for Copilot-Assisted Development

When Copilot is suggesting code:

1. ✅ **Always use `config("KEY", default=None)`** for environment variables.  
   Never hardcode API keys.
2. ✅ **Wrap API logic in try/except** with descriptive error messages.
3. ✅ **Leverage `pydantic.BaseModel`** for data validation and schema consistency.
4. ✅ **Keep docstrings up-to-date** with argument/return types.
5. ✅ **Follow modular imports** — reference from `src.llm`, not from relative paths.
6. ✅ **Include unit tests** in `tests/` for every new helper or model.
7. 🚫 **Do not introduce new dependencies** without adding them to `pyproject.toml`.
8. 🚫 **Avoid direct external network calls** unless mocking or using configured APIs.

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

## 🧩 Contribution Guidelines Summary

- Follow [CONTRIBUTING.md](../CONTRIBUTING.md)
- Use `black`, `isort`, and `pytest` before submitting PRs
- Write descriptive commit messages:
  - `feat:` → new feature
  - `fix:` → bug fix
  - `docs:` → documentation only
  - `refactor:` → code restructuring
- Open PRs with **clear description + linked issue**

---

## 🔒 Environment & Security

The project uses `.env` variables for API credentials:
```
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
GROQ_API_KEY=
```

Copilot must:
- **Never** suggest embedding plaintext keys or secrets.
- **Never** store keys in code examples.
- Use `python-decouple`’s `config()` exclusively for API access.

---

## ✅ Summary

This repository powers an **AI-driven financial advisory framework** built on **LangChain**, **LangGraph**, and **Pydantic** principles.

Copilot should:
- Suggest code consistent with the existing modular architecture
- Follow PEP8, Pydantic models, and Google-style docstrings
- Use environment-based configuration, never hardcoded values
- Generate finance-aware logic (advice, portfolio handling, explainability)
- Prioritize reliability, transparency, and testability

```

```

