import time
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from app.agents.state import AgentState
from app.utils.gemini_client import call_gemini
from app.db import add_agent_log, update_lead_agent_data

class PersonaDetail(BaseModel):
    title: str = Field(description="Job title, e.g. CEO, CTO, Operations Head, Marketing Head")
    goals: List[str] = Field(description="Key business or operational goals for this role")
    challenges: List[str] = Field(description="Primary frustrations and bottlenecks in their day-to-day work")
    motivations: List[str] = Field(description="What drives this persona's career or business incentives")
    decision_factors: List[str] = Field(description="Core criteria they use to evaluate software or service vendors")

class PersonaOutput(BaseModel):
    personas: List[PersonaDetail] = Field(description="List of structured buyer personas")

def persona_agent_node(state: AgentState) -> AgentState:
    """
    LangGraph node representing the Persona Agent.
    """
    start_time = time.time()
    lead_id = state["lead_id"]
    company_name = state["company_name"]
    product_sold = state["product_sold"]
    research_data = state["research"]
    
    print(f"[Persona Agent] Creating buyer personas for {company_name}...")
    add_agent_log(lead_id, "Persona Agent", "RUNNING", log_message=f"Creating tailored buyer personas for decision makers at {company_name}.")
    
    system_instruction = (
        "You are an expert Corporate User Persona Designer and Sales Strategist. Your task is to generate "
        "ideal buyer personas (specifically for the CEO, CTO, Operations Head, and Marketing Head) "
        "at the target company. Tailor their goals and challenges to match how they would view our product."
    )
    
    prompt = f"""
    Target Company: '{company_name}'
    Our Product: '{product_sold}'
    
    Company Research Data:
    - Industry: {research_data.get('industry', 'Technology')}
    - Business Model: {research_data.get('business_model', 'B2B SaaS')}
    - Pain Points: {', '.join(research_data.get('pain_points', []))}
    - Strategic Insights: {', '.join(research_data.get('strategic_insights', []))}
    
    Generate detailed buyer personas (CEO, CTO, Operations Head, Marketing Head).
    Make them highly specific to how this company operates and what these decision makers care about.
    """
    
    mock_data = {
        "personas": [
            {
                "title": "CEO (Chief Executive Officer)",
                "goals": ["Drive enterprise revenue growth", "Maximize shareholder value", "Expand market share"],
                "challenges": ["Aligning diverse departments under unified systems", "Managing rising operational costs", "Navigating macro-economic slowdowns"],
                "motivations": ["Strategic innovation", "Industry leadership", "Long-term scalability"],
                "decision_factors": ["Total ROI and business impact", "Time-to-value", "Vendor stability and track record"]
            },
            {
                "title": "CTO (Chief Technology Officer)",
                "goals": ["Maintain robust security and compliance", "Ensure system uptime and scalability", "Drive technical innovation"],
                "challenges": ["Integration backlog and legacy technology debt", "Shortage of specialized engineering talent", "Ensuring data privacy"],
                "motivations": ["Clean system architecture", "Minimal developer friction", "Future-proof engineering tools"],
                "decision_factors": ["API flexibility and integration ease", "Security standards (SOC 2, ISO)", "Developer documentation quality"]
            },
            {
                "title": "Operations Head",
                "goals": ["Streamline departmental workflows", "Reduce manual operational errors", "Optimize resource utilization"],
                "challenges": ["Repetitive administrative tasks slowing down key talent", "High turnaround times on critical reports", "Inconsistent standard operating procedures"],
                "motivations": ["Team productivity", "Process automation", "Operational transparency"],
                "decision_factors": ["Ease of use for non-technical users", "Workflow customization capability", "Customer support availability"]
            },
            {
                "title": "Marketing Head",
                "goals": ["Increase pipeline and sales-qualified leads", "Enhance brand engagement", "Optimize customer acquisition costs (CAC)"],
                "challenges": ["Fragmented tracking across marketing campaigns", "Personalizing outreach at scale", "Measuring exact ROI of ad campaigns"],
                "motivations": ["High conversions", "Creativity and innovation", "Data-driven experimentation"],
                "decision_factors": ["Analytics and reporting capabilities", "Integrations with existing marketing tools", "A/B testing features"]
            }
        ]
    }
    
    try:
        result = call_gemini(
            prompt=prompt,
            system_instruction=system_instruction,
            response_schema=PersonaOutput,
            mock_fallback_data=mock_data
        )
        
        # Save output in SQLite
        update_lead_agent_data(lead_id, "persona_data", result["personas"])
        
        # Log success
        execution_time = int((time.time() - start_time) * 1000)
        add_agent_log(
            lead_id=lead_id,
            agent_name="Persona Agent",
            status="SUCCESS",
            confidence_score=0.90,
            execution_time_ms=execution_time,
            log_message=f"Successfully generated {len(result['personas'])} buyer personas for {company_name}."
        )
        
        # Update State
        state["personas"] = result["personas"]
        state["current_node"] = "personas"
        return state
        
    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        add_agent_log(
            lead_id=lead_id,
            agent_name="Persona Agent",
            status="FAILED",
            execution_time_ms=execution_time,
            log_message=f"Error running Persona Agent: {str(e)}"
        )
        state["error"] = str(e)
        state["status"] = "FAILED"
        return state
