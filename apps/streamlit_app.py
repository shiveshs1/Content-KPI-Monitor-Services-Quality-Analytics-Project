#!/usr/bin/env python3
from __future__ import annotations
import sqlite3
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "content_kpi.db"

st.set_page_config(page_title="Content KPI Monitor", page_icon="📈", layout="wide")
st.title("📈 Mini Content KPI Monitor")

# Plotly settings (recommended by Streamlit going forward)
PLOTLY_CFG = {"displayModeBar": True, "responsive": True}

@st.cache_data(show_spinner=False)
def load_df() -> pd.DataFrame:
    if not DB_PATH.exists():
        return pd.DataFrame()
    con = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query("SELECT * FROM v_content_kpi", con, parse_dates=["date"])
    finally:
        con.close()
    return df

df = load_df()
if df.empty:
    st.info("No data yet. Run: `python src/generate_sample.py` then `python src/ingest_and_export.py`.", icon="ℹ️")
    st.stop()

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    min_d, max_d = df["date"].min(), df["date"].max()
    date_range = st.date_input("Date range", (min_d, max_d), min_value=min_d, max_value=max_d)
    cats = ["All"] + sorted(df["category"].unique().tolist())
    cat = st.selectbox("Category", cats)
    q = st.text_input("Search title", "")

mask = (df["date"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
if cat != "All":
    mask &= df["category"].eq(cat)
if q.strip():
    mask &= df["title"].str.contains(q, case=False, na=False)

dff = df.loc[mask].copy()
if dff.empty:
    st.warning("No rows match your filters.")
    st.stop()

# KPI tiles
col1, col2, col3, col4, col5 = st.columns(5)
impr = int(dff["impressions"].sum())
clk = int(dff["clicks"].sum())
conv = int(dff["conversions"].sum())
ctr = (clk / impr) if impr else 0
cr = (conv / clk) if clk else 0
dwell = dff["avg_dwell_sec"].mean()
bounce = dff["bounce_rate"].mean()

col1.metric("Impressions", f"{impr:,}")
col2.metric("Clicks", f"{clk:,}", f"{ctr*100:.1f}% CTR")
col3.metric("Conversions", f"{conv:,}", f"{cr*100:.1f}% CR")
col4.metric("Avg Dwell (s)", f"{dwell:.1f}")
col5.metric("Bounce Rate", f"{bounce*100:.1f}%")

st.divider()

# Charts (no deprecated kwargs; rely only on config=)
left, right = st.columns(2)

with left:
    daily = dff.groupby("date", as_index=False).agg(ctr=("ctr", "mean"))
    fig = px.line(daily, x="date", y="ctr", title="CTR Over Time", markers=True)
    fig.update_yaxes(tickformat=".1%")
    st.plotly_chart(fig, config=PLOTLY_CFG)

with right:
    by_cat = dff.groupby("category", as_index=False).agg(cr=("conversion_rate","mean"))
    fig2 = px.bar(by_cat, x="category", y="cr", title="Conversion Rate by Category")
    fig2.update_yaxes(tickformat=".1%")
    st.plotly_chart(fig2, config=PLOTLY_CFG)

st.subheader("Top Content (by CTR)")
top = dff.sort_values("ctr", ascending=False)[
    ["date","title","category","impressions","clicks","conversions","ctr","conversion_rate","avg_dwell_sec","bounce_rate"]
].head(20)
top = top.rename(columns={"ctr":"CTR","conversion_rate":"CR","avg_dwell_sec":"Dwell (s)","bounce_rate":"Bounce"})
top["CTR"] = top["CTR"].map(lambda x: f"{x:.2%}")
top["CR"] = top["CR"].map(lambda x: f"{x:.2%}")
top["Bounce"] = top["Bounce"].map(lambda x: f"{x:.1%}")
st.dataframe(top, hide_index=True)

st.caption("Built with SQLite + Streamlit • KPIs: CTR, CR, Dwell Time, Bounce Rate")
