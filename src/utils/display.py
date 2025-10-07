from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from data.models import Portfolio, Strategy, AnalysisResponse

console = Console()

def print_portfolio(portfolio: Portfolio) -> None:
    if not portfolio:
        console.print("[bold red]No portfolio to display[/bold red]")
        return

    console.print(Panel.fit("[bold cyan] PORTFOLIO DETAILS[/bold cyan]", style="cyan", expand=False))

    console.print(f"[bold white]Portfolio Name:[/bold white] {portfolio.name}")

    if portfolio.holdings:
        table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE_HEAVY)
        table.add_column("Symbol", style="yellow")
        table.add_column("Name", style="white", overflow="fold")
        table.add_column("ISIN", justify="center", style="cyan")
        table.add_column("Asset Class", style="green")
        table.add_column("Weight (%)", justify="right", style="bright_white")

        for h in portfolio.holdings:
            isin_display = h.isin if h.isin else "N/A"
            table.add_row(h.symbol, h.name, isin_display, h.asset_class, f"{h.weight:.2f}")

        total_weight = sum(h.weight for h in portfolio.holdings)
        table.add_row("", "", "", "[bold yellow]TOTAL[/bold yellow]", f"[bold yellow]{total_weight:.2f}[/bold yellow]")

        console.print(table)
        if abs(total_weight - 100.0) > 0.01:
            console.print(f":warning: [bold yellow]Weights sum to {total_weight:.2f}% (not 100%)![/bold yellow]")
    else:
        console.print("[red]No holdings found in portfolio.[/red]")


def print_strategy(strategy: Strategy) -> None:
    if not strategy:
        console.print("[bold red]No strategy to display[/bold red]")
        return

    console.print(Panel.fit("[bold cyan] INVESTMENT STRATEGY[/bold cyan]", style="cyan", expand=False))
    console.print(f"[bold white]Name:[/bold white] {strategy.name}")
    if strategy.description:
        console.print(f"[bold white]Description:[/bold white] {strategy.description}")
    console.print(f"[bold white]Stock Exchange:[/bold white] {strategy.stock_exchange.value}")
    console.print(f"[bold white]Risk Tolerance:[/bold white] {strategy.risk_tolerance}")
    console.print(f"[bold white]Time Horizon:[/bold white] {strategy.time_horizon}")
    console.print(f"[bold white]Expected Returns:[/bold white] {strategy.expected_returns}")

    # Asset Allocation Table
    console.print("\n[bold yellow]Asset Allocation[/bold yellow]")
    alloc_table = Table(show_header=True, header_style="bold green", box=box.SQUARE)
    alloc_table.add_column("Asset", style="cyan")
    alloc_table.add_column("Weight (%)", justify="right", style="white")

    alloc = strategy.asset_allocation
    for asset, pct in [
        ("Stocks", alloc.stocks_percentage),
        ("Bonds", alloc.bonds_percentage),
        ("Real Estate", alloc.real_estate_percentage),
        ("Commodities", alloc.commodities_percentage),
        ("Crypto", alloc.cryptocurrency_percentage),
        ("Cash", alloc.cash_percentage)
    ]:
        if pct and pct > 0:
            alloc_table.add_row(asset, f"{pct:.1f}")

    console.print(alloc_table)

    # Geographical Diversification
    if strategy.geographical_diversification and strategy.geographical_diversification.regions:
        console.print("\n[bold yellow]Geographical Diversification[/bold yellow]")
        geo_table = Table(show_header=True, box=box.MINIMAL_DOUBLE_HEAD)
        geo_table.add_column("Region", style="cyan")
        geo_table.add_column("Weight (%)", justify="right", style="white")
        for r in strategy.geographical_diversification.regions:
            geo_table.add_row(r.region, f"{r.weight:.1f}")
        console.print(geo_table)

    # Sector Diversification
    if strategy.sector_diversification and strategy.sector_diversification.sectors:
        console.print("\n[bold yellow]Sector Diversification[/bold yellow]")
        sec_table = Table(show_header=True, box=box.MINIMAL_DOUBLE_HEAD)
        sec_table.add_column("Sector", style="cyan")
        sec_table.add_column("Weight (%)", justify="right", style="white")
        for s in strategy.sector_diversification.sectors:
            sec_table.add_row(s.sector, f"{s.weight:.1f}")
        console.print(sec_table)


def print_analysis_response(analysis_response: AnalysisResponse) -> None:
    if not analysis_response:
        console.print("[bold red]No analysis response to display[/bold red]")
        return

    console.print(Panel.fit("[bold cyan] PORTFOLIO ANALYSIS[/bold cyan]", style="cyan", expand=False))

    if hasattr(analysis_response, 'is_approved'):
        color = "green" if analysis_response.is_approved else "red"
        status = " APPROVED" if analysis_response.is_approved else "❌ REJECTED"
        console.print(f"[bold white]Portfolio Status:[/bold white] [{color}]{status}[/{color}]\n")

    if getattr(analysis_response, "strengths", None):
        console.print(Panel.fit(f" [bold green]STRENGTHS[/bold green]\n{analysis_response.strengths}", style="green"))

    if getattr(analysis_response, "weeknesses", None):
        console.print(Panel.fit(f" [bold red]WEAKNESSES[/bold red]\n{analysis_response.weeknesses}", style="red"))

    if getattr(analysis_response, "overall_assessment", None):
        console.print(Panel.fit(f" [bold blue]OVERALL ASSESSMENT[/bold blue]\n{analysis_response.overall_assessment}", style="blue"))

    if getattr(analysis_response, "advices", None):
        console.print(Panel.fit(f" [bold cyan]ACTIONABLE ADVICE[/bold cyan]\n{analysis_response.advices}", style="cyan"))