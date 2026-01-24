import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from PIL import Image
import streamlit.components.v1 as components

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(
    page_title="NYC Citi Bike Dashboard (2022)",
    layout="wide"
)

# -------------------------------------------------
# Sidebar navigation
# -------------------------------------------------
page = st.sidebar.selectbox(
    "Select an aspect of the analysis",
    [
        "Intro page",
        "Weather component and bike usage",
        "Most popular bike stations",
        "Interactive map with aggregated bike trips",
        "User and bike type breakdown",
        "Conclusions and recommendations"
    ]
)

# -------------------------------------------------
# Paths
# -------------------------------------------------
PROJECT_DIR = Path.cwd()
DATA_DIR = PROJECT_DIR / "data" / "processed"

TOP20_PATH = DATA_DIR / "top20_stations.csv"
DAILY_PATH = DATA_DIR / "daily_trips_weather_2022.csv"
KEPLER_HTML_PATH = PROJECT_DIR / "visualizations" / "NYC_CitiBike_Trips.html"
USER_BIKE_PATH = DATA_DIR / "user_bike_sample.csv"

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

@st.cache_data
def load_user_bike(path):
    return pd.read_csv(path)

if not USER_BIKE_PATH.exists():
    st.error("User and bike sample file not found in data/processed/")
    st.stop()

df_user_bike = load_user_bike(USER_BIKE_PATH)

df_user_bike = load_user_bike(USER_BIKE_PATH)
# -------------------------------------------------
# Pages
# -------------------------------------------------
if page == "Intro page":
    st.title("NYC Citi Bike Strategy Dashboard")

    st.markdown(
        """
        #### Purpose
        Citi Bike riders in New York City experience availability issues at certain times and locations, including empty docks and bike shortages. This dashboard analyzes 2022 usage patterns to help the strategy team understand where and when demand concentrates, and how rider behaviour shifts with seasonality and weather conditions.

        #### What’s inside
        - **Weather component and bike usage:** daily trips vs average temperature (seasonality signal)
        - **Most popular stations:** top stations to highlight demand hotspots
        - **Interactive map:** aggregated trips to spot corridors / clusters
        - **User and bike type breakdown**
        - **Conclusions and recommendations:** practical next steps for operations and rebalancing

        Use the dropdown in the left sidebar to navigate between sections.
        """
    )

    intro_image = Image.open(PROJECT_DIR / "citibike-image.jpg")
    st.image(
        intro_image,
        caption="Citi Bike usage across New York City",
        width=800
    )
elif page == "Weather component and bike usage":

    st.header("Daily bike trips and temperatures in 2022")

    df_plot = df_daily.dropna(subset=["avgTemp_C"])

    fig_line = make_subplots(specs=[[{"secondary_y": True}]])

    # Trips per day (LEFT axis)
    fig_line.add_trace(
        go.Scatter(
            x=df_plot["date"],
            y=df_plot["trips_per_day"],
            mode="lines",
            name="Trips per day",
            line=dict(color="royalblue")
        ),
        secondary_y=False
    )

    # Average temperature (RIGHT axis)
    fig_line.add_trace(
        go.Scatter(
            x=df_plot["date"],
            y=df_plot["avgTemp_C"],
            mode="lines",
            name="Avg temperature (°C)",
            line=dict(color="firebrick")
        ),
        secondary_y=True
    )

    # Layout
    fig_line.update_layout(
        hovermode="x unified",
        height=600,
        margin=dict(t=40, b=40)
    )

    # X-axis: months only
    fig_line.update_xaxes(
        dtick="M1",
        tickformat="%b"
    )

    # Remove axis titles (legend explains lines)
    fig_line.update_yaxes(title_text=None, secondary_y=False)
    fig_line.update_yaxes(title_text=None, secondary_y=True)

    st.plotly_chart(fig_line, use_container_width=True)

    # Interpretation
    st.markdown(
        """
        Daily Citi Bike usage closely tracks temperature throughout the year.
        Trips increase steadily from spring, peak during summer months, and decline
        sharply as temperatures drop in late fall and winter.

        This pattern indicates strong **seasonality**, suggesting that supply shortages
        are most likely during warmer months when demand is consistently higher.
        """
    )

# -------------------------------------------------
# Chart 1: Top 20 stations
# -------------------------------------------------
elif page == "Most popular bike stations":
    # Page header
    st.header("20 most popular bike stations")


    # total_trips = int(top20['trips'].sum())
    # st.metric("Total trips (top 20 stations)", f"{total_trips:,}")

    # Build horizontal bar chart for the top 20 stations
    # Ensure 'top20' has columns: 'start_station_name' and 'trips'
    fig_bar = go.Figure(
        go.Bar(
            x=top20["trips"],
            y=top20["start_station_name"],
            orientation="h",
            marker=dict(
                color=top20["trips"],
                colorscale="Blues"
            ),
            hovertemplate="%{y}: %{x:,} trips<extra></extra>"
        )
    )

    fig_bar.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        yaxis=dict(autorange="reversed"),  # highest at top
        margin=dict(l=200, r=40, t=40, b=40),
        height=700,
        showlegend=False
    )

    st.plotly_chart(fig_bar, use_container_width=True)

    # Interpretation / Insights (Markdown)
    st.markdown(
        """
        The chart shows a **strong concentration of demand among a small number of Citi Bike start stations, with a sharp drop-off after the top three locations**. This indicates that a handful of stations account for a large share of trips and are likely under the most operational pressure. These stations are prime candidates for more frequent rebalancing or targeted capacity increases, especially during peak months. Comparing these stations with the interactive map helps determine whether they also sit along the system’s most heavily used travel corridors.
        """
    )
# -------------------------------------------------

