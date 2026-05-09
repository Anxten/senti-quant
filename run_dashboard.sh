#!/bin/bash
# Launcher script untuk Senti-Quant Dashboard

# Warna untuk output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🛡️  Starting Senti-Quant Dashboard...${NC}"

# Set PYTHONPATH ke root project
export PYTHONPATH="$(pwd)"

# Pakai virtual environment project kalau tersedia.
if [ -f "venv/bin/activate" ]; then
	source venv/bin/activate
fi

# Jalankan Streamlit
if [ -x "venv/bin/streamlit" ]; then
	venv/bin/streamlit run src/app/dashboard.py
else
	streamlit run src/app/dashboard.py
fi

echo -e "${GREEN}✅ Dashboard stopped${NC}"
