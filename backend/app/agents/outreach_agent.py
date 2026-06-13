import time
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from app.agents.state import AgentState
from app.utils.gemini_client import call_gemini
from app.db import add_agent_log, update_lead_agent_data

class OutreachOutput(BaseModel):
    cold_email_subject: str = Field(description="Engaging, non-spammy subject line for the email")
    cold_email_body: str = Field(description="Complete personalized cold email body with placeholders like [Prospect Name]")
    linkedin_message: str = Field(description="Short, professional LinkedIn connection request / direct message (under 300 characters)")
    sales_pitch: str = Field(description="30-second elevator pitch customized to their primary challenge")
    follow_up_sequence: List[str] = Field(description="Array of 2 short follow-up messages/emails to send later")

def outreach_agent_node(state: AgentState) -> AgentState:
    """
    LangGraph node representing the Outreach Agent.
    """
    start_time = time.time()
    lead_id = state["lead_id"]
    company_name = state["company_name"]
    product_sold = state["product_sold"]
    research_data = state["research"]
    qualification_data = state["qualification"]
    
    print(f"[Outreach Agent] Crafting outreach collateral for {company_name}...")
    add_agent_log(lead_id, "Outreach Agent", "RUNNING", log_message=f"Drafting personalized emails and LinkedIn outreach targeting pain points.")
    
    system_instruction = (
        "You are an Elite Enterprise SDR Copywriter. Your task is to write high-converting, personalized, "
        "and clear outreach content. Avoid hype, emojis overload, and generic sales talk. "
        "Reference the specific challenges discovered in the research and position our product as the solution."
    )
    
    prompt = f"""
    Write sales outreach materials for pitching '{product_sold}' to '{company_name}'.
    
    Company Context:
    - Industry: {research_data.get('industry', '')}
    - Key Pain Points: {', '.join(research_data.get('pain_points', []))}
    - Strategic Insights: {', '.join(research_data.get('strategic_insights', []))}
    
    Evaluation Context:
    - Qualification score: {qualification_data.get('qualification_score', 80)}
    - ICP fit rating: {qualification_data.get('icp_fit', 'High')}
    
    Generate:
    1. A cold email (subject line + body).
    2. A short LinkedIn connect / pitch message (max 300 characters).
    3. A 30-second elevator pitch.
    4. Two follow-up sequence drafts.
    """
    
    mock_data = {
        "cold_email_subject": f"Solving operational bottlenecks at {company_name}",
        "cold_email_body": f"Hi [Prospect Name],\n\nI've been following {company_name}'s growth in the space, and noticed your focus on scaling operations. Often, companies at your stage face challenges like fragmented communication and manual database errors.\n\nWe built '{product_sold}' specifically to address these bottlenecks, allowing teams to automate up to 40% of administrative overhead.\n\nDo you have 10 minutes next Tuesday at 2 PM for a quick demonstration on how this could work for your team?\n\nBest regards,\n[Your Name]",
        "linkedin_message": f"Hi [Prospect Name], saw your focus on team scalability at {company_name}. We help firms reduce workflow delays using our '{product_sold}' engine. Love to connect and share a quick workflow blueprint!",
        "sales_pitch": f"We help companies like {company_name} who are experiencing operational bottlenecks automate their core administrative pipelines using '{product_sold}', resulting in a 30% speed boost and complete audit logs.",
        "follow_up_sequence": [
            "Hi [Prospect Name], just following up on my previous note. Thought you might find this case study interesting on how we helped a similar team reduce pipeline friction. Do you have a few minutes this week?",
            "Hi [Prospect Name], since I haven't heard back, I assume this isn't a priority right now. If things change and operational efficiency becomes a focus, feel free to reach out. Wishing you the best!"
        ]
    }
    
    try:
        result = call_gemini(
            prompt=prompt,
            system_instruction=system_instruction,
            response_schema=OutreachOutput,
            mock_fallback_data=mock_data
        )
        
        # Save output in SQLite
        update_lead_agent_data(lead_id, "outreach_data", result)
        
        # Log success
        execution_time = int((time.time() - start_time) * 1000)
        add_agent_log(
            lead_id=lead_id,
            agent_name="Outreach Agent",
            status="SUCCESS",
            confidence_score=0.95,
            execution_time_ms=execution_time,
            log_message=f"Successfully generated personalized cold outreach assets for {company_name}."
        )
        
        # Update State
        state["outreach"] = result
        state["current_node"] = "outreach"
        return state
        
    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        add_agent_log(
            lead_id=lead_id,
            agent_name="Outreach Agent",
            status="FAILED",
            execution_time_ms=execution_time,
            log_message=f"Error running Outreach Agent: {str(e)}"
        )
        state["error"] = str(e)
        state["status"] = "FAILED"
        return state
