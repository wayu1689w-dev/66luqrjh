"""SUEA AI Dashboard — FastAPI Backend
เชื่อม Windsor.ai / Metricool / TikTok Marketing API / Plugin Pipeline"""

import os
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from contextlib import contextmanager

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from suea_ai.kpi_engine import get_kpi_status, get_policy, enforce_policy, compute_kpi_score, AGENTS
from suea_ai.ack_handler import init_ack_table, record_ack, get_ack_log, get_agent_ack_summary
from suea_ai.task_queue import init_task_table, enqueue, update_task, get_queue, queue_stats
from suea_ai.backup_worker import backup_now, list_backups

DB_PATH = Path(__file__).parent / "suea.db"
TZ_BKK = timezone(timedelta(hours=7))

APP_CONFIG = {
    "APP_NAME": "SUEA_AI",
    "APP_ENV": os.getenv("APP_ENV", "staging"),
    "HOST": "127.0.0.1",
    "PORT": 8766,
    "FREE_ONLY": True,
    "READ_ONLY": True,
    "PRIVATE_MODE": True,
    "AUTO_AD_SPEND": False,
    "AUTO_PUBLISH": False,
    "AUTO_CHANGE_PERMISSION": False,
    "AUTO_CONNECT_NEW_PLUGINS": False,
    "EXTERNAL_SHARING": False,
    "REQUIRE_OWNER_APPROVAL": True,
    "KPI_ENABLED": True,
    "ACK_REQUIRED": True,
    "REPORT_INTERVAL_SECONDS": 3600,
    "MAX_RETRIES": 3,
}

app = FastAPI(title="SUEA AI Dashboard", version="0.8.0")
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")


# ── Database ─────────────────────────────────────────────────────

