# Product Live Demo Script
*A step-by-step guide to executing a flawless, high-impact demo for the judges.*

---

## Preparation & Setup
1. Start the FastAPI backend:
   ```bash
   cd backend
   python app/main.py
   ```
2. Start the Next.js frontend:
   ```bash
   cd frontend
   npm run dev
   ```
3. Open browser to `http://localhost:3000`.
4. Ensure you have internet access (or the backend will automatically run in Mock Fallback mode).

---

## Demo Step-by-Step Flow

### **Step 1: Ground the RAG System (Optional but Recommended)**
1. In the **RAG Sales Playbooks** panel (bottom-left of dashboard), click "Click to upload collateral".
2. Select a plain text file containing some sales/product context. (Example: Create a quick file `pricing_sheet.txt` containing: *"Enterprise price for Threat Intel platform starts at $50,000/year. Targeted towards CTOs and CISOs. Key competitor is FireEye."*)
3. Watch the uploader change to **"Chunking & Indexing Vectors..."** and then display your file in the **Active Grounding Files** list.
4. *Narrative:* "First, we ground our AI. I am uploading our internal product pricing brief. It is instantly split, vectorized, and indexed inside ChromaDB."

---

### **Step 2: Enter Prospect Details**
1. In the **Prospect Intake Command** form (top-left), enter:
   * **Company Name**: `Slack`
   * **Company Website**: `slack.com`
   * **Product Being Sold**: `Automated Developer Productivity Analytics Tool`
2. Click **Execute GTM Center**.
3. *Narrative:* "We want to pitch an Automated Developer Productivity tool to Slack. We feed in their basic metadata and launch the multi-agent graph."

---

### **Step 3: Walkthrough the Agent Telemetry HUD**
1. Point to the **Agentic Workflow HUD** (top-right).
2. Show the active node changing as it progresses:
   * **Research Agent** (glowing, scraping slack.com website text).
   * **Qualification Agent** (glowing, running vector searches on the pricing guidelines we uploaded).
   * **Persona Agent** (generating goals/challenges for CEO, CTO, Operations, Marketing).
   * **Outreach Agent** (drafting cold copy).
   * **Objection, CRM, Forecast, Manager Agents** completing in sequence.
3. *Narrative:* "Look at our agent telemetry HUD. You can watch the workflow transition states in real-time. LangGraph manages the state machine sequentially, checking off each agent node on success."

---

### **Step 4: Inspect Compiled Results**
1. When the Manager Agent finishes, the **Lead Status** badge updates to `Complete`, and the **Metric Summary** panel renders:
   * High fit score (e.g. `78/100`).
   * Estimated ACV (e.g. `$64,000`).
   * Deal probability.
   * Aggregate model confidence.
2. Select the **Briefing Report** tab: Show the comprehensive Account Briefing document.
3. Click the **Research** tab: Point out the pain points and growth opportunities discovered.
4. Click the **Outreach** tab: Point out the customized Cold Email and click the **"Copy"** button to show the interactive copy indicator. Show the short LinkedIn connection message.
5. Click the **CRM Mapping** tab: Show the table representation, then toggle **"Raw JSON"** to display the Salesforce-ready JSON.
6. Click the **Forecast** tab: Show the deal risk drivers and recommended next-step actions.
7. *Narrative:* "Within 30 seconds, the Command Center compiles a complete sales toolkit. We have qualified fit scores, target buyer personas, customized email templates, objection playbooks, Salesforce-ready JSON logs, and deal risks analyzed."
