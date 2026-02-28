"""
Migration script to add source_credibility and noise_probability columns
Run this once to update existing database schema
"""

from src.data.database import engine
from sqlalchemy import text

def migrate():
    print("🔄 Running database migration...")
    
    with engine.connect() as conn:
        try:
            # Add source_credibility column
            conn.execute(text("""
                ALTER TABLE sentiment_logs 
                ADD COLUMN IF NOT EXISTS source_credibility FLOAT DEFAULT 0.5
            """))
            print("✅ Added source_credibility column")
            
            # Add noise_probability column
            conn.execute(text("""
                ALTER TABLE sentiment_logs 
                ADD COLUMN IF NOT EXISTS noise_probability FLOAT DEFAULT 0.0
            """))
            print("✅ Added noise_probability column")
            
            conn.commit()
            print("🎉 Migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            conn.rollback()

if __name__ == "__main__":
    migrate()
