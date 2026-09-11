import pandas as pd
import numpy as np

from src.config import (
    TRAIN_DATA_PATH,
    TEST_DATA_PATH,
    COST_TARGET,
    SCHEDULE_TARGET
)


print("=" * 75)
print("       SIH 25192 - PROJECT LEVEL DATA AUDIT")
print("=" * 75)


def audit_projects(df, dataset_name):

    print("\n")
    print("=" * 75)
    print(f"{dataset_name.upper()} PROJECT AUDIT")
    print("=" * 75)

    projects = []

    for project_code, group in df.groupby("project_code"):

        group = group.sort_values("snapshot_date")

        cost_values = group[COST_TARGET].dropna()
        schedule_values = group[SCHEDULE_TARGET].dropna()

        # ----------------------------------------------------
        # Basic project information
        # ----------------------------------------------------

        project_name = group["project_name"].iloc[0]

        category = group["project_category"].iloc[0]

        snapshots = len(group)

        # ----------------------------------------------------
        # Cost target information
        # ----------------------------------------------------

        cost_unique = cost_values.nunique()

        cost_mean = (
            cost_values.mean()
            if len(cost_values) > 0
            else np.nan
        )

        cost_max = (
            cost_values.max()
            if len(cost_values) > 0
            else np.nan
        )

        cost_min = (
            cost_values.min()
            if len(cost_values) > 0
            else np.nan
        )

        positive_cost_count = (
            (cost_values > 0).sum()
            if len(cost_values) > 0
            else 0
        )

        # ----------------------------------------------------
        # Schedule target information
        # ----------------------------------------------------

        schedule_unique = schedule_values.nunique()

        schedule_mean = (
            schedule_values.mean()
            if len(schedule_values) > 0
            else np.nan
        )

        schedule_max = (
            schedule_values.max()
            if len(schedule_values) > 0
            else np.nan
        )

        # ----------------------------------------------------
        # Feature ranges
        # ----------------------------------------------------

        progress_min = group[
            "physical_progress_pct"
        ].min()

        progress_max = group[
            "physical_progress_pct"
        ].max()

        expenditure_pct_min = group[
            "expenditure_pct_of_original_cost"
        ].min()

        expenditure_pct_max = group[
            "expenditure_pct_of_original_cost"
        ].max()

        elapsed_max = group[
            "elapsed_months"
        ].max()

        planned_duration = group[
            "planned_duration_months"
        ].iloc[0]

        # ----------------------------------------------------
        # Suspicion flags
        # ----------------------------------------------------

        flags = []

        # Too few observations
        if snapshots < 2:
            flags.append(
                "VERY_FEW_SNAPSHOTS"
            )

        # Impossible physical progress
        if (
            progress_min < 0
            or progress_max > 100
        ):
            flags.append(
                "INVALID_PROGRESS"
            )

        # Impossible expenditure
        if (
            group[
                "cumulative_expenditure_cr"
            ].min() < 0
        ):
            flags.append(
                "NEGATIVE_EXPENDITURE"
            )

        # Impossible original cost
        if (
            group[
                "original_cost_cr"
            ].min() <= 0
        ):
            flags.append(
                "INVALID_ORIGINAL_COST"
            )

        # Cost target extreme
        if cost_max > 50:
            flags.append(
                "EXTREME_COST_OVERRUN"
            )

        # Schedule target extreme
        if schedule_max > 40:
            flags.append(
                "EXTREME_SCHEDULE_OVERRUN"
            )

        # Expenditure dramatically above original cost
        if expenditure_pct_max > 150:
            flags.append(
                "VERY_HIGH_EXPENDITURE"
            )

        # Elapsed time dramatically exceeds planned duration
        if (
            planned_duration > 0
            and elapsed_max
            > planned_duration * 5
        ):
            flags.append(
                "VERY_LONG_DURATION"
            )

        # Cost target changes within project
        if cost_unique > 1:
            flags.append(
                "COST_TARGET_VARIES"
            )

        # Schedule target changes
        if schedule_unique > 1:
            flags.append(
                "SCHEDULE_TARGET_VARIES"
            )

        projects.append(
            {
                "project_code": project_code,
                "project_name": project_name,
                "project_category": category,
                "snapshots": snapshots,
                "cost_mean": cost_mean,
                "cost_min": cost_min,
                "cost_max": cost_max,
                "positive_cost_snapshots":
                    positive_cost_count,
                "schedule_mean":
                    schedule_mean,
                "schedule_max":
                    schedule_max,
                "progress_min":
                    progress_min,
                "progress_max":
                    progress_max,
                "expenditure_pct_min":
                    expenditure_pct_min,
                "expenditure_pct_max":
                    expenditure_pct_max,
                "elapsed_max":
                    elapsed_max,
                "planned_duration":
                    planned_duration,
                "flags":
                    "; ".join(flags)
                    if flags
                    else "NONE"
            }
        )

    result = pd.DataFrame(projects)

    # --------------------------------------------------------
    # Print project summary
    # --------------------------------------------------------

    print(
        f"\nProjects: {len(result)}"
    )

    print(
        f"Rows: {len(df)}"
    )

    print(
        "\nProject categories:"
    )

    print(
        result[
            "project_category"
        ].value_counts()
    )

    # --------------------------------------------------------
    # Flagged projects
    # --------------------------------------------------------

    flagged = result[
        result["flags"] != "NONE"
    ].copy()

    print("\n")
    print("-" * 75)
    print("FLAGGED PROJECTS")
    print("-" * 75)

    if flagged.empty:

        print(
            "No suspicious projects found."
        )

    else:

        print(
            flagged[
                [
                    "project_code",
                    "project_category",
                    "snapshots",
                    "cost_mean",
                    "cost_max",
                    "schedule_mean",
                    "schedule_max",
                    "flags"
                ]
            ].to_string(
                index=False
            )
        )

    return result


