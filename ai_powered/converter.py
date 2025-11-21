import os
from huggingface_hub import InferenceClient

# Load model embedding once
# Model light-weight, create vector 384 dimensions
api_key = os.getenv("HUGGINGFACE_TOKEN", "")
client = InferenceClient(model="sentence-transformers/all-MiniLM-L6-v2", token=api_key) if api_key else None

def text_to_vector(text: str) -> list:
    """Convert text to vector embedding using HuggingFace API"""
    if not text:
        return [0.0] * 384
    
    if not client:
        raise ValueError("HUGGINGFACE_TOKEN not configured")
    
    try:
        # Use the feature_extraction method
        embedding = client.feature_extraction(text)
        
        # Convert to flat list of floats (ChromaDB requirement)
        # HuggingFace API may return numpy array or nested list
        if isinstance(embedding, list):
            # If nested list, flatten
            if isinstance(embedding[0], (list, tuple)):
                embedding = embedding[0]
        else:
            # If numpy array, convert to list
            embedding = embedding.tolist()
            if isinstance(embedding[0], (list, tuple)):
                embedding = embedding[0]
        
        # Ensure all values are floats
        return [float(x) for x in embedding]
    except Exception as e:
        raise ValueError(f"Failed to fetch embedding: {e}")

def vector_to_text(vector: list) -> str:
    if not vector or all(v == 0 for v in vector):
        return ""
    return "Reconstructed text not fully supported from vector"
