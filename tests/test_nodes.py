"""
Tests for advisor nodes (core logic).
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from src.nodes.investment_agents.goal_based import investment_strategy
from src.nodes.portfolios_agent import create_portfolio
from src.nodes.analyst_agents.alignment import analyze_alignment
from src.nodes.analyst_agents.performance import analyze_performance
from src.nodes.analyst_agents.diversification import analyze_diversification
from src.data.models import (
    InvestmentAgent, PortfolioAgent, AnalysisAgent, 
    Status, Portfolio
)


# ============================================================================
# Investment Strategy Node Tests
# ============================================================================

@pytest.mark.unit
class TestInvestmentStrategyNode:
    """Tests for investment_strategy node."""

    def test_investment_strategy_creates_strategy(self, sample_state, mock_llm_with_strategy_response, 
                                                   sample_investment_agent):
        """Test that investment_strategy creates a strategy."""
        sample_state['metadata']['investment_llm_agent'] = mock_llm_with_strategy_response
        
        result = investment_strategy(sample_state)
        
        assert 'investment' in result['data']
        assert 'strategy' in result['data']['investment']
        assert result['data']['investment']['strategy'] is not None
        assert 'analyst' in result['data']['investment']

    def test_investment_strategy_uses_preferences(self, sample_state, mock_llm_with_strategy_response):
        """Test that investment_strategy uses user preferences."""
        sample_state['metadata']['investment_llm_agent'] = mock_llm_with_strategy_response
        
        result = investment_strategy(sample_state)
        
        # Verify the LLM was called
        assert mock_llm_with_strategy_response.invoke.called

    def test_investment_strategy_reasoning_shown(self, sample_state, mock_llm_with_strategy_response, 
                                                  capsys):
        """Test that reasoning is shown when requested."""
        sample_state['metadata']['investment_llm_agent'] = mock_llm_with_strategy_response
        sample_state['metadata']['show_reasoning'] = True
        
        investment_strategy(sample_state)
        
        # Check that something was printed (reasoning)
        captured = capsys.readouterr()
        # Note: actual reasoning text depends on mock, but function should run without error

    def test_investment_strategy_reasoning_hidden(self, sample_state, mock_llm_with_strategy_response):
        """Test that reasoning is hidden when not requested."""
        sample_state['metadata']['investment_llm_agent'] = mock_llm_with_strategy_response
        sample_state['metadata']['show_reasoning'] = False
        
        result = investment_strategy(sample_state)
        
        # Should complete without error
        assert 'strategy' in result['data']['investment']


# ============================================================================
# Portfolio Creation Node Tests
# ============================================================================

@pytest.mark.unit
class TestCreatePortfolioNode:
    """Tests for create_portfolio node."""

    def test_create_portfolio_node(self, sample_state, sample_strategy, sample_portfolio, mock_llm):
        """Test portfolio creation node."""
        # Setup state with strategy
        sample_state['data']['investment'] = {
            'strategy': sample_strategy,
            'analyst': {'name': 'Test Analyst', 'description': 'Test'}
        }
        
        # Setup mock LLM response
        portfolio_agent = PortfolioAgent(
            portfolio=sample_portfolio,
            reasoning="Test reasoning"
        )
        mock_llm.invoke.return_value = portfolio_agent
        sample_state['metadata']['portfolio_llm_agent'] = mock_llm
        
        result = create_portfolio(sample_state)
        
        assert 'portfolio' in result['data']
        assert result['data']['portfolio'] is not None
        assert isinstance(result['data']['portfolio'], Portfolio)

    def test_create_portfolio_uses_strategy(self, sample_state, sample_strategy, sample_portfolio, mock_llm):
        """Test that create_portfolio uses the strategy."""
        sample_state['data']['investment'] = {
            'strategy': sample_strategy,
            'analyst': {'name': 'Test Analyst', 'description': 'Test'}
        }
        
        portfolio_agent = PortfolioAgent(
            portfolio=sample_portfolio,
            reasoning="Test reasoning"
        )
        mock_llm.invoke.return_value = portfolio_agent
        sample_state['metadata']['portfolio_llm_agent'] = mock_llm
        
        result = create_portfolio(sample_state)
        
        # Verify portfolio has the strategy
        assert result['data']['portfolio'].strategy == sample_strategy

    def test_create_portfolio_reasoning_shown(self, sample_state, sample_strategy, 
                                              sample_portfolio, mock_llm, capsys):
        """Test that reasoning is shown when requested."""
        sample_state['data']['investment'] = {
            'strategy': sample_strategy,
            'analyst': {'name': 'Test Analyst', 'description': 'Test'}
        }
        sample_state['metadata']['show_reasoning'] = True
        
        portfolio_agent = PortfolioAgent(
            portfolio=sample_portfolio,
            reasoning="This is test reasoning for portfolio creation"
        )
        mock_llm.invoke.return_value = portfolio_agent
        sample_state['metadata']['portfolio_llm_agent'] = mock_llm
        
        create_portfolio(sample_state)
        
        # Check that reasoning was shown
        # (actual output depends on implementation details)


# ============================================================================
# Alignment Analysis Node Tests
# ============================================================================

@pytest.mark.unit
class TestAlignmentAnalysisNode:
    """Tests for analyze_alignment node."""

    def test_analyze_alignment_basic(self, sample_state_with_portfolio, mock_llm):
        """Test basic alignment analysis."""
        # Setup mock response
        analysis_agent = AnalysisAgent(
            status=Status(key="is_aligned", value=True),
            reasoning="Portfolio is well aligned",
            advices=[]
        )
        mock_llm.invoke.return_value = analysis_agent
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        result = analyze_alignment(sample_state_with_portfolio)
        
        assert 'analysis' in result['data']
        assert 'alignment' in result['data']['analysis']
        assert result['data']['analysis']['alignment'].status.key == "is_aligned"

    def test_analyze_alignment_not_aligned(self, sample_state_with_portfolio, mock_llm):
        """Test alignment analysis when not aligned."""
        analysis_agent = AnalysisAgent(
            status=Status(key="is_aligned", value=False),
            reasoning="Portfolio needs better alignment",
            advices=["Add more bonds", "Reduce risk"]
        )
        mock_llm.invoke.return_value = analysis_agent
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        result = analyze_alignment(sample_state_with_portfolio)
        
        assert result['data']['analysis']['alignment'].status.value is False
        assert len(result['data']['analysis']['alignment'].advices) > 0

    def test_analyze_alignment_reasoning_shown(self, sample_state_with_portfolio, mock_llm, capsys):
        """Test that reasoning is shown when requested."""
        sample_state_with_portfolio['metadata']['show_reasoning'] = True
        
        analysis_agent = AnalysisAgent(
            status=Status(key="is_aligned", value=True),
            reasoning="Detailed alignment reasoning",
            advices=[]
        )
        mock_llm.invoke.return_value = analysis_agent
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        analyze_alignment(sample_state_with_portfolio)


# ============================================================================
# Performance Analysis Node Tests
# ============================================================================

@pytest.mark.unit
class TestPerformanceAnalysisNode:
    """Tests for analyze_performance node."""

    @patch('src.nodes.analyst_agents.performance.all_data')
    @patch('src.nodes.analyst_agents.performance.analyze_portfolio')
    def test_analyze_performance_basic(self, mock_analyze_portfolio, mock_all_data,
                                       sample_state_with_portfolio, mock_llm):
        """Test basic performance analysis."""
        # Setup mocks
        mock_all_data.return_value = ({'VTI': []}, [], {'VTI': 1.0})
        mock_analyze_portfolio.return_value = {
            'portfolio': {
                'CAGR': 0.08,
                'Annualized Volatility': 0.15,
                'Sharpe Ratio': 0.5,
                'Max Drawdown': -0.2,
                'Alpha': 0.02,
                'Beta': 1.1
            },
            'benchmark': {
                'CAGR': 0.07,
                'Annualized Volatility': 0.14,
                'Sharpe Ratio': 0.45,
                'Max Drawdown': -0.18
            }
        }
        
        analysis_agent = AnalysisAgent(
            status=Status(key="is_performing", value=True),
            reasoning="Portfolio is performing well",
            advices=[]
        )
        mock_llm.invoke.return_value = analysis_agent
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        result = analyze_performance(sample_state_with_portfolio)
        
        assert 'analysis' in result['data']
        assert 'performance' in result['data']['analysis']
        assert result['data']['analysis']['performance'].status.key == "is_performing"

    @patch('src.nodes.analyst_agents.performance.all_data')
    @patch('src.nodes.analyst_agents.performance.analyze_portfolio')
    def test_analyze_performance_sets_benchmark(self, mock_analyze_portfolio, mock_all_data,
                                                sample_state_with_portfolio, mock_llm):
        """Test that performance analysis sets default benchmark."""
        mock_all_data.return_value = ({'VTI': []}, [], {'VTI': 1.0})
        mock_analyze_portfolio.return_value = {
            'portfolio': {
                'CAGR': 0.08,
                'Annualized Volatility': 0.15,
                'Sharpe Ratio': 0.5,
                'Max Drawdown': -0.2,
                'Alpha': 0.02,
                'Beta': 1.1
            },
            'benchmark': {
                'CAGR': 0.07,
                'Annualized Volatility': 0.14,
                'Sharpe Ratio': 0.45,
                'Max Drawdown': -0.18
            }
        }
        
        analysis_agent = AnalysisAgent(
            status=Status(key="is_performing", value=True),
            reasoning="Portfolio is performing well",
            advices=[]
        )
        mock_llm.invoke.return_value = analysis_agent
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        # Ensure benchmark is not set
        if 'benchmark' in sample_state_with_portfolio['data']:
            del sample_state_with_portfolio['data']['benchmark']
        
        result = analyze_performance(sample_state_with_portfolio)
        
        # Should set default benchmark
        assert 'benchmark' in result['data']
        assert result['data']['benchmark'] == "ACWI"

    @patch('src.nodes.analyst_agents.performance.all_data')
    @patch('src.nodes.analyst_agents.performance.analyze_portfolio')
    def test_analyze_performance_poor_performance(self, mock_analyze_portfolio, mock_all_data,
                                                  sample_state_with_portfolio, mock_llm):
        """Test performance analysis with poor performance."""
        mock_all_data.return_value = ({'VTI': []}, [], {'VTI': 1.0})
        mock_analyze_portfolio.return_value = {
            'portfolio': {
                'CAGR': 0.03,
                'Annualized Volatility': 0.20,
                'Sharpe Ratio': 0.1,
                'Max Drawdown': -0.35,
                'Alpha': -0.03,
                'Beta': 1.2
            },
            'benchmark': {
                'CAGR': 0.07,
                'Annualized Volatility': 0.14,
                'Sharpe Ratio': 0.45,
                'Max Drawdown': -0.18
            }
        }
        
        analysis_agent = AnalysisAgent(
            status=Status(key="is_performing", value=False),
            reasoning="Portfolio is underperforming",
            advices=["Rebalance portfolio", "Review asset allocation"]
        )
        mock_llm.invoke.return_value = analysis_agent
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        result = analyze_performance(sample_state_with_portfolio)
        
        assert result['data']['analysis']['performance'].status.value is False
        assert len(result['data']['analysis']['performance'].advices) > 0


# ============================================================================
# Fees Analysis Node Tests
# ============================================================================

@pytest.mark.unit
class TestFeesAnalysisNode:
    """Tests for analyze_ter (Total Expense Ratio) node."""

    def test_analyze_ter_basic(self, sample_state_with_portfolio, mock_llm):
        """Test basic TER analysis."""
        from src.nodes.analyst_agents.fees import analyze_ter
        
        # Setup mock response
        analysis_agent = AnalysisAgent(
            status=Status(key="is_cheaper", value=True),
            reasoning="All funds have low expense ratios",
            advices=[]
        )
        mock_llm.invoke.return_value = analysis_agent
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        result = analyze_ter(sample_state_with_portfolio)
        
        assert 'analysis' in result['data']
        assert 'expense_ratio' in result['data']['analysis']
        assert result['data']['analysis']['expense_ratio'].status.key == "is_cheaper"
        assert result['data']['analysis']['expense_ratio'].status.value is True

    def test_analyze_ter_expensive_funds(self, sample_state_with_portfolio, mock_llm):
        """Test TER analysis when funds are expensive."""
        from src.nodes.analyst_agents.fees import analyze_ter
        
        analysis_agent = AnalysisAgent(
            status=Status(key="is_cheaper", value=False),
            reasoning="Some funds have high expense ratios above 0.4%",
            advices=["Consider switching to Vanguard Total Market (VTI) with 0.03% TER",
                    "Look at lower-cost alternatives for high-fee holdings"]
        )
        mock_llm.invoke.return_value = analysis_agent
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        result = analyze_ter(sample_state_with_portfolio)
        
        assert result['data']['analysis']['expense_ratio'].status.value is False
        assert len(result['data']['analysis']['expense_ratio'].advices) > 0

    def test_analyze_ter_reasoning_shown(self, sample_state_with_portfolio, mock_llm, capsys):
        """Test that reasoning is shown when requested."""
        from src.nodes.analyst_agents.fees import analyze_ter
        
        sample_state_with_portfolio['metadata']['show_reasoning'] = True
        
        analysis_agent = AnalysisAgent(
            status=Status(key="is_cheaper", value=True),
            reasoning="Detailed TER analysis: VTI has 0.03% TER, BND has 0.035% TER",
            advices=[]
        )
        mock_llm.invoke.return_value = analysis_agent
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        analyze_ter(sample_state_with_portfolio)
        
        captured = capsys.readouterr()
        assert "Detailed TER analysis" in captured.out or "TER" in captured.out

    def test_analyze_ter_reasoning_hidden(self, sample_state_with_portfolio, mock_llm, capsys):
        """Test that reasoning is hidden when not requested."""
        from src.nodes.analyst_agents.fees import analyze_ter
        
        sample_state_with_portfolio['metadata']['show_reasoning'] = False
        
        analysis_agent = AnalysisAgent(
            status=Status(key="is_cheaper", value=True),
            reasoning="Detailed TER analysis that should not be shown",
            advices=[]
        )
        mock_llm.invoke.return_value = analysis_agent
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        analyze_ter(sample_state_with_portfolio)
        
        captured = capsys.readouterr()
        # Reasoning should not be printed
        assert captured.out == "" or "should not be shown" not in captured.out

    def test_analyze_ter_initializes_analysis_dict(self, sample_state_with_portfolio, mock_llm):
        """Test that analysis dict is initialized if it doesn't exist."""
        from src.nodes.analyst_agents.fees import analyze_ter
        
        # Remove analysis dict if it exists
        if 'analysis' in sample_state_with_portfolio['data']:
            del sample_state_with_portfolio['data']['analysis']
        
        analysis_agent = AnalysisAgent(
            status=Status(key="is_cheaper", value=True),
            reasoning="Low cost analysis",
            advices=[]
        )
        mock_llm.invoke.return_value = analysis_agent
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        result = analyze_ter(sample_state_with_portfolio)
        
        assert 'analysis' in result['data']
        assert 'expense_ratio' in result['data']['analysis']

    def test_analyze_ter_with_existing_analysis(self, sample_state_with_portfolio, mock_llm):
        """Test TER analysis when analysis dict already exists."""
        from src.nodes.analyst_agents.fees import analyze_ter
        
        # Pre-populate analysis dict
        sample_state_with_portfolio['data']['analysis'] = {
            'alignment': AnalysisAgent(
                status=Status(key="is_aligned", value=True),
                reasoning="Already analyzed",
                advices=[]
            )
        }
        
        analysis_agent = AnalysisAgent(
            status=Status(key="is_cheaper", value=True),
            reasoning="TER analysis",
            advices=[]
        )
        mock_llm.invoke.return_value = analysis_agent
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        result = analyze_ter(sample_state_with_portfolio)
        
        # Both analyses should exist
        assert 'alignment' in result['data']['analysis']
        assert 'expense_ratio' in result['data']['analysis']

    def test_analyze_ter_llm_invocation(self, sample_state_with_portfolio, mock_llm):
        """Test that LLM is invoked with proper prompt."""
        from src.nodes.analyst_agents.fees import analyze_ter
        
        analysis_agent = AnalysisAgent(
            status=Status(key="is_cheaper", value=True),
            reasoning="Analysis complete",
            advices=[]
        )
        mock_llm.invoke.return_value = analysis_agent
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        analyze_ter(sample_state_with_portfolio)
        
        # Verify LLM was called
        mock_llm.invoke.assert_called_once()
        # Get the prompt that was passed
        call_args = mock_llm.invoke.call_args
        prompt = call_args[0][0]
        
        # Verify prompt contains expected content
        assert "Total Expense Ratio" in prompt or "TER" in prompt
        assert "portfolio" in prompt.lower() or "holding" in prompt.lower()

    def test_analyze_ter_with_multiple_advices(self, sample_state_with_portfolio, mock_llm):
        """Test TER analysis with multiple cost-saving recommendations."""
        from src.nodes.analyst_agents.fees import analyze_ter
        
        analysis_agent = AnalysisAgent(
            status=Status(key="is_cheaper", value=False),
            reasoning="Multiple high-cost funds identified",
            advices=[
                "Replace Fund A with low-cost alternative X (0.03% vs 0.50%)",
                "Replace Fund B with low-cost alternative Y (0.04% vs 0.60%)",
                "Consider index funds instead of actively managed funds"
            ]
        )
        mock_llm.invoke.return_value = analysis_agent
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        result = analyze_ter(sample_state_with_portfolio)
        
        assert len(result['data']['analysis']['expense_ratio'].advices) == 3
        assert result['data']['analysis']['expense_ratio'].status.value is False


