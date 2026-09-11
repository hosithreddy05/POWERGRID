import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# SIH 25192 - POWERGRID DATA PREPROCESSING
# ============================================================

# ------------------------------------------------------------
# Project directories
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = BASE_DIR / "data" / "POWERGRID.csv"
OUTPUT_PATH = BASE_DIR / "data" / "POWERGRID_cleaned.csv"


# ------------------------------------------------------------
# Required columns
# ------------------------------------------------------------

REQUIRED_COLUMNS = [
    "project_code",
    "project_name",
    "state",
    "snapshot_date",
    "start_date",
    "original_doc",
    "original_cost_cr",
    "cumulative_expenditure_cr",
    "physical_progress_pct",
    "planned_duration_months",
    "elapsed_months",
    "months_to_original_target",
    "expenditure_pct_of_original_cost",
    "progress_gap_pct",
    "project_category",
    "target_cost_overrun_pct",
    "target_schedule_overrun_months",
    "delay_flag",
    "cost_overrun_flag",
]


# ------------------------------------------------------------
# Main preprocessing function
# ------------------------------------------------------------

def preprocess_data():

    print("=" * 70)
    print("        SIH 25192 - POWERGRID DATA PREPROCESSING")
    print("=" * 70)

    # ========================================================
    # 1. Check input file
    # ========================================================

    if not INPUT_PATH.exists():

        raise FileNotFoundError(
            f"\nDataset not found:\n{INPUT_PATH}"
        )

    print("\n[1] Input dataset found:")
    print(INPUT_PATH)

    # ========================================================
    # 2. Load dataset
    # ========================================================

    df = pd.read_csv(INPUT_PATH)

    print("\n[2] Dataset loaded successfully.")

    original_rows = len(df)

    print(f"Original rows: {original_rows}")
    print(f"Original columns: {len(df.columns)}")

    # ========================================================
    # 3. Validate columns
    # ========================================================

    print("\n[3] Checking required columns...")

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            "The following required columns are missing:\n"
            + "\n".join(missing_columns)
        )

    print("All required columns are present.")

    # ========================================================
    # 4. Check duplicate rows
    # ========================================================

    duplicate_count = df.duplicated().sum()

    print("\n[4] Duplicate check")

    print(f"Duplicate rows: {duplicate_count}")

    if duplicate_count > 0:

        print("Removing duplicate rows...")

        df = df.drop_duplicates().copy()

    else:

        print("No duplicate rows found.")

    # ========================================================
    # 5. Drop state
    # ========================================================

    print("\n[5] Handling state")

    state_missing = df["state"].isna().sum()

    print(
        f"Missing state values: "
        f"{state_missing} "
        f"({state_missing / len(df) * 100:.2f}%)"
    )

    print(
        "Decision: dropping raw state because of "
        "high missingness and high cardinality."
    )

    df = df.drop(columns=["state"])

    # ========================================================
    # 6. Drop redundant progress_gap_pct
    # ========================================================

    print("\n[6] Checking progress_gap_pct")

    calculated_gap = (
        100 - df["physical_progress_pct"]
    )

    difference = (
        df["progress_gap_pct"] - calculated_gap
    ).abs().max()

    print(
        f"Maximum difference from "
        f"(100 - physical_progress_pct): {difference}"
    )

    if difference < 1e-8:

        print(
            "progress_gap_pct is mathematically redundant."
        )

        print("Dropping progress_gap_pct.")

        df = df.drop(
            columns=["progress_gap_pct"]
        )

    else:

        print(
            "progress_gap_pct is NOT exactly redundant."
        )

    # ========================================================
    # 7. Handle rare project categories
    # ========================================================

    print("\n[7] Handling project categories")

    print("Original categories:")

    print(
        df["project_category"]
        .value_counts(dropna=False)
        .to_string()
    )

    # Merge Communication into Other_Power_Transmission

    communication_count = (
        df["project_category"]
        .eq("Communication")
        .sum()
    )

    print(
        f"\nCommunication observations: "
        f"{communication_count}"
    )

    if communication_count > 0:

        df.loc[
            df["project_category"] == "Communication",
            "project_category"
        ] = "Other_Power_Transmission"

        print(
            "Communication merged into "
            "Other_Power_Transmission."
        )

    print("\nFinal categories:")

    print(
        df["project_category"]
        .value_counts(dropna=False)
        .to_string()
    )

    # ========================================================
    # 8. Handle schedule target sentinel 99
    # ========================================================

    print("\n[8] Handling schedule target value 99")

    sentinel_count = (
        df["target_schedule_overrun_months"]
        .eq(99)
        .sum()
    )

    print(
        f"Number of 99 values: {sentinel_count}"
    )

    if sentinel_count > 0:

        print(
            "Replacing 99 with NaN because 99 is "
            "treated as a sentinel/unknown value."
        )

        df.loc[
            df["target_schedule_overrun_months"] == 99,
            "target_schedule_overrun_months"
        ] = np.nan

    # ========================================================
    # 9. Validate numerical ranges
    # ========================================================

    print("\n[9] Numerical validation")

    # Physical progress

    invalid_progress = (
        (df["physical_progress_pct"] < 0)
        | (df["physical_progress_pct"] > 100)
    ).sum()

    print(
        f"Invalid physical progress values: "
        f"{invalid_progress}"
    )

    # Original cost

    invalid_original_cost = (
        df["original_cost_cr"] <= 0
    ).sum()

    print(
        f"Invalid original cost values: "
        f"{invalid_original_cost}"
    )

    # Cumulative expenditure

    invalid_expenditure = (
        df["cumulative_expenditure_cr"] < 0
    ).sum()

    print(
        f"Invalid cumulative expenditure values: "
        f"{invalid_expenditure}"
    )

    # Planned duration

    invalid_planned_duration = (
        df["planned_duration_months"] <= 0
    ).sum()

    print(
        f"Invalid planned duration values: "
        f"{invalid_planned_duration}"
    )

    # Elapsed months

    invalid_elapsed = (
        df["elapsed_months"] < 0
    ).sum()

    print(
        f"Invalid elapsed month values: "
        f"{invalid_elapsed}"
    )

    # ========================================================
    # 10. Check target missing values
    # ========================================================

    print("\n[10] Target information")

    cost_missing = (
        df["target_cost_overrun_pct"]
        .isna()
        .sum()
    )

    schedule_missing = (
        df["target_schedule_overrun_months"]
        .isna()
        .sum()
    )

    print(
        f"Missing cost targets: "
        f"{cost_missing}"
    )

    print(
        f"Missing schedule targets: "
        f"{schedule_missing}"
    )

    # ========================================================
    # 11. Ensure dates are parsed correctly
    # ========================================================

    print("\n[11] Date validation")

    df["snapshot_date"] = pd.to_datetime(
        df["snapshot_date"],
        errors="coerce"
    )

    df["start_date"] = pd.to_datetime(
        df["start_date"],
        errors="coerce"
    )

    invalid_snapshot_dates = (
        df["snapshot_date"].isna().sum()
    )

    invalid_start_dates = (
        df["start_date"].isna().sum()
    )

    print(
        f"Invalid snapshot dates: "
        f"{invalid_snapshot_dates}"
    )

    print(
        f"Invalid start dates: "
        f"{invalid_start_dates}"
    )

    # ========================================================
    # 12. Sort by project and snapshot
    # ========================================================

    print("\n[12] Sorting historical snapshots")

    df = df.sort_values(
        by=[
            "project_code",
            "snapshot_date"
        ]
    ).reset_index(drop=True)

    print(
        "Rows sorted by project_code and snapshot_date."
    )

    # ========================================================
    # 13. Final feature list
    # ========================================================

    print("\n[13] Final ML feature candidates")

    feature_columns = [
        "original_cost_cr",
        "cumulative_expenditure_cr",
        "physical_progress_pct",
        "planned_duration_months",
        "elapsed_months",
        "months_to_original_target",
        "expenditure_pct_of_original_cost",
        "project_category",
    ]

    for column in feature_columns:

        print(f"  ✓ {column}")

    # ========================================================
    # 14. Verify feature columns exist
    # ========================================================

    missing_features = [
        column
        for column in feature_columns
        if column not in df.columns
    ]

    if missing_features:

        raise ValueError(
            "Missing feature columns:\n"
            + "\n".join(missing_features)
        )

    # ========================================================
    # 15. Save cleaned dataset
    # ========================================================

    df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("\n[14] Cleaned dataset saved")

    print(OUTPUT_PATH)

    # ========================================================
    # 16. Final summary
    # ========================================================

    print("\n" + "=" * 70)
    print("PREPROCESSING COMPLETED SUCCESSFULLY")
    print("=" * 70)

    print(
        f"\nOriginal rows : {original_rows}"
    )

    print(
        f"Final rows    : {len(df)}"
    )

    print(
        f"Rows removed  : {original_rows - len(df)}"
    )

    print(
        f"Final columns : {len(df.columns)}"
    )

    print(
        "\nOriginal dataset was NOT modified."
    )

    print(
        "Cleaned dataset:"
    )

    print(
        OUTPUT_PATH
    )

    print("=" * 70)


if __name__ == "__main__":
    preprocess_data()