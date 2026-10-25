import json, os, sqlite3
from pathlib import Path

DB_PATH = Path(os.getenv("SHILPSETU_DB", Path(__file__).resolve().parent / "data" / "products.sqlite3"))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as db:
        db.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT DEFAULT CURRENT_TIMESTAMP, data TEXT NOT NULL)")

def save_product(data: dict) -> dict:
    with connect() as db:
        cur = db.execute("INSERT INTO products(data) VALUES (?)", (json.dumps(data),))
        pid = cur.lastrowid
    return {"id": pid, **data}

def get_product(pid: int):
    with connect() as db:
        row = db.execute("SELECT id, created_at, data FROM products WHERE id=?", (pid,)).fetchone()
    if not row: return None
    return {"id": row["id"], "created_at": row["created_at"], **json.loads(row["data"])}

def list_products():
    with connect() as db:
        rows = db.execute("SELECT id, created_at, data FROM products ORDER BY id DESC").fetchall()
    return [{"id": r["id"], "created_at": r["created_at"], **json.loads(r["data"])} for r in rows]
