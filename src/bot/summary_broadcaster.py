"""
Summary Broadcaster untuk Telegram
Mengirim ringkasan berita 12 jam terakhir dengan sentimen POSITIVE/NEGATIVE
ke group Telegram menggunakan Telegram Bot API.
"""

import logging
import requests
import os
import re
from html import escape
from datetime import date, datetime, timedelta, timezone
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import holidays
from src.data.models import Article, SentimentLog, NewsSource

logger = logging.getLogger(__name__)

_INDONESIA_HOLIDAYS = holidays.ID()


def _format_sentiment_display(sentiment_label: str, integrity: float) -> str:
    """
    Map raw integrity score + sentiment label to a retail-friendly text label.

    Rules (retail-focused):
    - POSITIVE with high integrity -> [STRONG POSITIVE]
    - POSITIVE otherwise -> [POSITIVE]
    - NEGATIVE with very low integrity -> [STRONG NEGATIVE]
    - NEGATIVE moderately -> [NEGATIVE]
    - NEGATIVE mild -> [MILD NEGATIVE]
    """
    lab = (sentiment_label or "").upper()
    if lab == "POSITIVE":
        if integrity is not None and integrity >= 0.6:
            return "[STRONG POSITIVE]"
        return "[POSITIVE]"
    if lab == "NEGATIVE":
        if integrity is not None and integrity <= -0.6:
            return "[STRONG NEGATIVE]"
        if integrity is not None and integrity <= -0.15:
            return "[NEGATIVE]"
        return "[MILD NEGATIVE]"
    return f"[{lab}]"


def _should_mute_telegram_broadcast(today: date | None = None) -> bool:
    """Return True when Telegram broadcast should be muted."""
    current_day = today or date.today()
    return current_day.weekday() >= 5 or current_day in _INDONESIA_HOLIDAYS


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

        # Aggregate counts for market pulse (group by sentiment_label)
        agg = (
            db.query(SentimentLog.sentiment_label, func.count(func.distinct(SentimentLog.article_id)))
            .join(Article, SentimentLog.article_id == Article.id)
            .filter(Article.scraped_at >= cutoff_time)
            .group_by(SentimentLog.sentiment_label)
            .all()
        )

        # normalize aggregation into counters
        positive_count = 0
        negative_count = 0
        noise_count = 0
        for label, cnt in agg:
            lab = (label or "").upper()
            if lab == "POSITIVE":
                positive_count = int(cnt)
            elif lab == "NEGATIVE":
                negative_count = int(cnt)
            elif lab in ("NEUTRAL", "IRRELEVANT"):
                noise_count += int(cnt)
            else:
                # any other labels count as noise
                noise_count += int(cnt)
        
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
            f"📊 <b>Nadi Pasar:</b> 🟢 {positive_count} Positif | 🔴 {negative_count} Negatif | ⚪ {noise_count} Noise",
            "",
        ]
        
        # helper: extract 4-letter uppercase ticker-like tokens
        def _extract_ticker(title: str, content: str | None = None) -> str | None:
            """
            Extract valid stock ticker (4 uppercase letters).
            - Search in title first, then in content
            - Exclude index symbols (IHSG, LQ45) and common words
            - Return first match or None
            """
            # Blacklist: indices, common words, and abbreviations
            blacklist = {"THIS", "HTML", "HTTP", "NEWS", "IHSG", "LQ45", "WHEN", "THAT", "WITH"}
            
            # Search title first (higher priority)
            if title:
                for m in re.finditer(r"\$?\b([A-Z]{4})\b", title):
                    cand = m.group(1)
                    if cand not in blacklist:
                        return cand
            
            # If no ticker in title, search content
            if content:
                for m in re.finditer(r"\$?\b([A-Z]{4})\b", content):
                    cand = m.group(1)
                    if cand not in blacklist:
                        return cand
            
            return None

        for idx, (article, sentiment, source) in enumerate(top_articles, 1):
            # Tentukan emoji dan warna berdasarkan sentiment
            emoji = "📈" if sentiment.sentiment_label == "POSITIVE" else "📉"
            
            # Format integrity score dengan 2 desimal
            integrity = sentiment.integrity_score
            sentiment_display = _format_sentiment_display(sentiment.sentiment_label, integrity)

            # Do not truncate title anymore; show full title. Prepend detected ticker or macro label.
            raw_title = article.title or ""
            raw_content = article.content or ""
            ticker = _extract_ticker(raw_title, raw_content)
            if ticker:
                title_prefix = f"[$%s] " % ticker
            else:
                title_prefix = "[IHSG / MAKRO] "

            full_title = f"{title_prefix}{raw_title}"
            escaped_title = escape(full_title)
            escaped_url = escape(article.url, quote=True)
            
            # Buat line dengan format: bullet + clickable title + source + sentimen eksplisit
            line = (
                f"🔹 <a href=\"{escaped_url}\">{escaped_title}</a>\n"
                f"🏢 Sumber: {escape(source.domain)} | {sentiment_display}"
            )
            message_lines.append(line)
            message_lines.append("")
        
        # 6. Tambah footer
        message_lines.append("---")
        # Show timestamp in WIB (UTC+7)
        WIB = timezone(timedelta(hours=7))
        message_lines.append(f"⏰ Update: {datetime.now(WIB).strftime('%Y-%m-%d %H:%M:%S')} WIB")
        
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
        if _should_mute_telegram_broadcast():
            logger.info("Hari libur terdeteksi, menahan broadcast Telegram.")
            return False

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
