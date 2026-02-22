# 🛡️ Senti-Quant Dashboard

Web-based visualization dashboard untuk Truth Engine.

## 🚀 Quick Start

```bash
# Jalankan dashboard
streamlit run src/app/dashboard.py
```

Dashboard akan terbuka di browser pada `http://localhost:8501`

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
