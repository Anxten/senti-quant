# Credibility Configuration
# Manual credibility scores untuk sumber berita Indonesia
# Score range: 0.0 (tidak kredibel) - 1.0 (sangat kredibel)

CREDIBILITY_SCORES = {
    # Tier 1: Media Mainstream Terpercaya (0.75 - 0.90)
    "www.cnbcindonesia.com": 0.80,
    "www.kompas.com": 0.85,
    "www.tempo.co": 0.85,
    "www.detik.com": 0.75,
    "www.kontan.co.id": 0.80,
    
    # Tier 2: Media Online Kredibel (0.60 - 0.75)
    "www.liputan6.com": 0.70,
    "www.tribunnews.com": 0.65,
    "www.okezone.com": 0.60,
    
    # Tier 3: Blog/Media Kecil (0.30 - 0.50)
    # Default untuk sumber tidak dikenal
}

# Default credibility untuk sumber baru
DEFAULT_CREDIBILITY = 0.50

def get_credibility(domain: str) -> float:
    """
    Ambil credibility score berdasarkan domain.
    Jika tidak ada di config, return default.
    """
    return CREDIBILITY_SCORES.get(domain, DEFAULT_CREDIBILITY)
