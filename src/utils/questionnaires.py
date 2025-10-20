import questionary
import sys
from colorama import Fore, Style

from data.models import (
    PortfolioPreference, RiskProfile, InvestmentHorizon, InvestmentGoal, 
    Currency, StockExchange, InvestmentKnowledge, IncomeLevel, 
    InvestmentPurpose, LiquidityNeed, MarketDownturnReaction, InvestmentPriority,
    Benchmarks
)
from llm.models import AllModels, LLMModel, ModelProvider


# Simple style configuration
STYLE = questionary.Style([
    ("checkbox-selected", "fg:green"),
    ("selected", "fg:green noinherit"),
    ("highlighted", "noinherit"),
    ("pointer", "noinherit"),
])

def get_user_preferences() -> PortfolioPreference:
    """Collect user investment preferences with enhanced questionnaire."""
    
    try:
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{'🤖 AI-ROBO-ADVISOR - Investment Questionnaire':^70}")
        print(f"{'='*70}{Style.RESET_ALL}\n")
        print(f"{Fore.YELLOW}We'll ask you questions to create a personalized investment strategy.{Style.RESET_ALL}\n")
        
        # ===== SECTION 1: BASIC INFORMATION =====
        print(f"{Fore.CYAN}{'─'*70}")
        print(f"SECTION 1: Basic Information")
        print(f"{'─'*70}{Style.RESET_ALL}\n")
        
        # Age
        age_input = questionary.text(
            "What is your age?",
            validate=lambda text: validate_age(text),
            style=STYLE
        ).ask()
        
        if age_input is None:
            print(f"\n{Fore.RED}✗ Questionnaire cancelled{Style.RESET_ALL}")
            sys.exit(0)
        
        age = int(age_input)
        
        # Investment Knowledge
        investment_knowledge = questionary.select(
            "What is your level of investment knowledge?",
            choices=[questionary.Choice(level.value, value=level) for level in InvestmentKnowledge],
            style=STYLE
        ).ask()
        
        if investment_knowledge is None:
            print(f"\n{Fore.RED}✗ Questionnaire cancelled{Style.RESET_ALL}")
            sys.exit(0)
        
        # Income Level
        income_level = questionary.select(
            "What is your annual income level?",
            choices=[questionary.Choice(level.value, value=level) for level in IncomeLevel],
            style=STYLE
        ).ask()
        
        if income_level is None:
            print(f"\n{Fore.RED}✗ Questionnaire cancelled{Style.RESET_ALL}")
            sys.exit(0)
        
        # ===== SECTION 2: INVESTMENT GOALS & TIMELINE =====
        print(f"\n{Fore.CYAN}{'─'*70}")
        print(f"SECTION 2: Investment Goals & Timeline")
        print(f"{'─'*70}{Style.RESET_ALL}\n")
        
        # Investment Goal
        goal = questionary.select(
            "What is your primary investment goal?",
            choices=[questionary.Choice(g.value, value=g) for g in InvestmentGoal],
            style=STYLE
        ).ask()
        
        if goal is None:
            print(f"\n{Fore.RED}✗ Questionnaire cancelled{Style.RESET_ALL}")
            sys.exit(0)
        
        # Investment Purpose
        investment_purpose = questionary.select(
            "What is your investment purpose?",
            choices=[questionary.Choice(purpose.value, value=purpose) for purpose in InvestmentPurpose],
            style=STYLE
        ).ask()
        
        if investment_purpose is None:
            print(f"\n{Fore.RED}✗ Questionnaire cancelled{Style.RESET_ALL}")
            sys.exit(0)
        
        # Investment Horizon
        investment_horizon = questionary.select(
            "What is your investment time horizon?",
            choices=[questionary.Choice(horizon.value, value=horizon) for horizon in InvestmentHorizon],
            style=STYLE
        ).ask()
        
        if investment_horizon is None:
            print(f"\n{Fore.RED}✗ Questionnaire cancelled{Style.RESET_ALL}")
            sys.exit(0)
        
        # Liquidity Need
        liquidity_need = questionary.select(
            "When might you need to access these funds?",
            choices=[questionary.Choice(need.value, value=need) for need in LiquidityNeed],
            style=STYLE
        ).ask()
        
        if liquidity_need is None:
            print(f"\n{Fore.RED}✗ Questionnaire cancelled{Style.RESET_ALL}")
            sys.exit(0)
        
        # ===== SECTION 3: RISK ASSESSMENT =====
        print(f"\n{Fore.CYAN}{'─'*70}")
        print(f"SECTION 3: Risk Assessment")
        print(f"{'─'*70}{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}Imagine you invested $10,000 and the market drops 20% ($2,000 loss).{Style.RESET_ALL}\n")
        
        # Market Downturn Reaction
        market_downturn_reaction = questionary.select(
            "What would you do?",
            choices=[questionary.Choice(reaction.value, value=reaction) for reaction in MarketDownturnReaction],
            style=STYLE
        ).ask()
        
        if market_downturn_reaction is None:
            print(f"\n{Fore.RED}✗ Questionnaire cancelled{Style.RESET_ALL}")
            sys.exit(0)
        
        # Investment Priority
        investment_priority = questionary.select(
            "What matters most to you in your investments?",
            choices=[questionary.Choice(priority.value, value=priority) for priority in InvestmentPriority],
            style=STYLE
        ).ask()
        
        if investment_priority is None:
            print(f"\n{Fore.RED}✗ Questionnaire cancelled{Style.RESET_ALL}")
            sys.exit(0)
        
        # Maximum Acceptable Loss
        max_loss_input = questionary.text(
            "What's the maximum percentage loss you could tolerate in a year? (0-100)",
            validate=lambda text: validate_percentage(text),
            style=STYLE
        ).ask()
        
        if max_loss_input is None:
            print(f"\n{Fore.RED}✗ Questionnaire cancelled{Style.RESET_ALL}")
            sys.exit(0)
        
        max_acceptable_loss = float(max_loss_input)
        
        # Calculate risk profile based on responses
        risk_profile = calculate_risk_profile(market_downturn_reaction, investment_priority, max_acceptable_loss)
        
        print(f"\n{Fore.GREEN}✓ Calculated Risk Profile: {risk_profile.value}{Style.RESET_ALL}\n")
        
        # ===== SECTION 4: FINANCIAL SITUATION =====
        print(f"{Fore.CYAN}{'─'*70}")
        print(f"SECTION 4: Financial Situation")
        print(f"{'─'*70}{Style.RESET_ALL}\n")
        
        # Emergency Fund
        has_emergency_fund = questionary.confirm(
            "Do you have an emergency fund (3-6 months of expenses)?",
            default=False,
            style=STYLE
        ).ask()
        
        if has_emergency_fund is None:
            print(f"\n{Fore.RED}✗ Questionnaire cancelled{Style.RESET_ALL}")
            sys.exit(0)
        
        # Other Investments
        other_investments_input = questionary.text(
            "What is the value of your other investments? (Enter 0 if none)",
            default="0",
            validate=validate_optional_amount,
            style=STYLE
        ).ask()
        
        if other_investments_input is None:
            print(f"\n{Fore.RED}✗ Questionnaire cancelled{Style.RESET_ALL}")
            sys.exit(0)
        
        other_investments = float(other_investments_input.replace(',', '').replace('$', '').replace('€', '').replace('£', ''))
        
        # Initial Investment
        initial_investment_input = questionary.text(
            "What is your initial investment amount?",
            validate=validate_investment_amount,
            style=STYLE
        ).ask()
        
        if initial_investment_input is None:
            print(f"\n{Fore.RED}✗ Questionnaire cancelled{Style.RESET_ALL}")
            sys.exit(0)
        
        cleaned_amount = initial_investment_input.replace(',', '').replace('$', '').replace('€', '').replace('£', '')
        initial_investment_float = float(cleaned_amount)
        
        # Monthly Contribution
        monthly_contribution_input = questionary.text(
            "How much do you plan to contribute monthly? (Enter 0 if none)",
            default="0",
            validate=validate_optional_amount,
            style=STYLE
        ).ask()
        
        if monthly_contribution_input is None:
            print(f"\n{Fore.RED}✗ Questionnaire cancelled{Style.RESET_ALL}")
            sys.exit(0)
        
        monthly_contribution = float(monthly_contribution_input.replace(',', '').replace('$', '').replace('€', '').replace('£', ''))
        
        # ===== SECTION 5: PREFERENCES =====
        print(f"\n{Fore.CYAN}{'─'*70}")
        print(f"SECTION 5: Currency & Exchange Preferences")
        print(f"{'─'*70}{Style.RESET_ALL}\n")
        
        # Currency
        currency = questionary.select(
            "What is your preferred currency?",
            choices=[questionary.Choice(curr.value, value=curr) for curr in Currency],
            style=STYLE
        ).ask()
        
        if currency is None:
            print(f"\n{Fore.RED}✗ Questionnaire cancelled{Style.RESET_ALL}")
            sys.exit(0)
        
        # Stock Exchange
        stock_exchange = questionary.select(
            "Which stock exchange do you prefer for ETF listings?",
            choices=[questionary.Choice(exchange.value, value=exchange) for exchange in StockExchange],
            style=STYLE
        ).ask()
        
        if stock_exchange is None:
            print(f"\n{Fore.RED}✗ Questionnaire cancelled{Style.RESET_ALL}")
            sys.exit(0)

        benchmark = questionary.select(
            "Select your preferred benchmark:",
            choices=[questionary.Choice(f"{b.value[0]} - {b.value[1]}", value=b) for b in Benchmarks],
            style=STYLE
        ).ask()

        if benchmark is None:
            benchmark = Benchmarks.ACWI 
        
        print(f"\n{Fore.GREEN}✓ Portfolio preferences collected successfully!{Style.RESET_ALL}\n")
        
        return PortfolioPreference(
            # Core fields
            goal=goal,
            risk_profile=risk_profile,
            investment_horizon=investment_horizon,
            currency=currency,
            stock_exchange=stock_exchange,
            initial_investment=initial_investment_float,
            benchmark=benchmark.value,  # Convert enum to tuple
            
            # Enhanced fields
            age=age,
            investment_knowledge=investment_knowledge,
            income_level=income_level,
            investment_purpose=investment_purpose,
            liquidity_need=liquidity_need,
            has_emergency_fund=has_emergency_fund,
            other_investments=other_investments,
            monthly_contribution=monthly_contribution,
            max_acceptable_loss=max_acceptable_loss,
            market_downturn_reaction=market_downturn_reaction,
            investment_priority=investment_priority
        )
    
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}✗ Questionnaire interrupted by user{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}✗ An error occurred: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

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
    
    if selected_provider is None:
        print(f"\n{Fore.RED}✗ Provider selection cancelled{Style.RESET_ALL}")
        sys.exit(0)
    
    print(f"Selected provider: {Fore.GREEN}{selected_provider.value.title()}{Style.RESET_ALL}\n")
    return selected_provider

