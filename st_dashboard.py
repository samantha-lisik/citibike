import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(
    page_title="NYC Citi Bike Dashboard (2022)",
    layout="wide"
)

st.title("NYC Citi Bike Dashboard (2022)")
st.markdown(
    "This dashboard visualizes Citi Bike usage patterns in New York City during 2022, "
    "including the most popular start stations and the relationship between daily trips "
    "and average temperature."
)

# -------------------------------------------------
# Paths
# -------------------------------------------------
PROJECT_DIR = Path.cwd()
DATA_DIR = PROJECT_DIR / "data" / "processed"

TOP20_PATH = DATA_DIR / "top20_stations.csv"
DAILY_PATH = DATA_DIR / "daily_trips_weather_2022.csv"

# -------------------------------------------------
# Load data
# -------------------------------------------------
@st.cache_data
def load_top20(path):
    return pd.read_csv(path)

@st.cache_data
def load_daily(path):
    df = pd.read_csv(path, parse_dates=["date"])
    return df

if not TOP20_PATH.exists() or not DAILY_PATH.exists():
    st.error("Required data files not found in data/processed/")
    st.stop()

top20 = load_top20(TOP20_PATH)
df_daily = load_daily(DAILY_PATH)

# -------------------------------------------------
# Chart 1: Top 20 stations
# -------------------------------------------------
st.subheader("Top 20 Most Popular Citi Bike Start Stations")

fig_bar = go.Figure(
    go.Bar(
        x=top20["trips"],
        y=top20["start_station_name"],
        orientation="h",
        marker=dict(
            color=top20["trips"],
            colorscale="Blues"
        )
    )
)

fig_bar.update_layout(
    title="Top 20 Most Popular Citi Bike Stations",
    xaxis_title="Number of Trips",
    yaxis_title="Start Station",
    yaxis=dict(autorange="reversed"),
    height=600
)

st.plotly_chart(fig_bar, use_container_width=True)

# -------------------------------------------------
# Chart 2: Daily trips vs temperature
# -------------------------------------------------
st.subheader("Daily Citi Bike Trips and Temperature (2022)")

df_plot = df_daily.dropna(subset=["avgTemp_C"])

fig_line = make_subplots(specs=[[{"secondary_y": True}]])

fig_line.add_trace(
    go.Scatter(
        x=df_plot["date"],
        y=df_plot["trips_per_day"],
        mode="lines",
        name="Trips per day"
    ),
    secondary_y=False
)

fig_line.add_trace(
    go.Scatter(
        x=df_plot["date"],
        y=df_plot["avgTemp_C"],
        mode="lines",
        name="Avg Temperature (°C)"
    ),
    secondary_y=True
)

fig_line.update_layout(
    title="Daily Citi Bike Trips and Temperature (NYC, 2022)",
    hovermode="x unified",
    height=600
)


fig_line.update_xaxes(
    dtick="M1",
    tickformat="%b\n%Y",
    ticklabelmode="period",
    title_text="Date"
)

fig_line.update_yaxes(title_text="Trips per day", secondary_y=False)
fig_line.update_yaxes(title_text="Average Temperature (°C)", secondary_y=True)

st.plotly_chart(fig_line, use_container_width=True)

import streamlit.components.v1 as components

st.subheader("Aggregated Citi Bike Trips (Kepler.gl Map)")

KEPLER_HTML_PATH = PROJECT_DIR / "visualizations" / "NYC_CitiBike_Trips.html"

if not KEPLER_HTML_PATH.exists():
    st.error(f"Kepler map HTML file not found at: {KEPLER_HTML_PATH}")
else:
    kepler_html = KEPLER_HTML_PATH.read_text(encoding="utf-8")
    components.html(kepler_html, height=800, scrolling=True)




