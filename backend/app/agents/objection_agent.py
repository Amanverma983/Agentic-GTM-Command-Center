import time
from pydantic import BaseModel, Field
from typing import Dict, Any
from app.agents.state import AgentState
from app.utils.gemini_client import call_gemini
from app.db import add_agent_log, update_lead_agent_data

class ObjectionHandlingOutput(BaseModel):
    too_expensive_response: str = Field(description="Professional rebuttal when prospect objects that the product is 'too expensive'")
    no_budget_response: str = Field(description="Professional rebuttal when prospect claims they have 'no budget'")
    competitor_response: str = Field(description="Professional rebuttal when prospect states they 'already use a competitor'")
    not_interested_response: str = Field(description="Professional rebuttal when prospect says they are 'not interested'")
    need_time_response: str = Field(description="Professional rebuttal when prospect says they 'need more time/later'")

def objection_agent_node(state: AgentState) -> AgentState:
    """
    LangGraph node representing the Objection Handling Agent.
    """
    start_time = time.time()
    lead_id = state["lead_id"]
    company_name = state["company_name"]
    product_sold = state["product_sold"]
    research_data = state["research"]
    
    print(f"[Objection Agent] Formulating objection handling script for {company_name}...")
    add_agent_log(lead_id, "Objection Agent", "RUNNING", log_message=f"Generating tailored sales rebuttals for {company_name}.")
    
    system_instruction = (
        "You are a Master Sales Trainer and Negotiations Consultant. Your task is to provide professional, "
        "empathetic, and highly persuasive rebuttals to common sales objections. Frame the answers specifically "
        "for the product being sold and the target company's challenges. Avoid aggressive selling; use consultative reframing."
    )
    
    prompt = f"""
    Our Product: '{product_sold}'
    Target Company: '{company_name}'
    Company Pain Points: {', '.join(research_data.get('pain_points', []))}
    
    Generate tailored sales rebuttals for these 5 common objections:
    1. 'Too expensive'
    2. 'No budget'
    3. 'Already using a competitor'
    4. 'Not interested'
    5. 'Need more time'
    """
    
    mock_data = {
        "too_expensive_response": f"I appreciate you sharing that. '{product_sold}' is priced to reflect the immediate operational efficiency it brings. Our average customer sees a full return on investment within 3 months by reducing administrative error costs. I'd be glad to walk through an ROI model customized for {company_name} to see if it makes financial sense.",
        "no_budget_response": f"Understood—budget cycles are tough. Many of our clients start with a small pilot team to prove the value first. If we can show concrete savings of 20 hours per week for your operations team, would you be open to exploring how we can position this for your next budget cycle?",
        "competitor_response": f"It's great that you already have a solution in place; that means you recognize the value of automating this pipeline. What our customers usually find is that '{product_sold}' integrates more deeply with legacy databases and has a 2x faster execution speed. Would you be open to a quick comparison checklist?",
        "not_interested_response": f"That's completely fine. Timing is everything. Given that {company_name} is focusing on growth, I'd love to just send you our 2-page brief on how we help peers in your industry scale operational bandwidth. May I drop that over email for you to review at your convenience?",
        "need_time_response": f"No problem at all. Moving too fast leads to execution gaps. How about I check back in with you in about 3 weeks? In the meantime, I'll send over a short video showing how the database integration works so you have it handy."
    }
    
    try:
        result = call_gemini(
            prompt=prompt,
            system_instruction=system_instruction,
            response_schema=ObjectionHandlingOutput,
            mock_fallback_data=mock_data
        )
        
        # Save output in SQLite
        update_lead_agent_data(lead_id, "objection_data", result)
        
        # Log success
        execution_time = int((time.time() - start_time) * 1000)
        add_agent_log(
            lead_id=lead_id,
            agent_name="Objection Agent",
            status="SUCCESS",
            confidence_score=0.88,
            execution_time_ms=execution_time,
            log_message=f"Objection handling templates drafted for {company_name}."
        )
        
        # Update State
        state["objection_responses"] = result
        state["current_node"] = "objection"
        return state
        
    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        add_agent_log(
            lead_id=lead_id,
            agent_name="Objection Agent",
            status="FAILED",
            execution_time_ms=execution_time,
            log_message=f"Error running Objection Agent: {str(e)}"
        )
        state["error"] = str(e)
        state["status"] = "FAILED"
        return state
