import asyncio
import aiohttp
import logging
import cloudscraper
import time
import re
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

    def _resolve_google_news_redirect(self, url: str) -> str:
        """Extract actual article URL from Google News article page."""
        if 'news.google.com' not in url:
            return url  # Bukan Google News URL, langsung return
        
        try:
            import requests
            # Fetch the Google News article page
            response = requests.get(
                url,
                timeout=8,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            
            if response.status_code != 200:
                logger.warning(f"Google News page returned {response.status_code}")
                return url
            
            html = response.text
            
            # Look for redirect in various formats that Google News uses
            # Method 1: Check for meta redirect
            import re
            meta_redirect = re.search(r'<meta[^>]+?http-equiv=["\']refresh["\'][^>]*?content=["\']0;url=([^"\']+)', html, re.I)
            if meta_redirect:
                redirect_url = meta_redirect.group(1)
                if 'news.google.com' not in redirect_url:
                    logger.info(f"✓ Resolved (meta redirect): {redirect_url[:70]}...")
                    return redirect_url
            
            # Method 2: Check for onclick/href in article container
            # Google News article usually has a link with href to actual article
            article_link = re.search(r'href=["\']([^"\']*?(?:cnbc|kontan|liputan|kompas|detik|bisnis|antara|finance)[^"\']*?)["\']', html, re.I)
            if article_link:
                link = article_link.group(1)
                if 'news.google.com' not in link and link.startswith('http'):
                    logger.info(f"✓ Resolved (article href): {link[:70]}...")
                    return link
            
            # Method 3: Check response history for redirect
            if response.history:
                for resp in response.history:
                    if resp.status_code in [301, 302, 303, 307, 308]:
                        location = resp.headers.get('location', '')
                        if location and 'news.google.com' not in location:
                            logger.info(f"✓ Resolved (response history): {location[:70]}...")
                            return location
            
            logger.warning(f"Could not extract article URL from Google News page")
            return url
            
        except Exception as e:
            logger.warning(f"Error resolving Google News URL: {str(e)[:60]}")
            return url

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
        """Fungsi utama: Resolve redirect (jika Google News) -> Fetch -> Parse"""
        # Jika dari Google News, resolve redirect ke artikel asli terlebih dahulu
        actual_url = self._resolve_google_news_redirect(url)
        
        html = await self.fetch_html(actual_url)
        if html:
            return self.parse_html(html, actual_url)
        return None

# --- FUNGSI RSS PARSER -------------------------------------------------------
def parse_rss_items_directly(rss_urls: list) -> list:
    """Extract article data directly from RSS items without scraping HTML."""
    articles = []
    
    scraper = cloudscraper.create_scraper()
    
    for url in rss_urls:
        try:
            print(f"📡 Mengambil RSS Feed dari: {url}...")
            time.sleep(random.uniform(0.3, 0.8))
            
            response = scraper.get(url, timeout=15)
            
            if response.status_code == 200:
                xml_data = response.text
                soup = BeautifulSoup(xml_data, "xml")
                items = soup.find_all("item")
                
                count = 0
                for item in items:
                    try:
                        title_el = item.find("title")
                        link_el = item.find("link")
                        description_el = item.find("description")
                        pubdate_el = item.find("pubDate")
                        source_el = item.find("source")
                        
                        title = title_el.text.strip() if title_el else "No title"
                        link = link_el.text.strip() if link_el else None
                        description_raw = description_el.text.strip() if description_el else ""
                        # Google News description biasanya berisi HTML (<a>, <font>, dll), jadi dibersihkan dulu.
                        description = BeautifulSoup(description_raw, "html.parser").get_text(" ", strip=True)
                        pub_date = pubdate_el.text.strip() if pubdate_el else datetime.now().isoformat()
                        
                        # Extract domain from link
                        domain = "unknown"
                        source_url = source_el.get("url", "").strip() if source_el else ""
                        source_name = source_el.text.strip() if source_el and source_el.text else ""

                        if source_url:
                            source_domain_match = re.search(r'(?:https?://)?(?:www\.)?([^/]+)', source_url)
                            if source_domain_match:
                                domain = source_domain_match.group(1)
                        elif source_name:
                            domain = source_name
                        elif link:
                            # Fallback domain dari link item
                            domain_match = re.search(r'(?:https?://)?(?:www\.)?([^/]+)', link)
                            if domain_match:
                                domain = domain_match.group(1)
                        
                        # Create ScrapedData from RSS item
                        article = ScrapedData(
                            url=link or url,
                            title=title,
                            content=description or title,  # Use description if available, else title
                            source_domain=domain,
                            published_at=pub_date
                        )
                        
                        articles.append(article)
                        count += 1
                    except Exception as e:
                        logger.warning(f"Gagal parse item: {str(e)[:50]}")
                        continue
                
                print(f"✅ Berhasil mengekstrak {count} artikel dari {url}")
            else:
                print(f"⚠️ HTTP {response.status_code} dari {url}")
                
        except Exception as e:
            print(f"⚠️ Error saat membaca RSS {url}: {str(e)[:80]}")
    
    print(f"\n📊 Total: {len(articles)} artikel diektrak langsung dari RSS items")
    return articles


def fetch_rss_links(rss_urls: list) -> list:
    """Menyedot ratusan link artikel terbaru dari RSS Feed, with error handling & Cloudflare bypass."""
    all_links = []
    successful_feeds = 0
    failed_feeds = []
    
    # Gunakan cloudscraper untuk bypass Cloudflare challenges
    scraper = cloudscraper.create_scraper()
    
    for url in rss_urls:
        try:
            print(f"📡 Mengambil RSS Feed dari: {url}...")
            time.sleep(random.uniform(0.3, 0.8))  # Sopan santun ke server
            
            response = scraper.get(url, timeout=15)
            
            if response.status_code == 200:
                xml_data = response.text
                
                # Gunakan "xml" parser untuk RSS/Atom feeds
                soup = BeautifulSoup(xml_data, "xml")
                
                items = soup.find_all("item")
                
                count = 0
                for item in items:
                    link = item.find("link")
                    if link and link.text:
                        all_links.append(link.text.strip())
                        count += 1
                        
                print(f"✅ Berhasil mendapatkan {count} link dari {url}")
                successful_feeds += 1
            else:
                print(f"⚠️ HTTP {response.status_code} dari {url} — Skipping...")
                failed_feeds.append((url, response.status_code))
        except Exception as e:
            print(f"⚠️ Error saat membaca RSS {url}: {str(e)[:80]}")
            failed_feeds.append((url, str(e)[:50]))
    
    unique_links = list(set(all_links))
    print(f"\n📊 RSS Summary: {successful_feeds} feeds OK, {len(failed_feeds)} feeds failed, {len(unique_links)} total unique links")
    
    if not unique_links:
        print("⚠️ WARNING: No RSS links fetched! Pipeline may have limited data.")
    
    return unique_links


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