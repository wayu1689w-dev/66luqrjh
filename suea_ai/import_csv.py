"""CSV Importer — นำเข้าข้อมูลสินค้าจากไฟล์ CSV เข้า SQLite"""

import csv
import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

DB_PATH = Path(__file__).parent / "suea.db"
TZ_BKK = timezone(timedelta(hours=7))


def import_products(csv_path: str):
    if not Path(csv_path).exists():
        print(f"ไม่พบไฟล์: {csv_path}")
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    cur.execute("""
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
    )
    """)

    now = datetime.now(TZ_BKK).isoformat()
    count = 0

    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("name", "").strip()
            if not name:
                continue

            gmv = float(row.get("gmv", 0) or 0)
            orders = int(row.get("orders", 0) or 0)
            clicks = int(row.get("clicks", 0) or 0)
            commission = float(row.get("commission_rate", 0) or 0)
            conversion = float(row.get("conversion_rate", 0) or 0)

            score = (gmv * 0.3) + (orders * 0.3) + (conversion * 0.2) + (commission * 0.2)

            cur.execute(
                "INSERT INTO products (name, category, source, commission_rate, "
                "gmv, orders, clicks, conversion_rate, score, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    name,
                    row.get("category", ""),
                    row.get("source", "csv"),
                    commission,
                    gmv,
                    orders,
                    clicks,
                    conversion,
                    round(score, 2),
                    now,
                ),
            )
            count += 1

    conn.commit()
    conn.close()
    print(f"นำเข้าสำเร็จ: {count} รายการ → {DB_PATH}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ใช้งาน: python import_csv.py <path_to_csv>")
        sys.exit(1)
    import_products(sys.argv[1])
