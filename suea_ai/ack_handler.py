"""ACK Handler — ตรวจสอบการตอบรับจาก AI Agent"""

import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "suea.db"
TZ_BKK = timezone(timedelta(hours=7))


def init_ack_table():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
    CREATE TABLE IF NOT EXISTS ack_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent TEXT NOT NULL,
        task_id TEXT,
        ack_status TEXT DEFAULT 'PENDING',
        evidence TEXT,
        kpi_score REAL,
        created_at TEXT,
        updated_at TEXT
    )
    """)
    conn.commit()
    conn.close()


def record_ack(agent: str, task_id: str, evidence: str = "") -> dict:
    now = datetime.now(TZ_BKK).isoformat()
    status = "ACK" if evidence else "NO_EVIDENCE"
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "INSERT INTO ack_log (agent, task_id, ack_status, evidence, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (agent, task_id, status, evidence, now, now),
    )
    conn.commit()
    conn.close()
    return {"agent": agent, "task_id": task_id, "status": status, "timestamp": now}


def get_ack_log(limit: int = 50) -> list:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM ack_log ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_agent_ack_summary() -> list:
    from kpi_engine import AGENTS
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    result = []
    for agent in AGENTS:
        row = conn.execute(
            "SELECT COUNT(*) as total, "
            "SUM(CASE WHEN ack_status='ACK' THEN 1 ELSE 0 END) as acked "
            "FROM ack_log WHERE agent = ?", (agent,)
        ).fetchone()
        result.append({
            "agent": agent,
            "total_tasks": row["total"],
            "acked": row["acked"],
            "rate": round(row["acked"] / row["total"] * 100, 1) if row["total"] > 0 else 0,
        })
    conn.close()
    return result
