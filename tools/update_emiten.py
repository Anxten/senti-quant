"""
Crontab setup for Linux VPS (run every Sunday at 01:00 AM WIB):

0 1 * * 0 cd /run/media/allan_bendatu/Windows/Git/senti-quant && /run/media/allan_bendatu/Windows/Git/senti-quant/venv/bin/python tools/update_emiten.py >> cron_log.txt 2>&1

Notes:
- Uses a public community GitHub raw JSON source.
- Replace RAW_EMITEN_URL later if you want another upstream source.
- The script will abort safely if the request fails, times out, or returns fewer than 100 entries.
"""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_PATH = BASE_DIR / "src" / "analysis" / "emiten_ihsg.json"
RAW_EMITEN_URL = "https://raw.githubusercontent.com/farizdotid/DAFTAR-SAHAM-INDONESIA/main/saham.json"
DEFAULT_TIMEOUT = 30
MIN_EXPECTED_ITEMS = 100


class EmitenUpdateError(RuntimeError):
    """Raised when the emiten update pipeline cannot continue safely."""


def fetch_emiten_payload(timeout: int = DEFAULT_TIMEOUT) -> Any:
    """Fetch raw payload from the public GitHub raw JSON source."""
    logger.info("Fetching emiten list from %s", RAW_EMITEN_URL)
    response = requests.get(
        RAW_EMITEN_URL,
        headers={
            "Accept": "application/json",
            "User-Agent": "senti-quant-emiten-updater/1.0",
        },
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def extract_items(payload: Any) -> List[Dict[str, Any]]:
    """Normalize the public JSON array into a list of dictionaries."""
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    raise EmitenUpdateError("Unsupported API response shape. Expected a JSON array of objects.")


def clean_company_name(name: str) -> str:
    """Remove corporate legal terms and normalize whitespace."""
    if not name:
        return ""

    cleaned = name.strip()
    patterns = [
        r"^PT\.?\s+",
        r"\s+PT\.?$",
        r"\s*\(Persero\)\s*",
        r"\s+Tbk\.?$",
        r"\s+Tbk$",
        r"\s*\(Tbk\)\s*",
    ]
    for pattern in patterns:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def transform_records(records: List[Dict[str, Any]]) -> Dict[str, str]:
    """Build a flat mapping of cleaned company names to ticker symbols."""
    result: Dict[str, str] = {}

    for record in records:
        company_name = str(record.get("Nama", "")).strip()
        ticker = str(record.get("Kode", "")).strip()

        if not company_name or not ticker:
            continue

        cleaned_name = clean_company_name(company_name)
        cleaned_ticker = re.sub(r"[^A-Z0-9]", "", ticker.upper()).strip()

        if not cleaned_name or not cleaned_ticker:
            continue

        result[cleaned_name] = cleaned_ticker

    return result


def save_mapping_atomically(mapping: Dict[str, str], output_path: Path) -> None:
    """Save JSON atomically so a failed run never overwrites good data."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_suffix(output_path.suffix + ".tmp")

    with temp_path.open("w", encoding="utf-8") as fh:
        json.dump(mapping, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")

    temp_path.replace(output_path)


def validate_mapping(mapping: Dict[str, str]) -> None:
    """Fail-safe checks before writing output."""
    if not isinstance(mapping, dict):
        raise EmitenUpdateError("Transformed mapping is not a dictionary.")

    if len(mapping) < MIN_EXPECTED_ITEMS:
        raise EmitenUpdateError(
            f"Aborting because only {len(mapping)} emiten entries were returned. Minimum expected is {MIN_EXPECTED_ITEMS}."
        )

    empty_keys = [k for k in mapping.keys() if not str(k).strip()]
    if empty_keys:
        raise EmitenUpdateError("Aborting because mapping contains empty company names.")


def main() -> int:
    try:
        payload = fetch_emiten_payload(timeout=DEFAULT_TIMEOUT)
        items = extract_items(payload)
        mapping = transform_records(items)
        validate_mapping(mapping)
        save_mapping_atomically(mapping, OUTPUT_PATH)
        logger.info("Successfully wrote %d emiten entries to %s", len(mapping), OUTPUT_PATH)
        return 0
    except requests.RequestException as exc:
        logger.error("API request failed or timed out: %s", exc)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.error("Invalid JSON response: %s", exc)
    except EmitenUpdateError as exc:
        logger.error("Configuration or validation error: %s", exc)
    except Exception as exc:
        logger.exception("Unexpected failure while updating emiten mapping: %s", exc)

    logger.error("No changes were written. Existing emiten_ihsg.json remains untouched.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
