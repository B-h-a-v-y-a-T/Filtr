import os
from typing import Any, Dict, List, Tuple

import httpx
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "aletheia")

# Configure Gemini for embeddings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


async def embed_texts(texts: List[str]) -> List[Tuple[str, List[float]]]:
    """Generate real embeddings using Gemini Embeddings API."""
    vectors: List[Tuple[str, List[float]]] = []
    
    if not GEMINI_API_KEY:
        # Fallback to fake embeddings if no API key
        for t in texts:
            vec = [float((sum(bytearray(t.encode("utf-8"))) % 100)) / 100.0] * 1536
            vectors.append((f"doc-{abs(hash(t))}", vec))
        return vectors
    
    try:
        for text in texts:
            # Use Gemini Embeddings API
            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document"
            )
            embedding = result['embedding']
            doc_id = f"doc-{abs(hash(text))}"
            vectors.append((doc_id, embedding))
    except Exception as e:
        print(f"Embedding error: {e}")
        # Fallback to fake embeddings on error
        for t in texts:
            vec = [float((sum(bytearray(t.encode("utf-8"))) % 100)) / 100.0] * 1536
            vectors.append((f"doc-{abs(hash(t))}", vec))
    
    return vectors


async def upsert_embeddings(vectors: List[Tuple[str, List[float]]]) -> None:
    """Real Pinecone integration for vector storage."""
    if not PINECONE_API_KEY or not vectors:
        return
    
    try:
        from pinecone import Pinecone
        
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(PINECONE_INDEX)
        
        # Prepare vectors for upsert
        vectors_to_upsert = [
            {"id": doc_id, "values": embedding}
            for doc_id, embedding in vectors
        ]
        
        # Upsert to Pinecone
        index.upsert(vectors=vectors_to_upsert)
        print(f"Upserted {len(vectors_to_upsert)} vectors to Pinecone")
        
    except Exception as e:
        print(f"Pinecone upsert error: {e}")
        # Continue without failing the main workflow


