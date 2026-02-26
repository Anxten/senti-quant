# 🛡️ Senti-Quant Dashboard

Web-based visualization dashboard untuk Truth Engine.

## 🚀 Quick Start

### Opsi 1: Menggunakan Launcher Script (Recommended)
```bash
# Dari root project
./run_dashboard.sh
```

### Opsi 2: Manual Command
```bash
# Dari root project
PYTHONPATH=$(pwd) streamlit run src/app/dashboard.py
```

Dashboard akan terbuka di browser pada `http://localhost:8501`

### ⚠️ Important Note
Jangan jalankan `streamlit run src/app/dashboard.py` langsung tanpa set PYTHONPATH, karena akan error import.

## 📊 Features

- **Real-time Metrics**: Total berita, organik vs noise, sentimen dominan
- **Interactive Charts**: Bar chart & pie chart dengan Plotly
- **Live Data Feed**: Tabel interaktif dengan filter sentimen
- **Auto-refresh**: Data di-cache 60 detik untuk performa optimal

## 🎨 Screenshots

Dashboard menampilkan:
1. Metrik utama (4 cards)
2. Distribusi sentimen (bar chart)
3. Rasio integritas (donut chart)
4. Live truth feed (filterable table)

## 🔧 Configuration

Dashboard otomatis membaca dari PostgreSQL database yang sama dengan pipeline utama.

## 📝 Notes

- Dashboard menggunakan caching untuk mengurangi load database
- Data di-refresh otomatis setiap 60 detik
- Semua chart interaktif (zoom, pan, hover)
