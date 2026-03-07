import logging
import torch
import re
from transformers import pipeline

logger = logging.getLogger(__name__)

class TruthEngineAI:
    """
    Core AI Module untuk Senti-Quant.
    Menggabungkan Model Transformer (NLP) dengan Heuristic Logic (De-noising)
    dan Kamus Finansial (Financial Dictionary).
    """
    
    def __init__(self):
        logger.info("🧠 Memuat model NLP Transformer... (Mungkin butuh waktu beberapa detik)")
        
        # Deteksi otomatis apakah laptop punya GPU (CUDA/MPS) atau pakai CPU
        self.device = 0 if torch.cuda.is_available() else -1
        
        # Kita gunakan pre-trained model Bahasa Indonesia yang solid untuk sentimen
        self.model_name = "mdhugol/indonesia-bert-sentiment-classification"
        
        try:
            # Inisialisasi Hugging Face Pipeline
            self.nlp_pipeline = pipeline(
                "sentiment-analysis", 
                model=self.model_name, 
                tokenizer=self.model_name,
                device=self.device
            )
            logger.info("✅ Model NLP berhasil dimuat ke memori!")
        except Exception as e:
            logger.error(f"❌ Gagal memuat model: {e}")
            raise e
            
        # --- KAMUS SAHAM (FINANCIAL HEURISTICS) ---
        # Kata kunci yang memaksa AI untuk mengubah sentimen
        self.positive_keywords = [
            'bullish', 'meroket', 'cuan', 'laba naik', 'dividen', 
            'rekor tertinggi', 'menguat tajam', 'akumulasi', 'terbang', 'rebound'
        ]
        self.negative_keywords = [
            'bearish', 'anjlok', 'rugi', 'jeblok', 'suspend', 
            'arb', 'koreksi tajam', 'melemah', 'bangkrut', 'gagal bayar', 'longsor'
        ]

    def _check_financial_dictionary(self, text: str) -> str:
        """Mengecek apakah ada kata kunci saham yang sangat kuat di dalam teks."""
        text_lower = text.lower()
        
        # Cek kata positif dulu
        if any(word in text_lower for word in self.positive_keywords):
            return "POSITIVE"
            
        # Cek kata negatif
        if any(word in text_lower for word in self.negative_keywords):
            return "NEGATIVE"
            
        # Kalau tidak ada kata kunci sakti, kembalikan None (Biar AI BERT yang mikir)
        return None
    
    def _calculate_noise_probability(self, text: str) -> float:
        """
        [Inovasi Senti-Quant] - De-noising Logic.
        Menghitung seberapa 'clickbait' atau manipulatif teks tersebut.
        Ini versi V1 (Heuristic Logic): Mengecek tanda baca berlebih dan huruf kapital berlebih.
        """
        if not text:
            return 1.0  # 100% noise kalau kosong
            
        # Hitung persentase huruf kapital
        uppercase_count = sum(1 for c in text if c.isupper())
        upper_ratio = uppercase_count / len(text) if len(text) > 0 else 0
        
        # Hitung jumlah tanda seru (biasanya dipakai untuk pump & dump / FOMO)
        exclamation_count = len(re.findall(r'!', text))
        
        noise_score = 0.0
        
        # Logika Kritis (Creativity + Logic = Innovation)
        if upper_ratio > 0.15:  # Jika lebih dari 15% teks adalah huruf besar
            noise_score += 0.4
        if exclamation_count > 3:  # Terlalu banyak tanda seru
            noise_score += 0.3
            
        # Batasi maksimal 1.0 (100%)
        return min(noise_score, 1.0)

    def analyze(self, text: str, source_credibility: float = 0.5) -> dict:
        """
        Menganalisis teks dan mengembalikan Sentiment + Integrity Score.
        
        Args:
            text: Konten artikel yang akan dianalisis
            source_credibility: Kredibilitas sumber (0.0 - 1.0), default 0.5
        
        Returns:
            Dict dengan sentiment_label, confidence, integrity_score, dll
        """
        # Truncate teks ke 512 karakter pertama (batasan token BERT) agar cepat dan tidak crash
        safe_text = text[:512]
        
        # 1. CEK KAMUS SAHAM TERLEBIH DAHULU (Bypass AI jika ketemu)
        heuristic_label = self._check_financial_dictionary(safe_text)
        
        if heuristic_label:
            std_label = heuristic_label
            confidence = 0.95 # Anggap sangat yakin karena cocok dengan kamus
            logger.info(f"💡 Heuristik Terdeteksi! Kata kunci memicu sentimen: {std_label}")
        else:
            # 2. JIKA TIDAK ADA DI KAMUS, BIARKAN AI BERT BEKERJA
            ai_result = self.nlp_pipeline(safe_text)[0]
            raw_label = ai_result['label']
            confidence = ai_result['score']
            
            # Standarisasi Label (karena tiap model beda output nama labelnya)
            label_map = {
                "LABEL_0": "NEGATIVE",
                "LABEL_1": "NEUTRAL",
                "LABEL_2": "POSITIVE",
                "negative": "NEGATIVE",
                "neutral": "NEUTRAL",
                "positive": "POSITIVE",
                "label_0": "NEGATIVE",
                "label_1": "NEUTRAL",
                "label_2": "POSITIVE"
            }
            std_label = label_map.get(raw_label, raw_label.upper())

        # 3. Hitung Truth Metrics (Inovasi kita)
        noise_prob = self._calculate_noise_probability(safe_text)
        
        # Konversi sentimen ke skalar untuk perhitungan (-1, 0, 1)
        scalar_map = {"NEGATIVE": -1, "NEUTRAL": 0, "POSITIVE": 1}
        s_value = scalar_map.get(std_label, 0)
        
        # 4. Rumus Truth Engine Lengkap: Si × Ci × (1 - Ni)
        # Si = Sentiment Score
        # Ci = Source Credibility
        # Ni = Noise Probability
        integrity_score = s_value * source_credibility * (1.0 - noise_prob)

        return {
            "sentiment_label": std_label,
            "confidence": confidence,
            "noise_probability": noise_prob,
            "source_credibility": source_credibility,
            "integrity_score": integrity_score
        }