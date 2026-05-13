"""
Summary Broadcaster untuk Telegram
Mengirim ringkasan berita 12 jam terakhir dengan sentimen POSITIVE/NEGATIVE
ke group Telegram menggunakan Telegram Bot API.
"""

import logging
import requests
import os
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from src.data.models import Article, SentimentLog, NewsSource

logger = logging.getLogger(__name__)


def broadcast_summary(db: Session) -> bool:
    """
    Query artikel 12 jam terakhir, filter POSITIVE/NEGATIVE, sort by integrity,
    format jadi Telegram message, dan kirim.
    
    Args:
        db: Database session
        
    Returns:
        True jika berhasil kirim, False jika gagal atau tidak ada data
    """
    try:
        # 1. Tentukan waktu cutoff (12 jam terakhir)
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=12)
        
        # 2. Query artikel + sentiment log dari 12 jam terakhir
        articles_with_sentiment = (
            db.query(Article, SentimentLog, NewsSource)
            .join(SentimentLog, Article.id == SentimentLog.article_id)
            .join(NewsSource, Article.source_id == NewsSource.id)
            .filter(
                and_(
                    Article.scraped_at >= cutoff_time,
                    SentimentLog.sentiment_label.in_(["POSITIVE", "NEGATIVE"])
                )
            )
            .all()
        )
        
        if not articles_with_sentiment:
            logger.info("ℹ️ Tidak ada berita POSITIVE/NEGATIVE dalam 12 jam terakhir. Skip broadcast.")
            return False
        
        # 3. Sort by absolute integrity_score (tertinggi duluan)
        sorted_articles = sorted(
            articles_with_sentiment,
            key=lambda x: abs(x[1].integrity_score),
            reverse=True
        )
        
        # 4. Ambil top 5
        top_articles = sorted_articles[:5]
        
        logger.info(f"📊 Top {len(top_articles)} artikel akan disiarkan ke Telegram")
        
        # 5. Format pesan Markdown/HTML untuk Telegram
        message_lines = [
            "📰 <b>Senti-Quant Market Summary (12 jam)</b>",
            "",
        ]
        
        for idx, (article, sentiment, source) in enumerate(top_articles, 1):
            # Tentukan emoji dan warna berdasarkan sentiment
            emoji = "📈" if sentiment.sentiment_label == "POSITIVE" else "📉"
            sentiment_text = sentiment.sentiment_label
            
            # Format integrity score dengan 2 desimal
            integrity = sentiment.integrity_score
            integrity_display = f"{integrity:+.3f}" if integrity != 0 else "0.000"
            
            # Potong judul jika terlalu panjang
            title = article.title[:60]
            if len(article.title) > 60:
                title += "…"
            
            # Buat line dengan format: emoji + title + source + score
            line = (
                f"{emoji} <b>{title}</b>\n"
                f"   Sumber: {source.domain} | Integritas: {integrity_display}"
            )
            message_lines.append(line)
            message_lines.append("")
        
        # 6. Tambah footer
        message_lines.append("---")
        message_lines.append(f"⏰ Update: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        full_message = "\n".join(message_lines)
        
        # 7. Kirim ke Telegram
        success = _send_telegram_message(full_message)
        
        if success:
            logger.info(f"✅ Broadcast summary berhasil dikirim ({len(top_articles)} berita)")
            return True
        else:
            logger.warning("⚠️ Broadcast summary gagal dikirim")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error saat broadcast summary: {e}")
        return False


def _send_telegram_message(message: str) -> bool:
    """
    Kirim pesan ke Telegram menggunakan Bot API.
    
    Args:
        message: Teks pesan (Markdown/HTML format)
        
    Returns:
        True jika berhasil, False jika gagal
    """
    try:
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not bot_token or not chat_id:
            logger.warning("⚠️ TELEGRAM_BOT_TOKEN atau TELEGRAM_CHAT_ID tidak tersedia")
            return False
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            logger.debug("📤 Telegram API response: OK")
            return True
        else:
            logger.warning(f"⚠️ Telegram API error {response.status_code}: {response.text[:100]}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Network error saat kirim Telegram: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error dalam _send_telegram_message: {e}")
        return False
