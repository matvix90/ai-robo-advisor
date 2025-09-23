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

6. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Add your API keys to .env file
   ```

7. **Test the setup:**
   ```bash
   run-advisor --show-reasoning
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

```bash
# Run the application to ensure it works
python src/main.py

# If you've added tests, run them
# python -m pytest tests/  # (when test suite is implemented)
```

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

### 6. Testing Framework
- Unit tests for core functionality

## Thank You

Thank you for contributing to AI Robo Advisor! Your efforts help make professional-grade investment tools accessible to everyone.

---

**Disclaimer:** This project is for educational and research purposes only. Contributors should not provide financial advice through their contributions.