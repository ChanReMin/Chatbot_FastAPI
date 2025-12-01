"""
FastAPI router for embedding generation.
API endpoint for Java backend to trigger embedding generation for specific products.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_write_db
from models import Product
from schemas import EmbeddingRequest, EmbeddingResponse
from ai_powered.converter import text_to_vector

router = APIRouter(
    prefix="/api",
    tags=["Embedding Generation"]
)


@router.post("/embedding", response_model=EmbeddingResponse)
async def generate_embedding(
    request: EmbeddingRequest,
    db: Session = Depends(get_write_db)
):
    """
    Generate and update embedding vector for a specific product.
    
    Designed to be called by Java backend after creating/updating products.
    
    Args:
        request: EmbeddingRequest with product id
        db: Write database session
    
    Returns:
        EmbeddingResponse with status and id or error message
    """
    try:
        # 1. Truy xuất sản phẩm theo id
        product = db.query(Product).filter(Product.id == request.id).first()
        
        if not product:
            return EmbeddingResponse(
                status="error",
                message=f"Product with id {request.id} not found"
            )
        
        # 2. Kiểm tra description
        if not product.description or product.description.strip() == "":
            return EmbeddingResponse(
                status="error",
                message=f"Product {request.id} has no description to generate embedding"
            )
        
        # 3. Tạo vector embedding từ description
        try:
            vector = text_to_vector(product.description)
            
            # Validate vector dimensions (should match model output: 384 for all-MiniLM-L6-v2)
            expected_dim = 384
            if not vector or len(vector) != expected_dim:
                return EmbeddingResponse(
                    status="error",
                    message=f"Failed to generate valid embedding vector (expected {expected_dim} dimensions, got {len(vector) if vector else 0})"
                )
        except Exception as e:
            return EmbeddingResponse(
                status="error",
                message=f"Embedding generation failed: {str(e)}"
            )
        
        # 4. Cập nhật description_vector trong database
        try:
            product.description_vector = vector
            db.commit()
            db.refresh(product)
        except Exception as e:
            db.rollback()
            return EmbeddingResponse(
                status="error",
                message=f"Database update failed: {str(e)}"
            )
        
        # 5. Trả về success
        return EmbeddingResponse(
            status="success",
            id=request.id
        )
        
    except Exception as e:
        # Catch-all exception handler
        db.rollback()
        return EmbeddingResponse(
            status="error",
            message=f"Unexpected error: {str(e)}"
        )
