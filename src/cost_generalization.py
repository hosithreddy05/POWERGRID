import pandas as pd
import numpy as np

from src.config import (
    TRAIN_DATA_PATH,
    TEST_DATA_PATH,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    COST_TARGET
)


print("=" * 70)
print("       SIH 25192 - COST GENERALIZATION ANALYSIS")
print("=" * 70)


def main():

    train = pd.read_csv(
        TRAIN_DATA_PATH
    )

    test = pd.read_csv(
        TEST_DATA_PATH
    )

    # --------------------------------------------------------
    # Training target distribution
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("TRAINING COST TARGET")
    print("=" * 70)

    train_target = train[
        COST_TARGET
    ].dropna()

    print(
        train_target.describe()
    )

    print(
        "\nPositive overrun snapshots:",
        (train_target > 0).sum()
    )

    print(
        "Zero snapshots:",
        (train_target == 0).sum()
    )

    # --------------------------------------------------------
    # Training project distribution
    # --------------------------------------------------------

    train_project_targets = (
        train
        .groupby("project_code")
        [COST_TARGET]
        .mean()
        .sort_values(
            ascending=False
        )
    )

    print(
        "\nTop training projects by "
        "average cost overrun:"
    )

    print(
        train_project_targets.head(
            15
        ).to_string()
    )

    # --------------------------------------------------------
    # Test project distribution
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("TEST COST TARGET")
    print("=" * 70)

    test_target = test[
        COST_TARGET
    ].dropna()

    print(
        test_target.describe()
    )

    print(
        "\nPositive overrun snapshots:",
        (test_target > 0).sum()
    )

    print(
        "Zero snapshots:",
        (test_target == 0).sum()
    )

    # --------------------------------------------------------
    # Test project targets
    # --------------------------------------------------------

    test_project_targets = (
        test
        .groupby("project_code")
        [COST_TARGET]
        .agg(
            [
                "mean",
                "min",
                "max"
            ]
        )
        .sort_values(
            "max",
            ascending=False
        )
    )

    print(
        "\nTest projects by cost overrun:"
    )

    print(
        test_project_targets.to_string()
    )

    # --------------------------------------------------------
    # Feature distribution comparison
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("NUMERICAL FEATURE DISTRIBUTION")
    print("=" * 70)

    for feature in NUMERICAL_FEATURES:

        train_median = train[
            feature
        ].median()

        test_median = test[
            feature
        ].median()

        train_mean = train[
            feature
        ].mean()

        test_mean = test[
            feature
        ].mean()

        print(
            f"\n{feature}"
        )

        print(
            f"  Train mean   : "
            f"{train_mean:.3f}"
        )

        print(
            f"  Test mean    : "
            f"{test_mean:.3f}"
        )

        print(
            f"  Train median : "
            f"{train_median:.3f}"
        )

        print(
            f"  Test median  : "
            f"{test_median:.3f}"
        )

    # --------------------------------------------------------
    # Problem projects
    # --------------------------------------------------------

    problem_projects = [
        "400005",
        "N18000264"
    ]

    print("\n" + "=" * 70)
    print("PROBLEM PROJECT FEATURE VALUES")
    print("=" * 70)

    for project in problem_projects:

        project_data = test[
            test["project_code"]
            == project
        ].copy()

        if project_data.empty:
            continue

        print(
            f"\nPROJECT: {project}"
        )

        print(
            project_data[
                [
                    "project_code",
                    "project_name",
                    "snapshot_date",
                    COST_TARGET
                ]
                + NUMERICAL_FEATURES
                + CATEGORICAL_FEATURES
            ].to_string(
                index=False
            )
        )

    print("\n" + "=" * 70)
    print("COST GENERALIZATION ANALYSIS COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()