"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


class SearchRequest(BaseModel):
    """Schema for product search request"""
    query: str = Field(..., min_length=1, description="Search query text")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "áo thun nam màu xanh"
            }
        }


class ProductResponse(BaseModel):
    """Schema for product response"""
    id: int
    name: str
    description: Optional[str] = None
    price: float
    slug: str
    gender: Optional[str] = None
    
    class Config:
        from_attributes = True  # Allows SQLAlchemy model conversion
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Áo thun nam basic",
                "description": "Áo thun cotton 100% thoáng mát",
                "price": 299000,
                "slug": "ao-thun-nam-basic",
                "gender": "MEN"
            }
        }


class HealthCheckResponse(BaseModel):
    """Schema for health check response"""
    status: str
    message: str
    version: str
    database_connected: bool
