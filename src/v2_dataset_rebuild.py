"""
SIH 25192 - V2 DATASET REBUILD

Creates separate real-data datasets for:
1. Cost model
2. Schedule model

IMPORTANT:
- V1 is untouched.
- No synthetic data.
- PDF rows are NOT appended.
- Missing cost target does not remove schedule rows.
- Missing schedule target does not remove cost rows.
- Project-level train/test separation is preserved.
"""

from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

TRAIN_SOURCE = ROOT / "data" / "train_trajectory.csv"
TEST_SOURCE = ROOT / "data" / "test_trajectory.csv"

V2_DIR = ROOT / "data" / "v2"

COST_TRAIN_OUTPUT = V2_DIR / "train_cost_v2.csv"
COST_TEST_OUTPUT = V2_DIR / "test_cost_v2.csv"

SCHEDULE_TRAIN_OUTPUT = V2_DIR / "train_schedule_v2.csv"
SCHEDULE_TEST_OUTPUT = V2_DIR / "test_schedule_v2.csv"


# ============================================================
# FEATURES
# ============================================================

BASE_FEATURES = [
    "original_cost_cr",
    "cumulative_expenditure_cr",
    "physical_progress_pct",
    "planned_duration_months",
    "elapsed_months",
    "months_to_original_target",
    "expenditure_pct_of_original_cost",
    "project_category",
]

TRAJECTORY_FEATURES = [
    "progress_velocity",
    "expenditure_velocity",
    "expenditure_progress_gap",
    "schedule_slippage_months",
    "schedule_pressure_ratio",
    "budget_consumption_ratio",
]

IDENTIFIERS = [
    "project_code",
    "project_name",
    "snapshot_date",
]

COST_TARGET = "target_cost_overrun_pct"

SCHEDULE_TARGET = "target_schedule_overrun_months"


def validate_columns(df, dataset_name):

    required = (
        IDENTIFIERS
        + BASE_FEATURES
        + TRAJECTORY_FEATURES
        + [
            COST_TARGET,
            SCHEDULE_TARGET,
        ]
    )

    missing = [
        col
        for col in required
        if col not in df.columns
    ]

    if missing:

        raise ValueError(
            f"{dataset_name} missing columns: {missing}"
        )


def clean_features(df, dataset_name):

    feature_columns = (
        BASE_FEATURES
        + TRAJECTORY_FEATURES
    )

    # Convert infinite numeric values to NaN.
    result = df.copy()

    result = result.replace(
        [float("inf"), float("-inf")],
        pd.NA
    )

    # We only remove rows where INPUT FEATURES are missing.
    # We do NOT require both targets to be present.
    before = len(result)

    result = result.dropna(
        subset=feature_columns
    )

    removed = before - len(result)

    print(
        f"{dataset_name} rows removed due to "
        f"missing INPUT features: {removed}"
    )

    return result


def create_target_dataset(
    df,
    target,
    dataset_name
):

    feature_columns = (
        IDENTIFIERS
        + BASE_FEATURES
        + TRAJECTORY_FEATURES
    )

    columns = (
        feature_columns
        + [target]
    )

    result = df[columns].copy()

    before = len(result)

    result = result.dropna(
        subset=[target]
    )

    removed = before - len(result)

    print(
        f"{dataset_name} rows removed because "
        f"{target} is missing: {removed}"
    )

    return result