def choose_llm_model(all_models: AllModels, agent: str) -> LLMModel:
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
    
    if selected_model is None:
        print(f"\n{Fore.RED}✗ Model selection cancelled{Style.RESET_ALL}")
        sys.exit(0)
    
    print(f"Selected model: {Fore.GREEN}{selected_model.provider.value} - {selected_model.display}{Style.RESET_ALL}\n")
    return selected_model

# ===== VALIDATION FUNCTIONS =====

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

def validate_age(age: str) -> bool | str:
    """Validate age input."""
    if not age.strip():
        return "Please enter your age"
    
    try:
        value = int(age)
        if value < 18:
            return "You must be at least 18 years old"
        if value > 100:
            return "Please enter a valid age"
        return True
    except ValueError:
        return "Please enter a valid number"

def validate_percentage(percentage: str) -> bool | str:
    """Validate percentage input."""
    if not percentage.strip():
        return "Please enter a percentage"
    
    try:
        value = float(percentage)
        if value < 0 or value > 100:
            return "Please enter a value between 0 and 100"
        return True
    except ValueError:
        return "Please enter a valid number"

def validate_optional_amount(amount: str) -> bool | str:
    """Validate optional investment amount input."""
    if not amount.strip():
        return True
    
    cleaned = amount.replace(',', '').replace('$', '').replace('€', '').replace('£', '').strip()
    
    try:
        value = float(cleaned)
        if value < 0:
            return "Amount cannot be negative"
        return True
    except ValueError:
        return "Please enter a valid number (e.g., 500, $1,000, 0)"

