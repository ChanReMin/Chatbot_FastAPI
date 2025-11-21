"""
FastAPI router for product search using pgvector cosine similarity.
Replaces Django SearchProductAPIView functionality.

COMMENTED: This entire router is disabled until database is deployed.
Uncomment all code blocks when PostgreSQL + pgvector is ready.
"""
from fastapi import APIRouter  # , Depends, HTTPException
# from sqlalchemy.orm import Session  # COMMENTED: DB not deployed yet
# from sqlalchemy import func  # COMMENTED: DB not deployed yet
from typing import List

# from db import get_db  # COMMENTED: DB not deployed yet
# from models import Product  # COMMENTED: DB not deployed yet
# from schemas import SearchRequest, ProductResponse  # COMMENTED: DB not deployed yet
# from ai_powered.converter import text_to_vector  # COMMENTED: DB not deployed yet

router = APIRouter(
    prefix="/api/fashion",
    tags=["Fashion Search"]
)


# COMMENTED: Search endpoint disabled until DB is ready
# @router.post("/search", response_model=List[ProductResponse])
# async def search_products(
#     request: SearchRequest,
#     db: Session = Depends(get_db)
# ):
#     """
#     Search products using semantic similarity with pgvector.
#     
#     This endpoint replaces the Django SearchProductAPIView.
#     It uses cosine distance to find the 5 most similar products to the query.
#     """
#     if not request.query or not request.query.strip():
#         raise HTTPException(status_code=400, detail="Search query cannot be empty")
#     
#     try:
#         query_vector = text_to_vector(request.query)
#         
#         if not query_vector or len(query_vector) != 384:
#             raise HTTPException(
#                 status_code=500, 
#                 detail="Failed to generate valid embedding vector"
#             )
#         
#         products = (
#             db.query(Product)
#             .filter(Product.description_vector.isnot(None))
#             .order_by(Product.description_vector.cosine_distance(query_vector))
#             .limit(5)
#             .all()
#         )
#         
#         return [
#             ProductResponse(
#                 id=p.id,
#                 name=p.name,
#                 description=p.description,
#                 price=float(p.price) if p.price else 0.0,
#                 slug=p.slug,
#                 gender=p.gender
#             )
#             for p in products
#         ]
#         
#     except ValueError as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Embedding generation error: {str(e)}"
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Search error: {str(e)}"
#         )


@router.get("/search/test")
async def test_search_endpoint():
    """Test endpoint to verify router is working"""
    return {
        "status": "ok",
        "message": "Search endpoint is active (DB search disabled)",
        "usage": "POST /api/fashion/search with JSON body: {\"query\": \"your search text\"}",
        "note": "Database search is temporarily disabled until deployment"
    }
