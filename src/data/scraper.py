import asyncio
import aiohttp
import logging
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime
import random

# Konfigurasi Logging agar terlihat profesional
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ScrapedData:
    """Struktur data standar untuk output scraper"""
    url: str
    title: str
    content: str
    published_at: Optional[str] = None
    source_domain: str = ""

class AsyncNewsScraper:
    """
    Engine scraping asinkronus (Non-blocking) dengan Rate Limiting.
    """
    
    def __init__(self, max_concurrent_requests: int = 5):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        self.session: Optional[aiohttp.ClientSession] = None
        # INI LAMPUNYA: Hanya izinkan maksimal 5 request jalan bersamaan
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)

    async def __aenter__(self):
        """Context Manager entry"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context Manager exit"""
        if self.session:
            await self.session.close()

    async def fetch_html(self, url: str) -> Optional[str]:
        """Mengambil raw HTML dari URL secara async dengan pengaman."""
        try:
            if not self.session:
                raise RuntimeError("Session belum diinisialisasi. Gunakan 'async with'.")

            # Minta izin ke lampu lalu lintas sebelum mengeksekusi request network
            async with self.semaphore:
                await asyncio.sleep(1) # Jeda sopan santun ke server (1 detik)
                
                async with self.session.get(url, timeout=10) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        logger.warning(f"Gagal fetch {url}: Status {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error koneksi ke {url}: {e}")
            return None

    def parse_html(self, html: str, url: str) -> Optional[ScrapedData]:
        """Logika ekstraksi data menggunakan BeautifulSoup."""
        try:
            soup = BeautifulSoup(html, 'lxml') # Untuk HTML web biasa, 'lxml' sudah benar
            
            title_tag = soup.find('h1')
            if not title_tag:
                return None
            title = title_tag.get_text(strip=True)

            paragraphs = soup.find_all('p')
            content_text = " ".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50])
            
            if len(content_text) < 200:
                logger.warning(f"Konten terlalu pendek untuk {url}, mungkin terblokir atau salah parsing.")
                return None

            domain = url.split("//")[-1].split("/")[0]

            return ScrapedData(
                url=url,
                title=title,
                content=content_text,
                source_domain=domain,
                published_at=datetime.now().isoformat()
            )

        except Exception as e:
            logger.error(f"Error parsing HTML {url}: {e}")
            return None

    async def scrape_url(self, url: str) -> Optional[ScrapedData]:
        """Fungsi utama: Fetch -> Parse"""
        html = await self.fetch_html(url)
        if html:
            return self.parse_html(html, url)
        return None

# --- FUNGSI RSS PARSER -------------------------------------------------------
async def fetch_rss_links(rss_urls: list) -> list:
    """Menyedot ratusan link artikel terbaru secara legal dari RSS Feed."""
    all_links = []
    
    async with aiohttp.ClientSession() as session:
        for url in rss_urls:
            try:
                print(f"📡 Mengambil RSS Feed dari: {url}...")
                async with session.get(url, timeout=15) as response:
                    if response.status == 200:
                        xml_data = await response.text()
                        
                        # PERBAIKAN: Gunakan "xml" murni untuk menghindari tag terpotong
                        soup = BeautifulSoup(xml_data, "xml") 
                        
                        items = soup.find_all("item")
                        
                        count = 0
                        for item in items:
                            link = item.find("link")
                            if link and link.text:
                                all_links.append(link.text.strip())
                                count += 1
                                
                        print(f"✅ Berhasil mendapatkan {count} link dari {url}")
                    else:
                        print(f"❌ Gagal akses {url} (Status: {response.status})")
            except Exception as e:
                print(f"⚠️ Error saat membaca RSS {url}: {e}")
                
    return list(set(all_links))


# --- BAGIAN TESTING (Hanya jalan jika file ini dieksekusi langsung) ---
async def test_run():
    # Contoh target: Salah satu berita saham (Kita pakai URL real untuk tes)
    # Ganti URL ini dengan berita saham random yang kamu temukan di Google
    target_urls = [
        "https://finance.yahoo.com/news/nvidia-stock-falls-market-cap-165042857.html", 
        "https://www.cnbcindonesia.com/market/20230829141022-17-467053/bursa-asia-hijau-ihsg-malah-galau" 
    ]
    
    print(f"🚀 Memulai Scraping {len(target_urls)} URL secara Async...")
    
    async with AsyncNewsScraper() as scraper:
        tasks = [scraper.scrape_url(url) for url in target_urls]
        results = await asyncio.gather(*tasks) # Jalan paralel!
        
        for res in results:
            if res:
                print("\n" + "="*40)
                print(f"✅ JUDUL: {res.title}")
                print(f"🌐 SUMBER: {res.source_domain}")
                print(f"📄 KONTEN (Depan): {res.content[:150]}...")
            else:
                print("\n❌ Gagal scrape data.")

if __name__ == "__main__":
    asyncio.run(test_run())