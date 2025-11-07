# app/charts.py
import plotly.express as px
import pandas as pd

def bar_chart(df: pd.DataFrame):
    melted = df.melt(id_vars=["prompt"], value_vars=["clarity", "factuality", "style"])
    return px.bar(
        melted,
        x="prompt", y="value", color="variable",
        barmode="group",
        title="Evaluation Scores by Prompt"
    )