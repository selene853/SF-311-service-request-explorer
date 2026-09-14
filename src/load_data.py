"""Load a small sample from the San Francisco 311 API."""
import os
import pandas as pd
import requests
from datetime import datetime, timedelta, timezone

API_URL = "https://data.sf.gov/api/v3/views/vw6y-z8j6/query.json"

COLUMNS = [
    "service_request_id",
    "requested_datetime",
    "closed_date",
    "status_description",
    "service_name",
    "service_subtype",
    "agency_responsible",
    "neighborhoods_sffind_boundaries",
    "source",
]


sampling_delay_days = 30

cutoff = (
    datetime.now(timezone.utc) - timedelta(days=sampling_delay_days)
).strftime("%Y-%m-%dT%H:%M:%S")
def load_sample(limit=1000, before_date=None):
    token = os.environ.get("SOCRATA_APP_TOKEN")

    if token is None:
        raise RuntimeError(
            "SOCRATA_APP_TOKEN has not been set in the terminal."
        )


    where_clause=''

    if before_date is not None:
      where_clause = (
        f"WHERE requested_datetime < '{before_date}'"
    )

    query = f"""
        SELECT {", ".join(COLUMNS)}
        {where_clause}
        ORDER BY requested_datetime DESC
    """

    response = requests.post(
        API_URL,
        headers={"X-App-Token": token},
        json={
            "query": query,
            "page": {
                "pageNumber": 1,
                "pageSize": limit
            },
            "includeSynthetic": False
        },
        timeout=30
    )


    response.raise_for_status()
    return pd.DataFrame(response.json())
def load_daily_request_counts(days=90):
    token = os.environ.get("SOCRATA_APP_TOKEN")

    if token is None:
        raise RuntimeError(
            "SOCRATA_APP_TOKEN has not been set in the terminal."
        )

    # Use complete days only; exclude today because it is unfinished
    end_date = datetime.now(timezone.utc).date()
    start_date = end_date - timedelta(days=days)

    start = f"{start_date}T00:00:00"
    end = f"{end_date}T00:00:00"

    query = f"""
        SELECT
            date_trunc_ymd(requested_datetime) AS request_date,
            count(*) AS request_count
        WHERE requested_datetime >= '{start}'
          AND requested_datetime < '{end}'
        GROUP BY request_date
        ORDER BY request_date
    """

    response = requests.post(
        API_URL,
        headers={"X-App-Token": token},
        json={
            "query": query,
            "page": {
                "pageNumber": 1,
                "pageSize": days + 1,
            },
            "includeSynthetic": False,
        },
        timeout=30,
    )

    response.raise_for_status()

    daily_counts = pd.DataFrame(response.json())

    daily_counts["request_date"] = pd.to_datetime(
        daily_counts["request_date"]
    )
    daily_counts["request_date"] = pd.to_datetime(
    daily_counts["request_date"]
)

    today = pd.Timestamp.now().normalize()

    daily_counts = daily_counts[
        daily_counts["request_date"] < today
    ].copy()
    daily_counts["request_count"] = pd.to_numeric(
        daily_counts["request_count"]
    )

    return daily_counts
def prepare_data(requests_df):
    """Clean dates and calculate resolution time."""
    cleaned = requests_df.copy()

    cleaned["requested_datetime"] = pd.to_datetime(
        cleaned["requested_datetime"],
        errors="coerce",
    )

    cleaned["closed_date"] = pd.to_datetime(
        cleaned["closed_date"],
        errors="coerce",
    )

    cleaned = cleaned.dropna(
        subset=["requested_datetime", "service_name"]
    )

    cleaned["resolution_hours"] = (
        cleaned["closed_date"] - cleaned["requested_datetime"]
    ).dt.total_seconds() / 3600

    cleaned.loc[
        cleaned["resolution_hours"] < 0,
        "resolution_hours",
    ] = pd.NA

    return cleaned
def main():
    """Load, clean, and inspect SF311 data."""
    requests_df = load_sample()
    cleaned_df = prepare_data(requests_df)

    print("Raw shape:")
    print(requests_df.shape)

    print("\nCleaned shape:")
    print(cleaned_df.shape)

    print("\nMissing values:")
    print(cleaned_df.isna().sum())

    print("\nMost common request categories:")
    print(cleaned_df["service_name"].value_counts().head(10))

    print("\nResolution-time summary:")
    print(cleaned_df["resolution_hours"].describe())


if __name__ == "__main__":
    main()