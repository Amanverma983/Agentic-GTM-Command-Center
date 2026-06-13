import time
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from app.agents.state import AgentState
from app.utils.gemini_client import call_gemini
from app.db import add_agent_log, update_lead_agent_data
from app.vector_db import query_sales_context

class QualificationOutput(BaseModel):
    qualification_score: float = Field(description="Calculated lead quality score from 0 to 100")
    confidence_score: float = Field(description="Confidence score in our evaluation from 0 to 100")
    icp_fit: str = Field(description="Ideal Customer Profile fit: 'High', 'Medium', or 'Low'")
    reasoning: str = Field(description="Detailed step-by-step reasoning explaining the score")
    strengths: List[str] = Field(description="Key strengths making this lead a good fit for our product")
    weaknesses: List[str] = Field(description="Risk factors or gaps preventing a perfect fit")

def qualification_agent_node(state: AgentState) -> AgentState:
    """
    LangGraph node representing the Lead Qualification Agent.
    """
    start_time = time.time()
    lead_id = state["lead_id"]
    company_name = state["company_name"]
    product_sold = state["product_sold"]
    research_data = state["research"]
    
    print(f"[Qualification Agent] Evaluating ICP fit for {company_name}...")
    add_agent_log(lead_id, "Qualification Agent", "RUNNING", log_message=f"Evaluating ICP fit and product alignment for {company_name}.")
    
    # Query ChromaDB vector DB for any playbooks or pricing info related to the product being sold
    retrieved_items = query_sales_context(query_text=f"Product: {product_sold} ICP criteria target audience pricing", n_results=2)
    retrieved_text = ""
    if retrieved_items:
        retrieved_text = "\n".join([f"- Content from playbook: {item['content']}" for item in retrieved_items])
        state["retrieved_context"] = [item["content"] for item in retrieved_items]
        
    system_instruction = (
        "You are an expert Lead Qualification Specialist and Sales Operations Executive. Your job is "
        "to evaluate lead quality by comparing the target company's industry, business model, and pain points "
        "against the product being sold. You will calculate a qualification score and confidence score."
    )
    
    prompt = f"""
    We need to qualify the company: '{company_name}'
    We are selling them: '{product_sold}'
    
    Research findings about the target company:
    - Industry: {research_data.get('industry', 'Unknown')}
    - Business Model: {research_data.get('business_model', 'Unknown')}
    - Summary: {research_data.get('summary', '')}
    - Pain Points: {', '.join(research_data.get('pain_points', []))}
    
    Our Sales Playbooks/Context Info:
    {retrieved_text if retrieved_text else "No additional product files uploaded. Use standard enterprise product fit logic."}
    
    Evaluate the quality of this lead. Provide a score from 0-100, ICP Fit (High/Medium/Low), and detailed reasoning.
    """
    
    mock_data = {
        "qualification_score": 78.0,
        "confidence_score": 85.0,
        "icp_fit": "High",
        "reasoning": f"{company_name} shows a strong alignment with '{product_sold}'. Their pain points regarding operational inefficiencies and customer acquisition match the direct capabilities of our product. While there is a risk regarding procurement budget constraints typical of their segment, the overall value proposition makes them a high-priority lead.",
        "strengths": [
            f"Active pain points perfectly match the primary solution offered by '{product_sold}'.",
            f"Operating model benefits directly from automated workflows.",
            "High digital maturity suggests low friction during product integration."
        ],
        "weaknesses": [
            "Lack of public data on current department budget allocations.",
            "Potential competition from legacy tools they currently use."
        ]
    }
    
    try:
        result = call_gemini(
            prompt=prompt,
            system_instruction=system_instruction,
            response_schema=QualificationOutput,
            mock_fallback_data=mock_data
        )
        
        # Save output in SQLite
        update_lead_agent_data(lead_id, "qualification_data", result)
        
        # Log success
        execution_time = int((time.time() - start_time) * 1000)
        add_agent_log(
            lead_id=lead_id,
            agent_name="Qualification Agent",
            status="SUCCESS",
            confidence_score=result["confidence_score"] / 100.0,
            execution_time_ms=execution_time,
            log_message=f"Qualified {company_name}. Fit: {result['icp_fit']}, Score: {result['qualification_score']}."
        )
        
        # Update State
        state["qualification"] = result
        state["current_node"] = "qualification"
        return state
        
    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        add_agent_log(
            lead_id=lead_id,
            agent_name="Qualification Agent",
            status="FAILED",
            execution_time_ms=execution_time,
            log_message=f"Error running Qualification Agent: {str(e)}"
        )
        state["error"] = str(e)
        state["status"] = "FAILED"
        return state
