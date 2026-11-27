"""Data Integrity — SHA-256 checksums — Spec v008 Area 3
ตรวจว่าข้อมูลไม่ถูกแก้ไขโดยไม่ได้รับอนุญาต"""

import hashlib
import json
from datetime import datetime, timezone


def compute_hash(data: str | bytes) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def compute_file_hash(file_path: str) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def sign_record(record: dict) -> dict:
    payload = json.dumps(record, sort_keys=True, ensure_ascii=False)
    record["_hash"] = compute_hash(payload)
    record["_signed_at"] = datetime.now(timezone.utc).isoformat()
    return record


def verify_record(record: dict) -> tuple[bool, str]:
    stored = record.get("_hash")
    if not stored:
        return False, "ไม่มี hash — ยังไม่ได้ลงนาม"
    clean = {k: v for k, v in record.items() if k not in ("_hash", "_signed_at")}
    payload = json.dumps(clean, sort_keys=True, ensure_ascii=False)
    computed = compute_hash(payload)
    if computed == stored:
        return True, "ข้อมูลตรงกัน"
    return False, "ข้อมูลถูกแก้ไข — hash ไม่ตรง"


def compute_batch_hash(records: list[dict]) -> str:
    combined = json.dumps(records, sort_keys=True, ensure_ascii=False)
    return compute_hash(combined)
