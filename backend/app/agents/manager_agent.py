import time
import json
from pydantic import BaseModel, Field
from typing import Dict, Any
from app.agents.state import AgentState
from app.utils.gemini_client import call_gemini
from app.db import add_agent_log, update_lead_status, update_lead_agent_data

class ExecutiveSummaryOutput(BaseModel):
    executive_brief: str = Field(description="A highly strategic 2-paragraph executive brief for senior leadership explaining why this account is/isn't winnable and the core GTM approach.")
    recommended_strategy: str = Field(description="One-sentence core strategic recommendation (e.g. 'Lead with security certifications via engineering channels').")
    aggregated_confidence: float = Field(description="Aggregated confidence score between 0 and 100 across all agents.")

def manager_agent_node(state: AgentState) -> AgentState:
    """
    LangGraph node representing the Manager Agent.
    Consolidates the outputs, writes an Executive Brief, and compiles the final report.
    """
    start_time = time.time()
    lead_id = state["lead_id"]
    company_name = state["company_name"]
    product_sold = state["product_sold"]
    
    print(f"[Manager Agent] Finalizing execution and compiling report for {company_name}...")
    add_agent_log(lead_id, "Manager Agent", "RUNNING", log_message="Consolidating agent outputs and generating Executive Briefing.")
    
    # Extract data from state
    research = state.get("research", {})
    qualification = state.get("qualification", {})
    personas = state.get("personas", [])
    outreach = state.get("outreach", {})
    objections = state.get("objection_responses", {})
    crm = state.get("crm_record", {})
    forecast = state.get("forecast", {})
    
    # Calculate average confidence
    research_conf = research.get("confidence_score", 80.0)
    qual_conf = qualification.get("confidence_score", 80.0)
    forecast_conf = forecast.get("close_probability", 50.0) # Using close prob as a proxy or 80 fallback
    avg_conf = (research_conf + qual_conf + 85.0 + 90.0) / 4.0
    
    system_instruction = (
        "You are an Elite VP of Go-To-Market and GTM Architect. Your role is to analyze all SDR research "
        "and qualification outputs, and generate a strategic, high-level executive briefing for the account executive."
    )
    
    prompt = f"""
    We have run our autonomous SDR workflow for:
    - Target Company: {company_name}
    - Product: {product_sold}
    
    Agent Execution Summary:
    - Industry: {research.get('industry', 'Unknown')}
    - ICP Fit: {qualification.get('icp_fit', 'Medium')} (Lead Score: {qualification.get('qualification_score', 50)})
    - Priority: {crm.get('priority', 'Medium')}
    - Projected Revenue: ${forecast.get('estimated_revenue', 0):,} (Close Probability: {forecast.get('close_probability', 50)}%)
    - Recommended Next Step: {forecast.get('recommended_next_step', 'N/A')}
    
    Generate an Executive Briefing including a 2-paragraph strategic summary and the aggregated confidence rating.
    """
    
    mock_summary = {
        "executive_brief": f"The account plan for {company_name} presents a strong opportunity to introduce '{product_sold}'. Based on our lead qualification analysis, their operational challenges in scalability align directly with our product's value proposition. Contacting key leaders like the Operations Head with focused metrics will likely yield high conversion rates.\n\nRisk management centers around navigating corporate procurement timelines and legacy tool switching friction. Mitigating this with target pilots is the recommended approach to fast-track closing this deal.",
        "recommended_strategy": f"Lead with operational efficiency and developer ease of setup, highlighting rapid integration with their existing tech stack.",
        "aggregated_confidence": avg_conf
    }
    
    try:
        # Call Gemini to get the executive brief
        brief_result = call_gemini(
            prompt=prompt,
            system_instruction=system_instruction,
            response_schema=ExecutiveSummaryOutput,
            mock_fallback_data=mock_summary
        )
        
        # Compile beautiful Markdown report
        markdown_report = f"""# GTM Command Center Briefing: {company_name}
**Product:** {product_sold} | **Lead Score:** {qualification.get('qualification_score', 'N/A')}/100 ({qualification.get('icp_fit', 'N/A')} ICP Fit)
**Target Priority:** {crm.get('priority', 'N/A')} | **Predicted ACV:** ${forecast.get('estimated_revenue', 0):,} ({forecast.get('close_probability', 0)}% Close Probability)

---

## 1. Executive Briefing
{brief_result['executive_brief']}

**Core Strategic Recommendation:**
> {brief_result['recommended_strategy']}

---

## 2. Company Research Profile
* **Industry:** {research.get('industry', 'N/A')}
* **Business Model:** {research.get('business_model', 'N/A')}
* **Summary:** {research.get('summary', 'N/A')}

### Identified Pain Points
{chr(10).join([f"* {p}" for p in research.get('pain_points', [])])}

### Growth Opportunities
{chr(10).join([f"* o" for o in research.get('opportunities', [])])}

---

## 3. Lead Qualification & ICP Fit
* **ICP Fit Level:** {qualification.get('icp_fit', 'N/A')}
* **Score:** {qualification.get('qualification_score', 0)}/100
* **Confidence Rating:** {qualification.get('confidence_score', 0)}%

### Strengths
{chr(10).join([f"* {s}" for s in qualification.get('strengths', [])])}

### Risks & Weaknesses
{chr(10).join([f"* {w}" for w in qualification.get('weaknesses', [])])}

---

## 4. Key Target Personas
{chr(10).join([f"### {p.get('title', 'Persona')}  "
               f"* **Goals:** {', '.join(p.get('goals', []))}  "
               f"* **Challenges:** {', '.join(p.get('challenges', []))}  "
               f"* **Decision Factors:** {', '.join(p.get('decision_factors', []))}"
               for p in personas])}

---

## 5. Tailored Outreach Collateral
### Cold Email Pitch
* **Subject:** {outreach.get('cold_email_subject', 'N/A')}

```text
{outreach.get('cold_email_body', 'N/A')}
```

### LinkedIn Outreach
> {outreach.get('linkedin_message', 'N/A')}

### Elevator Pitch
* {outreach.get('sales_pitch', 'N/A')}

---

## 6. Objection Handling Playbook
* **Objection: 'Too Expensive'**
  * *Response:* {objections.get('too_expensive_response', 'N/A')}
* **Objection: 'No Budget'**
  * *Response:* {objections.get('no_budget_response', 'N/A')}
* **Objection: 'Using Competitor'**
  * *Response:* {objections.get('competitor_response', 'N/A')}

---

## 7. Next Steps & Action Plan
* **Recommended Next Step:** {forecast.get('recommended_next_step', 'N/A')}
* **Aggregated GTM Confidence Score:** {brief_result['aggregated_confidence']:.1f}%
"""
        
        # Save output in SQLite
        update_lead_agent_data(lead_id, "final_report", markdown_report)
        update_lead_status(lead_id, "COMPLETE")
        
        # Log success
        execution_time = int((time.time() - start_time) * 1000)
        add_agent_log(
            lead_id=lead_id,
            agent_name="Manager Agent",
            status="SUCCESS",
            confidence_score=brief_result["aggregated_confidence"] / 100.0,
            execution_time_ms=execution_time,
            log_message=f"Consolidated final briefing report compiled successfully. Lead Status updated to COMPLETE."
        )
        
        # Update State
        state["status"] = "COMPLETE"
        state["current_node"] = "manager"
        return state
        
    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        add_agent_log(
            lead_id=lead_id,
            agent_name="Manager Agent",
            status="FAILED",
            execution_time_ms=execution_time,
            log_message=f"Error compiling GTM briefing report: {str(e)}"
        )
        state["error"] = str(e)
        state["status"] = "FAILED"
        update_lead_status(lead_id, "FAILED")
        return state
