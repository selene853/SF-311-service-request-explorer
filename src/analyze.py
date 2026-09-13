import pandas as pd
from load_data import load_sample, prepare_data
from datetime import datetime, timedelta, timezone
def evaluate_resolution_window(df):
    print("\nHistorical cohort status:")
    print(df["status_description"].value_counts(dropna=False))

    resolution_times = df["resolution_hours"].dropna()

    print("\nResolution-time distribution:")
    print(
        resolution_times.describe(
            percentiles=[0.50, 0.75, 0.90, 0.95, 0.99]
        )
    )

    print("\nPercentage of all cases resolved within each period:")

    candidate_days = [1, 3, 7, 14, 30, 60]
    coverage = {}

    for days in candidate_days:
        resolved_by_then = df["resolution_hours"].le(days * 24)
        proportion = resolved_by_then.mean()
        coverage[days] = proportion

        print(f"{days:>2} days: {proportion:.1%}")

    suitable_days = [
        days
        for days, proportion in coverage.items()
        if proportion >= 0.90
    ]

    if suitable_days:
        recommended_days = min(suitable_days)
        print(
            f"\nRecommended setback: {recommended_days} days "
            "(at least 90% resolved)"
        )
    else:
        print(
            "\nNone of the tested periods reached 90% resolution."
        )
def summarize_data(df):
    ##printing summary
    print('\nDataset shape:')
    print(df.shape)
    print('\nRequests by source:')
    print(df['source'].value_counts())
    print('\nRequests by status:')
    print(df['status_description'].value_counts())
    print('\nTen most common service categories:')
    print(df['service_name'].value_counts().head(10))
    print('\nTen most common neighborhoods:')
    print(df['neighborhoods_sffind_boundaries'].value_counts().head(10))

    closed=df.dropna(subset=['resolution_hours'])

    print("\nMedian resolution hours by service category:")

    print(
    closed.groupby("service_name")["resolution_hours"]
    .median()
    .sort_values(ascending=False)
    .head(10)
)

    print("\nMean resolution hours by service category:")

    print(
    closed.groupby("service_name")["resolution_hours"]
    .mean()
    .sort_values(ascending=False)
    .head(10)
)

def cohort_metrics(df):
    closed_count = df["resolution_hours"].notna().sum()
    category_stats = (
        df.groupby("service_name")["resolution_hours"]
        .agg(["count", "median"])
        .query("count >= 10")
    )

    top_category = category_stats["median"].idxmax()
    
    return {
        "total_cases": len(df),
        "closed_cases": closed_count,
        "closed_percentage": closed_count / len(df) * 100,
        "median_resolution_hours": df["resolution_hours"].median(),
        "mean_resolution_hours": df["resolution_hours"].mean(),
        'top 1 category by median':top_category
    }
def main():
    cutoff = (
        datetime.now(timezone.utc) - timedelta(days=30)
    ).strftime("%Y-%m-%dT%H:%M:%S")

    recent_df = prepare_data(
        load_sample(limit=1000, before_date=None)
    )

    delayed_df = prepare_data(
        load_sample(limit=1000, before_date=cutoff)
    )

    comparison = pd.DataFrame(
        {
            "Newest 1,000 requests": cohort_metrics(recent_df),
            "30-day delayed sample": cohort_metrics(delayed_df),
        }
    ).T.round(1)

    print("\nSampling comparison:")
    print(comparison.to_string())

    # Use the delayed sample for the main analysis
    summarize_data(delayed_df)




if __name__ == "__main__":

    main()


     
