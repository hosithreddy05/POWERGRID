import pandas as pd

from src.config import (
    TRAIN_DATA_PATH,
    TEST_DATA_PATH,
    COST_TARGET
)


print("=" * 75)
print("       SIH 25192 - COST CLASSIFICATION ANALYSIS")
print("=" * 75)


def analyze_dataset(df, name):

    print("\n")
    print("=" * 75)
    print(f"{name.upper()} DATASET")
    print("=" * 75)

    # --------------------------------------------------------
    # Create classification target
    # --------------------------------------------------------

    df = df.copy()

    df["cost_risk"] = (
        df[COST_TARGET] > 0
    ).astype(int)

    # --------------------------------------------------------
    # Snapshot level
    # --------------------------------------------------------

    print("\nSNAPSHOT LEVEL")

    total_rows = len(df)

    positive_rows = (
        df["cost_risk"] == 1
    ).sum()

    negative_rows = (
        df["cost_risk"] == 0
    ).sum()

    print(
        f"Total snapshots       : {total_rows}"
    )

    print(
        f"Positive snapshots    : {positive_rows}"
    )

    print(
        f"Zero-overrun snapshots: {negative_rows}"
    )

    print(
        f"Positive percentage   : "
        f"{positive_rows / total_rows * 100:.2f}%"
    )

    # --------------------------------------------------------
    # Project level
    # --------------------------------------------------------

    print("\nPROJECT LEVEL")

    project_summary = (
        df
        .groupby("project_code")
        [COST_TARGET]
        .agg(
            [
                "mean",
                "max"
            ]
        )
        .reset_index()
    )

    project_summary[
        "has_cost_overrun"
    ] = (
        project_summary["max"] > 0
    ).astype(int)

    total_projects = len(
        project_summary
    )

    positive_projects = (
        project_summary[
            "has_cost_overrun"
        ] == 1
    ).sum()

    zero_projects = (
        project_summary[
            "has_cost_overrun"
        ] == 0
    ).sum()

    print(
        f"Total projects       : {total_projects}"
    )

    print(
        f"Positive projects    : {positive_projects}"
    )

    print(
        f"Zero-overrun projects: {zero_projects}"
    )

    print(
        f"Positive project %   : "
        f"{positive_projects / total_projects * 100:.2f}%"
    )

    # --------------------------------------------------------
    # Positive projects
    # --------------------------------------------------------

    print("\nPOSITIVE PROJECTS")

    positive = project_summary[
        project_summary[
            "has_cost_overrun"
        ] == 1
    ].sort_values(
        "max",
        ascending=False
    )

    if positive.empty:

        print(
            "No positive projects."
        )

    else:

        print(
            positive.to_string(
                index=False
            )
        )

    # --------------------------------------------------------
    # Negative projects
    # --------------------------------------------------------

    print("\nZERO-OVERRUN PROJECTS")

    zero = project_summary[
        project_summary[
            "has_cost_overrun"
        ] == 0
    ]

    print(
        f"Count: {len(zero)}"
    )

    # --------------------------------------------------------
    # Cost risk categories
    # --------------------------------------------------------

    print("\nCOST RISK DISTRIBUTION")

    def risk_category(value):

        if value <= 0:
            return "NO_OVERRUN"

        elif value <= 10:
            return "LOW_1_TO_10"

        elif value <= 30:
            return "MEDIUM_10_TO_30"

        else:
            return "HIGH_OVER_30"

    project_summary[
        "risk_category"
    ] = (
        project_summary["max"]
        .apply(
            risk_category
        )
    )

    print(
        project_summary[
            "risk_category"
        ].value_counts()
    )

    return project_summary


def main():

    train = pd.read_csv(
        TRAIN_DATA_PATH
    )

    test = pd.read_csv(
        TEST_DATA_PATH
    )

    train_projects = analyze_dataset(
        train,
        "Training"
    )

    test_projects = analyze_dataset(
        test,
        "Testing"
    )

    # --------------------------------------------------------
    # Important comparison
    # --------------------------------------------------------

    print("\n")
    print("=" * 75)
    print("TRAINING vs TESTING")
    print("=" * 75)

    print("\nTraining:")
    print(
        train_projects[
            "risk_category"
        ].value_counts()
    )

    print("\nTesting:")
    print(
        test_projects[
            "risk_category"
        ].value_counts()
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    output = pd.concat(
        [
            train_projects.assign(
                dataset="train"
            ),
            test_projects.assign(
                dataset="test"
            )
        ],
        ignore_index=True
    )

    output.to_csv(
        "reports/cost_classification_analysis.csv",
        index=False
    )

    print("\n")
    print("=" * 75)
    print(
        "COST CLASSIFICATION ANALYSIS COMPLETED"
    )
    print("=" * 75)


if __name__ == "__main__":
    main()