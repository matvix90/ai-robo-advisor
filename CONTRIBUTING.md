# Contributing to AI Robo Advisor 🤖

Thank you for your interest in contributing to the AI Robo Advisor project! We welcome contributions from developers of all skill levels. This document provides guidelines and information on how to contribute effectively.

## How to Contribute

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

### Ways to Contribute

- **Bug Reports**: Report bugs and issues
- **Feature Requests**: Suggest new features or improvements
- **Documentation**: Improve documentation and examples
- **Code Contributions**: Fix bugs, implement features, or optimize performance
- **Testing**: Write tests and improve test coverage
- **UI/UX**: Improve user interface and experience

### ONLY FOR CONTRIBUTORS PARTICIPATING IN HACKTOBERFEST

Here you can find the guidelines on how contributors and PR will be handled:

https://github.com/matvix90/ai-robo-advisor/discussions/15

## 🚀 Getting Started

### Setting Up Development Environment

1. **Fork the repository** on GitHub

2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/ai-robo-advisor.git
   cd ai-robo-advisor
   ```

3. **Add upstream remote:**
   ```bash
   git remote add upstream https://github.com/matvix90/ai-robo-advisor.git
   ```

4. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. **Install dependencies:**
   ```bash
   pip install -e .
   ```

6. **Install development and test dependencies:**
   ```bash
   pip install -e ".[dev]"
   pip install -e ".[test]"
   ```

7. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Add your API keys to .env file
   ```

8. **Test the setup:**
   ```bash
   # Run the application
   run-advisor --show-reasoning
   
   # Run the test suite
   python -m pytest tests/
   ```

## Contribution Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-description
# or
git checkout -b docs/documentation-improvement
```

### 2. Make Your Changes

- Write clean, readable code
- Follow existing code style and conventions
- Add comments for logic and changes
- Update documentation if needed

### 3. Test Your Changes

**All contributions must include tests!**

```bash
# Run the application to ensure it works
run-advisor

# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/ -m unit           # Unit tests only
python -m pytest tests/ -m integration    # Integration tests only

# Run tests with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Or use the test runner script
./run_tests.sh              # Run all tests
./run_tests.sh --unit       # Run unit tests
./run_tests.sh --verbose    # Verbose output
```

**Testing Requirements:**
- All new features must include unit tests
- Aim for 80%+ code coverage for new code
- Tests must pass before PR can be merged
- Include both positive and negative test cases
- Test edge cases and error conditions

---

## 🧪 Testing Guide

This project uses **pytest** for testing with a comprehensive test suite covering unit tests, integration tests, and end-to-end workflows.

### Test Structure

```
tests/
├── conftest.py                    # Shared fixtures and test configuration
├── test_models.py                 # Data model tests
├── test_nodes.py                  # Node function tests (investment, portfolio, analyst)
├── test_analyst_workflow.py       # Analyst workflow tests
├── test_workflow.py               # Main workflow tests
├── test_utils.py                  # Utility function tests
├── test_analysis_data_simple.py   # Analysis data fetching tests
├── test_display_simple.py         # Display function tests
└── test_questionnaires.py         # User interaction tests
```

### Running Tests

#### Basic Test Commands

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_nodes.py

# Run specific test class
python -m pytest tests/test_nodes.py::TestFeesAnalysisNode

# Run specific test function
python -m pytest tests/test_nodes.py::TestFeesAnalysisNode::test_analyze_ter_basic

# Run tests matching a pattern
python -m pytest -k "diversification"
```

#### Test Categories

Tests are organized by markers for easy filtering:

```bash
# Run only unit tests
python -m pytest -m unit

# Run only integration tests
python -m pytest -m integration

# Run tests excluding integration tests
python -m pytest -m "not integration"
```

#### Coverage Reports

```bash
# Generate coverage report in terminal
python -m pytest --cov=src --cov-report=term-missing

# Generate HTML coverage report
python -m pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser

# Generate XML coverage report (for CI/CD)
python -m pytest --cov=src --cov-report=xml

# Show coverage for specific module
python -m pytest --cov=src.utils.analysis_data --cov-report=term-missing

# Check coverage and fail if below threshold
python -m pytest --cov=src --cov-fail-under=90
```

### Writing Tests

#### Test File Naming

- Test files must start with `test_`
- Test functions must start with `test_`
- Test classes must start with `Test`

Example:
```python
# tests/test_my_feature.py
import pytest

class TestMyFeature:
    """Tests for my new feature."""
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        # Test code here
        pass
```

#### Using Fixtures

Common fixtures are defined in `conftest.py`:

```python
def test_portfolio_creation(sample_portfolio, mock_llm):
    """Test using fixtures from conftest.py."""
    # sample_portfolio: Pre-configured Portfolio instance
    # mock_llm: Mocked LLM for testing
    assert sample_portfolio.holdings is not None
```

Available fixtures:
- `sample_state`: Basic state dictionary
- `sample_state_with_portfolio`: State with portfolio data
- `sample_portfolio`: Portfolio instance with sample holdings
- `sample_strategy`: Investment strategy instance
- `mock_llm`: Mocked LLM agent
- `mock_llm_with_strategy_response`: LLM mock returning strategy

#### Mocking Best Practices

