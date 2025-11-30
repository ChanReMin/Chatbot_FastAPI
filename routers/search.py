"""
FastAPI router for wine product search using pgvector cosine similarity.
Semantic search for wine recommendations based on user queries.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from db import get_read_db
from schemas import SearchRequest, ProductResponse
from ai_powered.wine_service import search_wines_service

router = APIRouter(
    prefix="/api/wine",
    tags=["Wine Search"]
)


@router.post("/search", response_model=List[ProductResponse])
async def search_products(
    request: SearchRequest,
    db: Session = Depends(get_read_db)
):
    """
    Search wine products using semantic similarity with pgvector.
    
    Uses cosine distance to find the 5 most similar wine products to the query.
    Supports natural language queries like "rượu vang đỏ Pháp ngọt".
    Uses READ database connection for optimal performance.
    """
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")
    
    try:
        # Call service layer to get product dictionaries
        products_data = search_wines_service(request.query, db)
        
        # Convert dictionaries to Pydantic models for API response
        return [ProductResponse(**product) for product in products_data]
        
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Embedding generation error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search error: {str(e)}"
        )


@router.get("/search/test")
async def test_search_endpoint():
    """Test endpoint to verify router is working"""
    return {
        "status": "ok",
        "message": "Wine search endpoint is active",
        "usage": "POST /api/wine/search with JSON body: {\"query\": \"rượu vang đỏ Pháp\"}",
        "note": "Database search is enabled and ready"
    }