def main():

    train = pd.read_csv(
        TRAIN_DATA_PATH
    )

    test = pd.read_csv(
        TEST_DATA_PATH
    )

    # --------------------------------------------------------
    # Audit train
    # --------------------------------------------------------

    train_result = audit_projects(
        train,
        "Training"
    )

    # --------------------------------------------------------
    # Audit test
    # --------------------------------------------------------

    test_result = audit_projects(
        test,
        "Testing"
    )

    # --------------------------------------------------------
    # Combined audit
    # --------------------------------------------------------

    combined = pd.concat(
        [
            train_result.assign(
                dataset="train"
            ),
            test_result.assign(
                dataset="test"
            )
        ],
        ignore_index=True
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    output_path = (
        "reports/project_level_audit.csv"
    )

    combined.to_csv(
        output_path,
        index=False
    )

    print("\n")
    print("=" * 75)
    print("AUDIT SAVED")
    print("=" * 75)

    print(output_path)

    # --------------------------------------------------------
    # Important high-overrun projects
    # --------------------------------------------------------

    print("\n")
    print("=" * 75)
    print("HIGH COST-OVERRUN PROJECTS")
    print("=" * 75)

    high_cost = combined[
        combined["cost_max"] >= 10
    ].sort_values(
        "cost_max",
        ascending=False
    )

    if high_cost.empty:

        print(
            "No projects with >=10% cost overrun."
        )

    else:

        print(
            high_cost[
                [
                    "dataset",
                    "project_code",
                    "project_name",
                    "cost_mean",
                    "cost_max",
                    "positive_cost_snapshots",
                    "flags"
                ]
            ].to_string(
                index=False
            )
        )

    print("\n")
    print("=" * 75)
    print("PROJECT LEVEL AUDIT COMPLETED")
    print("=" * 75)


if __name__ == "__main__":
    main()