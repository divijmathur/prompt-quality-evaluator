# app/app.py
import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
import os

from charts import bar_chart
from layout import render_header

# ---------- Config ----------
# Turn on by setting a Streamlit secret: DEBUG = true
DEBUG = bool(st.secrets.get("DEBUG", False))

# ---------- Paths ----------
APP_DIR  = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent
DB_PATH  = ROOT_DIR / "db" / "evals.db"
CSV_PATH = APP_DIR / "example_data.csv"   # fallback shipped in repo

# Optional override via secrets
if "DB_PATH" in st.secrets:
    DB_PATH = Path(st.secrets["DB_PATH"])

# ---------- Optional diagnostics (only in DEBUG) ----------
if DEBUG:
    st.write("📁 CWD:", os.getcwd())
    st.write("📄 __file__:", __file__)
    st.write("🗂️ App dir contents:", [p.name for p in APP_DIR.iterdir()])
    if (ROOT_DIR / "db").exists():
        st.write("🗂️ db dir contents:", [p.name for p in (ROOT_DIR / "db").iterdir()])

# ---------- Load data (silent fallback) ----------
df = None
data_source = None

# Prefer DB if present
try:
    if DB_PATH.exists():
        uri = f"file:{DB_PATH.as_posix()}?mode=ro"
        conn = sqlite3.connect(uri, uri=True, check_same_thread=False)
        df = pd.read_sql_query("SELECT * FROM evals", conn)
        data_source = f"SQLite · {DB_PATH.name}"
except Exception as e:
    if DEBUG:
        st.warning(f"SQLite open failed: {e}")

# Fallback to CSV if no DB (no warning in normal mode)
if df is None:
    if CSV_PATH.exists():
        df = pd.read_csv(CSV_PATH)
        data_source = f"CSV · {CSV_PATH.name}"
    else:
        st.error("No data found. Add db/evals.db or app/example_data.csv.")
        st.stop()

# ---------- Clean & enrich ----------
for col in ["clarity", "factuality", "style"]:
    if col in df.columns:
        # ensure numeric for metrics
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Drop rows that have none of the three scores
if all(c in df.columns for c in ["clarity", "factuality", "style"]):
    df = df.dropna(subset=["clarity", "factuality", "style"], how="all")

# Fill reason columns if present
for col in ["clarity_reason", "factuality_reason", "style_reason"]:
    if col in df.columns:
        df[col] = df[col].fillna("No explanation available.")

df["status"] = df.apply(
    lambda r: "✅ Scored" if pd.notnull(r.get("clarity")) else "⚠️ Missing",
    axis=1
)

# ---------- UI ----------
render_header()

# Small, unobtrusive badge instead of warnings
st.caption(f"Data source: **{data_source}**")

st.markdown("### 📊 Overall Summary")
c1, c2, c3 = st.columns(3)
c1.metric("Avg Clarity",     round(df["clarity"].mean(), 2)     if "clarity" in df else "—")
c2.metric("Avg Factuality",  round(df["factuality"].mean(), 2)  if "factuality" in df else "—")
c3.metric("Avg Style",       round(df["style"].mean(), 2)       if "style" in df else "—")

st.markdown("### 🧾 Full Evaluation Table")
st.dataframe(df, use_container_width=True)

st.markdown("### 📈 Scores by Prompt")
st.plotly_chart(bar_chart(df), use_container_width=True)

st.subheader("💬 Reasons for Each Score")
if all(c in df.columns for c in ["clarity_reason", "factuality_reason", "style_reason"]):
    for _, row in df.iterrows():
        p = row.get("prompt")
        if pd.isna(p): 
            continue
        with st.expander(str(p)[:100] + "..."):
            st.markdown(f"**Clarity ({row.get('clarity', '—')}):** {row['clarity_reason']}")
            st.markdown(f"**Factuality ({row.get('factuality', '—')}):** {row['factuality_reason']}")
            st.markdown(f"**Style ({row.get('style', '—')}):** {row['style_reason']}")
else:
    st.info("⚠️ No explanation columns found. Re-run the evaluator with reasons.")