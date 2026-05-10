# Senti-Quant - Project State & Architecture
**Current Status:** Stabil di tahap 31 Commit

## 1. Project Overview
Senti-Quant (The Truth Engine) adalah sebuah platform financial sentiment analysis berskala Enterprise yang dirancang untuk menjadi filter integritas bagi investor ritel di pasar modal Indonesia. Aplikasi ini secara otomatis menyedot ratusan berita finansial terbaru, menyaring kebisingan (noise) atau narasi clickbait, dan memberikan sinyal sentimen pasar yang jujur dan akurat.

Output akhir dari sistem ini adalah sebuah Dashboard Live yang menampilkan metrik sentimen (Bullish/Bearish/Neutral) dan Integrity Score dari setiap artikel, memberikan keunggulan analitik tingkat institusi kepada investor biasa untuk menghindari jebakan pump-and-dump atau FOMO.

## 2. Tech Stack & Environment
Sistem ini berjalan secara optimal di atas sistem operasi Linux Fedora, dengan teknologi utama berikut (sejak commit 37, infrastruktur telah dimigrasikan ke cloud-native):
* **Bahasa Pemrograman:** Python (berjalan di dalam venv).
* **Data Ingestion (Scraping):** aiohttp & asyncio (untuk asynchronous request), BeautifulSoup (dengan parser lxml khusus mode "xml" untuk RSS).
* **AI & NLP Engine:** transformers (Hugging Face Pipeline), torch.
* **Pre-trained Model:** mdhugol/indonesia-bert-sentiment-classification.
* **Database:** Neon PostgreSQL (Cloud/Serverless) diakses menggunakan SQLAlchemy (ORM).
* **Frontend/UI:** Streamlit, pandas, plotly (untuk visualisasi Donut Chart dan Histogram interaktif).
* **Automation:** GitHub Actions (Cloud CI/CD dengan schedule cron di cloud, menggantikan laptop-dependent cron lokal).
* **Notifications:** Telegram Bot API (real-time alerts untuk pipeline success/failure).

## 3. Directory Structure
```text
senti-quant/
├── .env                        # Menyimpan secrets (Neon DB connection string)
├── requirements.txt            # Daftar dependensi (lxml, plotly, transformers, dll)
├── venv/                       # Virtual Environment Python
└── src/
    ├── main.py                 # Otak utama (Pipeline Ingestion -> DB -> AI Analysis)
    ├── app/
    │   └── dashboard.py        # UI Streamlit (SaaS Enterprise level dengan Plotly)
    ├── analysis/
    │   └── sentiment.py        # TruthEngineAI (Hybrid: Gatekeeper + BERT + Heuristics + De-noising)
    └── data/
        ├── scraper.py          # AsyncNewsScraper & RSS Parser dengan Semaphore (Rate Limiter)
        ├── database.py         # Konfigurasi engine DB dan SessionLocal
        ├── crud.py             # Operasi database (save_article, get_unprocessed_articles)
        └── models.py           # Skema tabel SQLAlchemy (Article, SentimentLog, NewsSource)
```

## 4. Core Architecture & Alur Data
Pipa data (Data Pipeline) Senti-Quant beroperasi secara otonom dengan alur berikut:
1. **Trigger (Automation):** Cron Job di Fedora mengeksekusi `src/main.py` setiap hari bursa (Senin-Jumat) pada pukul 08:00 dan 16:00.
2. **Extract (RSS Scraping):** Fungsi `fetch_rss_links` mengambil ratusan URL dari RSS feed portal berita (saat ini CNBC). `AsyncNewsScraper` kemudian menyedot konten HTML menggunakan rate limiting (`asyncio.Semaphore(5)` dan jeda 1 detik) untuk menghindari IP banned.
3. **Load (Database):** Data berita mentah dan kredibilitas sumbernya disimpan ke tabel PostgreSQL di Neon Cloud. Sistem mengecek dan melewati (skip) URL duplikat.
4. **AI Processing (Batching):** TruthEngineAI memproses antrian artikel (limit 100 per batch). Mesin ini memadukan 4 lapis logika berjenjang:
   * **Gatekeeper (Relevance Filter):** Memeriksa teks dengan 20 kata kunci saham. Jika kurang dari 2 kecocokan, teks dicap IRRELEVANT (batal dianalisis untuk menghemat resource).
   * **Financial Dictionary:** Mengecek kata kunci saham (bullish, cuan, anjlok). Jika cocok, sentimen langsung dikunci (Bypass AI).
   * **NLP BERT:** Jika lolos dari dua filter di atas, model Transformer berbahasa Indonesia akan menilai sentimennya.
   * **De-noising Logic:** Menghitung rasio huruf kapital (>15%) dan tanda seru (>3) untuk mendeteksi clickbait.
