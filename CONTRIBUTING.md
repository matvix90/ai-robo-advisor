# Contributing to AI Robo Advisor 🤖

Thank you for your interest in contributing to the AI Robo Advisor project! We welcome contributions from developers of all skill levels. This document provides comprehensive guidelines on how to contribute effectively to this open-source financial advisory tool.

## Table of Contents

- [How to Contribute](#how-to-contribute)
- [Getting Started](#-getting-started)
- [Development Workflow](#-development-workflow)
- [Creating Quality Pull Requests](#-creating-quality-pull-requests)
- [Code Standards](#-code-standards)
- [Testing Guidelines](#-testing-guidelines)
- [Documentation](#-documentation)
- [Priority Features](#priority-features-to-work-on)
- [Security Guidelines](#-security-guidelines)
- [Hacktoberfest Guidelines](#-hacktoberfest-guidelines)

## How to Contribute

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

### Ways to Contribute

- 🐛 **Bug Reports**: Report bugs and issues with detailed information
- ✨ **Feature Requests**: Suggest new features or improvements
- 📖 **Documentation**: Improve documentation, examples, and guides
- 💻 **Code Contributions**: Fix bugs, implement features, or optimize performance
- 🧪 **Testing**: Write tests and improve test coverage
- 🎨 **UI/UX**: Improve user interface and experience
- 🔧 **DevOps**: Improve CI/CD, Docker, deployment processes
- 🌍 **Localization**: Add multi-language support

### 🎃 Hacktoberfest Guidelines

**For contributors participating in Hacktoberfest:**

Please read our detailed Hacktoberfest guidelines and contribution rules:
👉 [Hacktoberfest Guidelines](https://github.com/matvix90/ai-robo-advisor/discussions/15)

**Key Hacktoberfest Rules:**
- All PRs must be meaningful and add value
- No spam or low-quality contributions
- Focus on priority features listed below
- Follow all guidelines in this document

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

## 🔄 Development Workflow

### 1. Fork and Clone

1. **Fork the repository** on GitHub by clicking the "Fork" button
2. **Clone your fork locally:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/ai-robo-advisor.git
   cd ai-robo-advisor
   ```
3. **Add upstream remote:**
   ```bash
   git remote add upstream https://github.com/matvix90/ai-robo-advisor.git
   ```

### 2. Set Up Development Environment

1. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -e .
   pip install -e ".[dev]"
   pip install -e ".[test]"
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Add your API keys to .env file
   ```

4. **Verify setup:**
   ```bash
   # Test the application
   run-advisor --show-reasoning
   
   # Run the test suite
   python -m pytest tests/
   ```

### 3. Create Feature Branch

**Always create a new branch for your work:**

```bash
# Keep your main branch up to date
git checkout main
git pull upstream main

# Create and switch to feature branch
git checkout -b feature/descriptive-name
# or for bug fixes:
git checkout -b bugfix/issue-description
# or for documentation:
git checkout -b docs/documentation-improvement
```

**Branch naming conventions:**
- `feature/add-european-etf-support`
- `bugfix/fix-portfolio-calculation`
- `docs/update-contributing-guide`
- `refactor/improve-llm-integration`
- `test/add-integration-tests`

### 4. Make Changes

- Write clean, readable, and well-documented code
- Follow existing code style and conventions
- Add comprehensive comments for complex logic
- Update documentation when needed
- **Write tests for all new functionality**

### 5. Test Your Changes

**Critical:** All changes must be thoroughly tested before submission.

```bash
# Run full test suite
python -m pytest tests/ -v

# Run tests with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Test specific functionality
python -m pytest tests/test_nodes.py -k "test_portfolio"

# Run the application to ensure it works
run-advisor --show-reasoning
```

## 🚀 Creating Quality Pull Requests

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

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions
- **Edge Cases**: Test boundary conditions and error scenarios
- **Regression Tests**: Ensure existing functionality still works

```bash
# Add tests for your new functionality
# tests/test_your_feature.py

# Run tests to ensure everything passes
python -m pytest tests/ -v

# Check test coverage for your changes
python -m pytest tests/ --cov=src --cov-report=term-missing

# Ensure coverage is above 90% for new code
python -m pytest tests/ --cov=src --cov-fail-under=90
```

#### 3. Code Quality Checks

**Before submitting, ensure your code meets quality standards:**

```bash
# Run linting (if configured)
flake8 src/ tests/

# Check imports and formatting
python -m pytest tests/ --cov=src

# Verify all tests pass
python -m pytest tests/ -v
```

#### 4. Documentation Updates

**Update documentation for any new features or changes:**

- Update docstrings for new functions/classes
- Update README.md if needed
- Add examples for new functionality
- Update API documentation
- Update this CONTRIBUTING.md if adding new processes

### Commit Message Guidelines

**Follow conventional commit format for clear history:**

```bash
# Format: <type>(<scope>): <description>
# 
# <optional body>
#
# <optional footer>

# Examples:
git commit -m "feat(portfolio): add European ETF support

- Add support for UCITS ETFs
- Implement EUR currency handling
- Update portfolio analysis for European markets

Closes #123"

git commit -m "fix(llm): resolve API timeout issues

- Increase timeout to 30 seconds
- Add retry mechanism for failed requests
- Improve error handling

Fixes #456"

git commit -m "docs(readme): update installation instructions

- Add Python 3.11 support
- Update dependency requirements
- Fix typos in setup section"

git commit -m "test(nodes): add comprehensive portfolio tests

- Add unit tests for portfolio creation
- Add integration tests for analysis workflow
- Achieve 95% test coverage for portfolio module"
```

**Commit Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring without functionality changes
- `perf`: Performance improvements
- `style`: Code style changes (formatting, etc.)
- `chore`: Maintenance tasks

### Creating the Pull Request

#### 1. Push Your Branch

```bash
git push origin feature/your-feature-name
```

#### 2. Open Pull Request on GitHub

**Fill out the PR template completely:**

**Title Format:**
```
[Type] Brief description of changes
```
Examples:
- `[Feature] Add European ETF market support`
- `[Fix] Resolve portfolio calculation accuracy issue`
- `[Docs] Update API documentation with examples`

**Description Template:**
```markdown
## 📋 Description
Brief description of what this PR accomplishes.

## 🎯 Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## 🔗 Related Issues
Closes #[issue-number]
Relates to #[issue-number]

## 🧪 Testing
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing completed
- [ ] Test coverage maintained/improved

### Test Commands Used:
```bash
python -m pytest tests/ -v
python -m pytest tests/ --cov=src --cov-report=term-missing
```

## 📝 Changes Made
- Detailed list of changes
- Include technical implementation details
- Mention any dependencies added/removed
- Note any configuration changes needed

## 🖼️ Screenshots/Examples
(If applicable, add screenshots or code examples)

## ✅ Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Code is well-commented
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] No merge conflicts
- [ ] Branch is up to date with main
```

#### 3. PR Review Process

**What happens after you submit:**

1. **Automated Checks**: CI/CD pipeline runs all tests
2. **Code Review**: Maintainers review your code
3. **Feedback**: You may receive suggestions for improvements
4. **Approval**: Once approved, your PR will be merged

**Responding to Review Feedback:**

```bash
# Make requested changes
# Commit the changes
git add .
git commit -m "fix: address review feedback

- Update variable naming
- Add error handling
- Improve documentation"

# Push updates
git push origin feature/your-feature-name
```

### PR Best Practices

#### ✅ DO:
- Keep PRs focused and small (< 400 lines when possible)
- Write clear, descriptive titles and descriptions
- Include tests for all new functionality
- Update documentation
- Respond promptly to review feedback
- Keep your branch up to date with main
- Test your changes thoroughly
- Follow code style guidelines

#### ❌ DON'T:
- Submit PRs with failing tests
- Include unrelated changes
- Add dependencies without discussion
- Submit large PRs that are hard to review
- Ignore review feedback
- Force push after review has started
- Submit PRs without proper testing

### Common PR Issues and Solutions

#### Issue: Merge Conflicts
```bash
# Solution: Update your branch with main
git checkout main
git pull upstream main
git checkout feature/your-branch
git merge main
# Resolve conflicts, then:
git add .
git commit -m "resolve merge conflicts"
git push origin feature/your-branch
```

#### Issue: Failing Tests
```bash
# Solution: Fix tests locally first
python -m pytest tests/ -v
# Fix any failing tests, then:
git add .
git commit -m "fix: resolve failing tests"
git push origin feature/your-branch
```

#### Issue: Low Test Coverage
```bash
# Solution: Add more tests
python -m pytest tests/ --cov=src --cov-report=term-missing
# Add tests for uncovered lines, then commit
```

---

## 📝 Code Standards

### Python Style Guidelines

**Follow PEP 8 and project conventions:**

```python
# Naming: snake_case for variables/functions, PascalCase for classes
user_portfolio = Portfolio()
def calculate_risk_score(): pass
class PortfolioAnalyzer: pass

# Constants: UPPER_CASE
MAX_PORTFOLIO_SIZE = 50
API_TIMEOUT = 30

# Documentation example
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

## 🧪 Testing Guidelines

## 🧪 Testing Guidelines

**All contributions must include comprehensive tests!** Maintain 90%+ coverage for new code.

### Test Requirements & Commands

```bash
# Run all tests
python -m pytest tests/ -v

# Run by category  
python -m pytest tests/ -m unit           # Unit tests
python -m pytest tests/ -m integration    # Integration tests

# Coverage reports
python -m pytest tests/ --cov=src --cov-report=html
python -m pytest tests/ --cov=src --cov-fail-under=90
```

### Writing Quality Tests

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

@pytest.mark.integration
class TestFeatureIntegration:
    """Integration tests."""
    
    def test_full_workflow(self, sample_portfolio):
        """Test complete workflow."""
        result = run_analysis_workflow(sample_portfolio)
        assert result.status == "complete"
```

### Available Fixtures

- `sample_state`: Basic state dictionary
- `sample_portfolio`: Portfolio with sample holdings  
- `mock_llm`: Mocked LLM agent
- `mock_llm_with_strategy_response`: LLM returning strategy

### Testing Best Practices

**✅ DO:**
- Write tests for all new functionality
- Test both success and error scenarios
- Use descriptive test names
- Mock external dependencies
- Test edge cases and boundaries

**❌ DON'T:**
- Write tests that depend on external services
- Create tests that depend on execution order
- Skip testing error conditions
- Write overly complex tests

## 📚 Documentation Requirements

**All code must include proper documentation:**

- **Functions**: Include docstrings with Args, Returns, Raises, and Examples
- **Classes**: Document purpose, attributes, and usage patterns  
- **README**: Update for new features and installation requirements
- **API**: Document public methods with types and examples

## 🔒 Security Guidelines

**Essential security practices:**

```python
# ✅ Environment variables for secrets
API_KEY = os.getenv("POLYGON_API_KEY")
if not API_KEY:
    raise ValueError("API_KEY required")

# ✅ Input validation  
def validate_input(data: dict):
    required = ["holdings", "total_value"]
    for field in required:
        if field not in data:
            raise ValueError(f"Missing: {field}")
    
    if float(data["total_value"]) <= 0:
        raise ValueError("Value must be positive")
```

**Security Checklist:**
- ✅ Use environment variables for secrets
- ✅ Validate all user inputs
- ✅ Handle errors without exposing internals
- ✅ Use HTTPS for API calls
- ❌ Never commit secrets to git
- ❌ Never trust user input without validation



## Thank You 🙏

Thank you for contributing to AI Robo Advisor! Your efforts help democratize access to professional-grade investment analysis tools and make financial planning more accessible to everyone.

### Recognition

All contributors are recognized in our:
- GitHub contributors list
- Release notes for significant contributions
- Special mentions for innovative features or major improvements

### Community

Join our community:
- 💬 **Discussions**: Share ideas and ask questions
- 🐛 **Issues**: Report bugs and request features  
- 📧 **Email**: Reach out to maintainers for complex questions
- 🌟 **Star the repo**: Show your support!

---

**⚠️ Disclaimer**: This project is for educational and research purposes only. It should not be considered as financial advice. Contributors should not provide financial advice through their contributions. Always consult with qualified financial professionals before making investment decisions.