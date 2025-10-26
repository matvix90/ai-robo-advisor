# Contributing to AI Robo Advisor 🤖

Thank you for your interest in contributing! We welcome contributions from developers of all skill levels.


## Table of Contents


- [How to Contribute](#how-to-contribute)
- [Hacktoberfest Guidelines](#hacktoberfest-guidelines)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Creating Quality Pull Requests](#creating-quality-pull-requests)
- [Code Standards](#code-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Requirements](#documentation-requirements)
- [Security Guidelines](#security-guidelines)
- [Thank You](#thank-you)
- [Community](#community)




<a id="how-to-contribute"></a>

## Ways to Contribute

- 🐛 **Bug Reports**: Report bugs with detailed information
- ✨ **Feature Requests**: Suggest new features or improvements
- 📖 **Documentation**: Improve docs, examples, and guides
- 💻 **Code**: Fix bugs, implement features, or optimize performance
- 🧪 **Testing**: Write tests and improve coverage
- 🎨 **UI/UX**: Improve user interface and experience
- 🔧 **DevOps**: Improve CI/CD, Docker, deployment processes
- 🌍 **Localization**: Add multi-language support

<a id="hacktoberfest-guidelines"></a>

##  Hacktoberfest Guidelines

### 🎃 Hacktoberfest Participants

All PRs must be meaningful and add value. Read our detailed guidelines:
👉 [Hacktoberfest Guidelines](https://github.com/matvix90/ai-robo-advisor/discussions/15)

**Key Hacktoberfest Rules:**
- All PRs must be meaningful and add value
- No spam or low-quality contributions
- Focus on priority features listed below
- Follow all guidelines in this document

<a id="getting-started"></a>

##  Getting Started

### Initial Setup

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
<a id="development-workflow"></a>

##  Development Workflow

### 1. Fork and Clone

1. **Fork the repository** on GitHub by clicking the "Fork" button
2. **Clone your fork locally:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/ai-robo-advisor.git
   cd ai-robo-advisor
   git remote add upstream https://github.com/matvix90/ai-robo-advisor.git
   ```

2. **Set up Python environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev,test]"
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Add your API keys to .env file
   ```

4. **Verify setup:**
   ```bash
   run-advisor --show-reasoning
   python -m pytest tests/ -v
   ```

## 🔄 Development Workflow

### 1. Create Feature Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/descriptive-name
```

**Branch naming conventions:**
- `feature/add-european-etf-support` - New features
- `bugfix/fix-portfolio-calculation` - Bug fixes
- `docs/update-contributing-guide` - Documentation
- `refactor/improve-llm-integration` - Refactoring
- `test/add-integration-tests` - Tests

### 2. Make Changes

- Write clean, readable, well-documented code
- Follow existing code style and conventions
- Add comprehensive comments for complex logic
- **Write tests for all new functionality**

### 3. Test Thoroughly

```bash
# Run full test suite
python -m pytest tests/ -v

# Check coverage
python -m pytest tests/ --cov=src --cov-report=html

# Test manually
run-advisor --show-reasoning
```

<a id="creating-quality-pull-requests"></a>

##  Creating Quality Pull Requests

This section provides comprehensive guidelines for creating high-quality PRs that will be accepted quickly and efficiently.

### Before Creating a PR

#### 1. Sync with Main Branch

**Always ensure your branch is up to date with the latest main branch:**

```bash
# Switch to main and update
git checkout main
git pull upstream main

# Switch back to your feature branch
git checkout feature/your-feature-name

# Merge or rebase main into your branch
git merge main
# OR (preferred for cleaner history):
git rebase main
```

#### 2. Update Test Suite

**All new functionality must include comprehensive tests:**

Follow conventional commit format:

```bash
git commit -m "feat(portfolio): add European ETF support

- Add support for UCITS ETFs
- Implement EUR currency handling
- Update portfolio analysis for European markets

Closes #123"
```

**Commit types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `test` - Tests
- `refactor` - Refactoring
- `perf` - Performance
- `style` - Formatting
- `chore` - Maintenance

## � Pull Request Guidelines

### Before Submitting

1. **Sync with upstream:**
   ```bash
   git checkout main
   git pull upstream main
   git checkout feature/your-feature-name
   git rebase main  # Preferred for cleaner history
   ```

2. **Ensure tests pass:**
   ```bash
   python -m pytest tests/ -v
   python -m pytest tests/ --cov=src --cov-fail-under=90
   ```

3. **Update documentation:**
   - Add/update docstrings
   - Update README.md if needed
   - Add usage examples

### Creating the PR

1. **Push your branch:**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Use clear PR title:**
   - `[Feature] Add European ETF market support`
   - `[Fix] Resolve portfolio calculation accuracy issue`
   - `[Docs] Update API documentation with examples`

3. **Complete PR description:**

```markdown
## Description
Brief description of what this PR accomplishes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #123

## Testing
- [ ] All existing tests pass
- [ ] New tests added
- [ ] Manual testing completed
- [ ] Coverage maintained/improved

## Changes Made
- List specific changes
- Include technical details
- Note any new dependencies
```

### PR Best Practices

**✅ DO:**
- Keep PRs focused and small (< 400 lines)
- Write clear, descriptive titles and descriptions
- Include tests for all new functionality
- Respond promptly to review feedback
- Keep your branch up to date

**❌ DON'T:**
- Submit PRs with failing tests
- Include unrelated changes
- Add dependencies without discussion
- Submit large, hard-to-review PRs
- Ignore review feedback

### Common Issues & Solutions

**Merge conflicts:**
```bash
git checkout main && git pull upstream main
git checkout feature/your-branch && git merge main
# Resolve conflicts, then:
git add . && git commit -m "resolve merge conflicts"
git push origin feature/your-branch
```

**Failing tests:**
```bash
python -m pytest tests/ -v  # Fix failing tests locally first
git add . && git commit -m "fix: resolve failing tests"
git push origin feature/your-branch
```

#### Issue: Low Test Coverage
```bash
# Solution: Add more tests
python -m pytest tests/ --cov=src --cov-report=term-missing
# Add tests for uncovered lines, then commit
```

---

<a id="code-standards"></a>

##  Code Standards

### Python Style

Follow PEP 8 conventions:

```python
# Naming conventions
user_portfolio = Portfolio()              # snake_case for variables/functions
class PortfolioAnalyzer: pass            # PascalCase for classes
MAX_PORTFOLIO_SIZE = 50                  # UPPER_CASE for constants

# Import order
import json                              # Standard library
import numpy as np                       # Third-party
from src.data.models import Portfolio    # Local

# Documentation
def analyze_portfolio_risk(portfolio: Portfolio, strategy: Strategy) -> RiskAnalysis:
    """
    Analyze portfolio risk profile.
    
    Args:
        portfolio: Portfolio instance with holdings
        strategy: Investment strategy with risk parameters
        
    Returns:
        RiskAnalysis: Risk assessment with scores and recommendations
        
    Raises:
        ValueError: If portfolio is empty
    """
    if not portfolio.holdings:
        raise ValueError("Portfolio cannot be empty")
    return RiskAnalysis(...)
```

### Code Organization

```python
# Import order: standard library, third-party, local
import json
import logging
import numpy as np
from src.data.models import Portfolio
```

### Security Requirements

```python
# ✅ Use environment variables for secrets
API_KEY = os.getenv("POLYGON_API_KEY")
if not API_KEY:
    raise ValueError("API_KEY required")

# ✅ Validate inputs
def validate_portfolio(data: dict):
    required = ["holdings", "total_value"]
    for field in required:
        if field not in data:
            raise ValueError(f"Missing: {field}")
```
<a id="testing-guidelines"></a>

##  Testing Guidelines


**All contributions must include comprehensive tests!** Maintain 90%+ coverage for new code.

### Test Commands

```bash
# Run all tests
python -m pytest tests/ -v

# Run by category  
python -m pytest tests/ -m unit
python -m pytest tests/ -m integration

# Coverage reports
python -m pytest tests/ --cov=src --cov-report=html
python -m pytest tests/ --cov=src --cov-fail-under=90
```

### Writing Tests

```python
"""Test module docstring."""
import pytest
from unittest.mock import patch

@pytest.mark.unit
class TestFeatureName:
    """Unit tests for feature."""
    
    def test_basic_functionality(self):
        """Test happy path scenario."""
        # Arrange
        input_data = "test"
        
        # Act  
        result = function_to_test(input_data)
        
        # Assert
        assert result == expected_output
    
    def test_error_handling(self):
        """Test error conditions."""
        with pytest.raises(ValueError, match="Invalid input"):
            function_to_test(None)
    
    @patch('src.module.external_api')
    def test_with_mock(self, mock_api):
        """Test with mocked dependencies."""
        mock_api.return_value = {"status": "success"}
        result = function_to_test("input")
        assert result is not None
        mock_api.assert_called_once()
```

### Available Fixtures

- `sample_state` - Basic state dictionary
- `sample_portfolio` - Portfolio with sample holdings  
- `mock_llm` - Mocked LLM agent
- `mock_llm_with_strategy_response` - LLM returning strategy

### Best Practices

**✅ DO:**
- Write tests for all new functionality
- Test both success and error scenarios
- Use descriptive test names
- Mock external dependencies
- Test edge cases

**❌ DON'T:**
- Depend on external services
- Create order-dependent tests
- Skip error testing
- Write overly complex tests


<a id="documentation-requirements"></a>

##  Documentation Requirements

**All code must include proper documentation:**

- **Functions**: Include docstrings with Args, Returns, Raises, and Examples
- **Classes**: Document purpose, attributes, and usage patterns  
- **README**: Update for new features and installation requirements
- **API**: Document public methods with types and examples


<a id="security-guidelines"></a>

##  Security Guidelines

**Essential security practices:**

```python
# ✅ Use environment variables for secrets
import os
API_KEY = os.getenv("POLYGON_API_KEY")
if not API_KEY:
    raise ValueError("API_KEY required")

# ✅ Validate all inputs
def validate_portfolio(data: dict):
    required = ["holdings", "total_value"]
    for field in required:
        if field not in data:
            raise ValueError(f"Missing: {field}")
    
    if float(data["total_value"]) <= 0:
        raise ValueError("Value must be positive")
```

**Security checklist:**
- ✅ Use environment variables for secrets
- ✅ Validate all user inputs
- ✅ Handle errors without exposing internals
- ✅ Use HTTPS for API calls
- ❌ Never commit secrets to git
- ❌ Never trust user input without validation

<a id="thank-you"></a>

## Thank You 

Thank you for contributing to AI Robo Advisor! Your efforts help democratize access to professional-grade investment analysis tools and make financial planning more accessible to everyone.

### Recognition

Contributors are recognized in:
- GitHub contributors list
- Release notes for significant contributions
- Special mentions for major improvements

<a id="community"></a>

### Community

- 💬 **Discussions**: Share ideas and ask questions
- 🐛 **Issues**: Report bugs and request features  
- 🌟 **Star the repo**: Show your support!

---

**⚠️ Disclaimer**: This project is for educational and research purposes only. It does not constitute financial advice. Always consult qualified financial professionals before making investment decisions.