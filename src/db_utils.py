# src/db_utils.py
import sqlite3
import pandas as pd
from pathlib import Path

def init_db(db_path: Path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS evals (
        id INTEGER PRIMARY KEY,
        prompt TEXT,
        response TEXT,
        clarity INTEGER,
        factuality INTEGER,
        style INTEGER,
        clarity_reason TEXT,
        factuality_reason TEXT,
        style_reason TEXT
    )
    """)
    conn.commit()
    conn.close()
    print("✅ Database initialized.")

def insert_from_csv(csv_path: Path, db_path: Path):
    df = pd.read_csv(csv_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # detect schema: if "scores" exists, handle old version; else handle new version
    if "scores" in df.columns:
        import json
        for _, row in df.iterrows():
            sc = json.loads(row["scores"])
            cur.execute(
                "INSERT INTO evals (prompt, response, clarity, factuality, style) VALUES (?, ?, ?, ?, ?)",
                (row["prompt"], row["response"], sc["clarity"], sc["factuality"], sc["style"])
            )
    else:
        for _, row in df.iterrows():
            cur.execute(
                """INSERT INTO evals
                (prompt, response, clarity, factuality, style,
                 clarity_reason, factuality_reason, style_reason)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    row["prompt"],
                    row["response"],
                    row.get("clarity"),
                    row.get("factuality"),
                    row.get("style"),
                    row.get("clarity_reason", ""),
                    row.get("factuality_reason", ""),
                    row.get("style_reason", "")
                )
            )

    conn.commit()
    conn.close()
    print(f"✅ Inserted {len(df)} rows into {db_path}")