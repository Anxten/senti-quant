import sys
from pathlib import Path

# Add project root to sys.path so `src` imports resolve when running tests directly
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import re

print('running test_sentiment.py (lightweight local analyzer)')


def _normalize_text(text: str) -> str:
    return re.sub(r'\s+', ' ', text.lower()).strip()


SECTORAL_KEYWORDS = {
    'keuangan': ['bbri', 'bmri', 'bca', 'bbca', 'bank', 'bi rate', 'suku bunga', 'dividen', 'laba', 'npl'],
    'tech': ['goto', 'buka', 'mtdl', 'e-commerce', 'startup', 'platform digital', 'aplikasi'],
    'properti': ['pwon', 'ctra', 'bsde', 'properti', 'real estate', 'residensial', 'apartemen', 'landbank'],
}


ABSOLUTE_POSITIVE = [
    'laba bersih naik', 'laba naik', 'bagikan dividen', 'bagi dividen', 'rugi menurun'
]

ABSOLUTE_NEGATIVE = [
    'kerugian', 'kerugian kuartal', 'rugi', 'phk', 'phk massal', 'pemutusan hubungan kerja', 'pemangkasan'
]

POM_POM = ['cuan luber', 'meroket tajam', 'terbang tinggi', 'pasti untung', 'bandar']


def calculate_noise_probability(text: str) -> float:
    normalized = _normalize_text(text)
    uppercase_count = sum(1 for c in text if c.isupper())
    upper_ratio = uppercase_count / len(text) if len(text) else 0
    exclamation_count = len(re.findall(r'!', text))
    score = 0.0
    if upper_ratio > 0.15:
        score += 0.4
    if exclamation_count > 3:
        score += 0.3
    if any(p in normalized for p in POM_POM):
        score += 0.35
    if re.search(r'\b(pasti|jamin|dijamin|auto)\b', normalized):
        score += 0.2
    return min(score, 1.0)


def is_financial(text: str) -> bool:
    normalized = _normalize_text(text)
    sector_hits = 0
    for kws in SECTORAL_KEYWORDS.values():
        for k in kws:
            if re.search(rf'\b{re.escape(k)}\b', normalized):
                sector_hits += 1
    context_hits = sum(1 for w in ['saham', 'bursa', 'laba', 'dividen', 'investor'] if w in normalized)
    if sector_hits >= 2 or (sector_hits >= 1 and context_hits >= 1):
        return True
    if any(p in normalized for p in ABSOLUTE_POSITIVE):
        return True
    if any(p in normalized for p in ABSOLUTE_NEGATIVE):
        return True
    return False


def analyze_light(text: str, source_credibility: float = 0.6) -> dict:
    safe = text[:512]
    if not is_financial(safe):
        return {"sentiment_label": "IRRELEVANT", "confidence": 0.0, "noise_probability": 1.0, "source_credibility": source_credibility, "integrity_score": 0.0}
    normalized = _normalize_text(safe)
    if any(p in normalized for p in ABSOLUTE_POSITIVE):
        std_label = 'POSITIVE'
        confidence = 0.98
    elif any(p in normalized for p in ABSOLUTE_NEGATIVE):
        std_label = 'NEGATIVE'
        confidence = 0.90
    elif any(p in normalized for p in POM_POM):
        std_label = 'POSITIVE'
        confidence = 0.6
    else:
        std_label = 'NEUTRAL'
        confidence = 0.5

    noise = calculate_noise_probability(safe)
    scalar_map = {'NEGATIVE': -1, 'NEUTRAL': 0, 'POSITIVE': 1}
    s_value = scalar_map.get(std_label, 0)
    integrity = s_value * source_credibility * (1.0 - noise)
    return {"sentiment_label": std_label, "confidence": confidence, "noise_probability": noise, "source_credibility": source_credibility, "integrity_score": integrity}


def run_tests():
    samples = [
        ("Fundamental solid", "Laba bersih BBRI naik tajam, bagikan dividen besar."),
        ("Negatif riil", "GOTO catat kerugian kuartal 3, PHK massal."),
        ("Pom-pom manipulatif", "Saham BUKA bakal meroket tajam cuan luber, diborong bandar, pasti untung!")
    ]
    for label, text in samples:
        res = analyze_light(text, source_credibility=0.6)
        print('\n---')
        print(f'Sample: {label}')
        print(f'Text: {text}')
        print(f"Sentiment: {res['sentiment_label']}")
        print(f"Confidence: {res['confidence']:.3f}")
        print(f"Noise Probability: {res['noise_probability']:.3f}")
        print(f"Integrity Score: {res['integrity_score']:.3f}")


if __name__ == '__main__':
    run_tests()
