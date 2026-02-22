import logging
import torch
import re
from transformers import pipeline

logger = logging.getLogger(__name__)

class TruthEngineAI:
    """
    Core AI Module untuk Senti-Quant.
    Menggabungkan Model Transformer (NLP) dengan Heuristic Logic (De-noising).
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

    def analyze(self, text: str) -> dict:
        """
        Menganalisis teks dan mengembalikan Sentiment + Integrity Score.
        """
        # Truncate teks ke 512 karakter pertama (batasan token BERT) agar cepat dan tidak crash
        safe_text = text[:512]
        
        # 1. Dapatkan Sentimen dari AI
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

        # 2. Hitung Truth Metrics (Inovasi kita)
        noise_prob = self._calculate_noise_probability(safe_text)
        
        # Konversi sentimen ke skalar untuk perhitungan (-1, 0, 1)
        scalar_map = {"NEGATIVE": -1, "NEUTRAL": 0, "POSITIVE": 1}
        s_value = scalar_map.get(std_label, 0)
        
        # Rumus Integritas (S_i * (1 - N_i)) - Mengurangi bobot sentimen jika noise tinggi
        integrity_score = s_value * (1.0 - noise_prob)

        return {
            "sentiment_label": std_label,
            "confidence": confidence,
            "noise_probability": noise_prob,
            "integrity_score": integrity_score
        }
    

