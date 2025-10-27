# 🛡️ Security Policy

## 📌 Supported Versions

We actively support the latest version of `ai-robo-advisor` with security updates. 

| Version | Supported          | End of Life |
|---------|-------------------|-------------|
| 0.1.x   | ✅ Yes             | TBD         |
| < 0.1   | ❌ No              | Immediate   |

**Note:** As this project is in early development, we recommend always using the latest version.

---

## 📬 Reporting a Vulnerability

**🚨 Do NOT report security vulnerabilities through public GitHub issues.**

### Reporting Process

1. **Email**: Send details to the maintainer at the repository owner's GitHub email
2. **Subject**: Use `[SECURITY] AI Robo Advisor - [Brief Description]`
3. **Include**:
   - Detailed vulnerability description
   - Steps to reproduce (with minimal example)
   - Affected versions/components
   - Potential impact assessment
   - Suggested mitigation (if known)

### Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 72 hours  
- **Status Updates**: Every 5 business days
- **Resolution Target**: 30 days for critical issues

---

## � Security Scope

### In Scope
- Authentication bypass
- API key exposure or mishandling
- Dependency vulnerabilities
- Code injection via user inputs
- Data exposure through logs/outputs
- Prompt injection attacks
- Financial data manipulation

### Out of Scope
- Social engineering attacks
- Physical security issues
- Issues requiring physical access
- Third-party service vulnerabilities (OpenAI, Polygon.io)
- Educational/demo limitations

---

## ⚠️ Project-Specific Security Considerations

### API Key Security
- **Never commit API keys** to version control
- Use `.env` files (included in `.gitignore`)
- Rotate keys if compromised
- Use environment-specific keys (dev/prod)

### AI/ML Security
- **Prompt Injection**: User inputs are sanitized before LLM processing
- **Data Privacy**: No personal financial data is stored permanently
- **Model Outputs**: All outputs include educational disclaimers

### Financial Data Handling
- **Educational Purpose**: No real trading or financial transactions
- **Data Sources**: Only public market data via Polygon.io API
- **No Storage**: Portfolio data exists only during session

---

## ✅ Security Best Practices for Users

### Environment Setup
```bash
# ✅ Good: Use environment variables
cp .env.example .env
# Edit .env with your actual API keys
export POLYGON_API_KEY="your-key-here"

# ❌ Bad: Hardcoding keys
POLYGON_API_KEY = "pk_live_1234567890"  # Never do this!
```

### Safe Usage
- **Isolated Environment**: Run in virtual environment or container
- **API Rate Limits**: Respect third-party API limits
- **Key Rotation**: Regularly rotate API keys
- **Dependency Updates**: Keep dependencies current
- **Educational Only**: Do not use for actual investment decisions

---

## �️ Security Controls

### Implemented Safeguards
- Input validation and sanitization
- Environment variable usage for secrets
- Dependency vulnerability scanning (dependabot)
- No persistent data storage
- Educational disclaimers on all outputs

### Continuous Monitoring
- Automated dependency updates
- Regular security audits of dependencies
- Code quality checks via CI/CD

---

## 🚫 Responsible Disclosure

### Research Guidelines
- **No Disruption**: Do not interfere with normal operations
- **Scope Limitation**: Only test your own instances
- **Data Protection**: Do not access others' data
- **Good Faith**: Act with integrity and respect

### After Reporting
- Allow reasonable time for fixes
- Do not publicly disclose until resolved
- Coordinate disclosure timing with maintainers

---

## � Security Credits

We appreciate security researchers who help keep our project safe. Verified reporters will be acknowledged in:
- Security advisories
- Release notes
- This document (with permission)

---

## 📞 Additional Resources

- **Documentation**: [Contributing Guide](CONTRIBUTING.md#security-guidelines)
- **Dependencies**: [Requirements](pyproject.toml)
- **Best Practices**: [OWASP Secure Coding](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)
- **AI Security**: [OWASP ML Top 10](https://owasp.org/www-project-machine-learning-security-top-10/)

---

**⚠️ Remember**: This is an educational project. Never use for real financial decisions without consulting qualified professionals.