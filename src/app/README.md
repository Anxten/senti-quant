# Senti-Quant Dashboard

This folder contains the Streamlit dashboard for the Senti-Quant Truth Engine.

## Quick Start

### Option 1: Use the launcher script
```bash
./run_dashboard.sh
```

### Option 2: Run Streamlit manually
```bash
PYTHONPATH=$(pwd) streamlit run src/app/dashboard.py
```

The dashboard will open at `http://localhost:8501`.

## Features

- Real-time market sentiment metrics
- Interactive Plotly charts
- Live data feed with sentiment coloring
- Automatic filtering of `IRRELEVANT` articles from the main dashboard metrics
- Cached database access for better responsiveness

## Dashboard Layout

The dashboard currently shows:
1. Summary KPI cards for processed articles and sentiment counts
2. Sentiment distribution chart
3. Integrity score histogram
4. Live truth feed table

## Configuration

The dashboard reads from the same PostgreSQL database used by the main pipeline.

## Notes

- The database connection is lazy and only opens when the dashboard actually queries data.
- Data refresh behavior is handled by Streamlit caching and the dashboard query layer.
- The dashboard is a supporting view; Telegram is now the primary executive delivery channel.
