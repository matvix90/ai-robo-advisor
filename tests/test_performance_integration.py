"""
Integration tests for performance analysis with error handling.
"""
import pytest
from unittest.mock import Mock, patch

from src.nodes.analyst_agents.performance import analyze_performance
from src.data.models import AnalysisAgent, Status


@pytest.mark.integration
class TestPerformanceAnalysisErrorHandling:
    """Integration tests for error handling in analyze_performance."""

    @patch('src.nodes.analyst_agents.performance.all_data')
    def test_critical_data_fetch_failure(self, mock_all_data, sample_portfolio):
        """Test handling of critical data fetch failures."""
        mock_all_data.side_effect = ValueError("Failed to fetch data for benchmark ticker: ACWI")
        
        mock_llm = Mock()
        state = {
            'metadata': {
                'analyst_llm_agent': mock_llm,
                'show_reasoning': False
            },
            'data': {
                'portfolio': sample_portfolio,
                'benchmark': ('ACWI', 'MSCI All Country World Index')
            }
        }
        
        result_state = analyze_performance(state)
        
        # Should have analysis with error status
        assert 'analysis' in result_state['data']
        assert 'performance' in result_state['data']['analysis']
        analysis = result_state['data']['analysis']['performance']
        
        assert isinstance(analysis, AnalysisAgent)
        assert analysis.status.key == 'is_performing'
        assert analysis.status.value is False
        assert 'data availability' in analysis.reasoning.lower()
        assert len(analysis.advices) > 0

    @patch('src.nodes.analyst_agents.performance.analyze_portfolio')
    @patch('src.nodes.analyst_agents.performance.all_data')
    def test_data_quality_warning_passed_to_llm(self, mock_all_data, mock_analyze, sample_portfolio):
        """Test that data quality warnings are passed to LLM context."""
        from src.utils.analysis_data import DataQualityWarning
        
        # Mock partial data with warning
        mock_all_data.return_value = (
            {'VTI': [{'date': '2023-01-01', 'close': 100}]},
            [{'date': '2023-01-01', 'close': 95}],
            {'VTI': 100.0},
            DataQualityWarning("Missing tickers: BND", ['BND'])
        )
        
        mock_analyze.return_value = (
            {
                'portfolio': {
                    'CAGR': 0.08,
                    'Annualized Volatility': 0.15,
                    'Sharpe Ratio': 0.5,
                    'Max Drawdown': -0.2,
                    'Alpha': 0.02,
                    'Beta': 1.0
                },
                'benchmark': {
                    'CAGR': 0.07,
                    'Annualized Volatility': 0.14,
                    'Sharpe Ratio': 0.48,
                    'Max Drawdown': -0.18
                },
                'tickers': {}
            },
            None
        )
        
        mock_llm = Mock()
        mock_llm.with_structured_output.return_value.invoke.return_value = AnalysisAgent(
            status=Status(key='is_performing', value=True),
            reasoning='Test reasoning',
            advices=[]
        )
        
        state = {
            'metadata': {
                'analyst_llm_agent': mock_llm,
                'show_reasoning': False
            },
            'data': {
                'portfolio': sample_portfolio,
                'benchmark': ('ACWI', 'MSCI All Country World Index')
            }
        }
        
        result_state = analyze_performance(state)
        
        # Verify LLM was called with warning in context
        call_args = mock_llm.with_structured_output.return_value.invoke.call_args
        prompt = call_args[0][0]
        assert 'WARNING' in prompt
        assert 'BND' in prompt or 'Missing' in prompt

    @patch('src.nodes.analyst_agents.performance.analyze_portfolio')
    @patch('src.nodes.analyst_agents.performance.all_data')
    def test_analysis_failure_after_data_fetch(self, mock_all_data, mock_analyze, sample_portfolio):
        """Test handling when analysis fails even with fetched data."""
        mock_all_data.return_value = (
            {'VTI': [{'date': '2023-01-01', 'close': 100}]},
            [{'date': '2023-01-01', 'close': 95}],
            {'VTI': 100.0},
            None
        )
        
        mock_analyze.side_effect = ValueError("No overlapping data found")
        
        mock_llm = Mock()
        state = {
            'metadata': {
                'analyst_llm_agent': mock_llm,
                'show_reasoning': False
            },
            'data': {
                'portfolio': sample_portfolio,
                'benchmark': ('ACWI', 'MSCI All Country World Index')
            }
        }
        
        result_state = analyze_performance(state)
        
        # Should have error analysis
        analysis = result_state['data']['analysis']['performance']
        assert analysis.status.key == 'is_performing'
        assert analysis.status.value is False
        assert 'data quality' in analysis.reasoning.lower()

    @patch('src.nodes.analyst_agents.performance.analyze_portfolio')
    @patch('src.nodes.analyst_agents.performance.all_data')
    def test_successful_analysis_with_warnings(self, mock_all_data, mock_analyze, sample_portfolio):
        """Test successful analysis with data quality warnings."""
        from src.utils.analysis_data import DataQualityWarning
        from src.utils.metrics import AnalysisWarning
        
        mock_all_data.return_value = (
            {'VTI': [{'date': '2023-01-01', 'close': 100}]},
            [{'date': '2023-01-01', 'close': 95}],
            {'VTI': 100.0},
            DataQualityWarning("Partial data", ['BND'])
        )
        
        mock_analyze.return_value = (
            {
                'portfolio': {
                    'CAGR': 0.08,
                    'Annualized Volatility': 0.15,
                    'Sharpe Ratio': 0.5,
                    'Max Drawdown': -0.2,
                    'Alpha': 0.02,
                    'Beta': 1.0
                },
                'benchmark': {
                    'CAGR': 0.07,
                    'Annualized Volatility': 0.14,
                    'Sharpe Ratio': 0.48,
                    'Max Drawdown': -0.18
                },
                'tickers': {}
            },
            AnalysisWarning("Some tickers skipped", ['BND'])
        )
        
        mock_llm = Mock()
        mock_llm.with_structured_output.return_value.invoke.return_value = AnalysisAgent(
            status=Status(key='is_performing', value=True),
            reasoning='Test reasoning',
            advices=[]
        )
        
        state = {
            'metadata': {
                'analyst_llm_agent': mock_llm,
                'show_reasoning': False
            },
            'data': {
                'portfolio': sample_portfolio,
                'benchmark': ('ACWI', 'MSCI All Country World Index')
            }
        }
        
        result_state = analyze_performance(state)
        
        # Should complete successfully with warnings passed to LLM
        assert 'performance' in result_state['data']['analysis']
        call_args = mock_llm.with_structured_output.return_value.invoke.call_args
        prompt = call_args[0][0]
        assert 'WARNING' in prompt

    @patch('src.nodes.analyst_agents.performance.analyze_portfolio')
    @patch('src.nodes.analyst_agents.performance.all_data')
    def test_default_benchmark_used_when_none(self, mock_all_data, mock_analyze, sample_portfolio):
        """Test that default benchmark is used when none provided."""
        mock_all_data.return_value = (
            {'VTI': [{'date': '2023-01-01', 'close': 100}]},
            [{'date': '2023-01-01', 'close': 95}],
            {'VTI': 100.0},
            None
        )
        
        mock_analyze.return_value = (
            {
                'portfolio': {
                    'CAGR': 0.08,
                    'Annualized Volatility': 0.15,
                    'Sharpe Ratio': 0.5,
                    'Max Drawdown': -0.2,
                    'Alpha': 0.02,
                    'Beta': 1.0
                },
                'benchmark': {
                    'CAGR': 0.07,
                    'Annualized Volatility': 0.14,
                    'Sharpe Ratio': 0.48,
                    'Max Drawdown': -0.18
                },
                'tickers': {}
            },
            None
        )
        
        mock_llm = Mock()
        mock_llm.with_structured_output.return_value.invoke.return_value = AnalysisAgent(
            status=Status(key='is_performing', value=True),
            reasoning='Test reasoning',
            advices=[]
        )
        
        state = {
            'metadata': {
                'analyst_llm_agent': mock_llm,
                'show_reasoning': False
            },
            'data': {
                'portfolio': sample_portfolio
                # No benchmark specified
            }
        }
        
        result_state = analyze_performance(state)
        
        # Should use default ACWI benchmark
        assert result_state['data']['benchmark'] is not None
        mock_all_data.assert_called_once()
        call_args = mock_all_data.call_args
        assert call_args[0][1] == 'ACWI'  # Second arg is benchmark_ticker
