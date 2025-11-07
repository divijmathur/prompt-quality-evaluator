# app/app.py
import streamlit as st
import pandas as pd
import sqlite3
import os
from pathlib import Path

from charts import bar_chart
from layout import render_header

# ---- Resolve paths deterministically ----
APP_DIR = Path(__file__).resolve().parent         # .../app
ROOT_DIR = APP_DIR.parent                         # repo root
DB_PATH = ROOT_DIR / "db" / "evals.db"            # .../db/evals.db

# Optional: override via secrets (useful later)
override = st.secrets.get("DB_PATH") if hasattr(st, "secrets") else None
if override:
    DB_PATH = Path(override)

# ---- Debug: show what the cloud sees (remove later if you want) ----
st.write("📁 CWD:", os.getcwd())
st.write("📄 __file__:", __file__)
st.write("🗂️ App dir contents:", [p.name for p in APP_DIR.iterdir()])
if (ROOT_DIR / "db").exists():
    st.write("🗂️ db dir contents:", [p.name for p in (ROOT_DIR / "db").iterdir()])

# ---- Try to open SQLite DB in read-only mode; fallback to CSV ----
df = None
try:
    if DB_PATH.exists():
        # Read-only mode avoids write errors on Streamlit Cloud
        uri = f"file:{DB_PATH.as_posix()}?mode=ro"
        conn = sqlite3.connect(uri, uri=True, check_same_thread=False)
        df = pd.read_sql_query("SELECT * FROM evals", conn)
    else:
        st.warning(f"Database not found at: {DB_PATH}. Loading fallback CSV.")
except Exception as e:
    st.warning(f"Could not open SQLite DB ({DB_PATH}). Error: {e}\nLoading fallback CSV.")

# ---- Fallback CSV (ship a tiny sample to app/example_data.csv) ----
if df is None:
    csv_fallback = APP_DIR / "example_data.csv"
    if csv_fallback.exists():
        df = pd.read_csv(csv_fallback)
    else:
        st.error("No DB and no fallback CSV found. Add db/evals.db or app/example_data.csv.")
        st.stop()

# ---- Clean & UI below ----
df = df.dropna(subset=["clarity", "factuality", "style"], how="all")
for col in ["clarity_reason", "factuality_reason", "style_reason"]:
    if col in df.columns:
        df[col] = df[col].fillna("No explanation available.")
df["status"] = df.apply(lambda r: "✅ Scored" if pd.notnull(r.get("clarity")) else "⚠️ Missing", axis=1)

render_header()

st.markdown("### 📊 Overall Summary")
c1, c2, c3 = st.columns(3)
c1.metric("Avg Clarity", round(df["clarity"].mean(), 2) if "clarity" in df else "—")
c2.metric("Avg Factuality", round(df["factuality"].mean(), 2) if "factuality" in df else "—")
c3.metric("Avg Style", round(df["style"].mean(), 2) if "style" in df else "—")

st.markdown("### 🧾 Full Evaluation Table")
st.dataframe(df)

st.markdown("### 📈 Scores by Prompt")
st.plotly_chart(bar_chart(df))

st.subheader("💬 Reasons for Each Score")
if all(c in df.columns for c in ["clarity_reason", "factuality_reason", "style_reason"]):
    for _, row in df.iterrows():
        p = row.get("prompt")
        if pd.isna(p): 
            continue
        with st.expander(str(p)[:100] + "..."):
            st.markdown(f"**Clarity ({row['clarity'] if 'clarity' in row else '—'}):** {row['clarity_reason']}")
            st.markdown(f"**Factuality ({row['factuality'] if 'factuality' in row else '—'}):** {row['factuality_reason']}")
            st.markdown(f"**Style ({row['style'] if 'style' in row else '—'}):** {row['style_reason']}")
else:
    st.info("⚠️ No explanation columns found. Re-run the evaluator with reasons.")