```python
from unittest.mock import Mock, patch, MagicMock

# Mock LLM responses
def test_with_mock_llm(mock_llm):
    """Test with mocked LLM."""
    # Setup mock response
    mock_llm.invoke.return_value = AnalysisAgent(
        status=Status(key="is_aligned", value=True),
        reasoning="Test reasoning",
        advices=[]
    )
    
    # Use in test
    result = my_function(state)
    
    # Verify mock was called
    mock_llm.invoke.assert_called_once()

# Patch external dependencies
@patch('src.tools.polygon_api.fetch_histories_concurrently')
def test_with_patched_api(mock_fetch):
    """Test with patched API call."""
    mock_fetch.return_value = {"AAPL": {"data": [...]}}
    # Test code here
```

#### Test Coverage Guidelines

When adding new code, ensure:

1. **Line Coverage**: Aim for 90%+ coverage
2. **Branch Coverage**: Test both if/else paths
3. **Error Handling**: Test error cases and exceptions
4. **Edge Cases**: Test boundary conditions

Example:
```python
def test_validation_valid_input():
    """Test with valid input."""
    result = validate_amount("1000")
    assert result is True

def test_validation_invalid_input():
    """Test with invalid input."""
    result = validate_amount("abc")
    assert result == "Please enter a valid number"

def test_validation_empty_input():
    """Test with empty input."""
    result = validate_amount("")
    assert result == "Please enter an amount"

def test_validation_negative_input():
    """Test with negative amount."""
    result = validate_amount("-100")
    assert result == "Amount must be greater than 0"
```

#### Testing Async Code

For async functions:
```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test async function."""
    result = await my_async_function()
    assert result is not None
```

#### Testing Console Output

Use `capsys` fixture to test printed output:
```python
def test_print_output(capsys):
    """Test console output."""
    print_portfolio(portfolio)
    captured = capsys.readouterr()
    assert "PORTFOLIO" in captured.out
```

### Continuous Integration

Tests are automatically run on every push and pull request. Ensure:

1. All tests pass locally before pushing
2. No test failures in CI/CD pipeline
3. Coverage threshold is maintained (90%+)
4. No new warnings are introduced

### Test Coverage Status

Current test coverage: **95%**
Total tests: **212 passing, 1 skipped**

Files with 100% coverage:
- `src/data/models.py`
- `src/graph/state.py`
- `src/nodes/analyst_agents/fees.py`
- `src/nodes/analyst_agents/analysis_workflow.py`
- `src/nodes/analyst_agents/diversification.py`
- `src/nodes/investment_agents/goal_based.py`
- `src/nodes/portfolios_agent.py`
- `src/utils/questionnaires.py`

Areas needing coverage improvement:
- `src/nodes/analyst_agents/performance.py` (86%)
- `src/utils/display.py` (91%)
- `src/utils/metrics.py` (91%)

### Debugging Tests

```bash
# Run tests with full output (no capture)
python -m pytest -s

# Run tests with detailed traceback
python -m pytest --tb=long

# Run tests and drop into debugger on failure
python -m pytest --pdb

# Run last failed tests only
python -m pytest --lf

# Run tests with print statements visible
python -m pytest -s -v
```

### Performance Testing

```bash
# Show slowest tests
python -m pytest --durations=10

# Time individual tests
python -m pytest --durations=0
```

### Best Practices

1. **Write tests first** (TDD approach when possible)
2. **Keep tests isolated** - don't rely on test execution order
3. **Use descriptive test names** - explain what is being tested
4. **One assertion per test** when possible
5. **Mock external dependencies** - don't make real API calls
6. **Test edge cases** - empty inputs, null values, boundaries
7. **Keep tests fast** - avoid slow operations
8. **Update tests** when changing functionality
9. **Document complex test scenarios**
10. **Review test coverage** for your changes

### Example Test Template

```python
"""
Tests for [module/feature name].
"""
import pytest
from unittest.mock import Mock, patch

from src.module import function_to_test


@pytest.mark.unit
class TestFeatureName:
    """Tests for specific feature."""

    def test_basic_functionality(self):
        """Test basic happy path."""
        # Arrange
        input_data = "test"
        
        # Act
        result = function_to_test(input_data)
        
        # Assert
        assert result == expected_output

    def test_error_handling(self):
        """Test error conditions."""
        with pytest.raises(ValueError):
            function_to_test(None)

    @patch('src.module.external_dependency')
    def test_with_mock(self, mock_dep):
        """Test with mocked dependencies."""
        # Setup mock
        mock_dep.return_value = "mocked"
        
        # Test
        result = function_to_test("input")
        
        # Verify
        assert result is not None
        mock_dep.assert_called_once()
```

---

### 4. Commit Your Changes

```bash
git add .
git commit -m "Add descriptive commit message

- Describe what you changed
- Explain why you made the change
- Reference any related issues"
```

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear title and description
- Reference to any related issues
- Screenshots if applicable
- Explanation of changes made

## Priority Features to Work On

Based on the project roadmap, these are high-priority areas for contribution:

### 1. Improve Agents & LLM Integrations
- Add support for new LLM providers
- Improve agent reasoning and decision-making

### 2. European Market Support
- Add Financial APIs for European ETFs
- Implement support for European market data

### 3. Enhanced Questionnaires
- Improve user onboarding questionnaire
- Add more sophisticated risk profiling
- Implement multi-language support

### 4. Docker Integration
- Create Dockerfile for easy deployment
- Add docker-compose for development

### 5. Web Interface
- Django backend development
- React frontend implementation
- API endpoints for workflow management

### 6. Testing & Quality
- Improve test coverage
- Add integration tests for workflows
- Implement performance benchmarks
- Add end-to-end tests

## Thank You

Thank you for contributing to AI Robo Advisor! Your efforts help make professional-grade investment tools accessible to everyone.

---

**Disclaimer:** This project is for educational and research purposes only. Contributors should not provide financial advice through their contributions.