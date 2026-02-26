---
title: "Senti-Quant: AI Truth Engine"
emoji: 🛡️
colorFrom: indigo
colorTo: purple
sdk: streamlit
sdk_version: 1.31.0
app_file: src/app.py
pinned: false
license: mit
---

# 🛡️ Senti-Quant: The AI-Powered Truth Engine

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![AI](https://img.shields.io/badge/AI-Transformers%20%7C%20NLP-orange.svg)
![Database](https://img.shields.io/badge/Database-PostgreSQL-336791.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-green.svg)

**Senti-Quant** is a next-generation financial analysis platform that bridges **Natural Language Processing (NLP)** with **Quantitative Analysis**. Unlike traditional tools that just read sentiment, Senti-Quant acts as a "Truth Engine" to filter out market noise, bot activities, and information pollution.

> *"In 2026, the problem isn't lack of information. It's Information Asymmetry and Data Pollution."*

## 🔗 Live Demo
✅ **Fully Functional** — Run locally with the commands above to see the Truth Engine in action!

**Features:**
- Real-time sentiment analysis with Indonesia-BERT
- Interactive dashboard with Plotly visualizations
- Noise detection and integrity scoring
- PostgreSQL data persistence

## 🚀 Key Features (The "Truth Engine")
* **Sentiment De-noising:** Automatically filters out social media bots, spam, and "pump-and-dump" attempts before calculating sentiment scores.
* **Integrity Scoring:** Assigns a credibility rating to every news source based on historical accuracy and domain authority.
* **Quantitative Synergy:** Correlates real-time sentiment spikes with price volatility to detect anomalies.
* **Hybrid Data Acquisition:** Asynchronous scraping engine capable of harvesting data from trusted news portals and social streams.
* **Zero-Cost Architecture:** Built entirely on open-source technologies (PostgreSQL, Hugging Face, Python).

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

### 1. Run Data Pipeline
```bash
# Scrape news, analyze sentiment, save to database
python -m src.main
```

### 2. Launch Dashboard
```bash
# Option 1: Using launcher script (recommended)
./run_dashboard.sh

# Option 2: Manual command
PYTHONPATH=$(pwd) streamlit run src/app/dashboard.py
```

Dashboard will open at `http://localhost:8501`

## 🛠️ Tech Stack
- **Core:** Python 3.10+, Asyncio
- **Data Layer:** PostgreSQL, SQLAlchemy ORM, BeautifulSoup, aiohttp
- **AI Engine:** Hugging Face Transformers (Indonesia-BERT)
- **Visualization:** Streamlit, Plotly
- **Environment:** Fedora Linux | VS Code

## 📦 Installation & Setup

Follow these steps to set up the **Truth Engine** locally:

### 1. Clone the Repository
```bash
git clone [https://github.com/Anxten/senti-quant.git](https://github.com/Anxten/senti-quant.git)
cd senti-quant
```

### 2. Set Up Virtual Environment (Fedora/Linux)
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

### 4. Database Setup (Docker Recommended)
Ensure you have a PostgreSQL instance running.

```bash
# Example if using Docker
docker run --name senti-db -e POSTGRES_PASSWORD=secret -d -p 5432:5432 postgres
```

## 📊 Project Structure
Designed with Clean Architecture principles for scalability.

```
senti-quant/
├── src/
│   ├── data/           # Database models & Async scrapers
│   ├── analysis/       # AI Models & Sentiment Logic
│   ├── app/            # Streamlit Dashboard
│   ├── main.py         # ETL Pipeline Orchestrator
│   └── __init__.py
├── test_db_connection.py  # Database tests
├── test_sentiment.py      # AI tests
├── run_dashboard.sh       # Dashboard launcher
├── requirements.txt       # Project dependencies
├── .env                   # Configuration
└── README.md              # Documentation
```

## 🎯 Use Cases
- **Retail Investors (Gen-Z):** Verifying if a trending stock is organic or a bot-driven hype.
- **Market Analysts:** Filtering "noise" from daily news feeds to focus on high-impact stories.
- **Academic Research:** Studying the correlation between fake news spread and market volatility.

## 📝 License
This project is open-source and available under the MIT License.

---

**Developed by Allan Bendatu**
*Informatics Student*
*Building the "Truth Engine" for the Capital Markets.*