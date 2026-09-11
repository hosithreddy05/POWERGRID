import pandas as pd
from pathlib import Path


# ============================================================
# SIH 25192 - POWERGRID DATA QUALITY CHECK
# ============================================================

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Dataset location
DATA_PATH = BASE_DIR / "data" / "POWERGRID.csv"


def main():

    print("=" * 70)
    print("        SIH 25192 - POWERGRID DATA QUALITY REPORT")
    print("=" * 70)

    # --------------------------------------------------------
    # 1. Check whether the dataset exists
    # --------------------------------------------------------

    if not DATA_PATH.exists():
        print("\nERROR: Dataset not found!")
        print(f"Expected location: {DATA_PATH}")
        return

    print("\n[1] Dataset found:")
    print(DATA_PATH)

    # --------------------------------------------------------
    # 2. Load dataset
    # --------------------------------------------------------

    try:
        df = pd.read_csv(DATA_PATH)
    except Exception as e:
        print("\nERROR while reading CSV:")
        print(e)
        return

    print("\n[2] Dataset loaded successfully.")

    # --------------------------------------------------------
    # 3. Basic information
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("BASIC DATASET INFORMATION")
    print("-" * 70)

    print(f"Rows    : {df.shape[0]}")
    print(f"Columns : {df.shape[1]}")

    # --------------------------------------------------------
    # 4. Column names
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("COLUMN NAMES")
    print("-" * 70)

    for i, column in enumerate(df.columns, start=1):
        print(f"{i:2}. {column}")

    # --------------------------------------------------------
    # 5. Unique projects
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("PROJECT INFORMATION")
    print("-" * 70)

    if "project_code" in df.columns:
        unique_projects = df["project_code"].nunique()

        print(f"Unique projects : {unique_projects}")

        print("\nSnapshots per project:")

        snapshots = df.groupby("project_code").size()

        print(snapshots.describe())

    else:
        print("WARNING: project_code column not found.")

    # --------------------------------------------------------
    # 6. Missing values
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("MISSING VALUES")
    print("-" * 70)

    missing = df.isnull().sum()

    missing = missing[missing > 0]

    if len(missing) == 0:
        print("No missing values found.")
    else:
        for column, count in missing.items():

            percentage = (count / len(df)) * 100

            print(
                f"{column:40} "
                f"{count:5} missing "
                f"({percentage:.2f}%)"
            )

    # --------------------------------------------------------
    # 7. Duplicate rows
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("DUPLICATE ROWS")
    print("-" * 70)

    duplicate_count = df.duplicated().sum()

    print(f"Duplicate rows: {duplicate_count}")

    # --------------------------------------------------------
    # 8. Project categories
    # --------------------------------------------------------

    if "project_category" in df.columns:

        print("\n" + "-" * 70)
        print("PROJECT CATEGORY DISTRIBUTION")
        print("-" * 70)

        print(
            df["project_category"]
            .value_counts(dropna=False)
            .to_string()
        )

    # --------------------------------------------------------
    # 9. Cost target analysis
    # --------------------------------------------------------

    if "target_cost_overrun_pct" in df.columns:

        print("\n" + "-" * 70)
        print("COST OVERRUN TARGET")
        print("-" * 70)

        target = df["target_cost_overrun_pct"]

        print(f"Minimum : {target.min():.2f}")
        print(f"Maximum : {target.max():.2f}")
        print(f"Mean    : {target.mean():.2f}")
        print(f"Median  : {target.median():.2f}")

        zero_count = (target == 0).sum()

        print(f"Zero values: {zero_count}")
        print(f"Zero percentage: {(zero_count / len(df)) * 100:.2f}%")

        if "project_code" in df.columns:

            project_cost_values = (
                df.groupby("project_code")["target_cost_overrun_pct"]
                .nunique()
            )

            print(
                "\nProjects with more than one "
                "cost-target value:"
            )

            print(
                (project_cost_values > 1).sum()
            )

    # --------------------------------------------------------
    # 10. Schedule target analysis
    # --------------------------------------------------------

    if "target_schedule_overrun_months" in df.columns:

        print("\n" + "-" * 70)
        print("SCHEDULE OVERRUN TARGET")
        print("-" * 70)

        target = df["target_schedule_overrun_months"]

        print(f"Minimum : {target.min():.2f}")
        print(f"Maximum : {target.max():.2f}")
        print(f"Mean    : {target.mean():.2f}")
        print(f"Median  : {target.median():.2f}")

        sentinel_count = (target == 99).sum()

        print(f"\nValue 99 count: {sentinel_count}")

        if sentinel_count > 0:

            print("\nProjects containing value 99:")

            if "project_code" in df.columns:

                projects_99 = df.loc[
                    target == 99,
                    "project_code"
                ].unique()

                for project in projects_99:
                    print(f"  - {project}")

    # --------------------------------------------------------
    # 11. Potential leakage columns
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("LEAKAGE CHECK")
    print("-" * 70)

    forbidden_columns = [
        "target_cost_overrun_pct",
        "target_schedule_overrun_months",
        "delay_flag",
        "cost_overrun_flag"
    ]

    print(
        "These columns are targets/outcomes and must NOT "
        "be used as model features:"
    )

    for column in forbidden_columns:

        if column in df.columns:
            print(f"  FOUND → {column}")

    # --------------------------------------------------------
    # 12. Numerical summary
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("NUMERICAL SUMMARY")
    print("-" * 70)

    print(df.describe().T.to_string())

    # --------------------------------------------------------
    # Final message
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("DATA QUALITY CHECK COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()