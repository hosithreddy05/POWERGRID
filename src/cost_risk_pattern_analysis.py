import pandas as pd
import numpy as np

from src.config import (
    TRAIN_DATA_PATH,
    COST_TARGET
)


print("=" * 75)
print("       SIH 25192 - COST RISK PATTERN ANALYSIS")
print("=" * 75)


# ============================================================
# FEATURES WE WANT TO STUDY
# ============================================================

NUMERICAL_FEATURES = [
    "original_cost_cr",
    "cumulative_expenditure_cr",
    "physical_progress_pct",
    "planned_duration_months",
    "elapsed_months",
    "months_to_original_target",
    "expenditure_pct_of_original_cost"
]


# ============================================================
# MAIN
# ============================================================

def main():

    # ========================================================
    # 1. LOAD TRAINING DATA
    # ========================================================

    print("\n[1] Loading training data...")

    df = pd.read_csv(
        TRAIN_DATA_PATH
    )

    print(
        f"Training rows   : {len(df)}"
    )

    print(
        f"Training projects: "
        f"{df['project_code'].nunique()}"
    )

    # ========================================================
    # 2. CREATE PROJECT-LEVEL COST TARGET
    # ========================================================

    print(
        "\n[2] Creating project-level cost risk..."
    )

    project_target = (
        df.groupby("project_code")
        [COST_TARGET]
        .max()
        .rename("max_cost_overrun")
    )

    df = df.merge(
        project_target,
        on="project_code",
        how="left"
    )

    # A project is considered an overrun project
    # if its maximum observed cost overrun is > 0.

    df["cost_risk"] = (
        df["max_cost_overrun"] > 0
    ).astype(int)

    # ========================================================
    # 3. SELECT LATEST SNAPSHOT
    # ========================================================

    print(
        "\n[3] Selecting latest snapshot..."
    )

    df["snapshot_date"] = pd.to_datetime(
        df["snapshot_date"],
        errors="coerce"
    )

    latest = (
        df.sort_values(
            [
                "project_code",
                "snapshot_date"
            ]
        )
        .groupby(
            "project_code"
        )
        .tail(1)
        .copy()
    )

    print(
        f"Projects analysed: "
        f"{len(latest)}"
    )

    # ========================================================
    # 4. CREATE DERIVED FEATURES
    # ========================================================

    print(
        "\n[4] Creating derived risk indicators..."
    )

    # --------------------------------------------------------
    # Expenditure - progress gap
    # --------------------------------------------------------

    latest[
        "expenditure_progress_gap"
    ] = (
        latest[
            "expenditure_pct_of_original_cost"
        ]
        -
        latest[
            "physical_progress_pct"
        ]
    )

    # --------------------------------------------------------
    # Schedule slippage
    #
    # Negative months_to_original_target means
    # the project is beyond the original target.
    # --------------------------------------------------------

    latest[
        "schedule_slippage_months"
    ] = (
        -latest[
            "months_to_original_target"
        ]
    ).clip(
        lower=0
    )

    # --------------------------------------------------------
    # Schedule pressure ratio
    # --------------------------------------------------------

    latest[
        "schedule_pressure_ratio"
    ] = (
        latest[
            "elapsed_months"
        ]
        /
        latest[
            "planned_duration_months"
        ].replace(
            0,
            np.nan
        )
    )

    # --------------------------------------------------------
    # Budget consumption ratio
    # --------------------------------------------------------

    latest[
        "budget_consumption_ratio"
    ] = (
        latest[
            "expenditure_pct_of_original_cost"
        ]
        /
        100
    )

    # --------------------------------------------------------
    # Expenditure / progress ratio
    # --------------------------------------------------------

    latest[
        "expenditure_progress_ratio"
    ] = (
        latest[
            "expenditure_pct_of_original_cost"
        ]
        /
        latest[
            "physical_progress_pct"
        ].replace(
            0,
            np.nan
        )
    )

    # Clean infinite values

    latest = latest.replace(
        [
            np.inf,
            -np.inf
        ],
        np.nan
    )

    # ========================================================
    # 5. SPLIT INTO NORMAL AND RISK PROJECTS
    # ========================================================

    normal = latest[
        latest["cost_risk"] == 0
    ].copy()

    risky = latest[
        latest["cost_risk"] == 1
    ].copy()

    print(
        f"\nNormal projects       : "
        f"{len(normal)}"
    )

    print(
        f"Cost-overrun projects: "
        f"{len(risky)}"
    )

    # ========================================================
    # 6. NUMERICAL FEATURE COMPARISON
    # ========================================================

    print("\n")
    print("=" * 75)
    print("NUMERICAL FEATURE COMPARISON")
    print("=" * 75)

    comparison = []

    for feature in NUMERICAL_FEATURES:

        normal_mean = normal[
            feature
        ].mean()

        risky_mean = risky[
            feature
        ].mean()

        normal_median = normal[
            feature
        ].median()

        risky_median = risky[
            feature
        ].median()

        comparison.append(
            {
                "feature": feature,
                "normal_mean": normal_mean,
                "risk_mean": risky_mean,
                "normal_median": normal_median,
                "risk_median": risky_median
            }
        )

    comparison_df = pd.DataFrame(
        comparison
    )

    print(
        comparison_df.to_string(
            index=False
        )
    )

    # ========================================================
    # 7. EXPENDITURE VS PHYSICAL PROGRESS
    # ========================================================

    print("\n")
    print("=" * 75)
    print("EXPENDITURE VS PHYSICAL PROGRESS")
    print("=" * 75)

    print(
        "\nAverage expenditure percentage:"
    )

    print(
        f"Normal projects : "
        f"{normal['expenditure_pct_of_original_cost'].mean():.2f}%"
    )

    print(
        f"Risk projects   : "
        f"{risky['expenditure_pct_of_original_cost'].mean():.2f}%"
    )

    print(
        "\nAverage expenditure-progress gap:"
    )

    print(
        f"Normal projects : "
        f"{normal['expenditure_progress_gap'].mean():.2f}"
    )

    print(
        f"Risk projects   : "
        f"{risky['expenditure_progress_gap'].mean():.2f}"
    )

    print(
        "\nAverage expenditure-progress ratio:"
    )

    print(
        f"Normal projects : "
        f"{normal['expenditure_progress_ratio'].mean():.2f}"
    )

    print(
        f"Risk projects   : "
        f"{risky['expenditure_progress_ratio'].mean():.2f}"
    )

    # ========================================================
    # 8. SCHEDULE SLIPPAGE
    # ========================================================

    print("\n")
    print("=" * 75)
    print("SCHEDULE SLIPPAGE")
    print("=" * 75)

    print(
        f"\nNormal project average : "
        f"{normal['schedule_slippage_months'].mean():.2f} months"
    )

    print(
        f"Risk project average   : "
        f"{risky['schedule_slippage_months'].mean():.2f} months"
    )

    print(
        f"\nNormal project median : "
        f"{normal['schedule_slippage_months'].median():.2f} months"
    )

    print(
        f"Risk project median   : "
        f"{risky['schedule_slippage_months'].median():.2f} months"
    )

    print(
        "\nSchedule pressure ratio:"
    )

    print(
        f"Normal projects : "
        f"{normal['schedule_pressure_ratio'].mean():.2f}"
    )

    print(
        f"Risk projects   : "
        f"{risky['schedule_pressure_ratio'].mean():.2f}"
    )

    # ========================================================
    # 9. PROJECT CATEGORY
    # ========================================================

    print("\n")
    print("=" * 75)
    print("PROJECT CATEGORY")
    print("=" * 75)

    category_table = pd.crosstab(
        latest["project_category"],
        latest["cost_risk"]
    )

    category_table.columns = [
        "NO_OVERRUN",
        "OVERRUN"
    ]

    print(
        category_table
    )

    # ========================================================
    # 10. RISK PROJECTS
    # ========================================================

    print("\n")
    print("=" * 75)
    print("HIGH-RISK PROJECTS")
    print("=" * 75)

    risk_columns = [
        "project_code",
        "original_cost_cr",
        "cumulative_expenditure_cr",
        "physical_progress_pct",
        "planned_duration_months",
        "elapsed_months",
        "months_to_original_target",
        "expenditure_pct_of_original_cost",
        "expenditure_progress_gap",
        "schedule_slippage_months",
        "schedule_pressure_ratio",
        "project_category",
        "max_cost_overrun"
    ]

    print(
        risky[
            risk_columns
        ]
        .sort_values(
            "max_cost_overrun",
            ascending=False
        )
        .to_string(
            index=False
        )
    )

    # ========================================================
    # 11. NORMAL PROJECT SUMMARY
    # ========================================================

    print("\n")
    print("=" * 75)
    print("NORMAL PROJECT SUMMARY")
    print("=" * 75)

    normal_summary = normal[
        [
            "project_code",
            "original_cost_cr",
            "physical_progress_pct",
            "elapsed_months",
            "months_to_original_target",
            "expenditure_pct_of_original_cost",
            "expenditure_progress_gap",
            "schedule_slippage_months",
            "project_category"
        ]
    ].copy()

    print(
        normal_summary.head(15).to_string(
            index=False
        )
    )

    # ========================================================
    # 12. POSSIBLE RISK INDICATORS
    # ========================================================

    print("\n")
    print("=" * 75)
    print("POSSIBLE RISK INDICATORS")
    print("=" * 75)

    # These are descriptive indicators only.
    # They are NOT being declared as final ML rules.

    indicators = {
        "Expenditure > 100%": (
            latest[
                "expenditure_pct_of_original_cost"
            ] > 100
        ),

        "Schedule slippage > 24 months": (
            latest[
                "schedule_slippage_months"
            ] > 24
        ),

        "Expenditure > progress": (
            latest[
                "expenditure_progress_gap"
            ] > 0
        ),

        "Expenditure > progress by 20 points": (
            latest[
                "expenditure_progress_gap"
            ] > 20
        ),

        "Elapsed > planned duration": (
            latest[
                "elapsed_months"
            ]
            >
            latest[
                "planned_duration_months"
            ]
        )
    }

    for name, condition in indicators.items():

        total = int(
            condition.sum()
        )

        risky_count = int(
            (
                condition
                &
                (
                    latest[
                        "cost_risk"
                    ] == 1
                )
            ).sum()
        )

        print(
            f"\n{name}"
        )

        print(
            f"Total projects meeting condition : "
            f"{total}"
        )

        print(
            f"Risk projects meeting condition  : "
            f"{risky_count}"
        )

    # ========================================================
    # 13. TARGET DISTRIBUTION
    # ========================================================

    print("\n")
    print("=" * 75)
    print("COST OVERRUN DISTRIBUTION")
    print("=" * 75)

    risk_distribution = (
        latest[
            "max_cost_overrun"
        ]
        .describe()
    )

    print(
        risk_distribution
    )

    # ========================================================
    # 14. SAVE REPORTS
    # ========================================================

    print("\n")
    print("=" * 75)
    print("SAVING ANALYSIS FILES")
    print("=" * 75)

    comparison_df.to_csv(
        "reports/cost_risk_feature_comparison.csv",
        index=False
    )

    latest.to_csv(
        "reports/cost_risk_project_analysis.csv",
        index=False
    )

    print(
        "✓ reports/cost_risk_feature_comparison.csv"
    )

    print(
        "✓ reports/cost_risk_project_analysis.csv"
    )

    # ========================================================
    # COMPLETE
    # ========================================================

    print("\n")
    print("=" * 75)
    print("COST RISK PATTERN ANALYSIS COMPLETED")
    print("=" * 75)


if __name__ == "__main__":
    main()