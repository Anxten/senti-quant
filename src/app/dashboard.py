import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy.orm import Session
from src.data.database import SessionLocal
from src.data.models import Article, SentimentLog, NewsSource

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Senti-Quant | Truth Engine",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- FUNGSI PENGAMBILAN DATA ---
@st.cache_data(ttl=60)  # Cache data selama 60 detik agar DB tidak jebol
def load_data():
    db: Session = SessionLocal()
    try:
        # Join tabel Articles, SentimentLogs, dan NewsSources
        query = db.query(
            Article.title,
            Article.url,
            NewsSource.domain,
            SentimentLog.sentiment_label,
            SentimentLog.confidence,
            SentimentLog.integrity_score,
            SentimentLog.analyzed_at
        ).join(SentimentLog, Article.id == SentimentLog.article_id)\
         .join(NewsSource, Article.source_id == NewsSource.id)
        
        # Eksekusi dan ubah ke Pandas DataFrame
        results = query.all()
        
        # Jika kosong
        if not results:
            return pd.DataFrame()
            
        df = pd.DataFrame(results)
        # Rename kolom agar lebih cantik
        df.columns = ["Judul", "URL", "Sumber", "Sentimen", "Confidence", "Integrity_Score", "Waktu_Analisis"]
        
        # Hitung status kredibilitas berdasarkan Integrity Score
        df['Status'] = df['Integrity_Score'].apply(lambda x: '✅ Valid' if x > 0 else '⚠️ Neutral/Noise')
        
        return df
    finally:
        db.close()

# --- HEADER APP ---
st.title("🛡️ Senti-Quant: AI Truth Engine")
st.markdown("*Menyaring Kebisingan, Menemukan Kebenaran di Pasar Modal.*")
st.divider()

# --- LOAD DATA ---
df = load_data()

if df.empty:
    st.warning("Belum ada data sentimen di database. Silakan jalankan scraper terlebih dahulu.")
    st.code("python -m src.main", language="bash")
else:
    # --- METRIK UTAMA (TOP ROW) ---
    col1, col2, col3, col4 = st.columns(4)
    
    total_berita = len(df)
    berita_valid = len(df[df['Integrity_Score'] > 0])
    berita_noise = total_berita - berita_valid
    
    # Hitung sentimen dominan (dari berita yang valid saja)
    if berita_valid > 0:
        sentimen_dominan = df[df['Integrity_Score'] > 0]['Sentimen'].mode()[0]
    else:
        sentimen_dominan = "N/A"

    col1.metric("Total Berita Diproses", total_berita)
    col2.metric("Berita Organik (Valid)", berita_valid, help="Berita dengan Integrity Score > 0")
    col3.metric("Berita Neutral/Noise", berita_noise, delta="-", delta_color="inverse")
    col4.metric("Sentimen Pasar (Organik)", sentimen_dominan)

    st.divider()

    # --- BARIS KEDUA (GRAFIK) ---
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("Distribusi Sentimen")
        # Hitung jumlah per sentimen
        sent_counts = df['Sentimen'].value_counts().reset_index()
        sent_counts.columns = ['Sentimen', 'Jumlah']
        
        fig_bar = px.bar(
            sent_counts, 
            x='Sentimen', 
            y='Jumlah', 
            color='Sentimen',
            color_discrete_map={"POSITIVE": "green", "NEGATIVE": "red", "NEUTRAL": "gray"}
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_chart2:
        st.subheader("Rasio Integritas Berita")
        status_counts = df['Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Jumlah']
        
        fig_pie = px.pie(
            status_counts, 
            names='Status', 
            values='Jumlah',
            hole=0.4,
            color='Status',
            color_discrete_map={"✅ Valid": "#2ecc71", "⚠️ Neutral/Noise": "#e74c3c"}
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- TAMPILAN DATA TABEL (LIVE FEED) ---
    st.subheader("🔍 Live Truth Feed (Data Log)")
    
    # Filter Interaktif
    filter_sentimen = st.multiselect(
        "Filter Sentimen:", 
        options=["POSITIVE", "NEGATIVE", "NEUTRAL"], 
        default=["POSITIVE", "NEGATIVE", "NEUTRAL"]
    )
    
    # Terapkan filter
    filtered_df = df[df['Sentimen'].isin(filter_sentimen)]
    
    # Tampilkan tabel yang sudah dipercantik
    st.dataframe(
        filtered_df[['Waktu_Analisis', 'Sumber', 'Judul', 'Sentimen', 'Confidence', 'Integrity_Score', 'Status']],
        use_container_width=True,
        hide_index=True
    )

    # --- FOOTER ---
    st.divider()
    st.caption("🛡️ Senti-Quant Truth Engine | Built with ❤️ by Allan Bendatu")
