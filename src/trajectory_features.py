import pandas as pd
import numpy as np

from src.config import (
    CLEANED_DATA_PATH
)


print("=" * 75)
print("       SIH 25192 - TRAJECTORY FEATURE ENGINEERING")
print("=" * 75)


# ============================================================
# Helper function
# ============================================================

def safe_change(series):
    """
    Calculate change from the previous snapshot.
    """
    return series.diff()


# ============================================================
# Main feature engineering
# ============================================================

def main():

    # --------------------------------------------------------
    # 1. Load cleaned dataset
    # --------------------------------------------------------

    print("\n[1] Loading cleaned dataset...")

    df = pd.read_csv(
        CLEANED_DATA_PATH
    )

    print(
        f"Rows loaded : {len(df)}"
    )

    print(
        f"Columns     : {len(df.columns)}"
    )

    # --------------------------------------------------------
    # 2. Convert dates
    # --------------------------------------------------------

    print("\n[2] Processing dates...")

    df["snapshot_date"] = pd.to_datetime(
        df["snapshot_date"],
        errors="coerce"
    )

    df["start_date"] = pd.to_datetime(
        df["start_date"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # 3. Sort projects chronologically
    # --------------------------------------------------------

    print(
        "\n[3] Sorting project snapshots..."
    )

    df = df.sort_values(
        [
            "project_code",
            "snapshot_date"
        ]
    ).reset_index(
        drop=True
    )

    # ========================================================
    # TRAJECTORY FEATURES
    # ========================================================

    print(
        "\n[4] Creating trajectory features..."
    )

    # --------------------------------------------------------
    # A. Progress change
    # --------------------------------------------------------

    df[
        "progress_change"
    ] = (
        df.groupby("project_code")
        ["physical_progress_pct"]
        .diff()
    )

    # --------------------------------------------------------
    # B. Expenditure change
    # --------------------------------------------------------

    df[
        "expenditure_change_cr"
    ] = (
        df.groupby("project_code")
        ["cumulative_expenditure_cr"]
        .diff()
    )

    # --------------------------------------------------------
    # C. Expenditure percentage change
    # --------------------------------------------------------

    df[
        "expenditure_pct_change"
    ] = (
        df.groupby("project_code")
        ["expenditure_pct_of_original_cost"]
        .diff()
    )

    # --------------------------------------------------------
    # D. Elapsed-month change
    # --------------------------------------------------------

    df[
        "elapsed_month_change"
    ] = (
        df.groupby("project_code")
        ["elapsed_months"]
        .diff()
    )

    # --------------------------------------------------------
    # E. Progress velocity
    #
    # Percentage points of progress per month
    # --------------------------------------------------------

    df[
        "progress_velocity"
    ] = (
        df["progress_change"]
        / df["elapsed_month_change"]
    )

    # --------------------------------------------------------
    # F. Expenditure velocity
    #
    # Percentage points of budget consumed per month
    # --------------------------------------------------------

    df[
        "expenditure_velocity"
    ] = (
        df["expenditure_pct_change"]
        / df["elapsed_month_change"]
    )

    # --------------------------------------------------------
    # G. Expenditure vs progress
    #
    # Positive value:
    # spending percentage > physical progress
    #
    # Negative value:
    # physical progress > spending
    # --------------------------------------------------------

    df[
        "expenditure_progress_gap"
    ] = (
        df["expenditure_pct_of_original_cost"]
        - df["physical_progress_pct"]
    )

    # --------------------------------------------------------
    # H. Cumulative expenditure per progress point
    # --------------------------------------------------------

    df[
        "cost_per_progress_pct"
    ] = (
        df["cumulative_expenditure_cr"]
        / df["physical_progress_pct"].replace(
            0,
            np.nan
        )
    )

    # --------------------------------------------------------
    # I. Schedule slippage
    #
    # Negative months_to_original_target means
    # the project is beyond its original target.
    # --------------------------------------------------------

    df[
        "schedule_slippage_months"
    ] = (
        -df["months_to_original_target"]
    ).clip(
        lower=0
    )

    # --------------------------------------------------------
    # J. Schedule pressure ratio
    #
    # elapsed duration / planned duration
    # --------------------------------------------------------

    df[
        "schedule_pressure_ratio"
    ] = (
        df["elapsed_months"]
        / df["planned_duration_months"].replace(
            0,
            np.nan
        )
    )

    # --------------------------------------------------------
    # K. Budget consumption ratio
    # --------------------------------------------------------

    df[
        "budget_consumption_ratio"
    ] = (
        df["expenditure_pct_of_original_cost"]
        / 100
    )

    # --------------------------------------------------------
    # L. Progress efficiency
    #
    # Progress achieved relative to elapsed/planned time.
    # --------------------------------------------------------

    df[
        "progress_time_ratio"
    ] = (
        df["physical_progress_pct"]
        / (
            df["elapsed_months"]
            + 1
        )
    )

    # --------------------------------------------------------
    # M. Spending efficiency
    #
    # Physical progress / expenditure percentage.
    #
    # Around 1:
    # spending and progress are similar.
    #
    # <1:
    # spending is ahead of progress.
    #
    # >1:
    # progress is ahead of spending.
    # --------------------------------------------------------

    df[
        "progress_expenditure_ratio"
    ] = (
        df["physical_progress_pct"]
        / df[
            "expenditure_pct_of_original_cost"
        ].replace(
            0,
            np.nan
        )
    )

    # --------------------------------------------------------
    # N. Project age
    # --------------------------------------------------------

    df[
        "project_age_months"
    ] = (
        df["elapsed_months"]
    )

    # ========================================================
    # Rolling trajectory features
    # ========================================================

    print(
        "\n[5] Creating rolling trajectory features..."
    )

    grouped = df.groupby(
        "project_code"
    )

    # --------------------------------------------------------
    # Recent progress change
    # --------------------------------------------------------

    df[
        "progress_change_3"
    ] = (
        grouped[
            "physical_progress_pct"
        ]
        .diff(
            periods=3
        )
    )

    # --------------------------------------------------------
    # Recent expenditure change
    # --------------------------------------------------------

    df[
        "expenditure_change_3"
    ] = (
        grouped[
            "expenditure_pct_of_original_cost"
        ]
        .diff(
            periods=3
        )
    )

    # --------------------------------------------------------
    # Rolling average progress velocity
    # --------------------------------------------------------

    df[
        "progress_velocity_rolling"
    ] = (
        df.groupby("project_code")
        ["progress_velocity"]
        .transform(
            lambda x:
            x.rolling(
                3,
                min_periods=1
            ).mean()
        )
    )

    # --------------------------------------------------------
    # Rolling expenditure velocity
    # --------------------------------------------------------

    df[
        "expenditure_velocity_rolling"
    ] = (
        df.groupby("project_code")
        ["expenditure_velocity"]
        .transform(
            lambda x:
            x.rolling(
                3,
                min_periods=1
            ).mean()
        )
    )

    # ========================================================
    # Clean infinite values
    # ========================================================

    print(
        "\n[6] Cleaning infinite values..."
    )

    df = df.replace(
        [
            np.inf,
            -np.inf
        ],
        np.nan
    )

    # --------------------------------------------------------
    # Fill trajectory values that are naturally unavailable
    # for first snapshots.
    #
    # We DO NOT use target values for filling.
    # --------------------------------------------------------

    trajectory_columns = [
        "progress_change",
        "expenditure_change_cr",
        "expenditure_pct_change",
        "elapsed_month_change",
        "progress_velocity",
        "expenditure_velocity",
        "progress_change_3",
        "expenditure_change_3",
        "progress_velocity_rolling",
        "expenditure_velocity_rolling"
    ]

    for column in trajectory_columns:

        df[column] = df[column].fillna(0)

    # ========================================================
    # Validation
    # ========================================================

    print(
        "\n[7] Validating trajectory features..."
    )

    print(
        f"Rows after feature engineering: "
        f"{len(df)}"
    )

    print(
        "\nNew trajectory features:"
    )

    new_features = [
        "progress_change",
        "expenditure_change_cr",
        "expenditure_pct_change",
        "elapsed_month_change",
        "progress_velocity",
        "expenditure_velocity",
        "expenditure_progress_gap",
        "cost_per_progress_pct",
        "schedule_slippage_months",
        "schedule_pressure_ratio",
        "budget_consumption_ratio",
        "progress_time_ratio",
        "progress_expenditure_ratio",
        "project_age_months",
        "progress_change_3",
        "expenditure_change_3",
        "progress_velocity_rolling",
        "expenditure_velocity_rolling"
    ]

    for feature in new_features:

        print(
            f"  ✓ {feature}"
        )

    # ========================================================
    # Important checks
    # ========================================================

    print(
        "\n[8] Checking project integrity..."
    )

    print(
        "Original projects:",
        df["project_code"].nunique()
    )

    print(
        "Total snapshots:",
        len(df)
    )

    duplicate_rows = df.duplicated().sum()

    print(
        "Duplicate rows:",
        duplicate_rows
    )

    # ========================================================
    # Save
    # ========================================================

    output_path = (
        "data/POWERGRID_trajectory.csv"
    )

    df.to_csv(
        output_path,
        index=False
    )

    print(
        "\n[9] Dataset saved:"
    )

    print(
        output_path
    )

    print("\n")
    print("=" * 75)
    print(
        "TRAJECTORY FEATURE ENGINEERING COMPLETED"
    )
    print("=" * 75)


if __name__ == "__main__":
    main()