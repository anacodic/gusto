"""
Embedding and vector operations using OpenAI API.
"""
from typing import List, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
from config import OPENAI_API_KEY

# Global OpenAI client instance
_openai_client: Optional[OpenAI] = None

# OpenAI embedding model - text-embedding-3-small (1536 dimensions)
EMBEDDING_MODEL = "text-embedding-3-small"


def get_openai_client() -> OpenAI:
    """Get or initialize the OpenAI client."""
    global _openai_client
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not set. Please set it in your .env file.")
    if _openai_client is None:
        _openai_client = OpenAI(api_key=OPENAI_API_KEY)
    return _openai_client


def get_embedding_model():
    """
    Compatibility function - returns OpenAI client for backward compatibility.
    Note: OpenAI embeddings are API-based, not a local model.
    """
    return get_openai_client()


def embed_text(text: str) -> List[float]:
    """
    Generate embedding vector for text using OpenAI API.
    
    Args:
        text: Text to embed
        
    Returns:
        List of floats representing the embedding vector (1536 dimensions)
    """
    if not text or not text.strip():
        # Return zero vector if text is empty
        return [0.0] * 1536
    
    client = get_openai_client()
    
    try:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text.strip()
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"[ERROR] Failed to generate embedding: {e}")
        # Return zero vector on error
        return [0.0] * 1536


def calculate_cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    if not vec1 or not vec2:
        return 0.0
    v1 = np.array(vec1).reshape(1, -1)
    v2 = np.array(vec2).reshape(1, -1)
    return float(cosine_similarity(v1, v2)[0][0])


def combine_vectors(primary: List[float], secondary: List[float], secondary_weight: float = 0.35) -> List[float]:
    """Combine two vectors with weighted average."""
    if not primary:
        return secondary or [0.0] * 6
    if not secondary:
        return primary
    
    primary_weight = 1.0 - secondary_weight
    combined = []
    for p, s in zip(primary, secondary):
        combined.append(p * primary_weight + s * secondary_weight)
    return combined


def normalize_vector(vec: List[float]) -> List[float]:
    """Normalize a vector to unit length."""
    if not vec:
        return vec
    
    magnitude = sum(x * x for x in vec) ** 0.5
    if magnitude == 0:
        return vec
    
    return [x / magnitude for x in vec]

