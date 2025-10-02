from pydantic import BaseModel, Field
from typing import Annotated, Optional, List
from enum import Enum

# === Investment Models ===
class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    JPY = "JPY"  # Japanese Yen
    GBP = "GBP"  # British Pound
    CAD = "CAD"  # Canadian Dollar
    AUD = "AUD"  # Australian Dollar
    CHF = "CHF"  # Swiss Franc

class StockExchange(str, Enum):
    NYSE = "NYSE"           # New York Stock Exchange
    NASDAQ = "NASDAQ"       # NASDAQ
    LSE = "LSE"             # London Stock Exchange
    EURONEXT = "EURONEXT"   # Euronext
    TSE = "TSE"             # Tokyo Stock Exchange
    TSX = "TSX"             # Toronto Stock Exchange
    ASX = "ASX"             # Australian Securities Exchange
    SIX = "SIX"             # SIX Swiss Exchange
    BORSA_ITALIANA = "BORSA_ITALIANA"  # Borsa Italiana

class InvestmentGoal(str, Enum):
    RETIREMENT = "Retirement"
    WEALTH_BUILDING = "Wealth Building"
    INCOME_GENERATION = "Income Generation"
    CAPITAL_PRESERVATION = "Capital Preservation"
    EDUCATION_FUNDING = "Education Funding"
    HOUSE_PURCHASE = "House Purchase"
    EMERGENCY_FUND = "Emergency Fund"
    SHORT_TERM_SAVINGS = "Short Term Savings"

class RiskProfile(str, Enum):
    ULTRA_CONSERVATIVE = "Ultra Conservative"
    CONSERVATIVE = "Conservative"
    MODERATE_CONSERVATIVE = "Moderate Conservative"
    MODERATE = "Moderate"
    MODERATE_AGGRESSIVE = "Moderate Aggressive"
    AGGRESSIVE = "Aggressive"
    ULTRA_AGGRESSIVE = "Ultra Aggressive"

class InvestmentHorizon(str, Enum):
    SHORT_TERM = "Short Term (1-3 years)"
    MEDIUM_TERM = "Medium Term (3-7 years)"
    LONG_TERM = "Long Term (7-15 years)"
    VERY_LONG_TERM = "Very Long Term (15+ years)"

class InvestmentKnowledge(str, Enum):
    NONE = "No knowledge - I'm just starting"
    BASIC = "Basic - I understand stocks and bonds"
    INTERMEDIATE = "Intermediate - I've invested before"
    ADVANCED = "Advanced - I actively manage investments"
    EXPERT = "Expert - I'm a finance professional"

class IncomeLevel(str, Enum):
    UNDER_30K = "Under $30,000"
    FROM_30K_TO_60K = "$30,000 - $60,000"
    FROM_60K_TO_100K = "$60,000 - $100,000"
    FROM_100K_TO_150K = "$100,000 - $150,000"
    FROM_150K_TO_250K = "$150,000 - $250,000"
    OVER_250K = "Over $250,000"

class InvestmentPurpose(str, Enum):
    GROW_WEALTH = "Grow my wealth over time"
    GENERATE_INCOME = "Generate regular income"
    PRESERVE_CAPITAL = "Preserve my capital with minimal risk"
    BALANCE_GROWTH_INCOME = "Balance between growth and income"
    SPECIFIC_GOAL = "Save for a specific goal"

class LiquidityNeed(str, Enum):
    ANYTIME = "I might need it anytime"
    WITHIN_1_YEAR = "Within 1 year"
    FROM_1_TO_3_YEARS = "1-3 years"
    FROM_3_TO_5_YEARS = "3-5 years"
    OVER_5_YEARS = "Not for 5+ years"

class MarketDownturnReaction(str, Enum):
    SELL_ALL = "Sell everything immediately"
    SELL_SOME = "Sell some to reduce risk"
    HOLD = "Hold and wait for recovery"
    BUY_MORE = "Buy more at lower prices"

class InvestmentPriority(str, Enum):
    STABILITY = "Stability and capital preservation"
    INCOME = "Regular income"
    BALANCED = "Balanced approach"
    GROWTH = "Maximum growth potential"

