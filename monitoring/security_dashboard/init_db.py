import sqlite3
from config import DB_PATH

conn = sqlite3.connect(DB_PATH)

cur = conn.cursor()

# ----------------------------------
# Workflow Runs
# ----------------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS workflow_runs (
    run_id INTEGER PRIMARY KEY,
    workflow_name TEXT,
    branch TEXT,
    status TEXT,
    conclusion TEXT,
    run_created_at TEXT
)
""")

# ----------------------------------
# Processed Runs
# ----------------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS processed_runs (
    run_id INTEGER PRIMARY KEY,
    processed_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# ----------------------------------
# Security Findings
# ----------------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS findings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER,
    tool TEXT,
    severity TEXT,
    title TEXT,
    file_path TEXT,
    cwe TEXT,
    vulnerability_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()

print("Database initialized successfully.")