"""Checkpoint Manager — บันทึกสถานะระบบเป็นระยะ"""

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

TZ_BKK = timezone(timedelta(hours=7))

CHECKPOINT_DIR = Path(__file__).parent.parent / "backups" / "checkpoints"


class CheckpointManager:
    def __init__(self, checkpoint_dir: Path = CHECKPOINT_DIR):
        self._dir = checkpoint_dir
        self._dir.mkdir(parents=True, exist_ok=True)
        self._checkpoints: list[dict] = []

    def create_checkpoint(self, state: dict, label: str = "") -> dict:
        ts = datetime.now(TZ_BKK)
        filename = f"checkpoint_{ts.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self._dir / filename
        checkpoint = {
            "label": label or f"auto_{len(self._checkpoints)}",
            "timestamp": ts.isoformat(),
            "state": state,
        }
        filepath.write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2))
        meta = {
            "label": checkpoint["label"],
            "timestamp": checkpoint["timestamp"],
            "file": str(filepath),
            "size_kb": round(filepath.stat().st_size / 1024, 1),
        }
        self._checkpoints.append(meta)
        return meta

    def list_checkpoints(self, limit: int = 20) -> list:
        files = sorted(self._dir.glob("checkpoint_*.json"), reverse=True)
        results = []
        for f in files[:limit]:
            results.append({
                "file": f.name,
                "size_kb": round(f.stat().st_size / 1024, 1),
                "modified": datetime.fromtimestamp(
                    f.stat().st_mtime, tz=TZ_BKK
                ).isoformat(),
            })
        return results

    def load_checkpoint(self, filename: str) -> dict | None:
        filepath = self._dir / filename
        if not filepath.exists():
            return None
        return json.loads(filepath.read_text())

    def cleanup(self, keep: int = 10) -> dict:
        files = sorted(self._dir.glob("checkpoint_*.json"))
        removed = 0
        while len(files) > keep:
            files[0].unlink()
            files.pop(0)
            removed += 1
        return {"removed": removed, "remaining": len(files)}
