import pandas as pd

from src.config import (
    TRAIN_DATA_PATH,
    TEST_DATA_PATH
)


print("=" * 75)
print("       SIH 25192 - TRAJECTORY TRAIN / TEST SPLIT")
print("=" * 75)


# ============================================================
# Paths
# ============================================================

TRAJECTORY_DATA = (
    "data/POWERGRID_trajectory.csv"
)

TRAJECTORY_TRAIN = (
    "data/train_trajectory.csv"
)

TRAJECTORY_TEST = (
    "data/test_trajectory.csv"
)


# ============================================================
# Main
# ============================================================

def main():

    print("\n[1] Loading trajectory dataset...")

    df = pd.read_csv(
        TRAJECTORY_DATA
    )

    print(
        f"Rows: {len(df)}"
    )

    print(
        f"Projects: "
        f"{df['project_code'].nunique()}"
    )

    # --------------------------------------------------------
    # Load ORIGINAL train/test project lists
    # --------------------------------------------------------

    print(
        "\n[2] Loading original project split..."
    )

    old_train = pd.read_csv(
        TRAIN_DATA_PATH
    )

    old_test = pd.read_csv(
        TEST_DATA_PATH
    )

    train_projects = set(
        old_train[
            "project_code"
        ].unique()
    )

    test_projects = set(
        old_test[
            "project_code"
        ].unique()
    )

    print(
        f"Training projects: "
        f"{len(train_projects)}"
    )

    print(
        f"Testing projects: "
        f"{len(test_projects)}"
    )

    # --------------------------------------------------------
    # Leakage check
    # --------------------------------------------------------

    overlap = (
        train_projects
        &
        test_projects
    )

    print(
        f"Project overlap: "
        f"{len(overlap)}"
    )

    if overlap:

        raise RuntimeError(
            "PROJECT LEAKAGE DETECTED!"
        )

    # --------------------------------------------------------
    # Create trajectory train/test
    # --------------------------------------------------------

    print(
        "\n[3] Creating trajectory split..."
    )

    train_df = df[
        df["project_code"].isin(
            train_projects
        )
    ].copy()

    test_df = df[
        df["project_code"].isin(
            test_projects
        )
    ].copy()

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    train_df = train_df.sort_values(
        [
            "project_code",
            "snapshot_date"
        ]
    )

    test_df = test_df.sort_values(
        [
            "project_code",
            "snapshot_date"
        ]
    )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    print("\n[4] Validation")

    print(
        f"Training rows : "
        f"{len(train_df)}"
    )

    print(
        f"Testing rows  : "
        f"{len(test_df)}"
    )

    print(
        f"Training projects : "
        f"{train_df['project_code'].nunique()}"
    )

    print(
        f"Testing projects : "
        f"{test_df['project_code'].nunique()}"
    )

    actual_overlap = (
        set(train_df["project_code"])
        &
        set(test_df["project_code"])
    )

    print(
        f"Actual project overlap : "
        f"{len(actual_overlap)}"
    )

    if actual_overlap:

        raise RuntimeError(
            "TRAJECTORY PROJECT LEAKAGE!"
        )

    # --------------------------------------------------------
    # Row accounting
    # --------------------------------------------------------

    if (
        len(train_df)
        +
        len(test_df)
        !=
        len(df)
    ):

        raise RuntimeError(
            "ROW ACCOUNTING ERROR!"
        )

    print(
        "Row accounting: PASSED"
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    train_df.to_csv(
        TRAJECTORY_TRAIN,
        index=False
    )

    test_df.to_csv(
        TRAJECTORY_TEST,
        index=False
    )

    print(
        "\n[5] Files saved"
    )

    print(
        f"Training: {TRAJECTORY_TRAIN}"
    )

    print(
        f"Testing : {TRAJECTORY_TEST}"
    )

    print("\n")
    print("=" * 75)
    print(
        "TRAJECTORY TRAIN / TEST SPLIT COMPLETED"
    )
    print("=" * 75)


if __name__ == "__main__":
    main()