from load_data import load_sample, prepare_data
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


def main():
    historical_requests = load_sample(
        limit=1000,
        before_date="2026-07-01T00:00:00"
    )

    historical_df = prepare_data(historical_requests)
    evaluate_resolution_window(historical_df)


if __name__ == "__main__":
    main()
     