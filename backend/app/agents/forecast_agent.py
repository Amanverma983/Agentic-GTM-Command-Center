import time
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from app.agents.state import AgentState
from app.utils.gemini_client import call_gemini
from app.db import add_agent_log, update_lead_agent_data

class ForecastOutput(BaseModel):
    close_probability: float = Field(description="Estimated deal close probability as a percentage (0 to 100)")
    estimated_revenue: float = Field(description="Estimated Contract Value (ACV) in USD")
    deal_risk: str = Field(description="Risk classification: 'Low', 'Medium', or 'High'")
    risk_factors: List[str] = Field(description="Primary reasons driving the deal risk evaluation")
    recommended_next_step: str = Field(description="Specific, immediate action the sales rep should take next")

def forecast_agent_node(state: AgentState) -> AgentState:
    """
    LangGraph node representing the Forecast Agent.
    """
    start_time = time.time()
    lead_id = state["lead_id"]
    company_name = state["company_name"]
    product_sold = state["product_sold"]
    research_data = state["research"]
    qualification_data = state["qualification"]
    crm_record = state["crm_record"]
    
    print(f"[Forecast Agent] Running revenue and close risk analysis for {company_name}...")
    add_agent_log(lead_id, "Forecast Agent", "RUNNING", log_message=f"Predicting deal probability and contract size for {company_name}.")
    
    system_instruction = (
        "You are an expert Sales Forecasting Analyst and Revenue Operations Manager. Your job is to predict "
        "the close probability, contract revenue value, and deal risk metrics for a prospect. Be realistic "
        "and analytical in your assessment."
    )
    
    # We will formulate a prompt that passes research, qualification score, and CRM data
    prompt = f"""
    We need a sales forecast for:
    - Company: {company_name}
    - Product: {product_sold}
    - Industry: {research_data.get('industry', 'Technology')}
    - Lead Qualification Score: {qualification_data.get('qualification_score', 50)}/100
    - Priority: {crm_record.get('priority', 'Medium')}
    
    Estimate the following:
    1. Close probability (0-100%).
    2. Estimated annual revenue value (in USD, typically ranging from $15,000 to $120,000 for mid-market/enterprise software).
    3. Deal risk ('Low', 'Medium', 'High').
    4. Key risk factors.
    5. Recommended next step.
    """
    
    score = qualification_data.get("qualification_score", 50)
    # Synthesize realistic values for fallback
    close_prob = min(90.0, max(15.0, score - 10.0))
    est_rev = 25000.0 + (score * 500.0) # E.g. 50 score -> $50,000
    risk = "Low" if score >= 80 else "Medium" if score >= 50 else "High"
    
    mock_data = {
        "close_probability": close_prob,
        "estimated_revenue": est_rev,
        "deal_risk": risk,
        "risk_factors": [
            "Procurement complexity in large organizations.",
            "Potential competition from established incumbent systems."
        ],
        "recommended_next_step": f"Schedule a 15-minute discovery call and focus on demonstrating how '{product_sold}' solves their specific operational bottlenecks."
    }
    
    try:
        result = call_gemini(
            prompt=prompt,
            system_instruction=system_instruction,
            response_schema=ForecastOutput,
            mock_fallback_data=mock_data
        )
        
        # Save output in SQLite
        update_lead_agent_data(lead_id, "forecast_data", result)
        
        # Log success
        execution_time = int((time.time() - start_time) * 1000)
        add_agent_log(
            lead_id=lead_id,
            agent_name="Forecast Agent",
            status="SUCCESS",
            confidence_score=0.85,
            execution_time_ms=execution_time,
            log_message=f"Deal forecast prepared: Prob {result['close_probability']}%, Est. Revenue ${result['estimated_revenue']:,}."
        )
        
        # Update State
        state["forecast"] = result
        state["current_node"] = "forecast"
        return state
        
    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        add_agent_log(
            lead_id=lead_id,
            agent_name="Forecast Agent",
            status="FAILED",
            execution_time_ms=execution_time,
            log_message=f"Error running Forecast Agent: {str(e)}"
        )
        state["error"] = str(e)
        state["status"] = "FAILED"
        return state
