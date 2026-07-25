import streamlit as st
import pandas as pd
from utils.storage import get_records

st.title("📊 Your Progress")

records = get_records()

if not records:
    st.info("You haven't completed any practice attempts yet. Go try Reading, Listening, Writing, or Speaking!")
else:
    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    st.subheader("Band scores over time")
    chart_df = df.pivot_table(index="timestamp", columns="section", values="band_score", aggfunc="mean")
    st.line_chart(chart_df)

    st.subheader("Average band score by section")
    avg_df = df.groupby("section")["band_score"].mean().round(1)
    cols = st.columns(len(avg_df))
    for i, (section, score) in enumerate(avg_df.items()):
        with cols[i]:
            st.metric(section, score)

    st.subheader("Full history")
    display_df = df[["timestamp", "section", "band_score", "details"]].sort_values("timestamp", ascending=False)
    st.dataframe(display_df, use_container_width=True, hide_index=True)
