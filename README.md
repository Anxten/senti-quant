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
![Status](https://img.shields.io/badge/Status-In%20Development-yellow.svg)

**Senti-Quant** is a next-generation financial analysis platform that bridges **Natural Language Processing (NLP)** with **Quantitative Analysis**. Unlike traditional tools that just read sentiment, Senti-Quant acts as a "Truth Engine" to filter out market noise, bot activities, and information pollution.

> *"In 2026, the problem isn't lack of information. It's Information Asymmetry and Data Pollution."*

## 🔗 Live Demo
*Coming Soon* — The project is currently in the architectural phase, focusing on building a robust Data Integrity Layer.

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

## 🛠️ Tech Stack
- **Core:** Python 3.10+, Asyncio
- **Data Layer:** PostgreSQL (Relational), BeautifulSoup/Playwright (Scraping)
- **AI Engine:** Hugging Face Transformers (RoBERTa / FinBERT)
- **Analysis:** Scikit-learn (K-Means Clustering for Outlier Detection)
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
│   ├── utils/          # Helper functions & Loggers
│   └── __init__.py
├── notebooks/          # Jupyter Notebooks for experimentation
├── tests/              # Unit & Integration tests
├── config/             # Configuration files (.env, settings)
├── requirements.txt    # Project dependencies
└── README.md           # Documentation
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