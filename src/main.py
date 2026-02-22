import asyncio
import logging
from src.data.database import init_db, get_db
from src.data.scraper import AsyncNewsScraper
from src.data.crud import save_article

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
    """
    logger.info("🚀 Memulai Senti-Quant Pipeline...")
    
    # 1. Inisialisasi Database (Aman dieksekusi berkali-kali)
    init_db()
    
    # Target URL (Kita pakai 3 berita CNBC Indonesia untuk testing)
    target_urls = [
        "https://www.cnbcindonesia.com/market/20230829141022-17-467053/bursa-asia-hijau-ihsg-malah-galau",
        "https://www.cnbcindonesia.com/investment/20230830103000-21-467321/waspada-penipuan-berkedok-investasi-saham",
        "https://www.cnbcindonesia.com/market/20240219080535-17-515431/ihsg-dibuka-hijau-lagi-saham-bumn-karya-berpesta"
    ]
    
    # 2. Extract (Scraping)
    scraped_results = []
    async with AsyncNewsScraper() as scraper:
        tasks = [scraper.scrape_url(url) for url in target_urls]
        results = await asyncio.gather(*tasks) # Tarik semua berita secara paralel!
        
        # Saring hasil yang tidak kosong (sukses di-scrape)
        scraped_results = [r for r in results if r is not None]

    logger.info(f"✅ Berhasil menarik {len(scraped_results)} artikel dari internet.")

    # 3. Load (Saving to DB)
    # Kita buka 1 koneksi database untuk menyimpan semua artikel
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        success_count = 0
        for item in scraped_results:
            if save_article(db, item):
                success_count += 1
        
        logger.info(f"🏁 Pipeline Selesai. {success_count} artikel baru tersimpan di Database.")
        
    finally:
        db.close() # Tutup koneksi agar server tidak berat

if __name__ == "__main__":
    # Menjalankan fungsi async utama
    asyncio.run(run_pipeline())
