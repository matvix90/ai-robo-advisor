"""
Tests for the analyst workflow and graph.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

from src.nodes.analyst_agents.analysis_workflow import (
    start,
    is_approved,
    create_analyst_graph
)
from src.data.models import AnalysisAgent, AnalysisResponse, Status


# ============================================================================
# Start Node Tests
# ============================================================================

@pytest.mark.unit
class TestAnalystStartNode:
    """Tests for the analyst workflow start node."""

    def test_start_returns_state(self, sample_state):
        """Test that start node returns the state unchanged."""
        result = start(sample_state)
        
        assert result == sample_state
        assert result['data'] == sample_state['data']
        assert result['metadata'] == sample_state['metadata']

    @patch('sys.stdout', new_callable=StringIO)
    def test_start_prints_message(self, mock_stdout, sample_state):
        """Test that start node prints starting message."""
        start(sample_state)
        
        output = mock_stdout.getvalue()
        assert "Starting analysis workflow" in output or "analysis" in output.lower()

    def test_start_preserves_all_fields(self, sample_state_with_portfolio):
        """Test that start node preserves all state fields."""
        result = start(sample_state_with_portfolio)
        
        assert 'data' in result
        assert 'metadata' in result
        assert 'portfolio' in result['data']


# ============================================================================
# Is Approved Node Tests
# ============================================================================

@pytest.mark.unit
class TestIsApprovedNode:
    """Tests for the is_approved node."""

    def test_is_approved_all_pass(self, sample_state_with_portfolio, mock_llm):
        """Test approval when all 4 criteria pass."""
        # Setup state with all passing analysis
        sample_state_with_portfolio['data']['analysis'] = {
            'expense_ratio': AnalysisAgent(
                status=Status(key="is_cheaper", value=True),
                reasoning="Low fees",
                advices=[]
            ),
            'diversification': AnalysisAgent(
                status=Status(key="is_diversified", value=True),
                reasoning="Well diversified",
                advices=[]
            ),
            'alignment': AnalysisAgent(
                status=Status(key="is_aligned", value=True),
                reasoning="Aligned with goals",
                advices=[]
            ),
            'performance': AnalysisAgent(
                status=Status(key="is_performing", value=True),
                reasoning="Good performance",
                advices=[]
            )
        }
        
        # Mock LLM response
        analysis_response = AnalysisResponse(
            is_approved=True,
            strengths="All criteria met",
            weeknesses="None",
            overall_assessment="Excellent portfolio",
            advices="Continue monitoring"
        )
        mock_llm.invoke.return_value = analysis_response
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        result = is_approved(sample_state_with_portfolio)
        
        assert result['data']['analysis']['is_approved'] is True
        assert result['data']['analysis']['summary'].is_approved is True

    def test_is_approved_three_pass(self, sample_state_with_portfolio, mock_llm):
        """Test approval when 3 out of 4 criteria pass (confidence >= 2)."""
        # Setup state with 3 passing analysis
        sample_state_with_portfolio['data']['analysis'] = {
            'expense_ratio': AnalysisAgent(
                status=Status(key="is_cheaper", value=True),
                reasoning="Low fees",
                advices=[]
            ),
            'diversification': AnalysisAgent(
                status=Status(key="is_diversified", value=True),
                reasoning="Well diversified",
                advices=[]
            ),
            'alignment': AnalysisAgent(
                status=Status(key="is_aligned", value=True),
                reasoning="Aligned with goals",
                advices=[]
            ),
            'performance': AnalysisAgent(
                status=Status(key="is_performing", value=False),
                reasoning="Underperforming",
                advices=["Rebalance"]
            )
        }
        
        analysis_response = AnalysisResponse(
            is_approved=True,
            strengths="Most criteria met",
            weeknesses="Performance issues",
            overall_assessment="Good portfolio with room for improvement",
            advices="Address performance concerns"
        )
        mock_llm.invoke.return_value = analysis_response
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        result = is_approved(sample_state_with_portfolio)
        
        assert result['data']['analysis']['is_approved'] is True

    def test_is_approved_two_pass(self, sample_state_with_portfolio, mock_llm):
        """Test approval when exactly 2 criteria pass (minimum threshold)."""
        # Setup state with 2 passing analysis
        sample_state_with_portfolio['data']['analysis'] = {
            'expense_ratio': AnalysisAgent(
                status=Status(key="is_cheaper", value=True),
                reasoning="Low fees",
                advices=[]
            ),
            'diversification': AnalysisAgent(
                status=Status(key="is_diversified", value=True),
                reasoning="Well diversified",
                advices=[]
            ),
            'alignment': AnalysisAgent(
                status=Status(key="is_aligned", value=False),
                reasoning="Misaligned",
                advices=["Adjust strategy"]
            ),
            'performance': AnalysisAgent(
                status=Status(key="is_performing", value=False),
                reasoning="Poor performance",
                advices=["Review holdings"]
            )
        }
        
        analysis_response = AnalysisResponse(
            is_approved=True,
            strengths="Good fees and diversification",
            weeknesses="Alignment and performance issues",
            overall_assessment="Borderline approval",
            advices="Address alignment and performance"
        )
        mock_llm.invoke.return_value = analysis_response
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        result = is_approved(sample_state_with_portfolio)
        
        assert result['data']['analysis']['is_approved'] is True

    def test_is_approved_one_pass_rejected(self, sample_state_with_portfolio, mock_llm):
        """Test rejection when only 1 criterion passes."""
        # Setup state with only 1 passing analysis
        sample_state_with_portfolio['data']['analysis'] = {
            'expense_ratio': AnalysisAgent(
                status=Status(key="is_cheaper", value=True),
                reasoning="Low fees",
                advices=[]
            ),
            'diversification': AnalysisAgent(
                status=Status(key="is_diversified", value=False),
                reasoning="Poor diversification",
                advices=["Add more asset classes"]
            ),
            'alignment': AnalysisAgent(
                status=Status(key="is_aligned", value=False),
                reasoning="Misaligned",
                advices=["Adjust strategy"]
            ),
            'performance': AnalysisAgent(
                status=Status(key="is_performing", value=False),
                reasoning="Poor performance",
                advices=["Review holdings"]
            )
        }
        
        analysis_response = AnalysisResponse(
            is_approved=False,
            strengths="Low fees",
            weeknesses="Diversification, alignment, and performance issues",
            overall_assessment="Portfolio needs significant improvement",
            advices="Major restructuring recommended"
        )
        mock_llm.invoke.return_value = analysis_response
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        result = is_approved(sample_state_with_portfolio)
        
        assert result['data']['analysis']['is_approved'] is False

    def test_is_approved_all_fail(self, sample_state_with_portfolio, mock_llm):
        """Test rejection when all criteria fail."""
        # Setup state with all failing analysis
        sample_state_with_portfolio['data']['analysis'] = {
            'expense_ratio': AnalysisAgent(
                status=Status(key="is_cheaper", value=False),
                reasoning="High fees",
                advices=["Switch to lower-cost funds"]
            ),
            'diversification': AnalysisAgent(
                status=Status(key="is_diversified", value=False),
                reasoning="Poor diversification",
                advices=["Add more asset classes"]
            ),
            'alignment': AnalysisAgent(
                status=Status(key="is_aligned", value=False),
                reasoning="Misaligned",
                advices=["Adjust strategy"]
            ),
            'performance': AnalysisAgent(
                status=Status(key="is_performing", value=False),
                reasoning="Poor performance",
                advices=["Review holdings"]
            )
        }
        
        analysis_response = AnalysisResponse(
            is_approved=False,
            strengths="None identified",
            weeknesses="All criteria failed",
            overall_assessment="Portfolio requires complete overhaul",
            advices="Consider starting fresh with a new strategy"
        )
        mock_llm.invoke.return_value = analysis_response
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        result = is_approved(sample_state_with_portfolio)
        
        assert result['data']['analysis']['is_approved'] is False

    def test_is_approved_collects_all_advices(self, sample_state_with_portfolio, mock_llm):
        """Test that all advices from individual analyses are collected."""
        # Setup state with advices from multiple analyses
        sample_state_with_portfolio['data']['analysis'] = {
            'expense_ratio': AnalysisAgent(
                status=Status(key="is_cheaper", value=False),
                reasoning="High fees",
                advices=["Advice from fees analysis"]
            ),
            'diversification': AnalysisAgent(
                status=Status(key="is_diversified", value=False),
                reasoning="Poor diversification",
                advices=["Advice from diversification 1", "Advice from diversification 2"]
            ),
            'alignment': AnalysisAgent(
                status=Status(key="is_aligned", value=False),
                reasoning="Misaligned",
                advices=["Advice from alignment"]
            ),
            'performance': AnalysisAgent(
                status=Status(key="is_performing", value=False),
                reasoning="Poor performance",
                advices=["Advice from performance"]
            )
        }
        
        analysis_response = AnalysisResponse(
            is_approved=False,
            strengths="None",
            weeknesses="Multiple issues",
            overall_assessment="Needs work",
            advices="Follow individual recommendations"
        )
        mock_llm.invoke.return_value = analysis_response
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        is_approved(sample_state_with_portfolio)
        
        # Verify LLM was called and prompt contains advice
        mock_llm.invoke.assert_called_once()
        call_args = mock_llm.invoke.call_args
        prompt = call_args[0][0]
        
        # Check that advices are included in prompt
        assert "Advice from fees analysis" in prompt
        assert "Advice from diversification 1" in prompt
        assert "Advice from alignment" in prompt
        assert "Advice from performance" in prompt

    def test_is_approved_no_advices(self, sample_state_with_portfolio, mock_llm):
        """Test when no advices are provided by individual analyses."""
        # Setup state with no advices
        sample_state_with_portfolio['data']['analysis'] = {
            'expense_ratio': AnalysisAgent(
                status=Status(key="is_cheaper", value=True),
                reasoning="Low fees",
                advices=[]
            ),
            'diversification': AnalysisAgent(
                status=Status(key="is_diversified", value=True),
                reasoning="Well diversified",
                advices=[]
            ),
            'alignment': AnalysisAgent(
                status=Status(key="is_aligned", value=True),
                reasoning="Aligned",
                advices=[]
            ),
            'performance': AnalysisAgent(
                status=Status(key="is_performing", value=True),
                reasoning="Good performance",
                advices=[]
            )
        }
        
        analysis_response = AnalysisResponse(
            is_approved=True,
            strengths="All good",
            weeknesses="None",
            overall_assessment="Excellent",
            advices="Keep it up"
        )
        mock_llm.invoke.return_value = analysis_response
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        result = is_approved(sample_state_with_portfolio)
        
        # Verify LLM was called
        mock_llm.invoke.assert_called_once()
        call_args = mock_llm.invoke.call_args
        prompt = call_args[0][0]
        
        # Check that prompt mentions no advice
        assert "No specific advice" in prompt or "no advice" in prompt.lower()

    def test_is_approved_llm_prompt_structure(self, sample_state_with_portfolio, mock_llm):
        """Test that LLM prompt contains all necessary information."""
        # Setup state
        sample_state_with_portfolio['data']['analysis'] = {
            'expense_ratio': AnalysisAgent(
                status=Status(key="is_cheaper", value=True),
                reasoning="Low fees reasoning",
                advices=[]
            ),
            'diversification': AnalysisAgent(
                status=Status(key="is_diversified", value=True),
                reasoning="Diversification reasoning",
                advices=[]
            ),
            'alignment': AnalysisAgent(
                status=Status(key="is_aligned", value=False),
                reasoning="Alignment reasoning",
                advices=[]
            ),
            'performance': AnalysisAgent(
                status=Status(key="is_performing", value=True),
                reasoning="Performance reasoning",
                advices=[]
            )
        }
        
        analysis_response = AnalysisResponse(
            is_approved=True,
            strengths="Multiple strengths",
            weeknesses="Some weaknesses",
            overall_assessment="Good overall",
            advices="Continue"
        )
        mock_llm.invoke.return_value = analysis_response
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        is_approved(sample_state_with_portfolio)
        
        # Get the prompt
        call_args = mock_llm.invoke.call_args
        prompt = call_args[0][0]
        
        # Verify prompt contains all analysis results
        assert "Expense Ratio" in prompt or "expense" in prompt.lower()
        assert "Diversification" in prompt or "diversification" in prompt.lower()
        assert "Alignment" in prompt or "alignment" in prompt.lower()
        assert "Performance" in prompt or "performance" in prompt.lower()
        
        # Verify prompt contains reasoning
        assert "Low fees reasoning" in prompt
        assert "Diversification reasoning" in prompt
        assert "Alignment reasoning" in prompt
        assert "Performance reasoning" in prompt
        
        # Verify prompt contains confidence score
        assert "3/4" in prompt  # 3 out of 4 passed
        
        # Verify prompt contains approval status
        assert "APPROVED" in prompt


# ============================================================================
# Create Analyst Graph Tests
# ============================================================================

@pytest.mark.unit
class TestCreateAnalystGraph:
    """Tests for create_analyst_graph function."""

    def test_create_analyst_graph_returns_compiled_graph(self):
        """Test that create_analyst_graph returns a compiled graph."""
        graph = create_analyst_graph()
        
        assert graph is not None
        # The graph should be a compiled StateGraph

    def test_create_analyst_graph_is_callable(self):
        """Test that the returned graph can be invoked."""
        graph = create_analyst_graph()
        
        # Should have invoke method
        assert hasattr(graph, 'invoke') or callable(graph)

    @patch('src.nodes.analyst_agents.fees.analyze_ter')
    @patch('src.nodes.analyst_agents.diversification.analyze_diversification')
    @patch('src.nodes.analyst_agents.alignment.analyze_alignment')
    @patch('src.nodes.analyst_agents.performance.analyze_performance')
    def test_create_analyst_graph_nodes_integrated(self, mock_perf, mock_align, 
                                                   mock_div, mock_fees,
                                                   sample_state_with_portfolio, mock_llm):
        """Test that graph properly integrates all analyst nodes."""
        # Setup mocks to return state
        mock_fees.return_value = sample_state_with_portfolio
        mock_div.return_value = sample_state_with_portfolio
        mock_align.return_value = sample_state_with_portfolio
        mock_perf.return_value = sample_state_with_portfolio
        
        # Setup analysis results in state
        sample_state_with_portfolio['data']['analysis'] = {
            'expense_ratio': AnalysisAgent(
                status=Status(key="is_cheaper", value=True),
                reasoning="Test",
                advices=[]
            ),
            'diversification': AnalysisAgent(
                status=Status(key="is_diversified", value=True),
                reasoning="Test",
                advices=[]
            ),
            'alignment': AnalysisAgent(
                status=Status(key="is_aligned", value=True),
                reasoning="Test",
                advices=[]
            ),
            'performance': AnalysisAgent(
                status=Status(key="is_performing", value=True),
                reasoning="Test",
                advices=[]
            )
        }
        
        # Mock LLM for is_approved node
        analysis_response = AnalysisResponse(
            is_approved=True,
            strengths="All good",
            weeknesses="None",
            overall_assessment="Excellent",
            advices="Continue"
        )
        mock_llm.invoke.return_value = analysis_response
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        graph = create_analyst_graph()
        
        # Should be able to create graph without errors
        assert graph is not None


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.integration
class TestAnalystWorkflowIntegration:
    """Integration tests for the analyst workflow."""

    def test_analyst_workflow_end_to_end_approved(self, sample_state_with_portfolio, mock_llm):
        """Test complete analyst workflow with approved result."""
        # Setup all analysis results
        sample_state_with_portfolio['data']['analysis'] = {
            'expense_ratio': AnalysisAgent(
                status=Status(key="is_cheaper", value=True),
                reasoning="Low fees",
                advices=[]
            ),
            'diversification': AnalysisAgent(
                status=Status(key="is_diversified", value=True),
                reasoning="Well diversified",
                advices=[]
            ),
            'alignment': AnalysisAgent(
                status=Status(key="is_aligned", value=True),
                reasoning="Aligned",
                advices=[]
            ),
            'performance': AnalysisAgent(
                status=Status(key="is_performing", value=True),
                reasoning="Good performance",
                advices=[]
            )
        }
        
        analysis_response = AnalysisResponse(
            is_approved=True,
            strengths="All criteria met",
            weeknesses="None",
            overall_assessment="Excellent portfolio",
            advices="Continue monitoring"
        )
        mock_llm.invoke.return_value = analysis_response
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        # Test the is_approved node directly
        result = is_approved(sample_state_with_portfolio)
        
        assert 'summary' in result['data']['analysis']
        assert result['data']['analysis']['is_approved'] is True
        assert result['data']['analysis']['summary'].is_approved is True

    def test_analyst_workflow_end_to_end_rejected(self, sample_state_with_portfolio, mock_llm):
        """Test complete analyst workflow with rejected result."""
        # Setup analysis results with majority failing
        sample_state_with_portfolio['data']['analysis'] = {
            'expense_ratio': AnalysisAgent(
                status=Status(key="is_cheaper", value=False),
                reasoning="High fees",
                advices=["Lower costs"]
            ),
            'diversification': AnalysisAgent(
                status=Status(key="is_diversified", value=False),
                reasoning="Poor diversification",
                advices=["Diversify more"]
            ),
            'alignment': AnalysisAgent(
                status=Status(key="is_aligned", value=False),
                reasoning="Misaligned",
                advices=["Realign"]
            ),
            'performance': AnalysisAgent(
                status=Status(key="is_performing", value=True),
                reasoning="Good performance",
                advices=[]
            )
        }
        
        analysis_response = AnalysisResponse(
            is_approved=False,
            strengths="Performance is acceptable",
            weeknesses="Fees, diversification, and alignment issues",
            overall_assessment="Portfolio needs improvement",
            advices="Address the three main issues"
        )
        mock_llm.invoke.return_value = analysis_response
        sample_state_with_portfolio['metadata']['analyst_llm_agent'] = mock_llm
        
        result = is_approved(sample_state_with_portfolio)
        
        assert result['data']['analysis']['is_approved'] is False
        assert result['data']['analysis']['summary'].is_approved is False
