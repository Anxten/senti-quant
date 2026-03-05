import asyncio
import logging
from src.data.database import init_db, get_db
from src.data.scraper import AsyncNewsScraper, fetch_rss_links
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
    
    # 2. Daftar "Mata Air" Berita Finansial (RSS Feeds)
    rss_sources = [
        "https://www.cnbcindonesia.com/market/rss",
        "https://www.cnbcindonesia.com/investment/rss",
        # Kamu bisa tambah RSS Kontan, Bisnis.com, dll di sini nanti
    ]
    
    # 3. Sedot semua link terbaru (Bisa dapat 50 - 100 link dalam 2 detik)
    target_urls = await fetch_rss_links(rss_sources)
    logger.info(f"🎯 Total target artikel hari ini: {len(target_urls)} artikel.")
    
    # --- BATASAN AMAN (SEMENTARA) ---
    # Karena kita belum mengatur "napas" AI dan server, kita potong dulu jadi 10 
    # agar laptop dan databasemu tidak kaget. Nanti bisa kita hapus batasannya.
    target_urls = target_urls[:10]
    
    # 4. Extract (Scraping)
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
                
                # Ambil credibility score dari sumber artikel
                source_credibility = article.source.credibility_score
                
                # Eksekusi AI dengan credibility score
                analysis_result = ai_engine.analyze(article.content, source_credibility)
                
                # Simpan ke Database
                save_sentiment_log(db, article.id, analysis_result)
                
        logger.info("🏁 Pipeline Selesai Secara Keseluruhan.")
        
    finally:
        db.close()  # Tutup koneksi agar server tidak berat

if __name__ == "__main__":
    # Menjalankan fungsi async utama
    asyncio.run(run_pipeline())
