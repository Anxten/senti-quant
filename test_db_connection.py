"""
Script untuk test koneksi database dan membuat tabel.
Jalankan: python test_db_connection.py
"""

from src.data.database import engine, init_db, SessionLocal
from src.data.models import NewsSource, Article, SentimentLog
from sqlalchemy import text

def test_connection():
    """Test koneksi ke PostgreSQL"""
    print("🔍 Testing database connection...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL!")
            print(f"📌 Version: {version[:50]}...")
            return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_create_tables():
    """Membuat semua tabel"""
    print("\n🏗️  Creating tables...")
    try:
        init_db()
        return True
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False

def test_insert_sample():
    """Test insert data sample"""
    print("\n💾 Testing insert operation...")
    try:
        db = SessionLocal()
        
        # Cek apakah sudah ada data
        existing = db.query(NewsSource).filter(NewsSource.domain == "test.com").first()
        if existing:
            print("♻️  Sample data already exists, skipping insert")
            db.close()
            return True
        
        # Insert sample source
        sample_source = NewsSource(
            domain="test.com",
            name="Test News",
            credibility_score=0.75,
            is_trusted=True
        )
        db.add(sample_source)
        db.commit()
        db.refresh(sample_source)
        
        print(f"✅ Sample data inserted! Source ID: {sample_source.id}")
        
        # Query back
        sources = db.query(NewsSource).all()
        print(f"📊 Total sources in database: {len(sources)}")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ Insert failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🛡️  SENTI-QUANT DATABASE TEST")
    print("=" * 50)
    
    # Test 1: Connection
    if not test_connection():
        print("\n⚠️  Fix connection issues first!")
        exit(1)
    
    # Test 2: Create Tables
    if not test_create_tables():
        print("\n⚠️  Fix table creation issues!")
        exit(1)
    
    # Test 3: Insert Sample
    if not test_insert_sample():
        print("\n⚠️  Fix insert issues!")
        exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED! Database is ready!")
    print("=" * 50)
