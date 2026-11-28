"""Task Queue — จัดคิวงานสำหรับ AI Agent"""

import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "suea.db"
TZ_BKK = timezone(timedelta(hours=7))


def init_task_table():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
    CREATE TABLE IF NOT EXISTS task_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_type TEXT NOT NULL,
        description TEXT,
        assigned_agent TEXT,
        status TEXT DEFAULT 'QUEUED',
        priority INTEGER DEFAULT 0,
        result TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    """)
    conn.commit()
    conn.close()


def enqueue(task_type: str, description: str, assigned_agent: str = "",
            priority: int = 0) -> dict:
    now = datetime.now(TZ_BKK).isoformat()
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.execute(
        "INSERT INTO task_queue (task_type, description, assigned_agent, "
        "priority, status, created_at, updated_at) VALUES (?, ?, ?, ?, 'QUEUED', ?, ?)",
        (task_type, description, assigned_agent, priority, now, now),
    )
    task_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {"id": task_id, "status": "QUEUED", "created_at": now}


def update_task(task_id: int, status: str, result: str = "") -> dict:
    now = datetime.now(TZ_BKK).isoformat()
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "UPDATE task_queue SET status = ?, result = ?, updated_at = ? WHERE id = ?",
        (status, result, now, task_id),
    )
    conn.commit()
    conn.close()
    return {"id": task_id, "status": status, "updated_at": now}


def get_queue(status: str = "", limit: int = 50) -> list:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    if status:
        rows = conn.execute(
            "SELECT * FROM task_queue WHERE status = ? ORDER BY priority DESC, created_at LIMIT ?",
            (status, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM task_queue ORDER BY priority DESC, created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def queue_stats() -> dict:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT COUNT(*) as total, "
        "SUM(CASE WHEN status='QUEUED' THEN 1 ELSE 0 END) as queued, "
        "SUM(CASE WHEN status='RUNNING' THEN 1 ELSE 0 END) as running, "
        "SUM(CASE WHEN status='DONE' THEN 1 ELSE 0 END) as done, "
        "SUM(CASE WHEN status='FAILED' THEN 1 ELSE 0 END) as failed "
        "FROM task_queue"
    ).fetchone()
    conn.close()
    return dict(row)
