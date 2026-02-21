from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.data.models import Article, NewsSource
from src.data.scraper import ScrapedData
import logging

logger = logging.getLogger(__name__)

def get_or_create_source(db: Session, domain: str) -> NewsSource:
    """
    Cek apakah sumber berita (misal: cnbc.com) sudah ada.
    Jika belum, buat baru. Jika sudah, kembalikan ID-nya.
    """
    source = db.query(NewsSource).filter(NewsSource.domain == domain).first()
    if not source:
        logger.info(f"🆕 Sumber baru terdeteksi: {domain}")
        source = NewsSource(domain=domain, name=domain, is_trusted=False)
        db.add(source)
        db.commit()
        db.refresh(source)
    return source

def save_article(db: Session, data: ScrapedData) -> bool:
    """
    Menyimpan artikel ke database.
    Return: True jika berhasil disimpan, False jika duplikat/gagal.
    """
    try:
        # 1. Pastikan Sumber Berita ada
        source = get_or_create_source(db, data.source_domain)
        
        # 2. Cek apakah URL sudah pernah discrape (Idempotency)
        existing_article = db.query(Article).filter(Article.url == data.url).first()
        if existing_article:
            logger.info(f"♻️ Skip duplikat: {data.title[:30]}...")
            return False

        # 3. Simpan Artikel Baru
        new_article = Article(
            source_id=source.id,
            url=data.url,
            title=data.title,
            content=data.content,
            # published_at bisa diparsing lebih lanjut nanti
        )
        
        db.add(new_article)
        db.commit()
        logger.info(f"💾 Tersimpan: {data.title[:30]}...")
        return True

    except IntegrityError:
        db.rollback()
        logger.warning(f"⚠️ Integrity Error pada {data.url}")
        return False
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Database Error: {e}")
        return False
