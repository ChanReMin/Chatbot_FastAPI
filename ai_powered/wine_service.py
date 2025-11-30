"""
Wine Search Service Layer
Extracted from router to eliminate internal HTTP calls and reduce latency.
"""
from typing import List, Dict
from sqlalchemy.orm import Session

from models import Product
from ai_powered.converter import text_to_vector


def search_wines_service(query: str, db: Session) -> List[Dict]:
    """
    Search wine products using semantic similarity with pgvector.
    
    Args:
        query: Search query text (e.g., "rượu vang đỏ Pháp ngọt")
        db: SQLAlchemy database session
    
    Returns:
        List[Dict]: List of product dictionaries matching the query.
                    Returns empty list if no products found or on error.
    
    Note:
        This function MUST return List[Dict] to maintain compatibility
        with existing chatbot logic that uses dict.get() operations.
    """
    if not query or not query.strip():
        return []
    
    try:
        # Generate embedding vector from query text
        query_vector = text_to_vector(query)
        
        if not query_vector or len(query_vector) != 384:
            print(f"[WINE_SERVICE ERROR] Invalid embedding vector for query: {query}")
            return []
        
        # Query database using pgvector cosine similarity
        products = (
            db.query(Product)
            .filter(Product.description_vector.isnot(None))
            .order_by(Product.description_vector.cosine_distance(query_vector))
            .limit(5)
            .all()
        )
        
        # Convert SQLAlchemy models to dictionaries
        # This ensures output format matches the old requests.post().json() behavior
        return [p.to_dict() for p in products]
        
    except ValueError as e:
        print(f"[WINE_SERVICE ERROR] Embedding generation failed: {e}")
        return []
    except Exception as e:
        print(f"[WINE_SERVICE ERROR] Search failed: {e}")
        return []
