import sys
import os

# Menambahkan root folder project ke system path agar Python bisa membaca package 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy.orm import Session
from src.data.database import SessionLocal
from src.data.models import Article, SentimentLog, NewsSource

# --- 1. KONFIGURASI HALAMAN (Wajib Paling Atas) ---
st.set_page_config(
    page_title="Senti-Quant | The Truth Engine",
    page_icon="🛡️",
    layout="wide", # Bikin lebar ala dashboard profesional
    initial_sidebar_state="expanded"
)

# --- 2. KONEKSI DATABASE ---
@st.cache_resource
def get_db_session():
    return SessionLocal()

db: Session = get_db_session()

# --- 3. AMBIL DATA DARI NEON DB ---
# Query menggabungkan Article, SentimentLog, dan NewsSource
# Memfilter out label 'IRRELEVANT' agar tidak merusak metrik dashboard
query = db.query(
    Article.title, 
    Article.url, 
    SentimentLog.sentiment_label, 
    SentimentLog.integrity_score,
    NewsSource.domain
).join(SentimentLog, Article.id == SentimentLog.article_id)\
 .join(NewsSource, Article.source_id == NewsSource.id)\
 .filter(SentimentLog.sentiment_label != 'IRRELEVANT').statement

# Masukkan ke Pandas DataFrame agar mudah diolah
df = pd.read_sql(query, db.bind)

# --- 4. SIDEBAR (Filter Interaktif) ---
st.sidebar.image("https://img.icons8.com/color/96/000000/bullish.png", width=80)
st.sidebar.title("⚙️ Control Panel")
st.sidebar.markdown("Filter data sentimen pasar secara *real-time*.")

# Filter Sumber Berita
sumber_list = ["Semua"] + df['domain'].unique().tolist()
sumber_pilihan = st.sidebar.selectbox("📰 Filter Sumber Berita:", sumber_list)

if sumber_pilihan != "Semua":
    df = df[df['domain'] == sumber_pilihan]

st.sidebar.markdown("---")
st.sidebar.info("💡 **Truth Engine V1.0**\n\nBerita dengan sentimen 'NEUTRAL' biasanya adalah berita faktual tanpa opini pasar.")

# --- 5. HEADER DASHBOARD ---
st.title("🛡️ Senti-Quant: AI Truth Engine")
st.markdown("*Menyaring Kebisingan, Menemukan Kebenaran di Pasar Modal.*")
st.markdown("---")

# --- 6. METRIK KPI (Key Performance Indicators) ---
# Menghitung statistik
total_berita = len(df)
bullish_count = len(df[df['sentiment_label'] == 'POSITIVE'])
bearish_count = len(df[df['sentiment_label'] == 'NEGATIVE'])
noise_count = len(df[df['sentiment_label'] == 'NEUTRAL'])

# Menampilkan 4 Kolom Metrik
col1, col2, col3, col4 = st.columns(4)
col1.metric("📊 Total Berita Diproses", total_berita)
col2.metric("🚀 Sentimen Bullish (Positif)", bullish_count)
col3.metric("🩸 Sentimen Bearish (Negatif)", bearish_count)
col4.metric("🌫️ Noise (Netral/Faktual)", noise_count)

st.markdown("---")

# --- 7. VISUALISASI GRAFIK INTERAKTIF ---
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("🍩 Distribusi Sentimen Pasar")
    if total_berita > 0:
        # Membuat Donut Chart Interaktif dengan Plotly
        fig_donut = px.pie(
            df, 
            names='sentiment_label', 
            hole=0.4, # Membuatnya jadi donat
            color='sentiment_label',
            color_discrete_map={
                'POSITIVE': '#00CC96', # Hijau
                'NEGATIVE': '#EF553B', # Merah
                'NEUTRAL': '#636EFA'   # Biru
            }
        )
        fig_donut.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_donut, use_container_width=True)
    else:
        st.warning("Belum ada data sentimen.")

with col_chart2:
    st.subheader("📈 Skor Integritas (Truth Score)")
    if total_berita > 0:
        # Histogram skor integritas
        fig_hist = px.histogram(
            df, 
            x="integrity_score", 
            nbins=10,
            color_discrete_sequence=['#AB63FA']
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.warning("Belum ada data integritas.")

# --- 8. TABEL DATA LANGSUNG (Truth Feed) ---
st.subheader("🔍 Live Truth Feed (Data Log)")

# Merapikan tabel agar enak dilihat
df_tabel = df[['title', 'domain', 'sentiment_label', 'integrity_score', 'url']]
df_tabel.columns = ['Judul Artikel', 'Sumber', 'Sentimen', 'Skor Integritas', 'URL']

# Tampilkan sebagai tabel interaktif di Streamlit
st.dataframe(
    df_tabel.style.applymap(
        lambda x: 'color: green;' if x == 'POSITIVE' else ('color: red;' if x == 'NEGATIVE' else ''),
        subset=['Sentimen']
    ),
    use_container_width=True,
    height=300
)

st.caption("🛡️ Senti-Quant Truth Engine")