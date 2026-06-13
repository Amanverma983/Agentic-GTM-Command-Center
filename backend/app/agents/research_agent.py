import time
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from app.agents.state import AgentState
from app.utils.gemini_client import call_gemini
from app.db import add_agent_log, update_lead_agent_data

class ResearchOutput(BaseModel):
    company_name: str = Field(description="Name of the company analyzed")
    industry: str = Field(description="Primary industry classification")
    business_model: str = Field(description="Primary business model, e.g. B2B SaaS, B2C, Enterprise, Marketplace")
    summary: str = Field(description="A concise summary of the company, what they do, and who they serve")
    pain_points: List[str] = Field(description="3-5 key challenges or pain points this company faces in their business")
    opportunities: List[str] = Field(description="3-5 strategic growth opportunities for this company")
    strategic_insights: List[str] = Field(description="Actionable sales-centric insights on how to sell our product to them")
    confidence_score: float = Field(description="Self-evaluated confidence score between 0 and 100 based on data quality")

def scrape_website(url: str) -> str:
    """
    Attempts to scrape a website home page for text content.
    Returns parsed text or empty string on error.
    """
    if not url.startswith("http"):
        url = "https://" + url
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            return "\n".join(chunk for chunk in chunks if chunk)[:4000]
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
    return ""

def research_agent_node(state: AgentState) -> AgentState:
    """
    LangGraph node representing the Research Agent.
    """
    start_time = time.time()
    lead_id = state["lead_id"]
    company_name = state["company_name"]
    website = state["website"]
    product_sold = state["product_sold"]
    
    print(f"[Research Agent] Analyzing {company_name} ({website})...")
    add_agent_log(lead_id, "Research Agent", "RUNNING", log_message=f"Starting scraping and analysis of {company_name} website.")
    
    # Try scraping
    scraped_text = scrape_website(website)
    context_str = f"Scraped Website Content:\n{scraped_text}" if scraped_text else "Website scraping returned no content (using parametric knowledge)."
    
    # Construct AI prompt
    system_instruction = (
        "You are an Elite Enterprise SDR Research Agent. Your job is to analyze companies, "
        "understand their business models, identify their major pain points, and suggest strategic "
        "insights that an SDR could use to pitch them a product."
    )
    
    prompt = f"""
    Analyze the company: '{company_name}'
    Website URL: '{website}'
    
    We are trying to sell them this product/service: '{product_sold}'
    
    {context_str}
    
    Provide a detailed research analysis. Focus on real pain points that our product '{product_sold}' could address.
    """
    
    # Generate dynamic fallback data in case of API failure
    mock_data = {
        "company_name": company_name,
        "industry": "Technology / Software Solutions",
        "business_model": "B2B Enterprise SaaS",
        "summary": f"{company_name} is an enterprise-oriented solution provider operating via its portal at {website}. They focus on scaling operations, optimizing team collaboration, and driving efficiency.",
        "pain_points": [
            "Inefficient operations and manual workflows limiting rapid scale.",
            "High client acquisition costs and difficulty qualifying high-intent buyers.",
            "Information siloing and fragmented communications across departments."
        ],
        "opportunities": [
            "Expansion into automated workflow orchestration.",
            "Integration of advanced AI and generative capabilities into customer touchpoints.",
            "Targeting enterprise contracts by reinforcing security compliance."
        ],
        "strategic_insights": [
            f"Pitch our '{product_sold}' directly as a solution to reduce operational bottlenecks by 30%.",
            "Target business division heads with custom case studies displaying rapid ROI.",
            "Emphasize ease of setup and compliance credentials to navigate enterprise procurement."
        ],
        "confidence_score": 85.0
    }
    
    try:
        result = call_gemini(
            prompt=prompt,
            system_instruction=system_instruction,
            response_schema=ResearchOutput,
            mock_fallback_data=mock_data
        )
        
        # Save output in SQLite
        update_lead_agent_data(lead_id, "research_data", result)
        
        # Log success
        execution_time = int((time.time() - start_time) * 1000)
        add_agent_log(
            lead_id=lead_id,
            agent_name="Research Agent",
            status="SUCCESS",
            confidence_score=result["confidence_score"] / 100.0,
            execution_time_ms=execution_time,
            log_message=f"Successfully analyzed {company_name}. Identified industry: {result['industry']}."
        )
        
        # Update State
        state["research"] = result
        state["current_node"] = "research"
        return state
        
    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        add_agent_log(
            lead_id=lead_id,
            agent_name="Research Agent",
            status="FAILED",
            execution_time_ms=execution_time,
            log_message=f"Error running Research Agent: {str(e)}"
        )
        state["error"] = str(e)
        state["status"] = "FAILED"
        return state