def main():

    print("=" * 75)
    print("       SIH 25192 - V2 DATASET REBUILD")
    print("=" * 75)

    # --------------------------------------------------------
    # 1. Load
    # --------------------------------------------------------

    print("\n[1] Loading original trajectory datasets...")

    if not TRAIN_SOURCE.exists():
        raise FileNotFoundError(
            TRAIN_SOURCE
        )

    if not TEST_SOURCE.exists():
        raise FileNotFoundError(
            TEST_SOURCE
        )

    train = pd.read_csv(
        TRAIN_SOURCE
    )

    test = pd.read_csv(
        TEST_SOURCE
    )

    print(
        "Training rows :",
        len(train)
    )

    print(
        "Testing rows  :",
        len(test)
    )

    # --------------------------------------------------------
    # 2. Validate columns
    # --------------------------------------------------------

    print("\n[2] Validating columns...")

    validate_columns(
        train,
        "Training"
    )

    validate_columns(
        test,
        "Testing"
    )

    print(
        "✓ Required columns present"
    )

    # --------------------------------------------------------
    # 3. Project separation
    # --------------------------------------------------------

    print("\n[3] Checking project separation...")

    train_projects = set(
        train["project_code"]
    )

    test_projects = set(
        test["project_code"]
    )

    overlap = (
        train_projects
        & test_projects
    )

    print(
        "Training projects:",
        len(train_projects)
    )

    print(
        "Testing projects :",
        len(test_projects)
    )

    print(
        "Project overlap  :",
        len(overlap)
    )

    if overlap:

        raise ValueError(
            "PROJECT LEAKAGE DETECTED"
        )

    print(
        "✓ Project separation valid"
    )

    # --------------------------------------------------------
    # 4. Clean INPUT features only
    # --------------------------------------------------------

    print("\n[4] Cleaning input features...")

    train = clean_features(
        train,
        "Training"
    )

    test = clean_features(
        test,
        "Testing"
    )

    # --------------------------------------------------------
    # 5. Cost dataset
    # --------------------------------------------------------

    print("\n[5] Creating COST V2 dataset...")

    cost_train = create_target_dataset(
        train,
        COST_TARGET,
        "Cost training"
    )

    cost_test = create_target_dataset(
        test,
        COST_TARGET,
        "Cost testing"
    )

    print(
        "Cost training rows:",
        len(cost_train)
    )

    print(
        "Cost testing rows :",
        len(cost_test)
    )

    print(
        "Cost training projects:",
        cost_train["project_code"].nunique()
    )

    print(
        "Cost testing projects:",
        cost_test["project_code"].nunique()
    )

    # --------------------------------------------------------
    # 6. Schedule dataset
    # --------------------------------------------------------

    print("\n[6] Creating SCHEDULE V2 dataset...")

    schedule_train = create_target_dataset(
        train,
        SCHEDULE_TARGET,
        "Schedule training"
    )

    schedule_test = create_target_dataset(
        test,
        SCHEDULE_TARGET,
        "Schedule testing"
    )

    print(
        "Schedule training rows:",
        len(schedule_train)
    )

    print(
        "Schedule testing rows :",
        len(schedule_test)
    )

    print(
        "Schedule training projects:",
        schedule_train["project_code"].nunique()
    )

    print(
        "Schedule testing projects:",
        schedule_test["project_code"].nunique()
    )

    # --------------------------------------------------------
    # 7. Verify project separation
    # --------------------------------------------------------

    print("\n[7] Final project leakage check...")

    cost_overlap = (
        set(cost_train["project_code"])
        &
        set(cost_test["project_code"])
    )

    schedule_overlap = (
        set(schedule_train["project_code"])
        &
        set(schedule_test["project_code"])
    )

    print(
        "Cost project overlap    :",
        len(cost_overlap)
    )

    print(
        "Schedule project overlap:",
        len(schedule_overlap)
    )

    if cost_overlap:
        raise ValueError(
            "COST PROJECT LEAKAGE"
        )

    if schedule_overlap:
        raise ValueError(
            "SCHEDULE PROJECT LEAKAGE"
        )

    print(
        "✓ No project leakage"
    )

    # --------------------------------------------------------
    # 8. Target statistics
    # --------------------------------------------------------

    print("\n[8] Target statistics")

    print("\nCOST TARGET")

    print(
        cost_train[COST_TARGET]
        .describe()
        .to_string()
    )

    print(
        "\nPositive cost rows (> 0.5%):",
        int(
            (
                cost_train[COST_TARGET]
                > 0.5
            ).sum()
        )
    )

    print("\nSCHEDULE TARGET")

    print(
        schedule_train[SCHEDULE_TARGET]
        .describe()
        .to_string()
    )

    # --------------------------------------------------------
    # 9. Save
    # --------------------------------------------------------

    print("\n[9] Saving V2 datasets...")

    V2_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    cost_train.to_csv(
        COST_TRAIN_OUTPUT,
        index=False
    )

    cost_test.to_csv(
        COST_TEST_OUTPUT,
        index=False
    )

    schedule_train.to_csv(
        SCHEDULE_TRAIN_OUTPUT,
        index=False
    )

    schedule_test.to_csv(
        SCHEDULE_TEST_OUTPUT,
        index=False
    )

    print(
        "✓",
        COST_TRAIN_OUTPUT
    )

    print(
        "✓",
        COST_TEST_OUTPUT
    )

    print(
        "✓",
        SCHEDULE_TRAIN_OUTPUT
    )

    print(
        "✓",
        SCHEDULE_TEST_OUTPUT
    )

    # --------------------------------------------------------
    # 10. Final summary
    # --------------------------------------------------------

    print("\n" + "=" * 75)
    print("V2 DATASET REBUILD SUMMARY")
    print("=" * 75)

    print(
        "Cost training rows       :",
        len(cost_train)
    )

    print(
        "Cost training projects   :",
        cost_train["project_code"].nunique()
    )

    print(
        "Cost testing rows        :",
        len(cost_test)
    )

    print(
        "Cost testing projects    :",
        cost_test["project_code"].nunique()
    )

    print(
        "Schedule training rows  :",
        len(schedule_train)
    )

    print(
        "Schedule training projects:",
        schedule_train["project_code"].nunique()
    )

    print(
        "Schedule testing rows   :",
        len(schedule_test)
    )

    print(
        "Schedule testing projects:",
        schedule_test["project_code"].nunique()
    )

    print(
        "Model features           :",
        len(
            BASE_FEATURES
            + TRAJECTORY_FEATURES
        )
    )

    print(
        "Synthetic data           : NO"
    )

    print(
        "PDF rows appended        : NO"
    )

    print(
        "V1 modified              : NO"
    )

    print("\n" + "=" * 75)
    print("V2 DATASET REBUILD COMPLETED")
    print("=" * 75)


if __name__ == "__main__":
    main()