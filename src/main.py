import asyncio
import logging
from src.data.database import init_db, get_db
from src.data.scraper import AsyncNewsScraper
from src.data.crud import save_article, get_unprocessed_articles, save_sentiment_log
from src.analysis.sentiment import TruthEngineAI

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
    
    # Target URL (Kita pakai 2 berita CNBC Indonesia untuk testing)
    target_urls = [
        "https://www.cnbcindonesia.com/market/20230829141022-17-467053/bursa-asia-hijau-ihsg-malah-galau",
        "https://www.cnbcindonesia.com/investment/20230830103000-21-467321/waspada-penipuan-berkedok-investasi-saham",
    ]
    
    # 2. Extract (Scraping)
    scraped_results = []
    async with AsyncNewsScraper() as scraper:
        tasks = [scraper.scrape_url(url) for url in target_urls]
        results = await asyncio.gather(*tasks)  # Tarik semua berita secara paralel!
        
        # Saring hasil yang tidak kosong (sukses di-scrape)
        scraped_results = [r for r in results if r is not None]

    logger.info(f"✅ Berhasil menarik {len(scraped_results)} artikel dari internet.")

    # 3. Load (Saving to DB)
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # Simpan artikel
        for item in scraped_results:
            save_article(db, item)
            
        # --- FASE 2: AI SENTIMENT ANALYSIS ---
        logger.info("🔍 Memulai Fase AI: Analisis Sentimen (Truth Engine)...")
        
        unprocessed_articles = get_unprocessed_articles(db, limit=5)
        
        if not unprocessed_articles:
            logger.info("✅ Semua artikel sudah dianalisis. Tidak ada antrian baru.")
        else:
            # Panggil model AI HANYA JIKA ada artikel yang harus dianalisis
            # Ini menghemat memory jika tidak ada data baru
            ai_engine = TruthEngineAI()
            
            for article in unprocessed_articles:
                logger.info(f"Menganalisis: {article.title[:40]}...")
                
                # Eksekusi AI
                analysis_result = ai_engine.analyze(article.content)
                
                # Simpan ke Database
                save_sentiment_log(db, article.id, analysis_result)
                
        logger.info("🏁 Pipeline Selesai Secara Keseluruhan.")
        
    finally:
        db.close()  # Tutup koneksi agar server tidak berat

if __name__ == "__main__":
    # Menjalankan fungsi async utama
    asyncio.run(run_pipeline())
