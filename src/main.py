import sys
import argparse

from langgraph.graph import StateGraph, START, END

from nodes.investment_agents.goal_based import investment_strategy
from nodes.portfolios_agent import create_portfolio
from nodes.analyst_agents.analysis_workflow import create_analyst_graph

from graph.state import State
from utils.display import print_strategy, print_portfolio, print_analysis_response
from utils.questionnaires import choose_llm_model, get_user_preferences

from llm.models import load_models, get_llm_model


# === Workflow Execution ===
def run_workflow(
        show_reasoning:bool, 
        investment_llm_agent, 
        portfolio_llm_agent,
        analyst_llm_agent,
        analyst:str=None,
        preferences:str=None
    ):
    
    agent = create_workflow()

    result = agent.invoke(
        {
            'data':{
                'investment': {
                    'analyst': analyst,
                    'user_preferences': preferences
                },
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
    
    # === Feedback Node ===
    def prepare_portfolio_feedback(state: State) -> State:
        """
        Prepare actionable feedback for the portfolio creation step using
        the results of the analyst workflow.

        - Collects consolidated advice from the analysis summary and individual
          analysis nodes (fees, diversification, alignment, performance).
        - Stores a concise feedback string in `state['data']['analysis']['portfolio_feedback']`
          to guide the next portfolio revision.

        Returns the updated state.
        """
        analysis = state.get("data", {}).get("analysis", {})

        # Start with the consolidated summary advice if present
        consolidated = analysis.get("summary").advices if analysis.get("summary") else None

        # Collect any per-dimension advices (lists)
        per_dimension_advices = []
        for key in ("expense_ratio", "diversification", "alignment", "performance"):
            item = analysis.get(key)
            if item and getattr(item, "advices", None):
                per_dimension_advices.extend(item.advices)

        # Build a final feedback text
        lines = []
        if per_dimension_advices:
            lines.append("Specific improvements from analysis:")
            lines.extend([f"- {advice}" for advice in per_dimension_advices])
        if consolidated:
            # The consolidated summary may already include a joined string
            if lines:
                lines.append("")
            lines.append("Consolidated analyst recommendations:")
            lines.append(str(consolidated))

        feedback_text = "\n".join(lines) if lines else ""

        # Store feedback to be consumed by the portfolio creator
        state.setdefault("data", {}).setdefault("analysis", {})["portfolio_feedback"] = feedback_text

        # Track iteration count for safety
        retries = state.get("data", {}).get("retries", 0)
        state["data"]["retries"] = retries

        return state

    graph_builder.add_node("prepare_feedback", prepare_portfolio_feedback)
    graph_builder.add_node("run_analysis", create_analyst_graph())

    graph_builder.add_edge(START, "start")
    graph_builder.add_edge("start", "goal_based_strategy")
    graph_builder.add_edge("goal_based_strategy", "create_portfolio")
    graph_builder.add_edge("create_portfolio", "run_analysis")

    # === Conditional ===
    def check_analysis(state: State):
        """
        Decide next step based on approval status and retry budget.

        - If analysis is not approved and retries remain, route to `prepare_feedback`
          so we can inform the next portfolio revision with concrete advice.
        - Otherwise, end the workflow.
        """
        retries = state.get("data", {}).get("retries", 0)
        is_approved = state.get("data", {}).get("analysis", {}).get("is_approved", False)

        if not is_approved:
            # Allow up to 2 revision cycles to avoid potential infinite loops
            if retries < 2:
                state.setdefault("data", {})["retries"] = retries + 1
                return "prepare_feedback"
            return "end"
        return "end"

    graph_builder.add_conditional_edges(
        "run_analysis",
        check_analysis,
        {"prepare_feedback": "prepare_feedback", "end": END},
    )

    # After preparing feedback, try creating the portfolio again
    graph_builder.add_edge("prepare_feedback", "create_portfolio")

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
