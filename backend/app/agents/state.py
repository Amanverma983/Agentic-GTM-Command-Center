from typing import TypedDict, Dict, Any, List, Optional

class AgentState(TypedDict):
    # Inputs
    lead_id: str
    company_name: str
    website: str
    product_sold: str
    
    # RAG Context
    retrieved_context: List[str]
    
    # Agent Outputs
    research: Dict[str, Any]
    qualification: Dict[str, Any]
    personas: List[Dict[str, Any]]
    outreach: Dict[str, Any]
    objection_responses: Dict[str, Any]
    crm_record: Dict[str, Any]
    forecast: Dict[str, Any]
    
    # Status / Control
    logs: List[Dict[str, Any]]
    current_node: str
    status: str
    error: Optional[str]
