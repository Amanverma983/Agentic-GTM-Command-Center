import os
import chromadb
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings
import google.generativeai as genai
from app.config import settings
from typing import List, Dict, Any

class GeminiEmbeddingFunction(EmbeddingFunction):
    def __init__(self, api_key: str):
        self.api_key = api_key
        if api_key:
            genai.configure(api_key=api_key)

    def __call__(self, input: Documents) -> Embeddings:
        if not self.api_key:
            # Generate mock embeddings (768 dimensions)
            return [self._mock_embedding(doc) for doc in input]
        try:
            # In ChromaDB, input is a list of strings
            embeddings = []
            for text in input:
                # Truncate text if too long
                truncated_text = text[:8000]
                response = genai.embed_content(
                    model="models/text-embedding-004",
                    contents=truncated_text,
                    task_type="RETRIEVAL_DOCUMENT"
                )
                embeddings.append(response['embedding'])
            return embeddings
        except Exception as e:
            print(f"ChromaDB Gemini embedding error: {e}. Falling back to mock embeddings.")
            return [self._mock_embedding(doc) for doc in input]

    def _mock_embedding(self, doc: str) -> List[float]:
        # Simple deterministic float array based on word characters
        # so same string gets same mock embedding
        emb = [0.0] * 768
        for i, char in enumerate(doc[:768]):
            emb[i] = ord(char) / 255.0
        # Pad with 0.1s
        for i in range(len(doc[:768]), 768):
            emb[i] = (i % 10) / 100.0
        return emb

# Initialize ChromaDB Client
# Persistent Client saves databases to settings.chroma_db_path
os.makedirs(settings.chroma_db_path, exist_ok=True)
chroma_client = chromadb.PersistentClient(path=settings.chroma_db_path)

# Initialize Embedding Function
emb_fn = GeminiEmbeddingFunction(api_key=settings.gemini_api_key)

# Get or create collection
collection = chroma_client.get_or_create_collection(
    name="sales_playbooks",
    embedding_function=emb_fn,
    metadata={"hnsw:space": "cosine"}
)

def add_playbook_document(doc_id: str, content: str, filename: str, chunk_index: int):
    """
    Splits text content and adds it to the ChromaDB vector database
    """
    collection.add(
        ids=[doc_id],
        documents=[content],
        metadatas=[{"source": filename, "chunk": chunk_index}]
    )

def query_sales_context(query_text: str, n_results: int = 3) -> List[Dict[str, Any]]:
    """
    Queries ChromaDB collection for semantic context matching the prompt
    """
    if collection.count() == 0:
        return []
        
    try:
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        contexts = []
        if results and 'documents' in results and results['documents']:
            docs = results['documents'][0]
            metas = results['metadatas'][0] if 'metadatas' in results else [{}] * len(docs)
            for doc, meta in zip(docs, metas):
                contexts.append({
                    "content": doc,
                    "source": meta.get("source", "Unknown"),
                    "chunk": meta.get("chunk", 0)
                })
        return contexts
    except Exception as e:
        print(f"Error querying ChromaDB: {e}")
        return []

def delete_playbook_by_source(filename: str):
    """
    Removes all chunks corresponding to a source file from vector store
    """
    try:
        collection.delete(
            where={"source": filename}
        )
    except Exception as e:
        print(f"Error deleting from ChromaDB: {e}")
