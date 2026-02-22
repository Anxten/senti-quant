from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.data.models import Article, NewsSource, SentimentLog
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


def save_sentiment_log(db: Session, article_id: int, analysis_result: dict) -> bool:
    """
    Menyimpan hasil analisis AI ke tabel sentiment_logs.
    """
    try:
        # Cek apakah artikel ini sudah pernah dianalisis
        existing_log = db.query(SentimentLog).filter(SentimentLog.article_id == article_id).first()
        if existing_log:
            logger.info(f"♻️ Sentimen untuk artikel ID {article_id} sudah ada. Skip.")
            return False

        new_log = SentimentLog(
            article_id=article_id,
            sentiment_score=analysis_result.get("integrity_score", 0.0),
            sentiment_label=analysis_result.get("sentiment_label", "NEUTRAL"),
            confidence=analysis_result.get("confidence", 0.0),
            integrity_score=analysis_result.get("integrity_score", 0.0)
        )
        
        db.add(new_log)
        db.commit()
        logger.info(f"🧠 Sentimen Tersimpan -> Label: {new_log.sentiment_label} | Integritas: {new_log.integrity_score:.2f}")
        return True

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Gagal menyimpan sentimen: {e}")
        return False

def get_unprocessed_articles(db: Session, limit: int = 10):
    """
    Mengambil artikel yang belum memiliki data di tabel sentiment_logs.
    """
    # Mencari artikel yang ID-nya TIDAK ADA di tabel sentiment_logs
    subquery = db.query(SentimentLog.article_id)
    articles = db.query(Article).filter(Article.id.notin_(subquery)).limit(limit).all()
    return articles
