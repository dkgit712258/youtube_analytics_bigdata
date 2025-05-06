import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from cassandra.cluster import Cluster

# Connect to Cassandra
cluster = Cluster(['youtube_trending_analytics-testing-cassandra-1'])  # or '172.19.0.3'
session = cluster.connect('youtube')

# Query trending videos
rows = session.execute("""
    SELECT video_id, title, views, publish_time
    FROM trending_videos
""")

# Convert to DataFrame
data = [(row.video_id, row.title, row.views, row.publish_time) for row in rows]
df = pd.DataFrame(data, columns=["video_id", "title", "views", "publish_time"])

# Convert publish_time to datetime if not already
df["publish_time"] = pd.to_datetime(df["publish_time"])

# Sort and display
df = df.sort_values("publish_time")

# Streamlit UI
st.title("📊 YouTube Trending Analytics")

# Simple line chart
fig, ax = plt.subplots(figsize=(10, 5))
df.groupby("publish_time")["views"].sum().plot(ax=ax, marker='o')
ax.set_xlabel("Publish Time")
ax.set_ylabel("Total Views")
ax.set_title("Total Views Over Time")
st.pyplot(fig)

# Optional: Show raw data
if st.checkbox("Show raw data"):
    st.dataframe(df)
