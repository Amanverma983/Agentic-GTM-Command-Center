import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.config import settings

def get_db_connection():
    conn = sqlite3.connect(settings.sqlite_db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create leads table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id TEXT PRIMARY KEY,
        company_name TEXT NOT NULL,
        website TEXT NOT NULL,
        product_sold TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        research_data TEXT,
        qualification_data TEXT,
        persona_data TEXT,
        outreach_data TEXT,
        objection_data TEXT,
        crm_data TEXT,
        forecast_data TEXT,
        final_report TEXT
    )
    """)
    
    # Create agent logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_id TEXT NOT NULL,
        agent_name TEXT NOT NULL,
        status TEXT NOT NULL,
        confidence_score REAL,
        execution_time_ms INTEGER,
        log_message TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(lead_id) REFERENCES leads(id)
    )
    """)
    
    # Create sales collateral table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales_collateral (
        id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        file_type TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()

def create_lead(lead_id: str, company_name: str, website: str, product_sold: str) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    cursor.execute(
        """
        INSERT INTO leads (id, company_name, website, product_sold, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, 'PENDING', ?, ?)
        """,
        (lead_id, company_name, website, product_sold, now, now)
    )
    conn.commit()
    conn.close()
    return {
        "id": lead_id,
        "company_name": company_name,
        "website": website,
        "product_sold": product_sold,
        "status": "PENDING"
    }

def update_lead_status(lead_id: str, status: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    cursor.execute(
        "UPDATE leads SET status = ?, updated_at = ? WHERE id = ?",
        (status, now, lead_id)
    )
    conn.commit()
    conn.close()

def update_lead_agent_data(lead_id: str, field_name: str, data: Any):
    """
    Updates specific agent output field (e.g. research_data, qualification_data)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    serialized_data = json.dumps(data) if data is not None else None
    
    cursor.execute(
        f"UPDATE leads SET {field_name} = ?, updated_at = ? WHERE id = ?",
        (serialized_data, now, lead_id)
    )
    conn.commit()
    conn.close()

def get_lead(lead_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
        
    lead = dict(row)
    # Deserialize JSON fields
    for field in [
        "research_data", "qualification_data", "persona_data", 
        "outreach_data", "objection_data", "crm_data", "forecast_data"
    ]:
        if lead[field]:
            try:
                lead[field] = json.loads(lead[field])
            except Exception:
                pass
    return lead

def get_all_leads() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leads ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    leads = []
    for row in rows:
        lead = dict(row)
        for field in [
            "research_data", "qualification_data", "persona_data", 
            "outreach_data", "objection_data", "crm_data", "forecast_data"
        ]:
            if lead[field]:
                try:
                    lead[field] = json.loads(lead[field])
                except Exception:
                    pass
        leads.append(lead)
    return leads

def add_agent_log(lead_id: str, agent_name: str, status: str, confidence_score: float = None, execution_time_ms: int = None, log_message: str = ""):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO agent_logs (lead_id, agent_name, status, confidence_score, execution_time_ms, log_message, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (lead_id, agent_name, status, confidence_score, execution_time_ms, log_message, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def get_agent_logs(lead_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agent_logs WHERE lead_id = ? ORDER BY timestamp ASC", (lead_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_sales_collateral(file_id: str, filename: str, file_type: str, file_size: int) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO sales_collateral (id, filename, file_type, file_size, uploaded_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (file_id, filename, file_type, file_size, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()
    return {
        "id": file_id,
        "filename": filename,
        "file_type": file_type,
        "file_size": file_size
    }

def get_all_sales_collateral() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sales_collateral ORDER BY uploaded_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_sales_collateral(file_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sales_collateral WHERE id = ?", (file_id,))
    conn.commit()
    conn.close()
