# Senti-Quant - Project State & Architecture
**Current Status:** Telegram-first market sentiment MVP running on DigitalOcean VPS Singapore

## 1. Project Overview
Senti-Quant (The Truth Engine) is a financial sentiment analysis platform for the Indonesian capital market. The system ingests financial news, removes noise and clickbait, evaluates sentiment with a hybrid AI pipeline, and delivers an executive summary to Telegram.

The primary product output is now the Telegram summary broadcast. The Streamlit dashboard remains available as a supporting inspection and visualization layer.

## 2. Tech Stack & Environment
The current stack is optimized for Linux Fedora development and a VPS-based production runtime:

* **Programming Language:** Python inside a virtual environment.
* **Production Runtime:** DigitalOcean VPS in Singapore, used as the always-on scheduler and execution host.
* **Data Ingestion:** asyncio, aiohttp, BeautifulSoup, and direct RSS parsing from XML feeds.
* **AI & NLP Engine:** Hugging Face transformers and torch.
* **Pre-trained Model:** `mdhugol/indonesia-bert-sentiment-classification`.
* **Database:** Neon PostgreSQL accessed through SQLAlchemy ORM.
* **Frontend/UI:** Streamlit, pandas, and Plotly for dashboard visualizations.
* **Notifications:** Telegram Bot API for executive summaries and pipeline alerts.
* **Utilities:** requests, python-dotenv, cloudscraper, lxml, and standard library helpers.

## 3. Directory Structure
```text
senti-quant/
├── .env
├── AI_INSTRUCTIONS.md
├── PROJECT_STATE.md
├── README.md
├── requirements.txt
├── run_dashboard.sh
├── scripts/
│   └── cleanup_example_dot_com_articles.py
├── src/
│   ├── main.py
│   ├── analysis/
│   │   └── sentiment.py
│   ├── app/
│   │   └── dashboard.py
│   ├── bot/
│   │   └── summary_broadcaster.py
│   ├── config/
│   │   └── credibility.py
│   ├── data/
│   │   ├── crud.py
│   │   ├── database.py
│   │   ├── models.py
│   │   └── scraper.py
│   └── utils/
└── tests/
    └── test_sentiment.py
```

## 4. Core Architecture & Data Flow
The system runs as an automated pipeline with the following flow:

1. **Trigger:** The VPS scheduler runs `src/main.py` at 08:00 WIB and 16:00 WIB on weekdays.
2. **Extract:** RSS feeds are parsed directly and converted into article records. The current default source is Google News RSS for Indonesian stock-market queries.
3. **Load:** Articles are stored in Neon PostgreSQL with duplicate protection.
4. **Analyze:** `TruthEngineAI` processes unprocessed articles in batches.
5. **Score:** Each article gets a sentiment label and integrity score.
6. **Cleanup:** Old records are removed based on the retention policy.
7. **Broadcast:** A 12-hour Telegram summary is generated and sent to the chat.
8. **Inspect:** The Streamlit dashboard reads from the same database for manual review.

## 5. Sentiment Pipeline
`TruthEngineAI` uses layered logic instead of a single-model sentiment decision:

* **Gatekeeper relevance filter:** Articles that are not financial enough are marked `IRRELEVANT` early.
* **Financial heuristics:** Strong positive/negative phrases can short-circuit the AI model when the signal is obvious.
* **BERT fallback:** Articles that survive the heuristics are classified by the Indonesian BERT sentiment model.
* **Noise detection:** Excessive capitalization, repeated exclamation marks, and pump-and-dump phrases increase the noise score.
* **Integrity formula:** `Integrity = S_i × C_i × (1 - N_i)`.

## 6. Database Schema
The database uses three primary tables:

* **NewsSource:** Stores source domain, credibility score, trust flag, and creation time.
* **Article:** Stores article URL, title, content, timestamps, and source reference.
* **SentimentLog:** Stores sentiment label, confidence, noise probability, source credibility, and integrity score.

The database connection remains lazy. A session is only created when the pipeline or dashboard actually needs it.

## 7. Completed Features
* **Direct RSS ingestion:** The pipeline reads RSS items directly and no longer depends on scraping article HTML as the primary ingestion path.
* **Duplicate protection:** URL idempotency and normalized-title checks prevent repeated inserts.
* **Hybrid sentiment analysis:** The project combines rules, heuristics, and BERT.
* **Noise / clickbait detection:** The system penalizes noisy or manipulative articles.
* **Retention cleanup:** Old articles and sentiment logs are automatically deleted according to retention settings.
* **Telegram executive summary:** The broadcaster sends the top 5 articles from the last 12 hours.
* **Clickable Telegram links:** Article titles are now sent as clickable links to the original article URLs.
* **Market pulse header:** The summary includes a top-level positive/negative/noise count.
* **Dashboard truth filter:** The dashboard excludes `IRRELEVANT` entries from core metrics.
* **Pandas compatibility fix:** The dashboard uses `DataFrame.style.map()` instead of the deprecated `applymap()`.
* **Cleanup utility:** A dedicated script exists to remove dummy `example.com` records from the live database when needed.

## 8. Production Deployment
The production deployment has moved away from GitHub Actions as the primary runtime. The current setup uses a DigitalOcean VPS in Singapore to keep the pipeline on time and avoid queue delays.

Operationally, the system is expected to run at:

* **08:00 WIB**
* **16:00 WIB**

This deployment choice was made to use the GitHub Education credit budget more efficiently and to make the schedule stable for market-hours delivery.

## 9. Current Status
**System Health:** Stable and production-oriented.

* The Telegram summary broadcaster is implemented and committed.
* The 12-hour summary format is already user-friendly and linkable.
* The dummy `example.com` rows have been cleaned from the live database.
* The dashboard remains available as a supporting interface.
* The VPS-based schedule is the current execution model.

## 10. Current Risks & Next Improvements
* The relevance gate can still be improved for macroeconomic news and ticker detection.
* Additional RSS sources can be added to broaden coverage beyond the current default feed.
* The Telegram summary could later be extended with sector-level clustering or volatility context.
* A formal VPS service definition or systemd timer can be documented if the operational setup needs to be hardened further.