# ===== RISK CALCULATION =====

def calculate_risk_profile(reaction: MarketDownturnReaction, 
                          priority: InvestmentPriority, 
                          max_loss: float) -> RiskProfile:
    """Calculate risk profile based on questionnaire responses."""
    score = 0.0
    
    # Score market reaction (0-3)
    if reaction == MarketDownturnReaction.SELL_ALL:
        score += 0
    elif reaction == MarketDownturnReaction.SELL_SOME:
        score += 1
    elif reaction == MarketDownturnReaction.HOLD:
        score += 2
    elif reaction == MarketDownturnReaction.BUY_MORE:
        score += 3
    
    # Score priority (0-3)
    if priority == InvestmentPriority.STABILITY:
        score += 0
    elif priority == InvestmentPriority.INCOME:
        score += 1
    elif priority == InvestmentPriority.BALANCED:
        score += 1.5
    elif priority == InvestmentPriority.GROWTH:
        score += 3
    
    # Score max loss tolerance (0-3)
    if max_loss <= 5:
        score += 0
    elif max_loss <= 10:
        score += 1
    elif max_loss <= 20:
        score += 2
    else:
        score += 3
    
    # Map score to risk profile (total score range: 0-9)
    if score <= 1.5:
        return RiskProfile.ULTRA_CONSERVATIVE
    elif score <= 3:
        return RiskProfile.CONSERVATIVE
    elif score <= 4:
        return RiskProfile.MODERATE_CONSERVATIVE
    elif score <= 5.5:
        return RiskProfile.MODERATE
    elif score <= 6.5:
        return RiskProfile.MODERATE_AGGRESSIVE
    elif score <= 7.5:
        return RiskProfile.AGGRESSIVE
    else:
        return RiskProfile.ULTRA_AGGRESSIVE
