import questionary
import sys
from colorama import Fore, Style

from src.data.models import (PortfolioPreference, RiskProfile,
                        InvestmentHorizon, InvestmentGoal, Currency, StockExchange)
from src.llm.models import AllModels, LLMModel, ModelProvider

# Simple style configuration
STYLE = questionary.Style([
    ("checkbox-selected", "fg:green"),
    ("selected", "fg:green noinherit"),
    ("highlighted", "noinherit"),
    ("pointer", "noinherit"),
])

def get_user_preferences() -> PortfolioPreference:
    """Collect user investment preferences."""
    
    # Investment Goal
    goal = questionary.select(
        "What is your primary investment goal?",
        choices=[questionary.Choice(goal.value, value=goal) for goal in InvestmentGoal],
        style=STYLE
    ).ask()
    
    if not goal:
        print("\nInterrupt received. Exiting...")
        sys.exit(0)
    
    # Risk Profile
    risk_profile = questionary.select(
        "What is your risk tolerance?",
        choices=[questionary.Choice(risk.value, value=risk) for risk in RiskProfile],
        style=STYLE
    ).ask()
    
    if not risk_profile:
        print("\nInterrupt received. Exiting...")
        sys.exit(0)
    
    # Investment Horizon
    investment_horizon = questionary.select(
        "What is your investment time horizon?",
        choices=[questionary.Choice(horizon.value, value=horizon) for horizon in InvestmentHorizon],
        style=STYLE
    ).ask()
    
    if not investment_horizon:
        print("\nInterrupt received. Exiting...")
        sys.exit(0)
    
    # Currency
    currency = questionary.select(
        "What is your preferred currency?",
        choices=[questionary.Choice(curr.value, value=curr) for curr in Currency],
        style=STYLE
    ).ask()
    
    if not currency:
        print("\nInterrupt received. Exiting...")
        sys.exit(0)
    
    # Stock Exchange
    stock_exchange = questionary.select(
        "Which stock exchange do you prefer for ETF listings?",
        choices=[questionary.Choice(exchange.value, value=exchange) for exchange in StockExchange],
        style=STYLE
    ).ask()
    
    if not stock_exchange:
        print("\nInterrupt received. Exiting...")
        sys.exit(0)
    
    # Initial investment amount
    initial_investment = questionary.text(
        "What is your initial investment amount?",
        validate=validate_investment_amount,
        style=STYLE
    ).ask()
    
    if not initial_investment:
        print("\nInterrupt received. Exiting...")
        sys.exit(0)
    
    # Clean and convert amount
    cleaned_amount = initial_investment.replace(',', '').replace('$', '').replace('€', '').replace('£', '')
    initial_investment_float = float(cleaned_amount)
    
    print(f"{Fore.GREEN}Portfolio preferences collected successfully!{Style.RESET_ALL}\n")
    
    return PortfolioPreference(
        goal=goal,
        risk_profile=risk_profile,
        investment_horizon=investment_horizon,
        currency=currency,
        stock_exchange=stock_exchange,
        initial_investment=initial_investment_float
    )

def choose_provider() -> ModelProvider:
    """Select an LLM provider.""" 
    
    choices = [
        questionary.Choice(
            provider.value.title(), 
            value=provider
        ) for provider in ModelProvider
    ]
    
    selected_provider = questionary.select(
        "Select your LLM provider:",
        choices=choices,
        instruction="\nInstructions: Use arrow keys to navigate, Enter to select.",
        style=STYLE
    ).ask()
    
    if not selected_provider:
        print("\nInterrupt received. Exiting...")
        sys.exit(0)
    
    print(f"Selected provider: {Fore.GREEN}{selected_provider.value.title()}{Style.RESET_ALL}\n")
    return selected_provider

def choose_llm_model(all_models: AllModels, agent:str) -> LLMModel:
    """Select an LLM model."""

    if agent == "investment_agent":
        print(f"{Fore.YELLOW}Note: Investment Agent requires models with advanced capabilities of resume.{Style.RESET_ALL}\n")
    elif agent == "portfolio_agent":
        print(f"{Fore.YELLOW}Note: Portfolio Agent requires models with advanced capabilities of financial analysis and math.{Style.RESET_ALL}\n")
    elif agent == "analyst_agent":
        print(f"{Fore.YELLOW}Note: Analyst Agent requires models with advanced capabilities of critical thinking and reasoning.{Style.RESET_ALL}\n")

    selected_provider = choose_provider()

    provider_models = [
        model for model in all_models.models 
        if model.provider == selected_provider
    ]
    
    choices = [
        questionary.Choice(
            model.display,
            value=model
        ) for model in provider_models
    ]
    
    selected_model = questionary.select(
        "Select your LLM model:",
        choices=choices,
        instruction="\nInstructions: Use arrow keys to navigate, Enter to select.",
        style=STYLE
    ).ask()
    
    if not selected_model:
        print("\nInterrupt received. Exiting...")
        sys.exit(0)
    
    print(f"Selected model: {Fore.GREEN}{selected_model.provider.value} - {selected_model.display}{Style.RESET_ALL}\n")
    return selected_model

def validate_investment_amount(amount: str) -> bool | str:
    """Validate investment amount input."""
    if not amount.strip():
        return "Please enter an investment amount"
    
    cleaned = amount.replace(',', '').replace('$', '').replace('€', '').replace('£', '').strip()
    
    try:
        value = float(cleaned)
        if value <= 0:
            return "Investment amount must be greater than 0"
        if value < 100:
            return "Minimum investment amount is 100"
        return True
    except ValueError:
        return "Please enter a valid number (e.g., 10000, $5,000, 1000.50)"