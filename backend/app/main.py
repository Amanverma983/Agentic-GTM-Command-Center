import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db import init_db
from app.routes import leads, files

app = FastAPI(
    title="Agentic GTM Command Center API",
    description="Backend API powering multi-agent GTM automation, database operations, and playbooks RAG search.",
    version="1.0.0"
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup DB setup
@app.on_event("startup")
def startup_event():
    print("[Database] Initializing database connections and schemas...")
    init_db()
    print("[Database] DB schema prepared successfully.")

# Include routers
app.include_router(leads.router, prefix="/api/leads", tags=["Leads & Workflow"])
app.include_router(files.router, prefix="/api/files", tags=["RAG Sales Collateral"])

@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "service": "Agentic GTM Command Center API",
        "gemini_api_configured": bool(settings.gemini_api_key)
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=True)
