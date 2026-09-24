from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

import pandas as pd
import streamlit as st

# Allow app.py to import files from src/
sys.path.append(str(Path(__file__).parent / "src"))

from load_data import load_sample
from analyze import prepare_data


st.set_page_config(
    page_title="SF 311 Service Request Explorer",
    page_icon="🏙️",
    layout="wide",
)

st.title("SF 311 Service Request Explorer")
st.write("Interactively explore current San Francisco 311 service-request data.")


# Sidebar controls
st.sidebar.header("Sampling settings")

sample_size = st.sidebar.slider(
    "Number of requests",
    min_value=100,
    max_value=5000,
    value=1000,
    step=100,
)

setback_days = st.sidebar.slider(
    "Sampling setback (days)",
    min_value=0,
    max_value=90,
    value=30,
)

minimum_cases = st.sidebar.slider(
    "Minimum closed cases per category",
    min_value=1,
    max_value=50,
    value=10,
)

if st.sidebar.button("Refresh data"):
    st.cache_data.clear()
    st.rerun()


@st.cache_data(ttl=3600)
def get_data(limit, days):
    if days == 0:
        cutoff = None
    else:
        cutoff = (
            datetime.now(timezone.utc) - timedelta(days=days)
        ).strftime("%Y-%m-%dT%H:%M:%S")

    raw_df = load_sample(limit=limit, before_date=cutoff)
    return prepare_data(raw_df)


try:
    with st.spinner("Loading SF 311 data..."):
        df = get_data(sample_size, setback_days)
except Exception as error:
    st.error(f"Unable to load the data: {error}")
    st.stop()


# Overall metrics
closed_count = df["resolution_hours"].notna().sum()
closed_percentage = closed_count / len(df) * 100 if len(df) else 0

column1, column2, column3 = st.columns(3)

column1.metric("Total requests", f"{len(df):,}")
column2.metric("Closed requests", f"{closed_count:,}")
column3.metric("Closed percentage", f"{closed_percentage:.1f}%")


tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Service categories",
        "Request volume",
        "Resolution time",
        "Neighborhoods",
    ]
)


with tab1:
    st.subheader("Most common service categories")

    top_categories = df["service_name"].value_counts().head(10)
    st.bar_chart(top_categories)

    st.dataframe(
        top_categories.rename("request_count"),
        use_container_width=True,
    )


with tab2:
    st.subheader("Request volume over time")

    volume_df = df.copy()
    volume_df["requested_datetime"] = pd.to_datetime(
        volume_df["requested_datetime"],
        errors="coerce",
        utc=True,
    )

    # Exclude today's incomplete data
    today = datetime.now(timezone.utc).date()
    volume_df = volume_df[
        volume_df["requested_datetime"].dt.date < today
    ]

    daily_volume = (
        volume_df.dropna(subset=["requested_datetime"])
        .assign(
            request_date=lambda data: data[
                "requested_datetime"
            ].dt.date
        )
        .groupby("request_date")
        .size()
        .rename("request_count")
    )

    st.line_chart(daily_volume)

    st.dataframe(daily_volume, use_container_width=True)


with tab3:
    st.subheader("Median resolution time by category")

    closed_df = df.dropna(
        subset=["resolution_hours", "service_name"]
    )

    category_counts = closed_df["service_name"].value_counts()
    eligible_categories = category_counts[
        category_counts >= minimum_cases
    ].index

    median_resolution = (
        closed_df[
            closed_df["service_name"].isin(eligible_categories)
        ]
        .groupby("service_name")["resolution_hours"]
        .median()
        .sort_values(ascending=False)
        .head(10)
    )

    st.bar_chart(median_resolution)

    st.dataframe(
        median_resolution.rename("median_resolution_hours"),
        use_container_width=True,
    )

    st.caption(
        f"Only categories with at least {minimum_cases} closed "
        "requests are included."
    )


with tab4:
    st.subheader("Requests by neighborhood")

    neighborhood_counts = (
        df["neighborhoods_sffind_boundaries"]
        .dropna()
        .value_counts()
        .head(10)
    )

    st.bar_chart(neighborhood_counts)

    st.dataframe(
        neighborhood_counts.rename("request_count"),
        use_container_width=True,
    )


st.caption(
    f"Displaying {sample_size:,} requests sampled with a "
    f"{setback_days}-day setback."
)