5. **Scoring:** Menghitung Skor Integritas dengan rumus: $Integrity = S_i \times C_i \times (1 - N_i)$.
6. **Visualization:** `dashboard.py` melakukan query ke database dan menampilkan data secara real-time ke antarmuka pengguna Streamlit.

## 5. Database Schema (PostgreSQL)
Struktur relasional yang saat ini berjalan di Neon PostgreSQL (direpresentasikan via SQLAlchemy):
* **NewsSource:** Menyimpan data portal berita (`id`, `domain`, `credibility_score`).
* **Article:** Menyimpan konten berita mentah (`id`, `title`, `url`, `content`, `published_at`, `source_id` sebagai Foreign Key).
* **SentimentLog:** Menyimpan hasil analisis AI (`article_id` sebagai Foreign Key, `sentiment_label`, `confidence`, `noise_probability`, `integrity_score`). Label sentimen sekarang mencakup: POSITIVE, NEGATIVE, NEUTRAL, dan IRRELEVANT.

> **Catatan Arsitektur:** Sesuai ketetapan engineering kita, koneksi ke database menerapkan sistem "Lazy Connection" (diinisialisasi hanya saat dibutuhkan melalui `SessionLocal()`) untuk memastikan tidak ada kebocoran memori atau error timeout saat UI Streamlit sedang diuji atau diakses oleh banyak pengguna.

## 6. Completed Features (Current State)
* ✅ **Mass RSS Ingestion:** Mampu menyedot ratusan link legal secara instan dengan parser XML akurat.
* ✅ **Anti-DDoS / Rate Limiting:** Implementasi asyncio.Semaphore menjaga server tetap aman dari pemblokiran firewall portal berita.
* ✅ **Scale-to-Zero Cloud DB:** Data tersimpan aman di Neon PostgreSQL yang efisien biaya.
* ✅ **Relevance Filter (Gatekeeper):** Filter otomatis yang mengecap IRRELEVANT pada berita non-finansial sebelum diproses NLP untuk menjaga validitas data.
* ✅ **Hybrid AI Truth Engine:** Kombinasi Dictionary Heuristics dan NLP Machine Learning.
* ✅ **Clickbait/Noise Detector:** Algoritma pemotongan skor integritas otomatis berdasarkan tanda baca dan kapitalisasi berlebih.
* ✅ **Full Cloud Automation:** Berjalan otonom via GitHub Actions (tidak bergantung laptop - always-on compute).
* ✅ **24/7 Reliability:** Data collection berjalan setiap hari Senin-Jumat pukul 08:00 & 16:00 UTC (15:00 & 23:00 WIB).
* ✅ **Data Retention Policy:** Auto-cleanup 30 hari untuk menjaga database quota Neon (0.5 GB) tetap stabil.
* ✅ **Telegram Notifications:** Real-time alerts untuk pipeline success (dengan cleanup metrics) dan failure (dengan GitHub Actions link).
* ✅ **Enterprise UI:** Dashboard berkelas SaaS dengan metrik Bloomberg-style, Donut Chart, dan tabel log data real-time.
* ✅ **UI Truth Filter (Commit 31):** Modifikasi pada `dashboard.py` yang berhasil menyaring artikel berlabel IRRELEVANT di level database, memastikan metrik dan grafik hanya menampilkan sentimen pasar murni.
* ✅ **Pandas 2.0+ Compatibility (Commit 36):** Fixed deprecated `DataFrame.style.applymap()` → `DataFrame.style.map()` untuk kompatibilitas dengan Streamlit Cloud.

