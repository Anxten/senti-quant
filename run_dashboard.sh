#!/bin/bash
# Launcher script untuk Senti-Quant Dashboard

# Warna untuk output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🛡️  Starting Senti-Quant Dashboard...${NC}"

# Set PYTHONPATH ke root project
export PYTHONPATH="$(pwd)"

# Jalankan Streamlit
streamlit run src/app/dashboard.py

echo -e "${GREEN}✅ Dashboard stopped${NC}"
