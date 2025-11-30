"""
SQLAlchemy models for database tables.
Maps to existing PostgreSQL database schema (shared with Java backend).
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from pgvector.sqlalchemy import Vector
from db import Base
from datetime import datetime


class Product(Base):
    """
    Product model mapping to 'products' table in PostgreSQL.
    Represents wine products in the database.
    
    This model maps to the existing table created by Java backend.
    Excludes audit fields (created_by, approve_by, created_at, updated_at) from API responses.
    """
    __tablename__ = "products"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    category_id = Column(Integer, nullable=True)
    brand_id = Column(Integer, nullable=True)
    
    # Basic product info
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=True)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    images = Column(String(500), nullable=True)
    status = Column(Integer, nullable=True)  # 0=inactive, 1=active
    
    # Wine-specific fields
    country_of_production = Column(String(100), nullable=True)
    grape_variety = Column(String(100), nullable=True)
    concentration = Column(Float, nullable=True)  # alcohol percentage
    production_area = Column(String(100), nullable=True)  # region
    capacity = Column(Integer, nullable=True)  # ml
    
    # Storage instructions
    ideal_temperature = Column(String(100), nullable=True)
    humidity = Column(String(100), nullable=True)
    avoid_light = Column(String(100), nullable=True)
    place_the_bottle_horizontally = Column(String(100), nullable=True)
    avoid_vibration = Column(String(100), nullable=True)
    opened_wine = Column(String(100), nullable=True)
    use_wine_cabinet = Column(String(100), nullable=True)
    
    # Audit fields (not returned in API responses)
    created_by = Column(String(100), nullable=True)
    approved_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    
    # Vector embedding for semantic search (384 dimensions for all-MiniLM-L6-v2)
    description_vector = Column(Vector(384), nullable=True)
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization (excludes audit fields)"""
        return {
            "id": self.id,
            "category_id": self.category_id,
            "brand_id": self.brand_id,
            "name": self.name,
            "slug": self.slug,
            "price": self.price,
            "description": self.description,
            "images": self.images,
            "status": self.status,
            "country_of_production": self.country_of_production,
            "grape_variety": self.grape_variety,
            "concentration": self.concentration,
            "production_area": self.production_area,
            "capacity": self.capacity,
            "ideal_temperature": self.ideal_temperature,
            "humidity": self.humidity,
            "avoid_light": self.avoid_light,
            "place_the_bottle_horizontally": self.place_the_bottle_horizontally,
            "avoid_vibration": self.avoid_vibration,
            "opened_wine": self.opened_wine,
            "use_wine_cabinet": self.use_wine_cabinet
        }


# If you have other tables, add them here
# class Category(Base):
#     __tablename__ = "category"
#     id = Column(Integer, primary_key=True)
#     name = Column(String(100), nullable=False)