## 7. Known Issues & Next Development Steps
## 8. Recent Infrastructure Improvements (Commits 33-37)
### Commit 33: Data Retention Policy
- Implementasi `cleanup_old_data()` di `src/data/crud.py` yang menghapus artikel & sentiment logs lebih tua dari retention_days.
- Terintegrasi ke pipeline `src/main.py` dengan JSON metrics emission: `PIPELINE_CLEANUP_METRICS={"retention_days": 30, "deleted_sentiment_logs": N, "deleted_articles": M}`.
- Database quota protection: Mencegah database quota (0.5 GB Neon free tier) terlampaui dengan auto-cleanup setiap pipeline run.
- **Manual Cleanup:** User dapat menjalankan `python manual_cleanup.py [days]` kapan saja untuk cleanup manual.

### Commit 34-35: GitHub Actions Workflow + Telegram Integration
- Migrasi dari local cron ke GitHub Actions (`.github/workflows/senti_quant_pipeline.yml`).
- Schedule: `cron: '0 1,9 * * 1-5'` (UTC) = Senin-Jumat pukul 08:00 & 16:00 WIB (sesuai jam operasional bursa).
- **Failure Notifications:** If pipeline error → Telegram alert dengan GitHub Actions run link (Markdown format).
- **Success Notifications:** If pipeline success → Telegram alert dengan cleanup metrics (HTML format untuk JSON pretty-print).
- Secrets: `DATABASE_URL`, `HF_TOKEN`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` ✅ terverifikasi berfungsi.

### Commit 36-37: Dashboard Fixes & Manual Cleanup Scripts
- Fixed Pandas 2.0+ incompatibility: `.applymap()` → `.map()` di `src/app/dashboard.py` line 127.
- Added `test_cleanup.py` & `manual_cleanup.py` untuk verifikasi dan manual execution retention cleanup.
- Verifikasi: Cleanup logic berfungsi sempurna (243 artikel lama dari Maret 2026 berhasil dihapus saat test).

## 9. Current Status (10 Mei 2026)
**System Health:** 🟢 Fully Operational (Cloud Infrastructure Complete)
- ✅ GitHub Actions workflow ready (active setiap hari kerja 08:00 & 16:00 WIB)
- ✅ Neon PostgreSQL stable (30 MB / 0.5 GB = 6% utilized after cleanup)
- ✅ Telegram notifications working (tested with success/failure alerts)
- ⚠️ Dashboard accessible di https://allan-senti-quant.streamlit.app/ (applymap fix deployed)
- 📊 Data: Cleaned up 243 old articles from March (retention policy verified working)

**Note:** Today is Sunday (not in schedule), so no pipeline execution today. Next run: Monday 11 May 2026 at 08:00 UTC.

## 10. Known Issues & Next Development Steps
* 🐛 **Known Issue (Gatekeeper Terlalu Agresif):** Relevance filter di `sentiment.py` masih buta terhadap istilah makroekonomi (minyak, perang, suku bunga) dan ticker emiten (misal: PGEO). Akibatnya, berita fundamental penting rentan terbuang menjadi IRRELEVANT karena tidak memenuhi kuota 2 kata kunci spesifik.
* 🚀 **Next Step (Gatekeeper V2):** Memperbaiki logic `_is_financial_news()` dengan menambahkan kamus makroekonomi dan deteksi *regex* untuk ticker emiten agar filter lebih akurat.
* 🚀 **Future (Monetization Layer):** API endpoints untuk data consumption, premium Telegram bot features, atau subscription model untuk enterprise clients.
* 🚀 **Next Step (Data Expansion):** Menambahkan sumber RSS baru di `main.py` di luar CNBC (misalnya Kontan, Bisnis.com, atau Investor.id) untuk memperkaya analisis sentimen.