from datetime import datetime, timedelta, timezone
from pathlib import Path
from load_data import (
    load_sample,
    prepare_data,
    load_daily_request_counts,
)
import matplotlib.pyplot as plt

from load_data import load_sample, prepare_data


def plot_top_services(df):
    counts = df["service_name"].value_counts().head(10)

    counts.sort_values().plot(
        kind="barh",
        figsize=(10, 6),
        color="steelblue",
    )

    plt.title("Ten Most Common SF 311 Service Categories")
    plt.xlabel("Number of Requests")
    plt.ylabel("Service Category")
    plt.tight_layout()

    Path("output").mkdir(exist_ok=True)
    plt.savefig("output/top_service_categories.png", dpi=300)
    plt.close()
def plot_resolution_by_service(df):
    closed = df.dropna(subset=["resolution_hours"])

    summary = (
        closed.groupby("service_name")["resolution_hours"]
        .agg(["median", "count"])
    )

    # Avoid categories with very few completed requests
    summary = summary[summary["count"] >= 10]

    # Select the ten categories with the longest median times
    summary = (
        summary.nlargest(10, "median")
        .sort_values("median")
    )

    summary["median"].plot(
        kind="barh",
        figsize=(10, 6),
        color="darkorange",
    )

    plt.title("Median Resolution Time by Service Category")
    plt.xlabel("Median Resolution Time (Hours)")
    plt.ylabel("Service Category")
    plt.tight_layout()

    Path("output").mkdir(exist_ok=True)
    plt.savefig(
        "output/median_resolution_by_service.png",
        dpi=300,
    )
    plt.close()
def plot_requests_by_neighborhood(df):
    counts = (
        df["neighborhoods_sffind_boundaries"]
        .value_counts()
        .head(10)
        .sort_values()
    )

    counts.plot(
        kind="barh",
        figsize=(10, 6),
        color="seagreen",
    )

    plt.title("Ten Neighborhoods with the Most SF 311 Requests")
    plt.xlabel("Number of Requests")
    plt.ylabel("Neighborhood")
    plt.tight_layout()

    Path("output").mkdir(exist_ok=True)
    plt.savefig(
        "output/requests_by_neighborhood.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()
def plot_request_volume_over_time(daily_counts):
    plt.figure(figsize=(12, 6))

    plt.plot(
        daily_counts["request_date"],
        daily_counts["request_count"],
        color="royalblue",
        linewidth=2,
    )

    plt.title("Daily Volume of SF 311 Service Requests")
    plt.xlabel("Request Date")
    plt.ylabel("Number of Requests")
    plt.grid(alpha=0.3)
    plt.xticks(rotation=45)
    plt.xlim(
    daily_counts["request_date"].min(),
    daily_counts["request_date"].max(),
)
    plt.tight_layout()

    Path("output").mkdir(exist_ok=True)
    plt.savefig(
        "output/request_volume_over_time.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()
def main():
    cutoff = (
    datetime.now(timezone.utc) - timedelta(days=30)
).strftime("%Y-%m-%dT%H:%M:%S")

    df = prepare_data(
        load_sample(limit=1000, before_date=cutoff)
    )

    plot_top_services(df)
    plot_requests_by_neighborhood(df)
    plot_resolution_by_service(df)

    print("Saved output/top_service_categories.png")
    daily_counts = load_daily_request_counts(days=90)
    plot_request_volume_over_time(daily_counts)
    print("Saved output/request_volume_over_time.png")
    

if __name__ == "__main__":
    main()