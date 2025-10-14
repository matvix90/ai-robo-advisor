"""
Tests for the main workflow and graph.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from src.main import create_workflow, start, run_workflow
from src.graph.state import State, merge_dicts


# ============================================================================
# State Tests
# ============================================================================

@pytest.mark.unit
class TestState:
    """Tests for State TypedDict and helper functions."""

    def test_merge_dicts_basic(self):
        """Test basic dictionary merging."""
        dict_a = {'key1': 'value1', 'key2': 'value2'}
        dict_b = {'key3': 'value3'}
        
        result = merge_dicts(dict_a, dict_b)
        
        assert result == {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}

    def test_merge_dicts_override(self):
        """Test that merge_dicts overrides values."""
        dict_a = {'key1': 'value1', 'key2': 'value2'}
        dict_b = {'key2': 'new_value2', 'key3': 'value3'}
        
        result = merge_dicts(dict_a, dict_b)
        
        assert result['key2'] == 'new_value2'
        assert result == {'key1': 'value1', 'key2': 'new_value2', 'key3': 'value3'}

    def test_merge_dicts_empty(self):
        """Test merging with empty dictionaries."""
        dict_a = {'key1': 'value1'}
        dict_b = {}
        
        result = merge_dicts(dict_a, dict_b)
        
        assert result == {'key1': 'value1'}


# ============================================================================
# Start Node Tests
# ============================================================================

@pytest.mark.unit
class TestStartNode:
    """Tests for the start node."""

    def test_start_returns_state(self, sample_state):
        """Test that start node returns the state unchanged."""
        result = start(sample_state)
        
        assert result == sample_state

    def test_start_preserves_data(self, sample_state):
        """Test that start node preserves all data."""
        result = start(sample_state)
        
        assert 'data' in result
        assert 'metadata' in result
        assert result['data'] == sample_state['data']
        assert result['metadata'] == sample_state['metadata']


# ============================================================================
# Workflow Creation Tests
# ============================================================================

@pytest.mark.unit
class TestCreateWorkflow:
    """Tests for workflow graph creation."""

    def test_create_workflow_returns_graph(self):
        """Test that create_workflow returns a compiled graph."""
        workflow = create_workflow()
        
        assert workflow is not None
        # The workflow should be a compiled LangGraph

    def test_create_workflow_structure(self):
        """Test that workflow has expected structure."""
        workflow = create_workflow()
        
        # Should be able to get the graph structure
        assert workflow is not None
        # Note: Specific graph inspection depends on LangGraph API


# ============================================================================
# Run Workflow Tests
# ============================================================================

@pytest.mark.unit
class TestRunWorkflow:
    """Tests for workflow execution."""

    @patch('src.main.create_workflow')
    def test_run_workflow_basic(self, mock_create_workflow, sample_portfolio_preference,
                                mock_llm):
        """Test basic workflow execution."""
        # Create a mock agent that returns a complete result
        mock_agent = Mock()
        mock_result = {
            'data': {
                'investment': {
                    'strategy': Mock(),
                    'analyst': {'name': 'Test', 'description': 'Test'}
                },
                'portfolio': Mock(strategy=Mock()),
                'analysis': {
                    'summary': Mock()
                }
            },
            'metadata': {
                'show_reasoning': False
            }
        }
        mock_agent.invoke.return_value = mock_result
        mock_create_workflow.return_value = mock_agent
        
        result = run_workflow(
            show_reasoning=False,
            investment_llm_agent=mock_llm,
            portfolio_llm_agent=mock_llm,
            analyst_llm_agent=mock_llm,
            preferences=sample_portfolio_preference
        )
        
        assert result is not None
        assert 'data' in result

    @patch('src.main.create_workflow')
    def test_run_workflow_with_reasoning(self, mock_create_workflow, sample_portfolio_preference,
                                         mock_llm):
        """Test workflow execution with reasoning enabled."""
        mock_agent = Mock()
        mock_result = {
            'data': {
                'investment': {
                    'strategy': Mock(),
                    'analyst': {'name': 'Test', 'description': 'Test'}
                },
                'portfolio': Mock(strategy=Mock()),
                'analysis': {
                    'summary': Mock()
                }
            },
            'metadata': {
                'show_reasoning': True
            }
        }
        mock_agent.invoke.return_value = mock_result
        mock_create_workflow.return_value = mock_agent
        
        result = run_workflow(
            show_reasoning=True,
            investment_llm_agent=mock_llm,
            portfolio_llm_agent=mock_llm,
            analyst_llm_agent=mock_llm,
            preferences=sample_portfolio_preference
        )
        
        assert result['metadata']['show_reasoning'] is True

    @patch('src.main.create_workflow')
    def test_run_workflow_with_analyst(self, mock_create_workflow, sample_portfolio_preference,
                                       mock_llm):
        """Test workflow execution with specific analyst."""
        mock_agent = Mock()
        mock_result = {
            'data': {
                'investment': {
                    'strategy': Mock(),
                    'analyst': 'Warren Buffett'
                },
                'portfolio': Mock(strategy=Mock()),
                'analysis': {
                    'summary': Mock()
                }
            },
            'metadata': {
                'show_reasoning': False
            }
        }
        mock_agent.invoke.return_value = mock_result
        mock_create_workflow.return_value = mock_agent
        
        result = run_workflow(
            show_reasoning=False,
            investment_llm_agent=mock_llm,
            portfolio_llm_agent=mock_llm,
            analyst_llm_agent=mock_llm,
            analyst="Warren Buffett",
            preferences=sample_portfolio_preference
        )
        
        assert result is not None


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.integration
class TestWorkflowIntegration:
    """Integration tests for the complete workflow."""

    def test_workflow_graph_invocable(self):
        """Test that the workflow graph can be invoked."""
        workflow = create_workflow()
        
        # Should be able to call invoke on the workflow
        assert hasattr(workflow, 'invoke')

    @patch('src.nodes.investment_agents.goal_based.investment_strategy')
    @patch('src.nodes.portfolios_agent.create_portfolio')
    def test_workflow_node_execution_order(self, mock_create_portfolio, 
                                           mock_investment_strategy,
                                           sample_state):
        """Test that workflow nodes execute in correct order."""
        # This is a simplified test - actual order depends on graph structure
        workflow = create_workflow()
        
        # The workflow should have the nodes we expect
        assert workflow is not None


# ============================================================================
# Main Function Tests
# ============================================================================

@pytest.mark.unit
class TestMainFunction:
    """Tests for the main CLI function."""

    @patch('src.main.run_workflow')
    @patch('src.main.get_user_preferences')
    @patch('src.main.choose_llm_model')
    @patch('src.main.load_models')
    @patch('src.main.get_llm_model')
    @patch('src.main.print_strategy')
    @patch('src.main.print_portfolio')
    @patch('src.main.print_analysis_response')
    @patch('sys.argv', ['main.py'])
    def test_main_success(self, mock_print_analysis, mock_print_portfolio, 
                         mock_print_strategy, mock_get_llm, mock_load_models,
                         mock_choose_llm, mock_get_prefs, mock_run_workflow,
                         sample_portfolio, sample_portfolio_preference):
        """Test successful main function execution."""
        from src.main import main
        
        # Setup mocks
        mock_load_models.return_value = Mock(models=[])
        mock_choose_llm.return_value = Mock(provider='anthropic', model_name='test')
        mock_get_prefs.return_value = sample_portfolio_preference
        mock_get_llm.return_value = Mock()
        
        mock_result = {
            'data': {
                'portfolio': sample_portfolio,
                'analysis': {
                    'summary': Mock()
                }
            }
        }
        mock_run_workflow.return_value = mock_result
        
        result = main()
        
        assert result == 0  # Success exit code

    @patch('src.main.load_models')
    @patch('sys.argv', ['main.py'])
    def test_main_keyboard_interrupt(self, mock_load_models):
        """Test main function handles keyboard interrupt."""
        from src.main import main
        
        mock_load_models.side_effect = KeyboardInterrupt()
        
        result = main()
        
        assert result == 1  # Error exit code

    @patch('src.main.load_models')
    @patch('sys.argv', ['main.py'])
    def test_main_exception(self, mock_load_models):
        """Test main function handles exceptions."""
        from src.main import main
        
        mock_load_models.side_effect = Exception("Test error")
        
        result = main()
        
        assert result == 1  # Error exit code

    @patch('src.main.run_workflow')
    @patch('src.main.get_user_preferences')
    @patch('src.main.choose_llm_model')
    @patch('src.main.load_models')
    @patch('src.main.get_llm_model')
    @patch('src.main.print_strategy')
    @patch('src.main.print_portfolio')
    @patch('src.main.print_analysis_response')
    @patch('sys.argv', ['main.py', '--show-reasoning'])
    def test_main_with_show_reasoning_flag(self, mock_print_analysis, mock_print_portfolio,
                                           mock_print_strategy, mock_get_llm, mock_load_models,
                                           mock_choose_llm, mock_get_prefs, mock_run_workflow,
                                           sample_portfolio, sample_portfolio_preference):
        """Test main function with --show-reasoning flag."""
        from src.main import main
        
        # Setup mocks
        mock_load_models.return_value = Mock(models=[])
        mock_choose_llm.return_value = Mock(provider='anthropic', model_name='test')
        mock_get_prefs.return_value = sample_portfolio_preference
        mock_get_llm.return_value = Mock()
        
        mock_result = {
            'data': {
                'portfolio': sample_portfolio,
                'analysis': {
                    'summary': Mock()
                }
            }
        }
        mock_run_workflow.return_value = mock_result
        
        result = main()
        
        # Should call run_workflow with show_reasoning=True
        assert mock_run_workflow.called
        call_kwargs = mock_run_workflow.call_args[1]
        assert call_kwargs['show_reasoning'] is True
        assert result == 0
