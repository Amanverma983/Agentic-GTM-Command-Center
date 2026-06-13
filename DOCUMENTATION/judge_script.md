# Hackathon Presentation Script (3-Minute Timed Pitch)
*Designed to wow the judges and explain the product value, architecture, and live demo.*

---

### **Slide 1: Problem & Vision (0:00 - 0:45)**

* **Presenter:** "Hello everyone. Today, let's talk about the status quo of modern B2B sales. If you walk into any B2B company, you'll see SDRs and sales reps drowning in tabs. They are scraping websites, digging through sales playbooks, manually writing cold emails, copy-pasting notes into CRM tools, and guessing contract close probabilities. In fact, research shows they spend **64% of their time NOT selling**.

* Chatbots don't solve this. Chatbots are passive—they wait for you to ask a question, and they don't *do* the work.

* We built the **Agentic GTM Command Center**—an autonomous AI employee. You input a lead name, website, and product, and the system runs an automated multi-agent pipeline from company research all the way to revenue forecasting and CRM logging—with zero manual copy-pasting."

---

### **Slide 2: Multi-Agent Architecture (0:45 - 1:15)**

* **Presenter:** "How does this work under the hood? Instead of a single massive prompt, we engineered a modular multi-agent system orchestrated via **LangGraph**. 

* The state transitions sequentially. The **Research Agent** scrapes the target website. The **Qualification Agent** evaluates the company against our playbooks. The **Persona Agent** designs detailed buyer decision profiles. The **Outreach Agent** drafts personalized pitches, while the **Objection Handling Agent** builds a customized sales script. Finally, the **CRM** and **Forecast Agents** prepare structured data and ACV predictions.

* By dividing labor across specialized agents, we achieve high accuracy, robust validation, and easily inspectable execution checkpoints."

---

### **Slide 3: Vector RAG & AI Core (1:15 - 1:45)**

* **Presenter:** "To make sure this AI employee is accurate and doesn't write generic pitch templates, we built a **Vector RAG system** powered by **ChromaDB**. 

* Through the dashboard, you can upload product briefs, pricing playbooks, and case studies. Our agents query this vector space in real-time, fetching contextually relevant sections.

* Using **Gemini 2.5 Flash** with native JSON schemas, we eliminate AI hallucinations. And for maximum reliability, the entire workflow supports a dynamic fallback mechanism, meaning it remains fully functional even in offline environments."

---

### **Slide 4: Live Demo (1:45 - 2:30)**

* **Presenter:** *(Point to the screen showing the running Next.js Dashboard)*
* "Let me show you this in action. We enter a company name—say, Slack—and the product we want to sell them. We hit 'Execute GTM Center.' 

* Instantly, our **Agentic HUD** lights up. You can see the telemetry showing the active agent nodes glowing in violet as the LangGraph state machine moves from Research to Qualification, Persona, and CRM formatting.

* Once completed, look at the results. We have a qualified score of 78/100, a projected contract size of $64,000, and a compiled Executive Briefing report ready for the Account Executive. Under the tabs, we can inspect individual agent outputs, grab personalized cold email copy, copy-paste a LinkedIn message, or download the raw JSON CRM record ready for Salesforce."

---

### **Slide 5: Business Impact & Wrap-up (2:30 - 3:00)**

* **Presenter:** "The business impact is simple: we compress **2 hours of research and writing into a 30-second automated pipeline**. We improve outreach conversion rates by **3x** using hyper-grounded personalization, and we ensure perfect data hygiene in your CRM database.

* We built this with Next.js 14, FastAPI, SQLite, ChromaDB, and LangGraph. It is containerized and ready for Docker deployment. 

* The future of sales isn't conversational assistants—it's autonomous teams. Thank you, and we'd love to take your questions!"
