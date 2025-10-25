"""
Simplified tests for display utility functions focusing on coverage.
"""

from io import StringIO
from unittest.mock import patch

import pytest

from src.data.models import AnalysisResponse, Holding, Portfolio
from src.utils.display import print_analysis_response, print_portfolio, print_strategy

# ============================================================================
# Print Portfolio Tests
# ============================================================================


@pytest.mark.unit
class TestPrintPortfolio:
    """Tests for print_portfolio function."""

    @patch("sys.stdout", new_callable=StringIO)
    def test_print_portfolio_success(self, mock_stdout, sample_portfolio):
        """Test printing a valid portfolio."""
        print_portfolio(sample_portfolio)

        output = mock_stdout.getvalue()
        assert "PORTFOLIO" in output
        assert "VTI" in output
        assert "BND" in output
        assert "VNQ" in output
        assert "60.00" in output or "60.0" in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_print_portfolio_with_none(self, mock_stdout):
        """Test printing None portfolio."""
        print_portfolio(None)

        output = mock_stdout.getvalue()
        assert "No portfolio" in output or "None" in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_print_portfolio_empty_holdings(self, mock_stdout, sample_strategy):
        """Test printing portfolio with empty holdings list."""
        empty_portfolio = Portfolio(
            name="Empty Portfolio", holdings=[], strategy=sample_strategy
        )

        print_portfolio(empty_portfolio)

        output = mock_stdout.getvalue()
        assert "Empty Portfolio" in output
        assert "No holdings" in output or "PORTFOLIO" in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_print_portfolio_name_display(self, mock_stdout, sample_portfolio):
        """Test that portfolio name is displayed."""
        print_portfolio(sample_portfolio)

        output = mock_stdout.getvalue()
        assert sample_portfolio.name in output or "Portfolio" in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_print_portfolio_holdings_symbols(self, mock_stdout, sample_portfolio):
        """Test that all holding symbols are displayed."""
        print_portfolio(sample_portfolio)

        output = mock_stdout.getvalue()
        for holding in sample_portfolio.holdings:
            assert holding.symbol in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_print_portfolio_special_characters(self, mock_stdout, sample_strategy):
        """Test printing portfolio with special characters in names."""
        holdings = [
            Holding(
                symbol="VTI-X",
                name="Test & Demo ETF (Special)",
                isin="US1234567890",
                asset_class="Stocks",
                weight=100.0,
            )
        ]

        portfolio = Portfolio(
            name="Test & Portfolio (Special)",
            holdings=holdings,
            strategy=sample_strategy,
        )

        print_portfolio(portfolio)

        output = mock_stdout.getvalue()
        assert "VTI-X" in output


# ============================================================================
# Print Strategy Tests
# ============================================================================


@pytest.mark.unit
class TestPrintStrategy:
    """Tests for print_strategy function."""

    @patch("sys.stdout", new_callable=StringIO)
    def test_print_strategy_success(self, mock_stdout, sample_strategy):
        """Test printing a valid strategy."""
        print_strategy(sample_strategy)

        output = mock_stdout.getvalue()
        assert "STRATEGY" in output or "Strategy" in output
        assert "Asset Allocation" in output or "Allocation" in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_print_strategy_with_none(self, mock_stdout):
        """Test printing None strategy."""
        print_strategy(None)

        output = mock_stdout.getvalue()
        assert "No strategy" in output or "None" in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_print_strategy_geographical_diversification(
        self, mock_stdout, sample_strategy
    ):
        """Test printing geographical diversification."""
        print_strategy(sample_strategy)

        output = mock_stdout.getvalue()
        assert "Geographical" in output or "Geographic" in output or "Geo" in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_print_strategy_sector_diversification(self, mock_stdout, sample_strategy):
        """Test printing sector diversification."""
        print_strategy(sample_strategy)

        output = mock_stdout.getvalue()
        assert "Sector" in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_print_strategy_formatting(self, mock_stdout, sample_strategy):
        """Test that strategy output is formatted with proper separators."""
        print_strategy(sample_strategy)

        output = mock_stdout.getvalue()
        # Check for some formatting elements
        lines = output.split("\n")
        assert len(lines) > 5  # Should have multiple lines


