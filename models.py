"""
SQLAlchemy models for database tables.
Maps to existing PostgreSQL database schema (shared with Java backend).
"""
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, Boolean
from sqlalchemy.dialects.postgresql import ARRAY
from pgvector.sqlalchemy import Vector
from db import Base


class Product(Base):
    """
    Product model mapping to 'product' table in PostgreSQL.
    
    This model maps to the existing table created by Java/Django backend.
    Make sure table name and column names match exactly.
    """
    __tablename__ = "product"  # Adjust to match your actual table name
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Product information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)  # Decimal for money
    slug = Column(String(255), unique=True, nullable=False, index=True)
    gender = Column(String(20), nullable=True)  # e.g., 'MEN', 'WOMEN', 'UNISEX'
    
    # Vector embedding for semantic search (384 dimensions for all-MiniLM-L6-v2)
    # Column name might be 'description_vector', 'embedding', etc. - adjust to match your DB
    description_vector = Column(Vector(384), nullable=True)
    
    # Optional fields - uncomment and adjust if your table has these
    # category = Column(String(100), nullable=True)
    # brand = Column(String(100), nullable=True)
    # stock_quantity = Column(Integer, default=0)
    # image_url = Column(String(500), nullable=True)
    # is_active = Column(Boolean, default=True)
    # created_at = Column(DateTime, nullable=True)
    # updated_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": float(self.price) if self.price else None,
            "slug": self.slug,
            "gender": self.gender,
        }


# If you have other tables, add them here
# class Category(Base):
#     __tablename__ = "category"
#     id = Column(Integer, primary_key=True)
#     name = Column(String(100), nullable=False)
