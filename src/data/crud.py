from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
import hashlib
from src.data.models import Article, NewsSource, SentimentLog
from src.data.scraper import ScrapedData
from src.config.credibility import get_credibility
import logging

logger = logging.getLogger(__name__)

def get_or_create_source(db: Session, domain: str) -> NewsSource:
    """
    Cek apakah sumber berita (misal: cnbc.com) sudah ada.
    Jika belum, buat baru dengan credibility score dari config.
    Jika sudah, kembalikan ID-nya.
    """
    source = db.query(NewsSource).filter(NewsSource.domain == domain).first()
    if not source:
        # Ambil credibility dari config
        credibility = get_credibility(domain)
        
        logger.info(f"🆕 Sumber baru terdeteksi: {domain} (Credibility: {credibility:.2f})")
        source = NewsSource(
            domain=domain, 
            name=domain, 
            credibility_score=credibility,
            is_trusted=(credibility >= 0.75)
        )
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
        # 2a. Dedup Level-2: Normalisasi judul (lowercase, hapus non-alphanum) dan cek kesamaan
        try:
            # Normalisasi judul di aplikasi
            def _normalize_title(t: str) -> str:
                import re
                s = (t or "").lower()
                s = re.sub(r'[^a-z0-9]', '', s)
                return s

            normalized = _normalize_title(data.title)
            title_hash = hashlib.md5(normalized.encode('utf-8')).hexdigest()

            # Coba normalisasi di sisi DB (Postgres regexp_replace) — jika tidak tersedia, fallback ke Python
            try:
                db_norm_expr = func.lower(func.regexp_replace(Article.title, '[^a-z0-9]', '', 'g'))
                existing_by_title = db.query(Article).filter(db_norm_expr == normalized).first()
                if existing_by_title:
                    logger.info(f"♻️ Skip duplikat judul (norm-md5={title_hash}): {data.title[:60]}...")
                    return False
            except Exception:
                # Fallback: lakukan normalisasi di sisi aplikasi dan bandingkan dengan semua judul di DB
                candidates = db.query(Article).all()
                for cand in candidates:
                    try:
                        cand_norm = _normalize_title(cand.title)
                        if cand_norm and cand_norm == normalized:
                            logger.info(f"♻️ Skip duplikat judul (norm-md5={title_hash}): {data.title[:60]}...")
                            return False
                    except Exception:
                        continue
        except Exception:
            # Jika ada error tak terduga saat proses normalisasi/cek, fallback ke pengecekan URL
            logger.debug("⚠️ Normalized title check mengalami error; fallback ke pengecekan URL saja.")
        # 2b. Cek apakah URL sudah pernah discrape (Idempotency)
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
            source_credibility=analysis_result.get("source_credibility", 0.5),
            noise_probability=analysis_result.get("noise_probability", 0.0),
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


def cleanup_old_data(db: Session, retention_days: int = 30) -> dict:
    """
    Menghapus data lama untuk menjaga kapasitas database tetap stabil.

    Strategi:
    1. Hapus sentiment_logs yang terkait artikel lama
    2. Hapus articles lama berdasarkan scraped_at

    Return dict untuk logging observabilitas pipeline.
    """
    try:
        if retention_days <= 0:
            retention_days = 30

        cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)

        old_article_ids = db.query(Article.id).filter(Article.scraped_at < cutoff)

        deleted_logs = (
            db.query(SentimentLog)
            .filter(SentimentLog.article_id.in_(old_article_ids))
            .delete(synchronize_session=False)
        )

        deleted_articles = (
            db.query(Article)
            .filter(Article.scraped_at < cutoff)
            .delete(synchronize_session=False)
        )

        db.commit()

        logger.info(
            "🧹 Retention cleanup selesai | Hari: %s | SentimentLog terhapus: %s | Article terhapus: %s",
            retention_days,
            deleted_logs,
            deleted_articles,
        )

        return {
            "retention_days": retention_days,
            "deleted_sentiment_logs": deleted_logs,
            "deleted_articles": deleted_articles,
        }

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Gagal menjalankan retention cleanup: {e}")
        return {
            "retention_days": retention_days,
            "deleted_sentiment_logs": 0,
            "deleted_articles": 0,
            "error": str(e),
        }
