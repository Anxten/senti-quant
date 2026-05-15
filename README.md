---
title: "Senti-Quant: AI Truth Engine"
emoji: 🛡️
colorFrom: indigo
colorTo: purple
sdk: streamlit
sdk_version: 1.31.0
app_file: src/app/dashboard.py
pinned: false
license: mit
---

# 🛡️ Senti-Quant: The AI-Powered Truth Engine

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![AI](https://img.shields.io/badge/AI-Transformers%20%7C%20NLP-orange.svg)
![Database](https://img.shields.io/badge/Database-PostgreSQL-336791.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-green.svg)

**Senti-Quant** is a financial sentiment platform that combines **Natural Language Processing (NLP)** with a lightweight truth-filtering pipeline. Unlike generic sentiment tools, Senti-Quant is designed to suppress market noise, highlight meaningful news, and produce an executive summary that is easier to act on.

> *"In 2026, the problem is not a lack of information. It is information asymmetry and data pollution."*

## 🔗 Live Demo

**Live Demo:** The dashboard is available here:  
👉 **[allan-senti-quant.streamlit.app](https://allan-senti-quant.streamlit.app/)**


**Features:**
- Real-time financial sentiment analysis with Indonesia-BERT
- Interactive Streamlit dashboard with Plotly charts
- Noise detection and integrity scoring
- PostgreSQL persistence on Neon
- Telegram executive summaries for the top 5 market-relevant articles

## 🚀 Key Features
* **Sentiment de-noising:** Filters bot-like, spammy, and pump-and-dump style content before scoring.
* **Integrity scoring:** Rates articles using sentiment, source credibility, and noise probability.
* **Hybrid data acquisition:** Uses RSS ingestion and direct parsing for stable article collection.
* **Telegram-first delivery:** Sends a concise 12-hour executive summary to Telegram with clickable article links.
* **Dashboard support:** Keeps a Streamlit dashboard for human inspection and historical review.

## 🧠 The Logic Behind the Innovation
Senti-Quant goes beyond simple polarity detection. It applies a weighted integrity logic:

$$
\text{True Sentiment} = \sum_{i=1}^{n} (S_i \times C_i \times (1 - N_i))
$$

Where:
* $S_i$: Raw Sentiment Score (from NLP Model)
* $C_i$: Source Credibility Factor (0.0 - 1.0)
* $N_i$: Detected Noise/Bot Probability (0.0 - 1.0)

**Innovation Formula:**
$$
Logic + Creativity = Innovation
$$

## 🚀 Quick Start

### 1. Run the Data Pipeline
```bash
# Ingest RSS news, analyze sentiment, save to database, and broadcast Telegram summary
python -m src.main
```

### 2. Launch the Dashboard
```bash
# Option 1: Using launcher script (recommended)
./run_dashboard.sh

# Option 2: Manual command
PYTHONPATH=$(pwd) streamlit run src/app/dashboard.py
```

The dashboard will open at `http://localhost:8501`

### 3. Run the cleanup utility manually
```bash
# Dry-run first
python scripts/cleanup_example_dot_com_articles.py

# Confirm deletion if you really need to remove example.com dummy rows
python scripts/cleanup_example_dot_com_articles.py --confirm
```

## 🛠️ Tech Stack
- **Core:** Python 3.10+, asyncio
- **Data layer:** PostgreSQL, SQLAlchemy ORM, BeautifulSoup, aiohttp
- **AI engine:** Hugging Face Transformers (Indonesia-BERT)
- **Notifications:** Telegram Bot API
- **Visualization:** Streamlit, Plotly
- **Environment:** Fedora Linux, VS Code, DigitalOcean VPS for production runtime

## 📦 Installation & Setup

Follow these steps to set up the project locally:

### 1. Clone the Repository
```bash
git clone https://github.com/Anxten/senti-quant.git
cd senti-quant
```

### 2. Set Up a Virtual Environment (Fedora/Linux)
Always use a virtual environment to prevent system package conflicts.

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Database Setup
Ensure you have a PostgreSQL instance running or a valid Neon connection string in `.env`.

```bash
# Example if using Docker
docker run --name senti-db -e POSTGRES_PASSWORD=secret -d -p 5432:5432 postgres
```

## 📊 Project Structure
Designed with clean architecture principles for scalability.

```
senti-quant/
├── src/
│   ├── data/           # Database models, CRUD, and RSS parsing
│   ├── analysis/       # AI models & sentiment logic
│   ├── app/            # Streamlit dashboard
│   ├── bot/            # Telegram summary broadcaster
│   ├── main.py         # ETL pipeline orchestrator
│   └── __init__.py
├── scripts/              # Utility scripts
├── tests/                # Test helpers
├── run_dashboard.sh      # Dashboard launcher
├── requirements.txt      # Project dependencies
├── .env                  # Configuration
└── README.md             # Documentation
```

## 🎯 Use Cases
- **Retail investors:** Checking whether a trending stock is driven by organic news or hype.
- **Market analysts:** Filtering noise from daily news feeds to focus on high-impact stories.
- **Academic research:** Studying the relationship between news quality and market movement.

## 🚀 Production Notes
The production pipeline currently runs on a DigitalOcean VPS in Singapore. The schedule is set to execute at **08:00 WIB** and **16:00 WIB** on weekdays, with the Telegram summary as the primary delivery channel.

The workflow is not dependent on GitHub Actions for runtime execution.

## 📝 License
This project is open-source and available under the MIT License.

---

**Developed by Allan Bendatu**
*Informatics Student*
*Building the Truth Engine for the capital markets.*