# Agentic GTM Command Center
An autonomous, enterprise-grade multi-agent Go-To-Market and SDR platform that researches leads, qualifies prospects against playbooks, maps target personas, generates customized outreach copy, reframes client objections, structures database records, and predicts deal metrics.

Designed to win an AI hackathon.

---

## 🚀 Key Features
* **Multi-Agent Workflow**: Coordinated via **LangGraph** to execute a structured, sequential GTM pipeline.
* **Semantic Grounding (RAG)**: Ingest sales sheets, playbooks, and competitor indices into **ChromaDB** to ground qualification and outreach.
* **Gemini 2.5 Flash Integration**: Model routing with Pydantic JSON schema constraints to eliminate hallucinations.
* **Modern Telemetry HUD**: Sleek, dark-mode Next.js dashboard featuring live agent execution node updates, logs viewer, and analytics metrics.
* **Enterprise Grade**: Local SQLite transactional memory, automated API retry handlers, and Docker container support.
* **Judge-Friendly Reliability**: Automatic fallback simulation. Runs fully offline or without a Gemini API Key.

---

## 🛠️ Architecture & Workflow

```
 [Intake Form] ──> Ingest playbooks to (ChromaDB)
       │
 [FastAPI Server] ──> Save Lead state in (SQLite)
       │
 [LangGraph Orchestrator]
       ├──> 1. Research Agent (Website Scraping & Parametric Analysis)
       ├──> 2. Qualification Agent (RAG pricing & ICP fit scoring)
       ├──> 3. Persona Agent (Goals & Challenges for C-Suite)
       ├──> 4. Outreach Agent (Cold email, InMails, elevator pitch)
       ├──> 5. Objection Agent (Sales rebuttal playbook)
       ├──> 6. CRM Agent (Format Salesforce / HubSpot JSON)
       ├──> 7. Forecast Agent (ACV estimation & close probability)
       └──> 8. Manager Agent (Generate Executive briefing briefing report)
```

---

## 📁 Folder Structure
```
agentic-gtm-command-center/
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI server entry point
│   │   ├── config.py              # Configuration & Pydantic settings
│   │   ├── db.py                  # SQLite schema definitions & CRUD
│   │   ├── vector_db.py           # ChromaDB client & vector embeddings
│   │   ├── agents/                # LangGraph workflow nodes
│   │   │   ├── state.py           # LangGraph state TypedDict
│   │   │   ├── graph.py           # LangGraph compiler
│   │   │   └── *_agent.py         # Sub-agents implementation
│   │   ├── routes/                # REST endpoints (leads, files)
│   │   └── utils/
│   │       └── gemini_client.py   # SDK caller with mock fallback
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx               # Control center dashboard
│   │   ├── layout.tsx             # Theme layout & SEO metadata
│   │   ├── globals.css            # Styles, glassmorphism, animations
│   │   └── components/            # UI components (Visualizer, Cards, Uploader)
│   └── package.json
├── DOCUMENTATION/                  # Hackathon pitch materials
│   ├── pitch_deck.md
│   ├── judge_script.md
│   └── demo_script.md
├── docker-compose.yml
└── README.md
```

---

## 💾 Database Schema

### Relational Schema (SQLite)
* **`leads`**: Strives Lead inputs (Company Name, Website, Product) and JSON serialized agent outputs (`research_data`, `qualification_data`, `persona_data`, `outreach_data`, `objection_data`, `crm_data`, `forecast_data`, `final_report`, `status`).
* **`agent_logs`**: Telemetry log table storing time, confidence score, and state logs.
* **`sales_collateral`**: Uploaded playbook files tracker metadata.

### Vector Collection (ChromaDB)
* **`sales_playbooks`**: Vectorized blocks (1500 char length, 200 char overlap) embedded via Gemini `text-embedding-004` (or mock-array fallbacks).

---

## 🔌 API Endpoints

### Leads Router (`/api/leads`)
* `POST /run`: Start the LangGraph async background task for a lead.
* `GET /`: Returns a list of all historical runs.
* `GET /{lead_id}`: Returns full details of a specific execution.
* `GET /{lead_id}/logs`: Returns step-by-step telemetry logs.

### Files Router (`/api/files`)
* `POST /upload`: Index text/markdown file into ChromaDB and SQLite.
* `GET /`: List all uploaded briefs.
* `DELETE /{file_id}`: Clear document vectors and database metadata.

---

## ⚙️ Setup Instructions

### 1. Configure Environment Variables
Create a `.env` file inside the `backend` folder:
```env
GEMINI_API_KEY="your-gemini-api-key"
SQLITE_DB_PATH="gtm_center.db"
CHROMA_DB_PATH="chroma_db"
HOST="0.0.0.0"
PORT=8000
```

---

### 2. Manual Installation

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/Scripts/activate # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app/main.py
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open browser to `http://localhost:3000`.

---

### 3. Docker Compose Deployment
Ensure Docker is running, then launch containerization:
```bash
docker-compose up --build
```
This builds the backend container and binds the FastAPI service port `8000`.
