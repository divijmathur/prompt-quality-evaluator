# app/app.py
import streamlit as st
import pandas as pd
import sqlite3
from charts import bar_chart
from layout import render_header
from pathlib import Path

# --- Connect to database ---
conn = sqlite3.connect(Path("../db/evals.db"))
df = pd.read_sql_query("SELECT * FROM evals", conn)

# --- Clean and preprocess ---
# Drop rows where all scores are None/NaN
df = df.dropna(subset=["clarity", "factuality", "style"], how="all")

# Replace missing reason text with placeholders
for col in ["clarity_reason", "factuality_reason", "style_reason"]:
    if col in df.columns:
        df[col] = df[col].fillna("No explanation available.")

# Add a quick quality status column
df["status"] = df.apply(
    lambda r: "✅ Scored" if pd.notnull(r["clarity"]) else "⚠️ Missing", axis=1
)

# --- Render header ---
render_header()

# --- Overview Metrics ---
st.markdown("### 📊 Overall Summary")
col1, col2, col3 = st.columns(3)
col1.metric("Avg Clarity", round(df["clarity"].mean(), 2))
col2.metric("Avg Factuality", round(df["factuality"].mean(), 2))
col3.metric("Avg Style", round(df["style"].mean(), 2))

# --- Show full dataframe ---
st.dataframe(df)

# --- Bar chart visualization ---
st.plotly_chart(bar_chart(df))

# --- Reasons section ---
st.subheader("💬 Reasons for Each Score")
if all(col in df.columns for col in ["clarity_reason", "factuality_reason", "style_reason"]):
    for _, row in df.iterrows():
        # Defensive: skip rows that somehow have None in prompt
        if pd.isna(row["prompt"]):
            continue
        with st.expander(row["prompt"][:100] + "..."):
            st.markdown(f"**Clarity ({int(row['clarity']) if pd.notna(row['clarity']) else '—'}):** {row['clarity_reason']}")
            st.markdown(f"**Factuality ({int(row['factuality']) if pd.notna(row['factuality']) else '—'}):** {row['factuality_reason']}")
            st.markdown(f"**Style ({int(row['style']) if pd.notna(row['style']) else '—'}):** {row['style_reason']}")
else:
    st.info("⚠️ No explanation columns found. Re-run the evaluator with the updated rubric.")