#!/usr/bin/env python3
"""
Manual cleanup script untuk menjalankan retention policy tanpa menunggu GitHub Actions
Gunakan: python manual_cleanup.py [retention_days]
Contoh: python manual_cleanup.py 30
"""

import sys
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

from src.data.database import init_db, SessionLocal
from src.data.crud import cleanup_old_data

if __name__ == "__main__":
    # Parse retention days dari argument
    retention_days = 30
    if len(sys.argv) > 1:
        try:
            retention_days = int(sys.argv[1])
        except ValueError:
            print(f"❌ Invalid argument. Usage: python manual_cleanup.py [retention_days]")
            sys.exit(1)

    # Init database
    init_db()
    db = SessionLocal()

    print("=" * 70)
    print("🧹 MANUAL DATA RETENTION CLEANUP")
    print("=" * 70)
    
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    print(f"\n📅 Retention Policy: {retention_days} hari")
    print(f"📅 Cutoff date (artikel lebih tua dihapus): {cutoff}")
    print(f"📅 Hari ini: {datetime.now(timezone.utc)}\n")

    # Run cleanup
    result = cleanup_old_data(db, retention_days=retention_days)

    print("\n" + "=" * 70)
    print("✅ CLEANUP RESULT")
    print("=" * 70)
    for key, value in result.items():
        if key == "error":
            print(f"❌ {key}: {value}")
        else:
            print(f"✓ {key}: {value}")

    db.close()
    
    print("\n✅ Cleanup selesai!")
    sys.exit(0)
