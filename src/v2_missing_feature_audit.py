"""
SIH 25192 - V2 MISSING TRAJECTORY FEATURE AUDIT

Investigates missing trajectory values before V2 training.

IMPORTANT:
- Does not modify any dataset.
- Does not fill missing values.
- Does not use synthetic data.
- Does not modify V1.
"""

from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

SOURCE = ROOT / "data" / "train_trajectory.csv"


TRAJECTORY_FEATURES = [
    "progress_velocity",
    "expenditure_velocity",
    "expenditure_progress_gap",
    "schedule_slippage_months",
    "schedule_pressure_ratio",
    "budget_consumption_ratio",
]


def main():

    print("=" * 75)
    print("       SIH 25192 - V2 MISSING FEATURE AUDIT")
    print("=" * 75)

    # ---------------------------------------------------------
    # 1. Load original trajectory training data
    # ---------------------------------------------------------

    print("\n[1] Loading original trajectory training data...")

    df = pd.read_csv(SOURCE)

    df["snapshot_date"] = pd.to_datetime(
        df["snapshot_date"],
        errors="coerce"
    )

    print("Rows    :", len(df))
    print("Projects:", df["project_code"].nunique())

    # ---------------------------------------------------------
    # 2. Missing-value summary
    # ---------------------------------------------------------

    print("\n[2] Missing values in V2 trajectory features")

    missing_summary = df[TRAJECTORY_FEATURES].isna().sum()

    for feature, count in missing_summary.items():

        print(
            f"{feature:35s}: {count}"
        )

    # ---------------------------------------------------------
    # 3. Rows containing missing values
    # ---------------------------------------------------------

    missing_mask = df[
        TRAJECTORY_FEATURES
    ].isna().any(axis=1)

    missing_rows = df.loc[
        missing_mask
    ].copy()

    print("\n[3] Rows containing missing V2 features")

    print(
        "Rows with missing values:",
        len(missing_rows)
    )

    print(
        "Projects affected:",
        missing_rows["project_code"].nunique()
    )

    if len(missing_rows) > 0:

        display_columns = [
            "project_code",
            "project_name",
            "snapshot_date",
            "target_cost_overrun_pct",
            "target_schedule_overrun_months",
        ] + TRAJECTORY_FEATURES

        print(
            missing_rows[
                display_columns
            ].to_string(index=False)
        )

    # ---------------------------------------------------------
    # 4. Determine whether missing rows are first snapshots
    # ---------------------------------------------------------

    print("\n[4] Checking whether missing rows are first snapshots")

    first_snapshot = (
        df.groupby("project_code")["snapshot_date"]
        .transform("min")
    )

    missing_rows = missing_rows.copy()

    missing_rows["is_first_snapshot"] = (
        missing_rows["snapshot_date"]
        == first_snapshot.loc[missing_rows.index]
    )

    first_count = int(
        missing_rows["is_first_snapshot"].sum()
    )

    not_first_count = (
        len(missing_rows) - first_count
    )

    print(
        "Missing rows that are first snapshot:",
        first_count
    )

    print(
        "Missing rows that are NOT first snapshot:",
        not_first_count
    )

    # ---------------------------------------------------------
    # 5. Project-level impact
    # ---------------------------------------------------------

    print("\n[5] Project-level impact")

    all_projects = set(
        df["project_code"]
    )

    projects_with_missing = set(
        missing_rows["project_code"]
    )

    projects_lost_if_removed = []

    for project in sorted(projects_with_missing):

        project_rows = df[
            df["project_code"] == project
        ]

        valid_rows = project_rows[
            ~project_rows[
                TRAJECTORY_FEATURES
            ].isna().any(axis=1)
        ]

        if len(valid_rows) == 0:

            projects_lost_if_removed.append(
                project
            )

    print(
        "Projects with any missing trajectory value:",
        len(projects_with_missing)
    )

    print(
        "Projects completely lost by row deletion:",
        len(projects_lost_if_removed)
    )

    if projects_lost_if_removed:

        print("\nProjects completely lost:")

        for project in projects_lost_if_removed:
            print("  ", project)

    # ---------------------------------------------------------
    # 6. Target information in affected rows
    # ---------------------------------------------------------

    print("\n[6] Target information in missing rows")

    if len(missing_rows) > 0:

        cost_positive = (
            missing_rows[
                "target_cost_overrun_pct"
            ] > 0.5
        )

        schedule_available = (
            missing_rows[
                "target_schedule_overrun_months"
            ].notna()
        )

        print(
            "Cost-overrun rows:",
            int(cost_positive.sum())
        )

        print(
            "Rows with schedule target:",
            int(schedule_available.sum())
        )

    # ---------------------------------------------------------
    # 7. Check each missing feature individually
    # ---------------------------------------------------------

    print("\n[7] Missing pattern by feature")

    for feature in TRAJECTORY_FEATURES:

        mask = df[feature].isna()

        if mask.sum() == 0:
            continue

        feature_rows = df.loc[mask]

        first_mask = (
            feature_rows["snapshot_date"]
            == first_snapshot.loc[feature_rows.index]
        )

        print(
            f"\n{feature}"
        )

        print(
            "  Missing rows:",
            int(mask.sum())
        )

        print(
            "  First snapshots:",
            int(first_mask.sum())
        )

        print(
            "  Other snapshots:",
            int((~first_mask).sum())
        )

    # ---------------------------------------------------------
    # 8. Final decision
    # ---------------------------------------------------------

    print("\n" + "=" * 75)
    print("V2 MISSING FEATURE AUDIT DECISION")
    print("=" * 75)

    print(
        "We will NOT automatically delete or fill missing values."
    )

    print(
        "We will inspect whether missing values are expected"
    )

    print(
        "trajectory initialization values before training V2."
    )

    print(
        "\nSynthetic data: NO"
    )

    print(
        "Dataset modified: NO"
    )

    print(
        "V1 modified: NO"
    )

    print("\n" + "=" * 75)
    print("V2 MISSING FEATURE AUDIT COMPLETED")
    print("=" * 75)


if __name__ == "__main__":
    main()