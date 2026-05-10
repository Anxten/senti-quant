"""
Test script untuk verifikasi cleanup_old_data() logic
Jalankan: python test_cleanup.py
"""
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# Load env vars
load_dotenv()

from src.data.database import init_db, SessionLocal
from src.data.crud import cleanup_old_data

# Init database
init_db()
db = SessionLocal()

print("=" * 60)
print("🔍 VERIFIKASI DATA SEBELUM CLEANUP")
print("=" * 60)

# Hitung cutoff (30 hari lalu)
cutoff = datetime.now(timezone.utc) - timedelta(days=30)
print(f"\n📅 Cutoff date: {cutoff}")
print(f"📅 Hari ini: {datetime.now(timezone.utc)}")

# Query data lama
from src.data.models import Article, SentimentLog

old_articles = db.query(Article).filter(Article.scraped_at < cutoff).all()
print(f"\n📊 Artikel lebih tua dari 30 hari: {len(old_articles)}")

if old_articles:
    print(f"   → Artikel tertua: {old_articles[0].scraped_at} | {old_articles[0].title[:50]}")
    print(f"   → Artikel terbaru (di bawah 30 hari): {old_articles[-1].scraped_at} | {old_articles[-1].title[:50]}")

old_logs = (
    db.query(SentimentLog)
    .join(Article, SentimentLog.article_id == Article.id)
    .filter(Article.scraped_at < cutoff)
    .all()
)
print(f"📊 SentimentLog untuk artikel lama: {len(old_logs)}")

print("\n" + "=" * 60)
print("🧹 MENJALANKAN CLEANUP")
print("=" * 60)

result = cleanup_old_data(db, retention_days=30)

print(f"\n✅ Cleanup Result:")
for key, value in result.items():
    print(f"   {key}: {value}")

print("\n" + "=" * 60)
print("🔍 VERIFIKASI DATA SETELAH CLEANUP")
print("=" * 60)

old_articles_after = db.query(Article).filter(Article.scraped_at < cutoff).all()
print(f"\n📊 Artikel lebih tua dari 30 hari (setelah): {len(old_articles_after)}")

print("\n✅ Test selesai!")
db.close()
