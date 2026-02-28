import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.data.models import Base

load_dotenv()

# Ambil langsung URL utuh dari .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Setup Engine
# echo=False agar terminal tidak terlalu penuh dengan log SQL
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Fungsi sakti untuk membuat semua tabel"""
    print("Connecting to Cloud Database...")
    Base.metadata.create_all(bind=engine)
    print("✅ Success! Tables created in the Cloud successfully.")

def get_db():
    """Dependency untuk mengambil session database."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()