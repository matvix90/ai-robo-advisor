from langgraph.graph import StateGraph, END

from src.graph.state import State
from src.data.models import AnalysisResponse
from . import alignment, diversification, fees, performance

def start(state: State) -> State:
    """Initial state function."""
    print("Starting analysis workflow...\n")
    return state

def is_approved(state:State) -> State:
    llm = state["metadata"]["analyst_llm_agent"]

    response = state["data"]["analysis"]
    confidence = 0
    if response["expense_ratio"].status.value:
        confidence += 1
    if response["diversification"].status.value:
        confidence += 1
    if response["alignment"].status.value:
        confidence += 1
    if response["performance"].status.value:
        confidence += 1

    if confidence >= 2:
        state["data"]["analysis"]["is_approved"] = True
    else:
        state["data"]["analysis"]["is_approved"] = False
    
    # Collect all existing advice from individual analyses
    all_advices = []
    if response["expense_ratio"].advices:
        all_advices.extend(response["expense_ratio"].advices)
    if response["diversification"].advices:
        all_advices.extend(response["diversification"].advices)
    if response["alignment"].advices:
        all_advices.extend(response["alignment"].advices)
    if response["performance"].advices:
        all_advices.extend(response["performance"].advices)
    
    advice_summary = "\n".join([f"- {advice}" for advice in all_advices]) if all_advices else "No specific advice provided from individual analyses."
    
    prompt = f"""
    You are a senior financial portfolio analyst with expertise in comprehensive investment assessment and portfolio evaluation.

    Based on the detailed analysis conducted across four critical dimensions, provide a comprehensive portfolio assessment:

    ANALYSIS RESULTS:
    - Expense Ratio Analysis: {"PASSED" if response["expense_ratio"].status.value else "FAILED"}
      Reasoning: {response["expense_ratio"].reasoning}
    
    - Diversification Analysis: {"PASSED" if response["diversification"].status.value else "FAILED"}
      Reasoning: {response["diversification"].reasoning}
    
    - Alignment Analysis: {"PASSED" if response["alignment"].status.value else "FAILED"}
      Reasoning: {response["alignment"].reasoning}
    
    - Performance Analysis: {"PASSED" if response["performance"].status.value else "FAILED"}
      Reasoning: {response["performance"].reasoning}

    EXISTING SPECIFIC ADVICE FROM INDIVIDUAL ANALYSES:
    {advice_summary}

    OVERALL CONFIDENCE SCORE: {confidence}/4 criteria met
    APPROVAL STATUS: {"APPROVED" if confidence >= 2 else "REJECTED"}

    Please provide a comprehensive analysis summary including:

    1. STRENGTHS: Identify and elaborate on the portfolio's strongest aspects based on the passing criteria
    2. WEAKNESSES: Highlight areas of concern or failure, explaining their potential impact  
    3. OVERALL ASSESSMENT: Provide a balanced evaluation considering all four dimensions
    4. ACTIONABLE ADVICE: Consolidate and prioritize the existing specific advice, add any additional strategic recommendations, and present them in order of importance for portfolio optimization

    Maintain a professional, objective tone while being specific about risks and opportunities. Focus on actionable insights that can guide investment decisions.
    """
    
    analysis_response = llm.with_structured_output(AnalysisResponse).invoke(prompt)
    analysis_response.is_approved = state["data"]["analysis"]["is_approved"]
    state["data"]["analysis"]["summary"] = analysis_response

    return state


def create_analyst_graph():
    """
    Creates and compiles the graph for portfolio analysis.
    """
    workflow = StateGraph(State)

    # Add nodes
    workflow.add_node("start", start)
    workflow.add_node("expense_ratio", fees.analyze_ter)
    workflow.add_node("diversification", diversification.analyze_diversification)
    workflow.add_node("alignment", alignment.analyze_alignment)
    workflow.add_node("performance", performance.analyze_performance)
    workflow.add_node("analyst", is_approved)
    
    # Set entry point
    workflow.set_entry_point("start")

    # Add edges
    workflow.add_edge("start", "expense_ratio")
    workflow.add_edge("start", "diversification")
    workflow.add_edge("start", "alignment")
    workflow.add_edge("start", "performance")
    workflow.add_edge("expense_ratio", "analyst")
    workflow.add_edge("diversification", "analyst")
    workflow.add_edge("alignment", "analyst")
    workflow.add_edge("performance", "analyst")
    workflow.add_edge("analyst", END)

    # Compile the graph
    app = workflow.compile()
    return app
