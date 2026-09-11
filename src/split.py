import pandas as pd
from pathlib import Path
from sklearn.model_selection import GroupShuffleSplit


# ============================================================
# SIH 25192 - PROJECT LEVEL TRAIN / TEST SPLIT
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = BASE_DIR / "data" / "POWERGRID_cleaned.csv"

TRAIN_PATH = BASE_DIR / "data" / "train.csv"
TEST_PATH = BASE_DIR / "data" / "test.csv"


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

TEST_SIZE = 0.25
RANDOM_STATE = 42


def main():

    print("=" * 70)
    print("       SIH 25192 - PROJECT LEVEL TRAIN / TEST SPLIT")
    print("=" * 70)

    # ========================================================
    # 1. Load cleaned dataset
    # ========================================================

    if not INPUT_PATH.exists():

        raise FileNotFoundError(
            f"Cleaned dataset not found:\n{INPUT_PATH}"
        )

    df = pd.read_csv(INPUT_PATH)

    print("\n[1] Dataset loaded")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    # ========================================================
    # 2. Check project_code
    # ========================================================

    if "project_code" not in df.columns:

        raise ValueError(
            "project_code column is missing."
        )

    unique_projects = df["project_code"].nunique()

    print(
        f"Unique projects: {unique_projects}"
    )

    # ========================================================
    # 3. GroupShuffleSplit
    # ========================================================

    print("\n[2] Creating project-level split...")

    splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE
    )

    groups = df["project_code"]

    train_indices, test_indices = next(
        splitter.split(
            df,
            groups=groups
        )
    )

    train_df = df.iloc[
        train_indices
    ].copy()

    test_df = df.iloc[
        test_indices
    ].copy()

    # ========================================================
    # 4. Sort datasets
    # ========================================================

    train_df = train_df.sort_values(
        by=[
            "project_code",
            "snapshot_date"
        ]
    ).reset_index(drop=True)

    test_df = test_df.sort_values(
        by=[
            "project_code",
            "snapshot_date"
        ]
    ).reset_index(drop=True)

    # ========================================================
    # 5. Get project IDs
    # ========================================================

    train_projects = set(
        train_df["project_code"].unique()
    )

    test_projects = set(
        test_df["project_code"].unique()
    )

    # ========================================================
    # 6. Check project overlap
    # ========================================================

    overlap = (
        train_projects
        .intersection(test_projects)
    )

    # ========================================================
    # 7. Print split information
    # ========================================================

    print("\n" + "-" * 70)
    print("SPLIT INFORMATION")
    print("-" * 70)

    print(
        f"Total projects       : "
        f"{unique_projects}"
    )

    print(
        f"Training projects    : "
        f"{len(train_projects)}"
    )

    print(
        f"Testing projects     : "
        f"{len(test_projects)}"
    )

    print(
        f"Training rows        : "
        f"{len(train_df)}"
    )

    print(
        f"Testing rows         : "
        f"{len(test_df)}"
    )

    print(
        f"Project overlap      : "
        f"{len(overlap)}"
    )

    # ========================================================
    # 8. Leakage check
    # ========================================================

    print("\n" + "-" * 70)
    print("PROJECT LEAKAGE CHECK")
    print("-" * 70)

    if len(overlap) == 0:

        print(
            "PASSED: No project appears in both "
            "training and testing sets. ✅"
        )

    else:

        print(
            "FAILED: Project leakage detected! ❌"
        )

        print(
            "Overlapping projects:"
        )

        for project in sorted(overlap):

            print(
                f"  - {project}"
            )

        raise RuntimeError(
            "Project leakage detected."
        )

    # ========================================================
    # 9. Check all rows accounted for
    # ========================================================

    total_split_rows = (
        len(train_df) + len(test_df)
    )

    print("\n" + "-" * 70)
    print("ROW ACCOUNTING CHECK")
    print("-" * 70)

    print(
        f"Original rows : {len(df)}"
    )

    print(
        f"Split rows    : {total_split_rows}"
    )

    if total_split_rows == len(df):

        print(
            "PASSED: All rows are accounted for. ✅"
        )

    else:

        raise RuntimeError(
            "Row count mismatch."
        )

    # ========================================================
    # 10. Save datasets
    # ========================================================

    train_df.to_csv(
        TRAIN_PATH,
        index=False
    )

    test_df.to_csv(
        TEST_PATH,
        index=False
    )

    print("\n" + "-" * 70)
    print("FILES SAVED")
    print("-" * 70)

    print(
        f"Training dataset:\n{TRAIN_PATH}"
    )

    print(
        f"\nTesting dataset:\n{TEST_PATH}"
    )

    # ========================================================
    # 11. Final summary
    # ========================================================

    print("\n" + "=" * 70)
    print("PROJECT-LEVEL SPLIT COMPLETED SUCCESSFULLY")
    print("=" * 70)

    print(
        "\nTraining projects:",
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

    print("=" * 70)


if __name__ == "__main__":
    main()