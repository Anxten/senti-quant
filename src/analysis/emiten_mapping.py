"""
Dynamic Emiten Mapping loader.
Reads `emiten_ihsg.json` from repo root or `src/analysis` and exposes
`get_ticker_from_text(text)` for heuristic matching.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Optional, List

_MAPPING: Dict[str, str] = {}
_SORTED_NAMES: List[str] = []

# Try possible locations for emiten_ihsg.json
_POSSIBLE_PATHS = [Path.cwd() / "emiten_ihsg.json", Path(__file__).parent / "emiten_ihsg.json"]

for p in _POSSIBLE_PATHS:
    try:
        if p.exists():
            with p.open("r", encoding="utf-8") as fh:
                _MAPPING = json.load(fh)
            break
    except Exception:
        _MAPPING = {}

# Prepare sorted keys by length desc to avoid partial matches
_SORTED_NAMES = sorted(list(_MAPPING.keys()), key=len, reverse=True)


def get_ticker_from_text(text: str) -> Optional[str]:
    """
    Search for company names in `text` using the loaded mapping.
    Returns ticker code (e.g. 'ASII') or None.
    """
    if not text or not _MAPPING:
        return None
    lt = text.lower()
    for name in _SORTED_NAMES:
        if name.lower() in lt:
            return _MAPPING.get(name)
    return None
