# Developer & Architecture Guide: Agentic GTM Command Center

This guide explains the technical details of the **Agentic GTM Command Center** architecture, state machine orchestration, database schemas, and AI grounding logic.

---

## 1. Multi-Agent State Orchestration (LangGraph)

The core engine is built using **LangGraph**, which maintains a sequential state machine. Each agent behaves as a node that reads the current `AgentState` dictionary, executes computations using Gemini 2.5 Flash, writes updates to the database, and returns the modified state.

### State Schema (`AgentState`)
Defined in [state.py](file:///C:/Users/Aman%20verma/.gemini/antigravity/scratch/agentic-gtm-command-center/backend/app/agents/state.py):
```python
class AgentState(TypedDict):
    # Core inputs
    lead_id: str
    company_name: str
    website: str
    product_sold: str
    
    # Context injected from Vector DB
    retrieved_context: List[str]
    
    # Structured outputs from agents
    research: Dict[str, Any]
    qualification: Dict[str, Any]
    personas: List[Dict[str, Any]]
    outreach: Dict[str, Any]
    objection_responses: Dict[str, Any]
    crm_record: Dict[str, Any]
    forecast: Dict[str, Any]
    
    # Telemetry and status flags
    logs: List[Dict[str, Any]]
    current_node: str
    status: str
    error: Optional[str]
```

### Graph Compiler (`graph.py`)
To prevent naming collisions in newer LangGraph releases, state keys and node names are separated. The graph compiles with unique node identifiers:
```python
workflow = StateGraph(AgentState)
workflow.add_node("research_node", research_agent_node)
workflow.add_node("qualification_node", qualification_agent_node)
# ... other nodes
workflow.set_entry_point("research_node")
workflow.add_edge("research_node", "qualification_node")
# ... linear transition edges
workflow.add_edge("manager_node", END)
```

---

## 2. Zero-Hallucination AI Core (Gemini 2.5 Flash)

To guarantee that AI outputs conform strictly to CRM tables and UI fields, we utilize **Gemini 2.5 Flash** with native structured JSON outputs:

* **Pydantic Validation**: Each agent defines a Pydantic output model (e.g. `ResearchOutput`, `QualificationOutput`, `CRMRecordOutput`).
* **Generation Constraints**: The model receives the Pydantic schema in the config (`response_mime_type="application/json"` and `response_schema=ModelClass`), instructing the Gemini API to output structured, validated JSON directly.
* **Mock Fallback Handling**: If no API key is present or the request fails, the wrapper in [gemini_client.py](file:///C:/Users/Aman%20verma/.gemini/antigravity/scratch/agentic-gtm-command-center/backend/app/utils/gemini_client.py) automatically intercepts the failure and yields structured placeholder data matching the exact fields, keeping the UI intact.

---

## 3. RAG Grounding Engine (ChromaDB)

The retrieval system is defined in [vector_db.py](file:///C:/Users/Aman%20verma/.gemini/antigravity/scratch/agentic-gtm-command-center/backend/app/vector_db.py):

* **Embedding Class**: A custom `GeminiEmbeddingFunction` implements the ChromaDB interface.
* **Dynamic Embedding Strategy**:
  - If a `GEMINI_API_KEY` is present, it uses `models/text-embedding-004` to create 768-dimension vectors.
  - If offline or keyless, it uses a deterministic mathematical vector builder that generates 768-float arrays from document strings, allowing local testing without crashing.
* **Triggering search**: Before qualification and outreach, the system queries ChromaDB using `query_sales_context("Product description match criteria")`, adding matching document slices to the agent's context.

---

## 4. Relational Storage Schema (SQLite)

Transactions are managed in [db.py](file:///C:/Users/Aman%20verma/.gemini/antigravity/scratch/agentic-gtm-command-center/backend/app/db.py):

```sql
-- Leads table
CREATE TABLE leads (
    id TEXT PRIMARY KEY,
    company_name TEXT NOT NULL,
    website TEXT NOT NULL,
    product_sold TEXT NOT NULL,
    status TEXT NOT NULL,         -- PENDING, RUNNING, COMPLETE, FAILED
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    research_data TEXT,           -- Serialized JSON
    qualification_data TEXT,      -- Serialized JSON
    persona_data TEXT,            -- Serialized JSON
    outreach_data TEXT,           -- Serialized JSON
    objection_data TEXT,          -- Serialized JSON
    crm_data TEXT,                -- Serialized JSON
    forecast_data TEXT,           -- Serialized JSON
    final_report TEXT             -- Markdown Report String
);

-- Real-time telemetry audits logs
CREATE TABLE agent_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    status TEXT NOT NULL,         -- RUNNING, SUCCESS, FAILED
    confidence_score REAL,
    execution_time_ms INTEGER,
    log_message TEXT,
    timestamp TIMESTAMP
);
```

---

## 5. Next.js Frontend State Polling

In [page.tsx](file:///C:/Users/Aman%20verma/.gemini/antigravity/scratch/agentic-gtm-command-center/frontend/app/page.tsx):
1. Clicking **Execute GTM Center** triggers `/api/leads/run` which starts the LangGraph task in a FastAPI `BackgroundTasks` loop.
2. The frontend starts a 2.5-second polling interval querying `/api/leads/{lead_id}`.
3. The UI updates the Workflow HUD based on `state.current_node` and `state.status`.
4. Once `state.status` equals `COMPLETE` or `FAILED`, the interval is cleared, and the detailed metrics and result cards render.
