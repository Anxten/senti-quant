import csv
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = BASE_DIR / "saham.csv"
OUTPUT_PATH = BASE_DIR / "src" / "analysis" / "emiten_ihsg.json"

def clean_company_name(name: str) -> str:
    cleaned = name.strip()
    patterns = [r"^PT\.?\s+", r"\s+PT\.?$", r"\s*\(Persero\)\s*", r"\s+Tbk\.?$", r"\s+Tbk$", r"\s*\(Tbk\)\s*"]
    for pattern in patterns:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", cleaned).strip()

def main():
    if not CSV_PATH.exists():
        print(f"ERROR: File {CSV_PATH} tidak ditemukan!")
        return 1

    mapping = {}
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            company_name = row.get("name", "")
            ticker = row.get("code", "")
            if company_name and ticker:
                clean_name = clean_company_name(company_name)
                mapping[clean_name] = ticker.strip().upper()

    if len(mapping) > 100:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2, sort_keys=True)
        print(f"SUKSES! {len(mapping)} emiten berhasil dibersihkan dan disimpan ke {OUTPUT_PATH}")
        return 0
    else:
        print(f"GAGAL: Hanya menemukan {len(mapping)} data. Proses dibatalkan.")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())