elif page == "Interactive map with aggregated bike trips":
    st.header("Aggregated bike trips in New York City")

    st.markdown(
        """
        Use the map below to explore **high-volume trip flows** between stations.
        Zoom and pan to inspect dense corridors and clusters.
        """
    )

    # Import here
    import streamlit.components.v1 as components

    # Path to the saved Kepler HTML
    KEPLER_HTML_PATH = PROJECT_DIR / "visualizations" / "NYC_CitiBike_Trips.html"

    # Fail fast if the file isn't found
    if not KEPLER_HTML_PATH.exists():
        st.error(f"Kepler map HTML file not found at: {KEPLER_HTML_PATH}")
        st.stop()

    # Read + render the Kepler map
    kepler_html = KEPLER_HTML_PATH.read_text(encoding="utf-8")

    components.html(
        kepler_html,
        height=400,      
        scrolling=True
    )

    st.markdown(
        """ 
        - **Manhattan dominates overall flow**, with the densest connections concentrated in **Midtown and Lower Manhattan**. Many routes are short and tightly clustered, suggesting frequent repeat trips between nearby stations (commuting, errands, and “last-mile” rides).
        - A clear **waterfront-adjacent corridor** appears along the **Hudson River**, consistent with recreational riding and bike-path access. These flows often connect stations that are close together but serve high turnover.
        - Compared to Manhattan, **outer-borough connections** appear more fragmented and lower-volume in this filtered view. This suggests demand is more centralized, while peripheral trips are either less frequent or spread across more varied origin–destination pairs.

        **What this implies operationally**
        - The Midtown / Downtown core behaves like a **high-throughput demand zone**. Stations here are most vulnerable to **rapid bike depletion and dock saturation**, especially during weekday peak commute windows.
        - Waterfront corridors may require **different rebalancing timing** (e.g., weekends/afternoons) than commuter corridors (weekday AM/PM peaks).
        - The most prominent links indicate where the system experiences **repeated directional pressure** - a useful signal for targeting rebalancing routes or adding temporary capacity (extra docks / valet operations) at key endpoints.

        **How to use this map**
        - Hover on the brightest/most prominent lines to identify the **specific station pairs** driving flow.
        - Use this alongside the **Most popular bike stations** page: stations that are highly popular *and* sit on dense corridors are strong candidates for **capacity expansion or more frequent rebalancing**.
        """
    )
# -------------------------------------------------
elif page == "User and bike type breakdown":

    st.header("User and bike type breakdown")


    # Aggregate counts
    user_counts = df_user_bike["member_casual"].value_counts().reset_index()
    user_counts.columns = ["user_type", "rides"]

    bike_counts = df_user_bike["rideable_type"].value_counts().reset_index()
    bike_counts.columns = ["bike_type", "rides"]

    # Friendly labels (for dashboard display only)
    user_counts["user_type"] = user_counts["user_type"].replace(
        {
            "member": "Citi Bike member",
            "casual": "Casual rider",
        }
    )

    bike_counts["bike_type"] = bike_counts["bike_type"].replace(
        {
            "classic_bike": "Classic bike",
            "electric_bike": "Electric bike",
        }
    )

    # Create two columns for side-by-side charts
    col1, col2 = st.columns(2)

    # --- User type bar chart ---
    with col1:
        fig_users = go.Figure(
            go.Bar(
                x=user_counts["user_type"],
                y=user_counts["rides"],
                # Different colours
                marker_color=["royalblue", "orange"],
                hovertemplate="%{x}: %{y:,} rides<extra></extra>",
            )
        )

        fig_users.update_layout(
            title="User types",
            xaxis_title=None,
            yaxis_title=None,
            showlegend=False,
            height=400,
        )

        st.plotly_chart(fig_users, use_container_width=True)


        
        # --- Bike type donut chart ---
    with col2:
        fig_bikes = go.Figure(
            go.Pie(
                labels=bike_counts["bike_type"],
                values=bike_counts["rides"],
                hole=0.4,
                marker=dict(
                colors=[
                    "darkgray",   # Classic bike
                    "seagreen",    # Electric bike
                ]
            ),
                hovertemplate="%{label}: %{percent}<extra></extra>",
            )
        )

        fig_bikes.update_layout(
            title="Bike type distribution",
            height=400,
        )

        st.plotly_chart(fig_bikes, use_container_width=True)
    st.markdown(
    """
Member riders account for the majority of Citi Bike trips in New York City, indicating that system usage is driven primarily by repeat, habitual users rather than occasional riders. While classic bikes still dominate overall usage, electric bikes represent a substantial and growing share of trips. This suggests increasing demand for assisted riding, particularly for longer or more frequent journeys, with implications for fleet composition and charging logistics.
    """
)


# -------------------------------------------------
elif page == "Conclusions and recommendations":

    st.header("Conclusions and recommendations")

    rec_image_path = PROJECT_DIR / "citibike-image2.jpg"
    if rec_image_path.exists():
        st.image(str(rec_image_path), width=900)
    else:
        st.warning(f"Image not found: {rec_image_path}")

    st.markdown(
        """
        Based on usage patterns, station popularity, seasonality, and trip-flow corridors,
       the following operational priorities stand out for NYC Citi Bike:
        """
    )

    st.markdown(
        """
        - Prioritize rebalancing and capacity increases in high-volume Manhattan corridors.
        - Adjust rebalancing schedules seasonally, with extra focus during warmer months.
        - Expand and strategically deploy electric bikes in high-demand corridors and at stations with high member usage, as e-bike adoption is significant and likely to grow. This should be paired with targeted charging and maintenance planning to avoid e-bike shortages during peak periods.
        - Treat waterfront and recreational corridors differently from commuter corridors,
          as they exhibit distinct usage patterns.
       """
    )