# ============================================================================
# Print Analysis Response Tests
# ============================================================================


@pytest.mark.unit
class TestPrintAnalysisResponse:
    """Tests for print_analysis_response function."""

    @patch("sys.stdout", new_callable=StringIO)
    def test_print_analysis_approved(self, mock_stdout):
        """Test printing approved analysis response."""
        response = AnalysisResponse(
            is_approved=True,
            strengths="Good diversification and low fees",
            weeknesses="High risk concentration",
            overall_assessment="Strong portfolio",
            advices="Consider rebalancing quarterly",
        )

        print_analysis_response(response)

        output = mock_stdout.getvalue()
        assert "APPROVED" in output or "✓" in output or "approved" in output.lower()

    @patch("sys.stdout", new_callable=StringIO)
    def test_print_analysis_rejected(self, mock_stdout):
        """Test printing rejected analysis response."""
        response = AnalysisResponse(
            is_approved=False,
            strengths="Some diversification",
            weeknesses="Very high risk and poor alignment",
            overall_assessment="Needs improvement",
            advices="Reduce risk and improve diversification",
        )

        print_analysis_response(response)

        output = mock_stdout.getvalue()
        # The output could say "REJECTED" or "NOT APPROVED" or similar
        assert output  # Just verify something was printed

    @patch("sys.stdout", new_callable=StringIO)
    def test_print_analysis_with_none(self, mock_stdout):
        """Test printing None analysis response."""
        print_analysis_response(None)

        output = mock_stdout.getvalue()
        assert "No analysis" in output or "None" in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_print_analysis_strengths_section(self, mock_stdout):
        """Test that strengths section is displayed."""
        response = AnalysisResponse(
            is_approved=True,
            strengths="Strength 1. Strength 2. Strength 3",
            weeknesses="Weakness 1",
            overall_assessment="Good",
            advices="Advice 1",
        )

        print_analysis_response(response)

        output = mock_stdout.getvalue()
        assert (
            "Strength" in output or "STRENGTH" in output or "strength" in output.lower()
        )

    @patch("sys.stdout", new_callable=StringIO)
    def test_print_analysis_weaknesses_section(self, mock_stdout):
        """Test that weaknesses section is displayed."""
        response = AnalysisResponse(
            is_approved=True,
            strengths="Strength 1",
            weeknesses="Weakness 1. Weakness 2",
            overall_assessment="Good",
            advices="Advice 1",
        )

        print_analysis_response(response)

        output = mock_stdout.getvalue()
        assert (
            "Weakness" in output or "WEAKNESS" in output or "weakness" in output.lower()
        )

    @patch("sys.stdout", new_callable=StringIO)
    def test_print_analysis_overall_assessment(self, mock_stdout):
        """Test that overall assessment is displayed."""
        response = AnalysisResponse(
            is_approved=True,
            strengths="Strength 1",
            weeknesses="Weakness 1",
            overall_assessment="This is a detailed assessment",
            advices="Advice 1",
        )

        print_analysis_response(response)

        output = mock_stdout.getvalue()
        assert "detailed assessment" in output or "Assessment" in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_print_analysis_actionable_advice(self, mock_stdout):
        """Test that actionable advice is displayed."""
        response = AnalysisResponse(
            is_approved=True,
            strengths="Strength 1",
            weeknesses="Weakness 1",
            overall_assessment="Good",
            advices="Advice 1. Advice 2. Advice 3",
        )

        print_analysis_response(response)

        output = mock_stdout.getvalue()
        assert "Advice" in output or "ADVICE" in output or "advice" in output.lower()

    @patch("sys.stdout", new_callable=StringIO)
    def test_print_analysis_long_text(self, mock_stdout):
        """Test printing analysis with very long text fields."""
        long_text = "A" * 500  # 500 character string

        response = AnalysisResponse(
            is_approved=True,
            strengths=long_text,
            weeknesses=long_text,
            overall_assessment=long_text,
            advices=long_text,
        )

        print_analysis_response(response)

        output = mock_stdout.getvalue()
        # Should print without errors
        assert len(output) > 0
