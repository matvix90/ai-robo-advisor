import sys
import argparse

from langgraph.graph import StateGraph, START, END

from src.nodes.investment_agents.goal_based import investment_strategy
from src.nodes.portfolios_agent import create_portfolio
from src.nodes.analyst_agents.analysis_workflow import create_analyst_graph

from src.graph.state import State
from utils.display import print_strategy, print_portfolio, print_analysis_response
from utils.questionnaires import choose_llm_model, get_user_preferences
from data.models import PortfolioPreference

from llm.models import load_models, get_llm_model


# === Workflow Execution ===
def run_workflow(
        show_reasoning:bool, 
        investment_llm_agent, 
        portfolio_llm_agent,
        analyst_llm_agent,
        analyst:str=None,
        preferences:PortfolioPreference=None
    ):
    
    agent = create_workflow()

    result = agent.invoke(
        {
            'data':{
                'investment': {
                    'analyst': analyst,
                    'user_preferences': preferences
                },
                'benchmark': preferences.benchmark
            },
            'metadata': 
            {'show_reasoning': show_reasoning,
             'investment_llm_agent': investment_llm_agent,
             'portfolio_llm_agent': portfolio_llm_agent,
             'analyst_llm_agent': analyst_llm_agent
            }
        }
    )

    return result


# === Start Node ===
def start(state: State) -> State:
    """Initial state function."""
    return state


# === Graph ===
def create_workflow():
    graph_builder = StateGraph(State)

    graph_builder.add_node("start", start)
    graph_builder.add_node("goal_based_strategy", investment_strategy)
    graph_builder.add_node("create_portfolio", create_portfolio)
    graph_builder.add_node("run_analysis", create_analyst_graph())

    graph_builder.add_edge(START, "start")
    graph_builder.add_edge("start", "goal_based_strategy")
    graph_builder.add_edge("goal_based_strategy", "create_portfolio")
    graph_builder.add_edge("create_portfolio", "run_analysis")
    graph_builder.add_edge("run_analysis", END)

    agent = graph_builder.compile()

    return agent

def main():
    """Entry point for the ai-robo-advisor CLI application."""
    try:
        parser = argparse.ArgumentParser(description="Run the AI Robo Advisor workflow.")
        parser.add_argument("--show-reasoning", action="store_true", help="Show reasoning from each agent")
        args = parser.parse_args()

        print("\n🤖 Welcome to AI Robo Advisor")
        print("=" * 50)

        # Load available LLM models
        all_models = load_models()

        # Choose LLM model for each agent
        investment_model = choose_llm_model(all_models, agent="investment_agent")
        portfolio_model = choose_llm_model(all_models, agent="portfolio_agent")
        analyst_model = choose_llm_model(all_models, agent="analyst_agent")
        
        investment_llm_agent = get_llm_model(investment_model.provider, investment_model.model_name)
        portfolio_llm_agent = get_llm_model(portfolio_model.provider, portfolio_model.model_name)
        analyst_llm_agent = get_llm_model(analyst_model.provider, analyst_model.model_name)

        # Choose User Preferences
        preferences = get_user_preferences()

        # Run the workflow
        result = run_workflow( 
            show_reasoning=args.show_reasoning,
            investment_llm_agent=investment_llm_agent,
            portfolio_llm_agent=portfolio_llm_agent,
            analyst_llm_agent=analyst_llm_agent,  # Fixed: was portfolio_llm_agent
            preferences=preferences
        )

        # Display results
        portfolio = result['data']['portfolio']
        analysis = result['data']['analysis']['summary']
        
        print_strategy(portfolio.strategy)
        print_portfolio(portfolio)
        print_analysis_response(analysis)

        return 0  # Success

    except KeyboardInterrupt:
        print("\n\n❌ Application interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())