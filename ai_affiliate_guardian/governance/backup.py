"""Backup — สำรองข้อมูล"""

import json
import shutil
from pathlib import Path
from datetime import datetime, timezone

STORAGE_DIR = Path(__file__).parent.parent / "storage"
BACKUP_DIR = STORAGE_DIR / "backups"


def create_backup():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / ts
    backup_path.mkdir(exist_ok=True)
    for f in STORAGE_DIR.glob("*.json"):
        shutil.copy2(f, backup_path / f.name)
    return str(backup_path)


def list_backups():
    if not BACKUP_DIR.exists():
        return []
    return sorted([d.name for d in BACKUP_DIR.iterdir() if d.is_dir()], reverse=True)
