"""
Emiten Mapping Dictionary
Mapping nama perusahaan Indonesia ke kode ticker IHSG.
Digunakan untuk heuristic extraction di Telegram broadcaster.
"""

EMITEN_MAPPING = {
    # Bank & Finance
    "Bank Rakyat Indonesia": "BBRI",
    "Bank Central Asia": "BBCA",
    "Bank Mandiri": "BMRI",
    "Bank Negara Indonesia": "BBNI",
    "BNI": "BBNI",
    "BRI": "BBRI",
    "BCA": "BBCA",
    
    # Automotive
    "Astra International": "ASII",
    "Astra": "ASII",
    "Indomobil": "INDOM",
    
    # Technology & E-Commerce
    "GoTo": "GOTO",
    "PT GoTo": "GOTO",
    "Gojek": "GOTO",
    "Tokopedia": "GOTO",
    
    # Energy & Mining
    "Pertamina": "PTRA",
    "PT Pertamina": "PTRA",
    "Medco Energi": "MEDC",
    
    # Consumer & Retail
    "Ramayana Lestari": "RALS",
    "Ramayana": "RALS",
    "Matahari": "MAPI",
    "Matahari Department Store": "MAPI",
    "Kalbe Farma": "KLBF",
    
    # Real Estate & Construction
    "Semen Indonesia": "SMGR",
    "Semen Gresik": "SMGR",
    "Lippo Karawaci": "LPKR",
    
    # Telecommunications
    "Telekomunikasi Indonesia": "TLKM",
    "Telkom": "TLKM",
    "Indosat": "ISAT",
    
    # Tobacco
    "HM Sampoerna": "HMSP",
    "Gudang Garam": "GGRM",
    
    # Media & Publishing
    "Media Nusantara Citra": "MNCN",
    "MNC": "MNCN",
}

def get_ticker_from_emiten_name(text: str) -> str | None:
    """
    Search for company name in mapping dictionary (case-insensitive).
    
    Args:
        text: Title, content, or any text to search
        
    Returns:
        Ticker code (e.g. "ASII") if found, None otherwise
    """
    if not text:
        return None
    
    text_lower = text.lower()
    
    # Search for matching company names (prioritize longer names first to avoid partial matches)
    sorted_names = sorted(EMITEN_MAPPING.keys(), key=len, reverse=True)
    
    for company_name in sorted_names:
        if company_name.lower() in text_lower:
            return EMITEN_MAPPING[company_name]
    
    return None
