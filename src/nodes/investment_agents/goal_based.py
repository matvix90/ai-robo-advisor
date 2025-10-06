from graph.state import State
from data.models import InvestmentAgent
from utils.investor_profile import create_investor_profile

# === Agents ===
def investment_strategy(state:State) -> State:
    """
    Collect user investment preferences through interactive questionnaire and 
    generate investment strategy based on user preferences.
    """
    print("Generating investment strategy based on user preferences...\n")
    
    llm = state["metadata"]["investment_llm_agent"]
    portfolio_preferences = state["data"]['investment']['user_preferences']
    
    # Use the utility function to create the investor profile prompt
    prompt = create_investor_profile(portfolio_preferences)
    
    analyst = {"name": "Self-Directed Investor", "description": "Investor who prefers to make their own investment decisions based on personal research and preferences."}
    response = llm.with_structured_output(InvestmentAgent).invoke(prompt)
    
    if state["metadata"]["show_reasoning"]:
        print(response.reasoning)
    
    state["data"]['investment']['strategy'] = response.strategy
    state["data"]['investment']['analyst'] = analyst
    
    return state