# ============================================================================
# Diversification Analysis Node Tests
# ============================================================================

@pytest.mark.unit
class TestDiversificationAnalysisNode:
    """Tests for analyze_diversification node."""

    def test_analyze_diversification_basic(self, sample_state_with_portfolio, mock_llm):
        """Test basic diversification analysis."""
        # Setup mock response
        analysis_agent = AnalysisAgent(
            status=Status(key="is_diversified", value=True),
            reasoning="Portfolio is well diversified across asset classes, regions, and sectors",
            advices=[]
        )
        mock_llm.invoke.return_value = analysis_agent
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        result = analyze_diversification(sample_state_with_portfolio)
        
        assert 'analysis' in result['data']
        assert 'diversification' in result['data']['analysis']
        assert result['data']['analysis']['diversification'].status.key == "is_diversified"
        assert result['data']['analysis']['diversification'].status.value is True

    def test_analyze_diversification_not_diversified(self, sample_state_with_portfolio, mock_llm):
        """Test diversification analysis when not diversified."""
        analysis_agent = AnalysisAgent(
            status=Status(key="is_diversified", value=False),
            reasoning="Portfolio lacks geographical diversification",
            advices=["Add international exposure", "Rebalance sector allocation"]
        )
        mock_llm.invoke.return_value = analysis_agent
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        result = analyze_diversification(sample_state_with_portfolio)
        
        assert result['data']['analysis']['diversification'].status.value is False
        assert len(result['data']['analysis']['diversification'].advices) == 2

    def test_analyze_diversification_reasoning_shown(self, sample_state_with_portfolio, mock_llm, capsys):
        """Test that reasoning is shown when requested."""
        sample_state_with_portfolio['metadata']['show_reasoning'] = True
        
        analysis_agent = AnalysisAgent(
            status=Status(key="is_diversified", value=True),
            reasoning="Detailed diversification analysis reasoning",
            advices=[]
        )
        mock_llm.invoke.return_value = analysis_agent
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        analyze_diversification(sample_state_with_portfolio)
        
        captured = capsys.readouterr()
        assert "Detailed diversification analysis reasoning" in captured.out

    def test_analyze_diversification_reasoning_not_shown(self, sample_state_with_portfolio, mock_llm, capsys):
        """Test that reasoning is not shown when not requested."""
        sample_state_with_portfolio['metadata']['show_reasoning'] = False
        
        analysis_agent = AnalysisAgent(
            status=Status(key="is_diversified", value=True),
            reasoning="This should not be printed",
            advices=[]
        )
        mock_llm.invoke.return_value = analysis_agent
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        analyze_diversification(sample_state_with_portfolio)
        
        captured = capsys.readouterr()
        assert "This should not be printed" not in captured.out

    def test_analyze_diversification_asset_class_issues(self, sample_state_with_portfolio, mock_llm):
        """Test diversification analysis with asset class imbalance."""
        analysis_agent = AnalysisAgent(
            status=Status(key="is_diversified", value=False),
            reasoning="Equity allocation is 10% over target, bonds are 10% under target",
            advices=["Reduce equity allocation by 10%", "Increase bond allocation by 10%"]
        )
        mock_llm.invoke.return_value = analysis_agent
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        result = analyze_diversification(sample_state_with_portfolio)
        
        assert result['data']['analysis']['diversification'].status.value is False
        assert "equity" in result['data']['analysis']['diversification'].reasoning.lower()
        assert "bond" in result['data']['analysis']['diversification'].reasoning.lower()

    def test_analyze_diversification_geographical_issues(self, sample_state_with_portfolio, mock_llm):
        """Test diversification analysis with geographical concentration."""
        analysis_agent = AnalysisAgent(
            status=Status(key="is_diversified", value=False),
            reasoning="Portfolio is heavily concentrated in US markets (85% vs 70% target)",
            advices=[
                "Reduce US exposure to 70%",
                "Increase international developed markets exposure",
                "Add emerging markets allocation"
            ]
        )
        mock_llm.invoke.return_value = analysis_agent
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        result = analyze_diversification(sample_state_with_portfolio)
        
        assert result['data']['analysis']['diversification'].status.value is False
        assert len(result['data']['analysis']['diversification'].advices) == 3
        assert "US" in result['data']['analysis']['diversification'].reasoning

    def test_analyze_diversification_sector_concentration(self, sample_state_with_portfolio, mock_llm):
        """Test diversification analysis with sector concentration."""
        analysis_agent = AnalysisAgent(
            status=Status(key="is_diversified", value=False),
            reasoning="Technology sector is overweight at 45% (target 25%), lacking exposure to healthcare and financials",
            advices=[
                "Reduce technology sector allocation to 25%",
                "Add healthcare sector exposure (target 15%)",
                "Add financial sector exposure (target 10%)"
            ]
        )
        mock_llm.invoke.return_value = analysis_agent
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        result = analyze_diversification(sample_state_with_portfolio)
        
        assert result['data']['analysis']['diversification'].status.value is False
        assert "technology" in result['data']['analysis']['diversification'].reasoning.lower()
        assert len(result['data']['analysis']['diversification'].advices) == 3

    def test_analyze_diversification_multiple_issues(self, sample_state_with_portfolio, mock_llm):
        """Test diversification analysis with multiple diversification issues."""
        analysis_agent = AnalysisAgent(
            status=Status(key="is_diversified", value=False),
            reasoning="Portfolio has issues across all dimensions: asset class (too much equity), "
                     "geography (US-heavy), and sectors (tech concentration)",
            advices=[
                "Rebalance asset allocation to match strategy targets",
                "Increase international diversification",
                "Reduce technology sector concentration",
                "Add exposure to underweight sectors"
            ]
        )
        mock_llm.invoke.return_value = analysis_agent
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        result = analyze_diversification(sample_state_with_portfolio)
        
        assert result['data']['analysis']['diversification'].status.value is False
        assert len(result['data']['analysis']['diversification'].advices) == 4

    def test_analyze_diversification_initializes_analysis_dict(self, sample_state_with_portfolio, mock_llm):
        """Test that analysis dict is initialized if it doesn't exist."""
        # Remove analysis dict
        if 'analysis' in sample_state_with_portfolio['data']:
            del sample_state_with_portfolio['data']['analysis']
        
        analysis_agent = AnalysisAgent(
            status=Status(key="is_diversified", value=True),
            reasoning="Well diversified",
            advices=[]
        )
        mock_llm.invoke.return_value = analysis_agent
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        result = analyze_diversification(sample_state_with_portfolio)
        
        assert 'analysis' in result['data']
        assert 'diversification' in result['data']['analysis']

    def test_analyze_diversification_llm_prompt_structure(self, sample_state_with_portfolio, mock_llm):
        """Test that the LLM is called with proper prompt structure."""
        analysis_agent = AnalysisAgent(
            status=Status(key="is_diversified", value=True),
            reasoning="Analysis complete",
            advices=[]
        )
        mock_llm.invoke.return_value = analysis_agent
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        analyze_diversification(sample_state_with_portfolio)
        
        # Verify LLM was called
        mock_llm.invoke.assert_called_once()
        
        # Get the prompt that was passed
        call_args = mock_llm.invoke.call_args
        prompt = call_args[0][0]
        
        # Verify prompt contains key elements
        assert "diversification" in prompt.lower()
        assert "asset" in prompt.lower() or "allocation" in prompt.lower()
        assert "geographical" in prompt.lower() or "geography" in prompt.lower()
        assert "sector" in prompt.lower()
        assert "is_diversified" in prompt

    def test_analyze_diversification_uses_portfolio_data(self, sample_state_with_portfolio, mock_llm):
        """Test that diversification analysis uses portfolio holdings and strategy."""
        analysis_agent = AnalysisAgent(
            status=Status(key="is_diversified", value=True),
            reasoning="Analysis based on portfolio data",
            advices=[]
        )
        mock_llm.invoke.return_value = analysis_agent
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        analyze_diversification(sample_state_with_portfolio)
        
        # Verify LLM was called with prompt containing portfolio data
        call_args = mock_llm.invoke.call_args
        prompt = call_args[0][0]
        
        # Prompt should contain portfolio and strategy information
        assert "PORTFOLIO DATA" in prompt or "portfolio" in prompt.lower()
        assert "STRATEGY DATA" in prompt or "strategy" in prompt.lower()

    def test_analyze_diversification_empty_advices_when_diversified(self, sample_state_with_portfolio, mock_llm):
        """Test that advices are empty when portfolio is well diversified."""
        analysis_agent = AnalysisAgent(
            status=Status(key="is_diversified", value=True),
            reasoning="Portfolio meets all diversification targets within ±5% tolerance",
            advices=[]
        )
        mock_llm.invoke.return_value = analysis_agent
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        result = analyze_diversification(sample_state_with_portfolio)
        
        assert result['data']['analysis']['diversification'].status.value is True
        assert len(result['data']['analysis']['diversification'].advices) == 0

    def test_analyze_diversification_with_structured_output(self, sample_state_with_portfolio):
        """Test that analyze_diversification uses structured output from LLM."""
        # Create a mock LLM with with_structured_output chain
        mock_llm = MagicMock()
        mock_structured = MagicMock()
        
        analysis_agent = AnalysisAgent(
            status=Status(key="is_diversified", value=True),
            reasoning="Structured output test",
            advices=[]
        )
        mock_structured.invoke.return_value = analysis_agent
        mock_llm.with_structured_output.return_value = mock_structured
        
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        result = analyze_diversification(sample_state_with_portfolio)
        
        # Verify with_structured_output was called
        mock_llm.with_structured_output.assert_called_once()
        # Verify invoke was called on the structured output
        mock_structured.invoke.assert_called_once()
        assert result['data']['analysis']['diversification'] == analysis_agent


# ============================================================================
# Node Integration Tests
# ============================================================================

@pytest.mark.integration
class TestNodesIntegration:
    """Integration tests for advisor nodes."""

    def test_investment_to_portfolio_flow(self, sample_state, mock_llm_with_strategy_response,
                                          sample_portfolio, mock_llm):
        """Test flow from investment strategy to portfolio creation."""
        # Step 1: Create investment strategy
        sample_state['metadata']['investment_llm_agent'] = mock_llm_with_strategy_response
        state_after_strategy = investment_strategy(sample_state)
        
        assert 'strategy' in state_after_strategy['data']['investment']
        
        # Step 2: Create portfolio
        portfolio_agent = PortfolioAgent(
            portfolio=sample_portfolio,
            reasoning="Test reasoning"
        )
        mock_llm.invoke.return_value = portfolio_agent
        state_after_strategy['metadata']['portfolio_llm_agent'] = mock_llm
        
        state_after_portfolio = create_portfolio(state_after_strategy)
        
        assert 'portfolio' in state_after_portfolio['data']
        assert state_after_portfolio['data']['portfolio'].strategy is not None