class PortfolioPreference(BaseModel):
    # Core investment fields
    goal: InvestmentGoal = Field(..., description="Investment goal")
    risk_profile: RiskProfile = Field(..., description="Risk tolerance level")
    investment_horizon: InvestmentHorizon = Field(..., description="Investment time horizon")
    currency: Currency = Field(default=Currency.USD, description="Currency code")
    stock_exchange: StockExchange = Field(default=StockExchange.NYSE, description="Preferred stock exchange")
    initial_investment: float = Field(..., gt=0, description="Initial investment amount")
    
    # Enhanced fields - Personal Information
    age: int = Field(..., ge=18, le=100, description="User's age")
    investment_knowledge: InvestmentKnowledge = Field(..., description="Level of investment knowledge")
    income_level: IncomeLevel = Field(..., description="Annual income level")
    
    # Enhanced fields - Investment Goals & Timeline
    investment_purpose: InvestmentPurpose = Field(..., description="Purpose of investment")
    liquidity_need: LiquidityNeed = Field(..., description="When funds might be needed")
    
    # Enhanced fields - Financial Situation
    has_emergency_fund: bool = Field(..., description="Whether user has 3-6 months emergency fund")
    other_investments: float = Field(default=0.0, ge=0, description="Value of other investments")
    monthly_contribution: float = Field(default=0.0, ge=0, description="Planned monthly contribution amount")
    
    # Enhanced fields - Risk Assessment
    max_acceptable_loss: float = Field(..., ge=0, le=100, description="Maximum acceptable loss percentage in a year")
    market_downturn_reaction: MarketDownturnReaction = Field(..., description="Reaction to market downturn")
    investment_priority: InvestmentPriority = Field(..., description="Investment priority")

class AssetAllocation(BaseModel):
    stocks_percentage: Optional[float] = None
    bonds_percentage: Optional[float] = None
    real_estate_percentage: Optional[float] = None
    commodities_percentage: Optional[float] = None
    cryptocurrency_percentage: Optional[float] = None
    cash_percentage: Optional[float] = None

class Region(BaseModel):
    region: str
    weight: float

class GeographicalDiversification(BaseModel):
    regions: Annotated[List[Region], "List of regions and their weights"]

class Sector(BaseModel):
    sector: str
    weight: float

class SectorDiversification(BaseModel):
    sectors: Annotated[List[Sector], "List of sectors and their weights"]

class Strategy(BaseModel):
    name: Annotated[str, "Name of the investment strategy"]
    description: Annotated[Optional[str], "Description of the investment strategy"]
    asset_allocation: Annotated[AssetAllocation, "Asset allocation for the investment strategy"]
    geographical_diversification: Annotated[GeographicalDiversification, "Geographical diversification for the investment strategy"]
    sector_diversification: Annotated[SectorDiversification, "Sector diversification for the investment strategy"]
    stock_exchange: Annotated[StockExchange, "Stock exchange where the ETFs have to be quoted"] = Field(default=StockExchange.NYSE)
    risk_tolerance: Annotated[str, "Risk tolerance level for the investment strategy"]
    time_horizon: Annotated[str, "Time horizon for the investment strategy"]
    expected_returns: Annotated[str, "Expected returns for the investment strategy"]

class InvestmentAgent(BaseModel):
    strategy: Strategy
    reasoning: str

# === Portfolio Models ===
class Holding(BaseModel):
    symbol: str
    name: str
    isin: str = Field(None, min_length=12, max_length=12, description="International Securities Identification Number")
    asset_class: str
    weight: float

class Portfolio(BaseModel):
    name: Annotated[str, "Name of the portfolio"]
    holdings: List[Holding]
    strategy: Strategy

class PortfolioAgent(BaseModel):
    portfolio: Portfolio
    reasoning: str

# === Analysis Models ===
class Status(BaseModel):
    key: str
    value: bool

class AnalysisAgent(BaseModel):
    status: Status
    reasoning: str
    advices: Optional[list[str]]

class AnalysisResponse(BaseModel):
    is_approved: bool
    strengths: Optional[str]
    weeknesses: Optional[str]
    overall_assessment: Optional[str]
    advices: Optional[str] = None