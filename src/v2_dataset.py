"""
SIH 25192 - V2 DATASET PREPARATION

Creates a separate V2 dataset using only real project data.

IMPORTANT:
- Does NOT modify V1 datasets.
- Does NOT use synthetic data.
- Does NOT append PDF rows.
- Keeps project-level train/test separation.
"""

from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

TRAIN_PATH = ROOT / "data" / "train_trajectory.csv"
TEST_PATH = ROOT / "data" / "test_trajectory.csv"

V2_DIR = ROOT / "data" / "v2"

TRAIN_OUTPUT = V2_DIR / "train_v2.csv"
TEST_OUTPUT = V2_DIR / "test_v2.csv"


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

TARGETS = [
    "target_cost_overrun_pct",
    "target_schedule_overrun_months",
]


def validate_columns(df, required_columns, dataset_name):

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"{dataset_name} is missing columns: {missing}"
        )


def prepare_dataset(df, dataset_name):

    required = (
        ["project_code", "project_name", "snapshot_date"]
        + BASE_FEATURES
        + TRAJECTORY_FEATURES
        + TARGETS
    )

    validate_columns(
        df,
        required,
        dataset_name
    )

    columns = (
        ["project_code", "project_name", "snapshot_date"]
        + BASE_FEATURES
        + TRAJECTORY_FEATURES
        + TARGETS
    )

    result = df[columns].copy()

    # Remove completely duplicated observations only.
    before = len(result)

    result = result.drop_duplicates(
        subset=[
            "project_code",
            "snapshot_date"
        ]
    )

    removed = before - len(result)

    print(f"{dataset_name} duplicate rows removed: {removed}")

    # Check numeric features
    numeric_features = [
        col
        for col in BASE_FEATURES + TRAJECTORY_FEATURES
        if col != "project_category"
    ]

    print(f"\n{dataset_name} missing values:")

    missing_counts = result[
        numeric_features
    ].isna().sum()

    for feature, count in missing_counts.items():

        if count > 0:
            print(
                f"  {feature}: {count}"
            )

    # Replace infinite values with NaN
    result = result.replace(
        [float("inf"), float("-inf")],
        pd.NA
    )

    # We do NOT fabricate missing values.
    # Rows missing required model features are removed.
    before_missing = len(result)

    result = result.dropna(
        subset=BASE_FEATURES + TRAJECTORY_FEATURES + TARGETS
    )

    removed_missing = (
        before_missing - len(result)
    )

    print(
        f"{dataset_name} rows removed due to "
        f"missing required values: {removed_missing}"
    )

    return result


def main():

    print("=" * 75)
    print("       SIH 25192 - V2 DATASET PREPARATION")
    print("=" * 75)

    # --------------------------------------------------------
    # 1. Load
    # --------------------------------------------------------

    print("\n[1] Loading trajectory datasets...")

    if not TRAIN_PATH.exists():
        raise FileNotFoundError(
            f"Training file not found: {TRAIN_PATH}"
        )

    if not TEST_PATH.exists():
        raise FileNotFoundError(
            f"Testing file not found: {TEST_PATH}"
        )

    train = pd.read_csv(TRAIN_PATH)
    test = pd.read_csv(TEST_PATH)

    print("Training rows :", len(train))
    print("Testing rows  :", len(test))

    # --------------------------------------------------------
    # 2. Project split validation
    # --------------------------------------------------------

    print("\n[2] Checking project separation...")

    train_projects = set(
        train["project_code"]
    )

    test_projects = set(
        test["project_code"]
    )

    overlap = train_projects & test_projects

    print("Training projects :", len(train_projects))
    print("Testing projects  :", len(test_projects))
    print("Project overlap   :", len(overlap))

    if overlap:

        print("Overlapping projects:")
        for project in sorted(overlap):
            print(" ", project)

        raise ValueError(
            "PROJECT LEAKAGE DETECTED"
        )

    print("✓ Project separation valid")

    # --------------------------------------------------------
    # 3. Prepare
    # --------------------------------------------------------

    print("\n[3] Selecting V2 features...")

    print("\nBase features:")

    for feature in BASE_FEATURES:
        print("  ✓", feature)

    print("\nTrajectory features:")

    for feature in TRAJECTORY_FEATURES:
        print("  ✓", feature)

    print("\nTotal model features:", len(
        BASE_FEATURES + TRAJECTORY_FEATURES
    ))

    train_v2 = prepare_dataset(
        train,
        "Training"
    )

    test_v2 = prepare_dataset(
        test,
        "Testing"
    )

    # --------------------------------------------------------
    # 4. Recheck project separation after cleaning
    # --------------------------------------------------------

    print("\n[4] Rechecking project integrity...")

    train_projects_after = set(
        train_v2["project_code"]
    )

    test_projects_after = set(
        test_v2["project_code"]
    )

    overlap_after = (
        train_projects_after
        & test_projects_after
    )

    print(
        "Training projects after cleaning :",
        len(train_projects_after)
    )

    print(
        "Testing projects after cleaning  :",
        len(test_projects_after)
    )

    print(
        "Project overlap after cleaning   :",
        len(overlap_after)
    )

    if overlap_after:
        raise ValueError(
            "PROJECT LEAKAGE AFTER CLEANING"
        )

    print("✓ Final project separation valid")

    # --------------------------------------------------------
    # 5. Target distributions
    # --------------------------------------------------------

    print("\n[5] Target distribution")

    cost_target = "target_cost_overrun_pct"
    schedule_target = "target_schedule_overrun_months"

    print("\nCOST")

    print(
        "Training positive:",
        int(
            (train_v2[cost_target] > 0.5).sum()
        )
    )

    print(
        "Training non-positive:",
        int(
            (train_v2[cost_target] <= 0.5).sum()
        )
    )

    print(
        "Testing positive:",
        int(
            (test_v2[cost_target] > 0.5).sum()
        )
    )

    print("\nSCHEDULE")

    print(
        "Training target rows:",
        train_v2[schedule_target].notna().sum()
    )

    print(
        "Testing target rows:",
        test_v2[schedule_target].notna().sum()
    )

    # --------------------------------------------------------
    # 6. Save
    # --------------------------------------------------------

    print("\n[6] Saving V2 datasets...")

    V2_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    train_v2.to_csv(
        TRAIN_OUTPUT,
        index=False
    )

    test_v2.to_csv(
        TEST_OUTPUT,
        index=False
    )

    print("✓", TRAIN_OUTPUT)
    print("✓", TEST_OUTPUT)

    # --------------------------------------------------------
    # 7. Final summary
    # --------------------------------------------------------

    print("\n" + "=" * 75)
    print("V2 DATASET SUMMARY")
    print("=" * 75)

    print(
        "Training rows     :",
        len(train_v2)
    )

    print(
        "Testing rows      :",
        len(test_v2)
    )

    print(
        "Training projects :",
        train_v2["project_code"].nunique()
    )

    print(
        "Testing projects  :",
        test_v2["project_code"].nunique()
    )

    print(
        "Model features    :",
        len(BASE_FEATURES + TRAJECTORY_FEATURES)
    )

    print(
        "Synthetic data    : NO"
    )

    print(
        "PDF rows appended : NO"
    )

    print(
        "V1 modified       : NO"
    )

    print("\n" + "=" * 75)
    print("V2 DATASET PREPARATION COMPLETED")
    print("=" * 75)


if __name__ == "__main__":
    main()