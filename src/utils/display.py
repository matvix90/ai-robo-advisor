from colorama import Fore, Style, init

from data.models import AnalysisResponse, Portfolio, Strategy

# Initialize colorama
init(autoreset=True)


def print_portfolio(portfolio: Portfolio) -> None:
    """Pretty print the portfolio details."""
    if not portfolio:
        print(Fore.RED + "No portfolio to display" + Style.RESET_ALL)
        return

    print("\n" + Fore.CYAN + "=" * 50 + Style.RESET_ALL)
    print(Fore.GREEN + "PORTFOLIO" + Style.RESET_ALL)
    print(Fore.CYAN + "=" * 50 + Style.RESET_ALL)

    print(f"Portfolio Name: {Fore.WHITE}{portfolio.name}{Style.RESET_ALL}")

    if portfolio.holdings:
        print("\n" + Fore.YELLOW + "Holdings:" + Style.RESET_ALL)
        print(
            f"{'Symbol':<10} {'Name':<60} {'ISIN':<15} {'Asset Class':<15} {'Weight':<10}"
        )
        print(Fore.MAGENTA + "-" * 110 + Style.RESET_ALL)

        for holding in portfolio.holdings:
            isin_display = holding.isin if holding.isin else "N/A"
            print(
                f"{holding.symbol:<10} {holding.name:<60} {isin_display:<15} {holding.asset_class:<15} {holding.weight:<10.2f}%"
            )

        # Calculate and display total weight
        total_calculated = sum(holding.weight for holding in portfolio.holdings)
        print(Fore.MAGENTA + "-" * 110 + Style.RESET_ALL)
        print(f"{'TOTAL':<86} {'':<15} {total_calculated:<10.2f}%")

        # Validation check
        if abs(total_calculated - 100.0) > 0.01:
            print(
                Fore.YELLOW
                + f"⚠️  Warning: Portfolio weights sum to {total_calculated:.2f}%, not 100%"
                + Style.RESET_ALL
            )
    else:
        print(Fore.RED + "No holdings found in portfolio" + Style.RESET_ALL)


def print_strategy(strategy: Strategy) -> None:
    """Pretty print the strategy details."""
    if not strategy:
        print(Fore.RED + "No strategy to display" + Style.RESET_ALL)
        return

    print("\n" + Fore.CYAN + "=" * 60 + Style.RESET_ALL)
    print(Fore.GREEN + "INVESTMENT STRATEGY" + Style.RESET_ALL)
    print(Fore.CYAN + "=" * 60 + Style.RESET_ALL)

    print(f"Strategy Name: {Fore.WHITE}{strategy.name}{Style.RESET_ALL}")
    if strategy.description:
        print(f"Description: {Fore.WHITE}{strategy.description}{Style.RESET_ALL}")
    print(
        f"Stock Exchange: {Fore.WHITE}{strategy.stock_exchange.value}{Style.RESET_ALL}"
    )
    print(f"Risk Tolerance: {Fore.WHITE}{strategy.risk_tolerance}{Style.RESET_ALL}")
    print(f"Time Horizon: {Fore.WHITE}{strategy.time_horizon}{Style.RESET_ALL}")
    print(f"Expected Returns: {Fore.WHITE}{strategy.expected_returns}{Style.RESET_ALL}")

    # Asset Allocation
    print("\n" + Fore.YELLOW + "Asset Allocation:" + Style.RESET_ALL)
    allocation = strategy.asset_allocation
    asset_items = [
        ("Stocks", allocation.stocks_percentage),
        ("Bonds", allocation.bonds_percentage),
        ("Real Estate", allocation.real_estate_percentage),
        ("Commodities", allocation.commodities_percentage),
        ("Cryptocurrency", allocation.cryptocurrency_percentage),
        ("Cash", allocation.cash_percentage),
    ]

    for asset, percentage in asset_items:
        if percentage is not None and percentage > 0:
            print(f"  {asset:<15}: {Fore.WHITE}{percentage:>6.1f}%{Style.RESET_ALL}")

    # Geographical Diversification
    if (
        strategy.geographical_diversification
        and strategy.geographical_diversification.regions
    ):
        print("\n" + Fore.YELLOW + "Geographical Diversification:" + Style.RESET_ALL)
        for region in strategy.geographical_diversification.regions:
            print(
                f"  {region.region:<20}: {Fore.WHITE}{region.weight:>6.1f}%{Style.RESET_ALL}"
            )

    # Sector Diversification
    if strategy.sector_diversification and strategy.sector_diversification.sectors:
        print("\n" + Fore.YELLOW + "Sector Diversification:" + Style.RESET_ALL)
        for sector in strategy.sector_diversification.sectors:
            print(
                f"  {sector.sector:<20}: {Fore.WHITE}{sector.weight:>6.1f}%{Style.RESET_ALL}"
            )


def print_analysis_response(analysis_response: AnalysisResponse) -> None:
    """Pretty print the analysis response summary."""
    if not analysis_response:
        print(Fore.RED + "No analysis response to display" + Style.RESET_ALL)
        return

    print("\n" + Fore.CYAN + "=" * 80 + Style.RESET_ALL)
    print(Fore.GREEN + "PORTFOLIO ANALYSIS RESPONSE" + Style.RESET_ALL)
    print(Fore.CYAN + "=" * 80 + Style.RESET_ALL)

    # Approval Status
    if (
        hasattr(analysis_response, "is_approved")
        and analysis_response.is_approved is not None
    ):
        approval_color = Fore.GREEN if analysis_response.is_approved else Fore.RED
        approval_text = "APPROVED" if analysis_response.is_approved else "REJECTED"
        print(
            f"{'Portfolio Status':<20}: {approval_color}{approval_text}{Style.RESET_ALL}\n"
        )

    # Strengths
    if hasattr(analysis_response, "strengths") and analysis_response.strengths:
        print(f"{Fore.GREEN}STRENGTHS:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{analysis_response.strengths}{Style.RESET_ALL}\n")

    # Weaknesses
    if hasattr(analysis_response, "weeknesses") and analysis_response.weeknesses:
        print(f"{Fore.RED}WEAKNESSES:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{analysis_response.weeknesses}{Style.RESET_ALL}\n")

    # Overall Assessment
    if (
        hasattr(analysis_response, "overall_assessment")
        and analysis_response.overall_assessment
    ):
        print(f"{Fore.BLUE}OVERALL ASSESSMENT:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{analysis_response.overall_assessment}{Style.RESET_ALL}\n")

    # Actionable Advice
    if hasattr(analysis_response, "advices") and analysis_response.advices:
        print(f"{Fore.CYAN}ACTIONABLE ADVICE:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{analysis_response.advices}{Style.RESET_ALL}\n")

    print(Fore.CYAN + "=" * 80 + Style.RESET_ALL)
