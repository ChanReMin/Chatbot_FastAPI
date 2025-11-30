"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional


class SearchRequest(BaseModel):
    """Schema for wine product search request"""
    query: str = Field(..., min_length=1, description="Search query text")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "rượu vang đỏ Pháp"
            }
        }


class ProductResponse(BaseModel):
    """Schema for wine product response (excludes audit fields)"""
    id: int
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    name: str
    slug: Optional[str] = None
    price: float
    description: Optional[str] = None
    images: Optional[str] = None
    status: Optional[int] = None
    
    # Wine-specific fields
    country_of_production: Optional[str] = None
    grape_variety: Optional[str] = None
    concentration: Optional[float] = None
    production_area: Optional[str] = None
    capacity: Optional[int] = None
    
    # Storage instructions
    ideal_temperature: Optional[str] = None
    humidity: Optional[str] = None
    avoid_light: Optional[str] = None
    place_the_bottle_horizontally: Optional[str] = None
    avoid_vibration: Optional[str] = None
    opened_wine: Optional[str] = None
    use_wine_cabinet: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "category_id": 1,
                "brand_id": 5,
                "name": "Rượu vang đỏ Bordeaux 2018",
                "slug": "ruou-vang-do-bordeaux-2018",
                "description": "Rượu vang đỏ cao cấp từ vùng Bordeaux, Pháp với hương vị đậm đà",
                "price": 2500000,
                "images": "bordeaux-2018.jpg",
                "status": 1,
                "country_of_production": "Pháp",
                "grape_variety": "Cabernet Sauvignon",
                "concentration": 13.5,
                "production_area": "Bordeaux",
                "capacity": 750,
                "ideal_temperature": "16-18°C",
                "humidity": "70-80%",
                "avoid_light": "Tránh ánh sáng trực tiếp",
                "place_the_bottle_horizontally": "Đặt chai nằm ngang",
                "avoid_vibration": "Tránh rung động",
                "opened_wine": "Sử dụng trong 3-5 ngày",
                "use_wine_cabinet": "Nên bảo quản trong tủ rượu chuyên dụng"
            }
        }


class HealthCheckResponse(BaseModel):
    """Schema for health check response"""
    status: str
    message: str
    version: str
    database_connected: bool


class EmbeddingRequest(BaseModel):
    """Schema for embedding generation request from Java backend"""
    id: int = Field(..., description="Product ID", gt=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 123
            }
        }


class EmbeddingResponse(BaseModel):
    """Schema for embedding generation response"""
    status: str
    id: Optional[int] = None
    message: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "examples": {
                "success": {
                    "value": {"status": "success", "id": 123}
                },
                "error": {
                    "value": {"status": "error", "message": "Product not found"}
                }
            }
        }
