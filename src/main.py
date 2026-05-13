import asyncio
import json
import logging
import os
from src.data.database import init_db, get_db
from src.data.scraper import parse_rss_items_directly
from src.data.crud import save_article, get_unprocessed_articles, save_sentiment_log, cleanup_old_data
from src.analysis.sentiment import TruthEngineAI
from src.bot.summary_broadcaster import broadcast_summary

# Setup Logging Profesional
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(module)s] - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_pipeline():
    """
    Pipeline Utama Senti-Quant:
    1. Pastikan Tabel Database Siap
    2. Ekstraksi Data Berita (Async Scraping)
    3. Simpan ke Database (Load)
    4. Analisis Sentimen dengan AI (Truth Engine)
    """
    logger.info("🚀 Memulai Senti-Quant Pipeline (Data Ingestion & AI Analysis)...")
    
    # 1. Inisialisasi Database (Aman dieksekusi berkali-kali)
    init_db()
    
    # 2. Daftar "Mata Air" Berita Finansial (RSS Feeds)
    # Menggunakan Google News aggregator untuk menghindari WAF/Cloudflare blocking
    rss_sources = [
        "https://news.google.com/rss/search?q=saham+OR+bursa+efek+OR+IHSG+OR+emiten+when:1d&hl=id&gl=ID&ceid=ID:id",
    ]
    
    # 3. Extract artikel langsung dari RSS items (tidak perlu scraping HTML lagi)
    # Google News RSS sudah berisi title, description, link, pubDate
    logger.info("📰 Mengekstrak artikel dari RSS feed items...")
    articles = parse_rss_items_directly(rss_sources)
    logger.info(f"✅ Berhasil mengekstrak {len(articles)} artikel dari RSS.")
    
    # Handle case where RSS fetch fails (e.g., blocked by Cloudflare in GitHub Actions)
    if len(articles) == 0:
        logger.warning("⚠️ PERINGATAN: Tidak ada artikel yang diektrak dari RSS feeds!")
        logger.warning("Penyebab: RSS feeds mungkin diblokir (Cloudflare/WAF), redirect, atau tidak tersedia.")
        logger.info("Pipeline akan dilewati untuk run ini. Akan dicoba ulang pada run berikutnya.")
        return  # Exit gracefully instead of failing

    logger.info(f"Sample extracted content: {articles[0].content[:100]}")

    # 3. Load (Saving to DB)
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # Simpan artikel
        for item in articles:
            save_article(db, item)
            
        # --- FASE 2: AI SENTIMENT ANALYSIS ---
        logger.info("🔍 Memulai Fase AI: Analisis Sentimen (Truth Engine)...")
        
        unprocessed_articles = get_unprocessed_articles(db, limit=100)
        
        if not unprocessed_articles:
            logger.info("✅ Semua artikel sudah dianalisis. Tidak ada antrian baru.")
        else:
            # Panggil model AI HANYA JIKA ada artikel yang harus dianalisis
            # Ini menghemat memory jika tidak ada data baru
            ai_engine = TruthEngineAI()
            
            for article in unprocessed_articles:
                logger.info(f"Menganalisis: {article.title[:40]}...")
                
                # Ambil credibility score dari sumber artikel
                source_credibility = article.source.credibility_score
                
                # Eksekusi AI dengan credibility score
                analysis_result = ai_engine.analyze(article.content, source_credibility)
                
                # Simpan ke Database
                save_sentiment_log(db, article.id, analysis_result)
                
        # --- FASE 3: RETENTION CLEANUP ---
        retention_days_raw = os.getenv("RETENTION_DAYS", "30")
        try:
            retention_days = int(retention_days_raw)
        except ValueError:
            logger.warning("⚠️ RETENTION_DAYS tidak valid (%s). Fallback ke 30 hari.", retention_days_raw)
            retention_days = 30

        cleanup_result = cleanup_old_data(db, retention_days=retention_days)
        logger.info("🧾 Ringkasan cleanup: %s", cleanup_result)
        logger.info(
            "PIPELINE_CLEANUP_METRICS=%s",
            json.dumps(cleanup_result, ensure_ascii=False),
        )

        # --- FASE 4: TELEGRAM SUMMARY BROADCAST ---
        logger.info("📢 Memulai Fase Broadcast: Mengirim ringkasan ke Telegram...")
        broadcast_summary(db)

        logger.info("🏁 Pipeline Selesai Secara Keseluruhan.")
        
    finally:
        if db:
            db.close()  # Tutup koneksi agar server tidak berat

if __name__ == "__main__":
    # Menjalankan fungsi async utama
    asyncio.run(run_pipeline())
