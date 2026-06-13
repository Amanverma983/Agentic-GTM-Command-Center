from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.research_agent import research_agent_node
from app.agents.qualification_agent import qualification_agent_node
from app.agents.persona_agent import persona_agent_node
from app.agents.outreach_agent import outreach_agent_node
from app.agents.objection_agent import objection_agent_node
from app.agents.crm_agent import crm_agent_node
from app.agents.forecast_agent import forecast_agent_node
from app.agents.manager_agent import manager_agent_node

def build_workflow_graph():
    """
    Creates and compiles the LangGraph StateGraph workflow for GTM command center.
    """
    workflow = StateGraph(AgentState)
    
    # Register agent nodes
    workflow.add_node("research_node", research_agent_node)
    workflow.add_node("qualification_node", qualification_agent_node)
    workflow.add_node("personas_node", persona_agent_node)
    workflow.add_node("outreach_node", outreach_agent_node)
    workflow.add_node("objections_node", objection_agent_node)
    workflow.add_node("crm_node", crm_agent_node)
    workflow.add_node("forecast_node", forecast_agent_node)
    workflow.add_node("manager_node", manager_agent_node)
    
    # Establish linear workflow edges
    workflow.set_entry_point("research_node")
    
    workflow.add_edge("research_node", "qualification_node")
    workflow.add_edge("qualification_node", "personas_node")
    workflow.add_edge("personas_node", "outreach_node")
    workflow.add_edge("outreach_node", "objections_node")
    workflow.add_edge("objections_node", "crm_node")
    workflow.add_edge("crm_node", "forecast_node")
    workflow.add_edge("forecast_node", "manager_node")
    
    workflow.add_edge("manager_node", END)
    
    return workflow.compile()

# Single precompiled graph instance
gtm_workflow = build_workflow_graph()
