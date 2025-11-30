"""
Database connection module for PostgreSQL with pgvector support.
Supports separate READ and WRITE database connections.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================
# Read Database Configuration
# ============================================
DB_DATABASE = os.getenv("DB_DATABASE")
SPRING_DATASOURCE_WRITE_USERNAME = os.getenv("SPRING_DATASOURCE_WRITE_USERNAME")
SPRING_DATASOURCE_WRITE_PASSWORD = os.getenv("SPRING_DATASOURCE_WRITE_PASSWORD")
DB_WRITE_HOST = os.getenv("DB_WRITE_HOST")
DB_WRITE_PORT = os.getenv("DB_WRITE_PORT")

SPRING_DATASOURCE_READ_USERNAME = os.getenv("SPRING_DATASOURCE_READ_USERNAME")
SPRING_DATASOURCE_READ_PASSWORD = os.getenv("SPRING_DATASOURCE_READ_PASSWORD")
DB_READ_HOST = os.getenv("DB_READ_HOST")
DB_READ_PORT = os.getenv("DB_READ_PORT")

# ============================================
# Validate Required Environment Variables
# ============================================
required_vars = {
    "DB_DATABASE": DB_DATABASE,
    "SPRING_DATASOURCE_WRITE_USERNAME": SPRING_DATASOURCE_WRITE_USERNAME,
    "SPRING_DATASOURCE_WRITE_PASSWORD": SPRING_DATASOURCE_WRITE_PASSWORD,
    "DB_WRITE_HOST": DB_WRITE_HOST,
    "DB_WRITE_PORT": DB_WRITE_PORT,
    "SPRING_DATASOURCE_READ_USERNAME": SPRING_DATASOURCE_READ_USERNAME,
    "SPRING_DATASOURCE_READ_PASSWORD": SPRING_DATASOURCE_READ_PASSWORD,
    "DB_READ_HOST": DB_READ_HOST,
    "DB_READ_PORT": DB_READ_PORT,
}

missing_vars = [key for key, value in required_vars.items() if not value]
if missing_vars:
    raise ValueError(
        f"Missing required environment variables: {', '.join(missing_vars)}. "
        "Check your .env file."
    )

# ============================================
# Build Database URLs
# ============================================
WRITE_DB_URL = (
    f"postgresql://{SPRING_DATASOURCE_WRITE_USERNAME}:{SPRING_DATASOURCE_WRITE_PASSWORD}"
    f"@{DB_WRITE_HOST}:{DB_WRITE_PORT}/{DB_DATABASE}"
)

READ_DB_URL = (
    f"postgresql://{SPRING_DATASOURCE_READ_USERNAME}:{SPRING_DATASOURCE_READ_PASSWORD}"
    f"@{DB_READ_HOST}:{DB_READ_PORT}/{DB_DATABASE}"
)

# ============================================
# Create SQLAlchemy Engines
# ============================================
# WRITE Engine - for INSERT, UPDATE, DELETE operations
write_engine = create_engine(
    WRITE_DB_URL,
    pool_pre_ping=True,  # Verify connection before using
    pool_size=10,        # Connection pool size
    max_overflow=20,     # Max connections beyond pool_size
    echo=False           # Set True for SQL query logging (debug only)
)

# READ Engine - for SELECT operations
read_engine = create_engine(
    READ_DB_URL,
    pool_pre_ping=True,  # Verify connection before using
    pool_size=10,        # Connection pool size
    max_overflow=20,     # Max connections beyond pool_size
    echo=False           # Set True for SQL query logging (debug only)
)

# ============================================
# Create Session Factories
# ============================================
WriteSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=write_engine)
ReadSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=read_engine)

# Backward compatibility: SessionLocal defaults to WRITE
SessionLocal = WriteSessionLocal

# ============================================
# Base Class for Models
# ============================================
Base = declarative_base()

# ============================================
# FastAPI Dependencies
# ============================================
def get_write_db():
    """
    Generator function to provide WRITE database session.
    Use for INSERT, UPDATE, DELETE operations.
    
    Usage in FastAPI routes:
    
    @app.post("/products")
    def create_product(product: ProductCreate, db: Session = Depends(get_write_db)):
        new_product = Product(**product.dict())
        db.add(new_product)
        db.commit()
        return new_product
    """
    db = WriteSessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_read_db():
    """
    Generator function to provide READ database session.
    Use for SELECT operations only.
    
    Usage in FastAPI routes:
    
    @app.get("/products")
    def list_products(db: Session = Depends(get_read_db)):
        products = db.query(Product).all()
        return products
    """
    db = ReadSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Backward compatibility: get_db defaults to WRITE
def get_db():
    """
    [DEPRECATED] Legacy function for backward compatibility.
    Use get_write_db() or get_read_db() instead.
    
    This function defaults to WRITE database for safety.
    """
    return get_write_db()
