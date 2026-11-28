"""Backup Worker — สำรองข้อมูล SQLite อัตโนมัติ"""

import shutil
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "suea.db"
BACKUP_DIR = Path(__file__).parent / "backups"
TZ_BKK = timezone(timedelta(hours=7))
MAX_BACKUPS = 7


def backup_now() -> dict:
    if not DB_PATH.exists():
        return {"ok": False, "error": "Database not found"}

    BACKUP_DIR.mkdir(exist_ok=True)
    now = datetime.now(TZ_BKK)
    stamp = now.strftime("%Y%m%d_%H%M%S")
    dest = BACKUP_DIR / f"suea_{stamp}.db"

    conn = sqlite3.connect(str(DB_PATH))
    backup_conn = sqlite3.connect(str(dest))
    conn.backup(backup_conn)
    backup_conn.close()
    conn.close()

    _rotate_backups()

    return {
        "ok": True,
        "file": str(dest),
        "size_kb": round(dest.stat().st_size / 1024, 1),
        "timestamp": now.isoformat(),
    }


def _rotate_backups():
    if not BACKUP_DIR.exists():
        return
    files = sorted(BACKUP_DIR.glob("suea_*.db"), key=lambda p: p.name, reverse=True)
    for old in files[MAX_BACKUPS:]:
        old.unlink()


def list_backups() -> list:
    if not BACKUP_DIR.exists():
        return []
    files = sorted(BACKUP_DIR.glob("suea_*.db"), key=lambda p: p.name, reverse=True)
    return [
        {"name": f.name, "size_kb": round(f.stat().st_size / 1024, 1)}
        for f in files
    ]
