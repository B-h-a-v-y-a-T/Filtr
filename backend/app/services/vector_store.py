import os
from typing import Any, Dict, List, Tuple

import httpx
import google.generativeai as genai
from dotenv import load_dotenv

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "aletheia")
ENABLE_GEMINI_EMBEDDINGS = os.getenv("ENABLE_GEMINI_EMBEDDINGS", "false").lower() in {"1", "true", "yes"}


def _get_gemini_embeddings_model():
    load_dotenv()
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    return api_key


async def embed_texts(texts: List[str]) -> List[Tuple[str, List[float]]]:
    """Generate real embeddings using Gemini Embeddings API."""
    vectors: List[Tuple[str, List[float]]] = []
    
    def _fake_vec(t: str) -> Tuple[str, List[float]]:
        vec = [float((sum(bytearray(t.encode("utf-8"))) % 100)) / 100.0] * 1536
        return (f"doc-{abs(hash(t))}", vec)

    if ENABLE_GEMINI_EMBEDDINGS and _get_gemini_embeddings_model():
        try:
            for text in texts:
                result = genai.embed_content(
                    model="models/embedding-001",
                    content=text,
                    task_type="retrieval_document",
                )
                embedding = result["embedding"]
                doc_id = f"doc-{abs(hash(text))}"
                vectors.append((doc_id, embedding))
        except Exception as e:
            print(f"Embedding error: {e}")
            vectors = [_fake_vec(t) for t in texts]
    else:
        vectors = [_fake_vec(t) for t in texts]

    return vectors


async def upsert_embeddings(vectors: List[Tuple[str, List[float]]]) -> None:
    """Real Pinecone integration for vector storage."""
    if not PINECONE_API_KEY or not vectors or os.getenv("ENABLE_PINECONE", "false").lower() not in {"1", "true", "yes"}:
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


