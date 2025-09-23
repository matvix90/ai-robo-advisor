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

class PortfolioPreference(BaseModel):
    goal: InvestmentGoal = Field(None, description="Investment goal")
    risk_profile: RiskProfile = Field(None, description="Risk tolerance level")
    investment_horizon: InvestmentHorizon = Field(None, description="Investment time horizon")
    currency: Currency = Field(default=Currency.USD, description="Currency code")
    stock_exchange: StockExchange = Field(default=StockExchange.NYSE, description="Preferred stock exchange")
    initial_investment: float

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