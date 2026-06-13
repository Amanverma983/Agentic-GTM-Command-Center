import time
from pydantic import BaseModel, Field
from typing import Dict, Any
from app.agents.state import AgentState
from app.utils.gemini_client import call_gemini
from app.db import add_agent_log, update_lead_agent_data

class CRMRecordOutput(BaseModel):
    lead_name: str = Field(description="Primary contact name mapped (typically e.g. Head of Operations or CTO, generated name)")
    company: str = Field(description="Company name")
    industry: str = Field(description="Industry sector")
    lead_score: int = Field(description="Qualification score as an integer (0-100)")
    deal_stage: str = Field(description="Proposed deal stage, e.g. 'Discovery', 'Qualified Prospecting', 'Nurturing'")
    priority: str = Field(description="Priority level: 'High', 'Medium', or 'Low'")
    notes: str = Field(description="Concise summary notes for a CRM log entry (max 3 sentences)")

def crm_agent_node(state: AgentState) -> AgentState:
    """
    LangGraph node representing the CRM Agent.
    """
    start_time = time.time()
    lead_id = state["lead_id"]
    company_name = state["company_name"]
    research_data = state["research"]
    qualification_data = state["qualification"]
    
    print(f"[CRM Agent] Formatting CRM record data for {company_name}...")
    add_agent_log(lead_id, "CRM Agent", "RUNNING", log_message=f"Structuring GTM logs into CRM JSON fields.")
    
    system_instruction = (
        "You are an expert Sales Operations Specialist and Database Administrator. Your task is to extract "
        "and format structured data into JSON fields that can be uploaded directly into CRM tools like Salesforce or HubSpot."
    )
    
    # Calculate a sensible priority and deal stage based on qualifications
    score = qualification_data.get("qualification_score", 50)
    icp = qualification_data.get("icp_fit", "Medium")
    
    prompt = f"""
    Format a CRM record for:
    - Company Name: {company_name}
    - Product: {state['product_sold']}
    - Industry: {research_data.get('industry', 'Technology')}
    - Lead Score: {score}
    - ICP Fit: {icp}
    - Key Challenge: {research_data.get('pain_points', ['Generic scalability'])[0]}
    
    Create a professional CRM record. Synthesize a reasonable contact name (e.g. 'Alex Rivera, Head of Operations') 
    based on the company structure.
    """
    
    # Setup fallback data
    priority = "High" if score >= 75 else "Medium" if score >= 50 else "Low"
    deal_stage = "Qualified Prospecting" if score >= 70 else "Discovery"
    
    mock_data = {
        "lead_name": "Sarah Jenkins, VP of Operations",
        "company": company_name,
        "industry": research_data.get("industry", "Information Technology"),
        "lead_score": int(score),
        "deal_stage": deal_stage,
        "priority": priority,
        "notes": f"Lead qualified based on clear operational pain points. Highly receptive to automation of workflows. Follow up with the customized '{state['product_sold']}' pitch."
    }
    
    try:
        result = call_gemini(
            prompt=prompt,
            system_instruction=system_instruction,
            response_schema=CRMRecordOutput,
            mock_fallback_data=mock_data
        )
        
        # Save output in SQLite
        update_lead_agent_data(lead_id, "crm_data", result)
        
        # Log success
        execution_time = int((time.time() - start_time) * 1000)
        add_agent_log(
            lead_id=lead_id,
            agent_name="CRM Agent",
            status="SUCCESS",
            confidence_score=1.0,
            execution_time_ms=execution_time,
            log_message=f"Formatted CRM schema for {company_name} successfully."
        )
        
        # Update State
        state["crm_record"] = result
        state["current_node"] = "crm"
        return state
        
    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        add_agent_log(
            lead_id=lead_id,
            agent_name="CRM Agent",
            status="FAILED",
            execution_time_ms=execution_time,
            log_message=f"Error running CRM Agent: {str(e)}"
        )
        state["error"] = str(e)
        state["status"] = "FAILED"
        return state
