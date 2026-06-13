import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from app.db import (
    save_sales_collateral, 
    get_all_sales_collateral, 
    delete_sales_collateral
)
from app.vector_db import add_playbook_document, delete_playbook_by_source

router = APIRouter()

def split_text_into_chunks(text: str, chunk_size: int = 1500, overlap: int = 200) -> List[str]:
    """
    Splits text content into character-based overlapping chunks.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

@router.post("/upload")
async def upload_collateral(file: UploadFile = File(...)):
    """
    Ingests text/markdown sales collateral, chunks it, and indexes it in ChromaDB for RAG context retrieval.
    """
    # Restrict to text and markdown for reliability
    filename = file.filename
    if not (filename.endswith(".txt") or filename.endswith(".md") or filename.endswith(".json")):
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file format. Please upload plain text (.txt) or markdown (.md) documents."
        )
        
    try:
        content_bytes = await file.read()
        content = content_bytes.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse text encoding: {str(e)}")
        
    if len(content.strip()) == 0:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
        
    file_id = str(uuid.uuid4())
    file_size = len(content_bytes)
    
    # Save metadata in SQLite
    metadata = save_sales_collateral(
        file_id=file_id,
        filename=filename,
        file_type=filename.split(".")[-1].upper(),
        file_size=file_size
    )
    
    # Chunk and Index in ChromaDB
    chunks = split_text_into_chunks(content)
    print(f"[RAG Ingestion] Indexing {filename} - Split into {len(chunks)} chunks.")
    
    for i, chunk in enumerate(chunks):
        chunk_id = f"{file_id}_chunk_{i}"
        add_playbook_document(
            doc_id=chunk_id,
            content=chunk,
            filename=filename,
            chunk_index=i
        )
        
    return {
        "success": True,
        "message": f"Successfully uploaded and indexed '{filename}' ({len(chunks)} vectors created).",
        "file": metadata
    }

@router.get("/")
def list_collateral():
    """
    Lists all uploaded sales playbooks metadata.
    """
    return get_all_sales_collateral()

@router.delete("/{file_id}")
def delete_collateral(file_id: str):
    """
    Deletes sales collateral, clearing its database record and ChromaDB vectors.
    """
    # Fetch list to identify file name
    all_files = get_all_sales_collateral()
    target_file = next((f for f in all_files if f["id"] == file_id), None)
    
    if not target_file:
        raise HTTPException(status_code=404, detail="Sales collateral file not found.")
        
    filename = target_file["filename"]
    
    # Delete from vector db
    delete_playbook_by_source(filename)
    
    # Delete from SQLITE
    delete_sales_collateral(file_id)
    
    return {
        "success": True,
        "message": f"Successfully deleted '{filename}' and all its indexing vectors."
    }
