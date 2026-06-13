import uuid
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.db import (
    create_lead, 
    get_lead, 
    get_all_leads, 
    get_agent_logs, 
    update_lead_status
)
from app.agents.graph import gtm_workflow
from app.utils.email_sender import send_cold_email

router = APIRouter()

class LeadCreateRequest(BaseModel):
    company_name: str
    website: str
    product_sold: str

def run_langgraph_workflow(lead_id: str, company_name: str, website: str, product_sold: str):
    """
    Executes the LangGraph multi-agent GTM pipeline asynchronously.
    """
    initial_state = {
        "lead_id": lead_id,
        "company_name": company_name,
        "website": website,
        "product_sold": product_sold,
        "retrieved_context": [],
        "research": {},
        "qualification": {},
        "personas": [],
        "outreach": {},
        "objection_responses": {},
        "crm_record": {},
        "forecast": {},
        "logs": [],
        "current_node": "start",
        "status": "RUNNING",
        "error": None
    }
    
    update_lead_status(lead_id, "RUNNING")
    try:
        # Run state machine
        gtm_workflow.invoke(initial_state)
    except Exception as e:
        print(f"Critical error executing LangGraph workflow for {company_name}: {e}")
        update_lead_status(lead_id, "FAILED")

@router.post("/run")
def trigger_gtm_run(request: LeadCreateRequest, background_tasks: BackgroundTasks):
    """
    Triggers a GTM research workflow for a prospect company.
    """
    if not request.company_name or not request.website or not request.product_sold:
        raise HTTPException(status_code=400, detail="Missing required input parameters.")
        
    lead_id = str(uuid.uuid4())
    lead = create_lead(
        lead_id=lead_id,
        company_name=request.company_name,
        website=request.website,
        product_sold=request.product_sold
    )
    
    # Run pipeline in the background
    background_tasks.add_task(
        run_langgraph_workflow,
        lead_id,
        request.company_name,
        request.website,
        request.product_sold
    )
    
    return {
        "success": True,
        "message": "GTM Command Center workflow initiated successfully.",
        "lead_id": lead_id,
        "lead": lead
    }

@router.get("/")
def list_leads():
    """
    Returns list of all prospect lead executions.
    """
    return get_all_leads()

@router.get("/{lead_id}")
def fetch_lead_details(lead_id: str):
    """
    Retrieves execution outputs and reports of a specific lead.
    """
    lead = get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead execution profile not found.")
    return lead

@router.get("/{lead_id}/logs")
def fetch_lead_agent_logs(lead_id: str):
    """
    Returns step-by-step audit logs of the agents executing for a specific lead.
    """
    lead = get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead execution profile not found.")
        
    logs = get_agent_logs(lead_id)
    return {
        "lead_id": lead_id,
        "status": lead["status"],
        "logs": logs
    }


class SendEmailRequest(BaseModel):
    to_email: str
    prospect_name: Optional[str] = None


@router.post("/{lead_id}/send-email")
def send_outreach_email(lead_id: str, request: SendEmailRequest):
    """
    Sends the AI-generated cold email for a specific lead to the prospect's email address.
    Requires SMTP_EMAIL and SMTP_APP_PASSWORD configured in backend .env.
    """
    lead = get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead execution profile not found.")

    outreach = lead.get("outreach")
    if not outreach:
        raise HTTPException(
            status_code=400,
            detail="Outreach has not been generated yet. Wait for the GTM workflow to complete."
        )

    subject = outreach.get("cold_email_subject", "Partnership Opportunity")
    body = outreach.get("cold_email_body", "")
    company_name = lead.get("company_name", "")

    if not body:
        raise HTTPException(
            status_code=400,
            detail="Cold email body is empty. Ensure the outreach agent ran successfully."
        )

    result = send_cold_email(
        to_email=request.to_email,
        subject=subject,
        body=body,
        prospect_name=request.prospect_name,
        company_name=company_name,
    )

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@router.get("/smtp-status")
def check_smtp_status():
    """
    Returns whether Gmail SMTP is configured for email sending.
    """
    from app.config import settings
    configured = bool(settings.smtp_email and settings.smtp_app_password)
    return {
        "configured": configured,
        "smtp_email": settings.smtp_email if configured else None,
        "message": "Gmail SMTP is ready" if configured else "Add SMTP_EMAIL and SMTP_APP_PASSWORD to backend .env to enable email sending"
    }
