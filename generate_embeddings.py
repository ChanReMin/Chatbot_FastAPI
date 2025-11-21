"""
Script to generate vector embeddings for existing products.
Run once after migration to populate description_vector column.

Usage:
    python generate_embeddings.py
"""
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from db import SessionLocal
from models import Product
from ai_powered.converter import text_to_vector

# Load environment variables
load_dotenv()


def generate_embeddings():
    """Generate embeddings for all products without vectors"""
    db: Session = SessionLocal()
    
    try:
        # Get all products without embeddings but have description
        products = db.query(Product).filter(
            Product.description_vector == None,
            Product.description != None,
            Product.description != ''
        ).all()
        
        total = len(products)
        print(f"🔍 Found {total} products without embeddings\n")
        
        if total == 0:
            print("✅ All products already have embeddings!")
            return
        
        success_count = 0
        error_count = 0
        
        for idx, product in enumerate(products, 1):
            try:
                # Generate vector from description
                vector = text_to_vector(product.description)
                
                if vector and len(vector) == 384:
                    product.description_vector = vector
                    db.commit()
                    success_count += 1
                    print(f"[{idx}/{total}] ✓ {product.name[:50]}")
                else:
                    error_count += 1
                    print(f"[{idx}/{total}] ✗ {product.name[:50]} - Invalid vector")
                    
            except Exception as e:
                error_count += 1
                print(f"[{idx}/{total}] ✗ {product.name[:50]}: {e}")
                db.rollback()
        
        print(f"\n{'='*60}")
        print(f"✅ Success: {success_count}/{total}")
        print(f"❌ Errors: {error_count}/{total}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        db.close()


def test_search():
    """Test vector search after generating embeddings"""
    db: Session = SessionLocal()
    
    try:
        test_query = "áo thun nam"
        print(f"\n🧪 Testing search with query: '{test_query}'")
        
        query_vector = text_to_vector(test_query)
        
        products = (
            db.query(Product)
            .filter(Product.description_vector.isnot(None))
            .order_by(Product.description_vector.cosine_distance(query_vector))
            .limit(5)
            .all()
        )
        
        print(f"\n📊 Top 5 results:")
        for idx, p in enumerate(products, 1):
            print(f"{idx}. {p.name} - {p.price} VND")
        
        if not products:
            print("⚠️  No results found. Check if embeddings were generated correctly.")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Starting embedding generation...\n")
    generate_embeddings()
    
    # Uncomment to test search after generation
    # test_search()
    
    print("\n✅ Done!")
