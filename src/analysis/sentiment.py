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
            'bullish', 'meroket', 'cuan', 'laba naik', 'laba bersih naik', 'dividen',
            'bagikan dividen', 'rekor tertinggi', 'menguat tajam', 'akumulasi', 'terbang', 'rebound',
            'rugi menurun'
        ]
        self.negative_keywords = [
            'bearish', 'anjlok', 'rugi', 'jeblok', 'suspend',
            'arb', 'koreksi tajam', 'melemah', 'bangkrut', 'gagal bayar', 'longsor'
        ]

        self.sectoral_keywords = {
            'keuangan': ['bbri', 'bmri', 'bca', 'bbca', 'bank', 'bi rate', 'suku bunga', 'dividen', 'laba', 'npl'],
            'tech': ['goto', 'buka', 'mtdl', 'e-commerce', 'startup', 'platform digital', 'aplikasi'],
            'properti': ['pwon', 'ctra', 'bsde', 'properti', 'real estate', 'residensial', 'apartemen', 'landbank'],
            'energi': ['adaro', 'medco', 'batubara', 'migas', 'oil', 'gas', 'brent', 'bbm'],
            'industri': ['otomotif', 'manufaktur', 'pabrik', 'produksi', 'kapasitas', 'ekspansi'],
            'consumer': ['ritel', 'konsumsi', 'fmcg', 'makanan', 'minuman', 'volume penjualan'],
        }

        self.financial_context_keywords = [
            'saham', 'ihsg', 'emiten', 'bursa', 'bei', 'investor',
            'dividen', 'laba', 'rugi bersih', 'kuartal', 'rupiah',
            'obligasi', 'reksa dana', 'sbn', 'suku bunga', 'inflasi',
            'akuisisi', 'ipo', 'sekuritas', 'trader', 'fundamental', 'market cap'
        ]

        self.absolute_positive_phrases = [
            'laba bersih naik',
            'laba naik',
            'bagikan dividen',
            'bagi dividen',
            'rugi menurun',
            'margin membaik',
            'arus kas positif',
            'pertumbuhan pendapatan',
            'pendapatan naik',
            'profit naik'
        ]

        self.pom_pom_noise_phrases = [
            'cuan luber',
            'meroket tajam',
            'terbang tinggi',
            'pasti untung',
            'bandar',
            'cuan besar',
            'auto cuan',
            'untung gede',
            'saham gorengan',
            'naik gila-gilaan',
            'to the moon'
        ]

        self.noise_booster_patterns = [
            r'\bcuan\s+luber\b',
            r'\bmeroket\s+tajam\b',
            r'\bterbang\s+tinggi\b',
            r'\bpasti\s+untung\b',
            r'\bbandar\b',
            r'\bauto\s+cuan\b',
            r'\buntung\s+gede\b',
            r'\bsaham\s+gorengan\b',
            r'\bnaik\s+gila-gilaan\b',
            r'\bto\s+the\s+moon\b'
        ]

    def _normalize_text(self, text: str) -> str:
        return re.sub(r'\s+', ' ', text.lower()).strip()

    def _count_sector_matches(self, text: str) -> tuple[int, dict[str, int]]:
        normalized_text = self._normalize_text(text)
        sector_hits: dict[str, int] = {}
        total_hits = 0

        for sector, keywords in self.sectoral_keywords.items():
            hits = 0
            for keyword in keywords:
                keyword_norm = keyword.lower()
                pattern = rf'\b{re.escape(keyword_norm)}\b'

                if re.search(pattern, normalized_text):
                    hits += 1

            if hits:
                sector_hits[sector] = hits
                total_hits += hits

        return total_hits, sector_hits

    def _has_absolute_positive_signal(self, text: str) -> bool:
        normalized_text = self._normalize_text(text)
        return any(phrase in normalized_text for phrase in self.absolute_positive_phrases)

    def _has_absolute_negative_signal(self, text: str) -> bool:
        normalized_text = self._normalize_text(text)
        negative_signals = [
            'laba turun', 'rugi naik', 'penurunan laba', 'pemangkasan dividen',
            'kinerja memburuk', 'ditekan', 'tekanan jual', 'gagal bayar'
        ]
        return any(phrase in normalized_text for phrase in negative_signals)

    def _check_financial_dictionary(self, text: str) -> str:
        """Mengecek apakah ada kata kunci saham yang sangat kuat di dalam teks."""
        text_lower = self._normalize_text(text)
        
        # Cek kata positif dulu
        if any(word in text_lower for word in self.positive_keywords):
            return "POSITIVE"
            
        # Cek kata negatif
        if any(word in text_lower for word in self.negative_keywords):
            return "NEGATIVE"
            
        # Kalau tidak ada kata kunci sakti, kembalikan None (Biar AI BERT yang mikir)
        return None
    
    def _is_financial_news(self, text: str) -> bool:
        """Memeriksa apakah artikel benar-benar membahas keuangan/saham."""
        text_lower = self._normalize_text(text)
        sector_hits, _ = self._count_sector_matches(text_lower)
        context_hits = sum(1 for word in self.financial_context_keywords if word in text_lower)

        if sector_hits >= 2:
            return True

        if sector_hits >= 1 and context_hits >= 1:
            return True

        if self._has_absolute_positive_signal(text_lower):
            return True

        if self._has_absolute_negative_signal(text_lower):
            return True

        ticker_pattern = r'\b[A-Z]{3,5}\b'
        if re.search(ticker_pattern, text):
            return True

        return False
    
    def _calculate_noise_probability(self, text: str) -> float:
        """
        [Inovasi Senti-Quant] - De-noising Logic.
        Menghitung seberapa 'clickbait' atau manipulatif teks tersebut.
        Versi ini menambahkan deteksi pom-pom saham dan superlatif kosong.
        """
        if not text:
            return 1.0  # 100% noise kalau kosong

        normalized_text = self._normalize_text(text)
            
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

        if any(phrase in normalized_text for phrase in self.pom_pom_noise_phrases):
            noise_score += 0.35

        booster_hits = sum(1 for pattern in self.noise_booster_patterns if re.search(pattern, normalized_text))
        if booster_hits:
            noise_score += min(0.25 * booster_hits, 0.5)

        if re.search(r'\b(pasti|jamin|dijamin|terbukti|auto|mustahil rugi)\b', normalized_text):
            noise_score += 0.2
            
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
        
        # 0. GATEKEEPER: Buang berita non-finansial
        if not self._is_financial_news(safe_text):
            return {
                "sentiment_label": "IRRELEVANT",
                "confidence": 0.0,
                "noise_probability": 1.0,
                "source_credibility": source_credibility,
                "integrity_score": 0.0
            }
        
        # 1. CEK FRASE POSITIF ABSOLUT TERLEBIH DAHULU (Bypass AI jika ketemu)
        if self._has_absolute_positive_signal(safe_text):
            std_label = "POSITIVE"
            confidence = 0.98
            logger.info("💡 Absolute positive financial signal terdeteksi, bypass Indo-BERT.")
        else:
            # 2. CEK KAMUS SAHAM TERLEBIH DAHULU (Bypass AI jika ketemu)
            heuristic_label = self._check_financial_dictionary(safe_text)

            if heuristic_label:
                std_label = heuristic_label
                confidence = 0.95
                logger.info(f"💡 Heuristik Terdeteksi! Kata kunci memicu sentimen: {std_label}")
            else:
                # 3. JIKA TIDAK ADA DI KAMUS, BIARKAN AI BERT BEKERJA
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