def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            source TEXT,
            commission_rate REAL DEFAULT 0,
            gmv REAL DEFAULT 0,
            orders INTEGER DEFAULT 0,
            clicks INTEGER DEFAULT 0,
            conversion_rate REAL DEFAULT 0,
            score REAL DEFAULT 0,
            updated_at TEXT
        );
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT UNIQUE,
            title TEXT,
            views INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0,
            product_id INTEGER,
            source TEXT,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (product_id) REFERENCES products(id)
        );
        CREATE TABLE IF NOT EXISTS ads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_name TEXT,
            ad_group TEXT,
            spend REAL DEFAULT 0,
            impressions INTEGER DEFAULT 0,
            clicks INTEGER DEFAULT 0,
            conversions INTEGER DEFAULT 0,
            revenue REAL DEFAULT 0,
            roas REAL DEFAULT 0,
            source TEXT,
            date TEXT,
            updated_at TEXT
        );
        CREATE TABLE IF NOT EXISTS connector_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            connector TEXT UNIQUE,
            status TEXT DEFAULT 'disconnected',
            last_sync TEXT,
            records_synced INTEGER DEFAULT 0,
            error TEXT
        );
        CREATE TABLE IF NOT EXISTS sync_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            connector TEXT,
            action TEXT,
            status TEXT,
            detail TEXT,
            created_at TEXT
        );
        """)


@contextmanager
def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# ── Security Guardian ────────────────────────────────────────────

BLOCKED_ACTIONS = {"PUBLISH", "SEND", "ADS_WRITE", "AD_CREATE",
                   "COMMERCE_WRITE", "OAUTH_GRANT"}

def security_check(action: str) -> dict:
    action_upper = action.upper()
    if action_upper in BLOCKED_ACTIONS:
        return {"allowed": False, "reason": f"Action '{action}' blocked by v008 read-only policy"}
    return {"allowed": True}


# ── Connector Manager ────────────────────────────────────────────

CONNECTORS = {
    "windsor_tiktok_organic": {
        "name": "Windsor.ai TikTok Organic",
        "env_key": "WINDSOR_API_KEY",
        "fields": ["date", "source", "views", "likes", "comments", "shares", "followers", "video_title"],
    },
    "windsor_instagram": {
        "name": "Windsor.ai Instagram",
        "env_key": "WINDSOR_API_KEY",
        "fields": ["date", "source", "impressions", "reach", "likes", "comments", "followers"],
    },
    "windsor_facebook": {
        "name": "Windsor.ai Facebook Organic",
        "env_key": "WINDSOR_API_KEY",
        "fields": ["date", "source", "impressions", "reach", "reactions", "comments", "shares"],
    },
    "windsor_youtube": {
        "name": "Windsor.ai YouTube",
        "env_key": "WINDSOR_API_KEY",
        "fields": ["date", "source", "views", "watch_time", "likes", "comments", "subscribers"],
    },
    "metricool": {
        "name": "Metricool",
        "env_key": "METRICOOL_API_KEY",
        "fields": ["followers", "impressions", "engagement", "posts"],
    },
    "tiktok_ads": {
        "name": "TikTok Marketing API",
        "env_key": "TIKTOK_ACCESS_TOKEN",
        "fields": ["campaign", "spend", "impressions", "clicks", "conversions", "roas"],
    },
}


def check_connector_status(connector_id: str) -> dict:
    info = CONNECTORS.get(connector_id)
    if not info:
        return {"status": "unknown", "error": f"Connector '{connector_id}' not registered"}
    key = os.getenv(info["env_key"], "").strip()
    if not key:
        return {"status": "no_credential", "connector": connector_id,
                "env_key": info["env_key"]}
    return {"status": "ready", "connector": connector_id, "name": info["name"],
            "fields": info["fields"]}


# ── API Routes ───────────────────────────────────────────────────

@app.on_event("startup")
def on_startup():
    init_db()
    init_ack_table()
    init_task_table()


@app.get("/")
def root():
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/api/health")
def health():
    now = datetime.now(TZ_BKK).isoformat()
    return {"status": "ok", "version": "0.8.0", "timestamp": now,
            "db_exists": DB_PATH.exists()}


@app.get("/api/connectors")
def list_connectors():
    results = {}
    for cid in CONNECTORS:
        results[cid] = check_connector_status(cid)
    return results


@app.get("/api/connectors/{connector_id}/status")
def connector_status(connector_id: str):
    result = check_connector_status(connector_id)
    if result["status"] == "unknown":
        raise HTTPException(404, result["error"])
    return result


# ── Products ─────────────────────────────────────────────────────

@app.get("/api/products")
def list_products(limit: int = 50, sort: str = "score"):
    allowed_sorts = {"score", "gmv", "orders", "commission_rate", "name"}
    if sort not in allowed_sorts:
        sort = "score"
    with get_db() as db:
        rows = db.execute(
            f"SELECT * FROM products ORDER BY {sort} DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


@app.get("/api/products/{product_id}")
def get_product(product_id: int):
    with get_db() as db:
        row = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Product not found")
    return dict(row)


@app.get("/api/products/ranking")
def product_ranking(top: int = 10):
    with get_db() as db:
        rows = db.execute(
            "SELECT *, (gmv * commission_rate / 100) AS est_profit "
            "FROM products ORDER BY score DESC LIMIT ?", (top,)
        ).fetchall()
    return {"ranking": [dict(r) for r in rows], "count": len(rows)}


# ── Videos ───────────────────────────────────────────────────────

@app.get("/api/videos")
def list_videos(limit: int = 50, sort: str = "views"):
    allowed_sorts = {"views", "likes", "comments", "shares", "created_at"}
    if sort not in allowed_sorts:
        sort = "views"
    with get_db() as db:
        rows = db.execute(
            f"SELECT * FROM videos ORDER BY {sort} DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


@app.get("/api/videos/performance")
def video_performance():
    with get_db() as db:
        total = db.execute("SELECT COUNT(*) as cnt FROM videos").fetchone()["cnt"]
        agg = db.execute(
            "SELECT SUM(views) as total_views, SUM(likes) as total_likes, "
            "SUM(comments) as total_comments, SUM(shares) as total_shares, "
            "AVG(views) as avg_views FROM videos"
        ).fetchone()
    return {
        "total_videos": total,
        "total_views": agg["total_views"] or 0,
        "total_likes": agg["total_likes"] or 0,
        "total_comments": agg["total_comments"] or 0,
        "total_shares": agg["total_shares"] or 0,
        "avg_views": round(agg["avg_views"] or 0, 1),
    }


# ── Ads ──────────────────────────────────────────────────────────

@app.get("/api/ads")
def list_ads(limit: int = 50):
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM ads ORDER BY date DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


@app.get("/api/ads/profit")
def ads_profit():
    with get_db() as db:
        agg = db.execute(
            "SELECT SUM(spend) as total_spend, SUM(revenue) as total_revenue, "
            "SUM(conversions) as total_conversions, SUM(clicks) as total_clicks, "
            "SUM(impressions) as total_impressions FROM ads"
        ).fetchone()
    spend = agg["total_spend"] or 0
    revenue = agg["total_revenue"] or 0
    return {
        "total_spend": spend,
        "total_revenue": revenue,
        "profit": revenue - spend,
        "roas": round(revenue / spend, 2) if spend > 0 else 0,
        "total_conversions": agg["total_conversions"] or 0,
        "total_clicks": agg["total_clicks"] or 0,
        "cpc": round(spend / agg["total_clicks"], 2) if agg["total_clicks"] else 0,
    }


# ── Sync Log ─────────────────────────────────────────────────────

@app.get("/api/sync/log")
def sync_log(limit: int = 20):
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM sync_log ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


# ── Dashboard Summary ────────────────────────────────────────────

@app.get("/api/dashboard")
def dashboard_summary():
    with get_db() as db:
        products_count = db.execute("SELECT COUNT(*) as cnt FROM products").fetchone()["cnt"]
        videos_count = db.execute("SELECT COUNT(*) as cnt FROM videos").fetchone()["cnt"]
        ads_count = db.execute("SELECT COUNT(*) as cnt FROM ads").fetchone()["cnt"]
        top_product = db.execute(
            "SELECT name, score FROM products ORDER BY score DESC LIMIT 1"
        ).fetchone()
        top_video = db.execute(
            "SELECT title, views FROM videos ORDER BY views DESC LIMIT 1"
        ).fetchone()

    connectors_ready = sum(
        1 for cid in CONNECTORS if check_connector_status(cid)["status"] == "ready"
    )

    return {
        "timestamp": datetime.now(TZ_BKK).isoformat(),
        "products": products_count,
        "videos": videos_count,
        "ads_records": ads_count,
        "connectors_total": len(CONNECTORS),
        "connectors_ready": connectors_ready,
        "top_product": dict(top_product) if top_product else None,
        "top_video": dict(top_video) if top_video else None,
        "version": "v008",
    }


# ── Security endpoint ────────────────────────────────────────────

@app.post("/api/security/check")
async def check_security(request: Request):
    body = await request.json()
    action = body.get("action", "")
    return security_check(action)


@app.get("/api/security/policy")
def security_policy():
    return {
        "mode": "FREE_MODE_ONLY",
        "billing_enabled": False,
        "public_access": False,
        "auto_publish": False,
        "source_write": False,
        "blocked_actions": sorted(BLOCKED_ACTIONS),
        "kill_switches": 7,
        "rbac_tiers": 4,
        "risk_approval_threshold": "R3+",
    }


# ── KPI Engine ───────────────────────────────────────────────────

@app.get("/api/kpi")
def kpi_report():
    return {
        "mode": "LOCAL_ONLY",
        "read_only": True,
        "agents": get_kpi_status(),
        "policy": get_policy(),
    }


@app.get("/api/kpi/policy")
def kpi_policy():
    return get_policy()


@app.post("/api/kpi/enforce")
async def kpi_enforce(request: Request):
    body = await request.json()
    action = body.get("action", "")
    return enforce_policy(action)


@app.get("/api/config")
def app_config():
    return APP_CONFIG


# ── ACK Handler ──────────────────────────────────────────────────

@app.post("/api/ack")
async def submit_ack(request: Request):
    body = await request.json()
    agent = body.get("agent", "")
    task_id = body.get("task_id", "")
    evidence = body.get("evidence", "")
    if not agent or not task_id:
        raise HTTPException(400, "agent and task_id required")
    return record_ack(agent, task_id, evidence)


@app.get("/api/ack/log")
def ack_log(limit: int = 50):
    return get_ack_log(limit)


@app.get("/api/ack/summary")
def ack_summary():
    return get_agent_ack_summary()


# ── Task Queue ───────────────────────────────────────────────────

@app.post("/api/tasks")
async def create_task(request: Request):
    body = await request.json()
    return enqueue(
        task_type=body.get("task_type", "general"),
        description=body.get("description", ""),
        assigned_agent=body.get("assigned_agent", ""),
        priority=body.get("priority", 0),
    )


@app.get("/api/tasks")
def list_tasks(status: str = "", limit: int = 50):
    return get_queue(status, limit)


@app.get("/api/tasks/stats")
def task_stats():
    return queue_stats()


@app.patch("/api/tasks/{task_id}")
async def patch_task(task_id: int, request: Request):
    body = await request.json()
    return update_task(task_id, body.get("status", "DONE"), body.get("result", ""))


# ── Backup ───────────────────────────────────────────────────────

@app.post("/api/backup")
def do_backup():
    return backup_now()


@app.get("/api/backup/list")
def backup_list():
    return list_backups()
