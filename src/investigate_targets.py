import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "POWERGRID.csv"


def main():

    df = pd.read_csv(DATA_PATH)

    print("=" * 70)
    print("COST TARGET INVESTIGATION")
    print("=" * 70)

    # ---------------------------------------------------------
    # Projects where cost target changes across snapshots
    # ---------------------------------------------------------

    cost_variation = (
        df.groupby("project_code")["target_cost_overrun_pct"]
        .nunique()
    )

    changing_projects = cost_variation[
        cost_variation > 1
    ].index

    print("\nProjects with changing cost targets:")
    print(list(changing_projects))

    for project in changing_projects:

        print("\n" + "-" * 70)
        print(f"PROJECT: {project}")
        print("-" * 70)

        project_df = df[
            df["project_code"] == project
        ].sort_values("snapshot_date")

        columns = [
            "project_code",
            "project_name",
            "snapshot_date",
            "original_cost_cr",
            "cumulative_expenditure_cr",
            "physical_progress_pct",
            "target_cost_overrun_pct",
            "cost_overrun_flag"
        ]

        print(
            project_df[columns].to_string(index=False)
        )

    # ---------------------------------------------------------
    # Schedule 99 investigation
    # ---------------------------------------------------------

    print("\n\n")
    print("=" * 70)
    print("SCHEDULE 99 INVESTIGATION")
    print("=" * 70)

    schedule_99 = df[
        df["target_schedule_overrun_months"] == 99
    ]

    projects_99 = schedule_99[
        "project_code"
    ].unique()

    print("\nProjects containing 99:")
    print(list(projects_99))

    for project in projects_99:

        print("\n" + "-" * 70)
        print(f"PROJECT: {project}")
        print("-" * 70)

        project_df = df[
            df["project_code"] == project
        ].sort_values("snapshot_date")

        columns = [
            "project_code",
            "project_name",
            "snapshot_date",
            "original_doc",
            "months_to_original_target",
            "target_schedule_overrun_months",
            "delay_flag"
        ]

        print(
            project_df[columns].to_string(index=False)
        )


if __name__ == "__main__":
    main()