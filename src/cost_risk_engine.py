import pandas as pd
import numpy as np


print("=" * 75)
print("       SIH 25192 - COST RISK ENGINE")
print("=" * 75)


# ============================================================
# RISK THRESHOLDS
# ============================================================
#
# IMPORTANT:
# These thresholds are NOT claimed to be universal truths.
#
# They are initial empirical thresholds derived from the
# patterns observed in the available POWERGRID training data.
#
# We can tune them later.
# ============================================================

RISK_THRESHOLDS = {

    # Expenditure has crossed the original approved cost
    "expenditure_over_100": 100.0,

    # Expenditure is substantially ahead of physical progress
    "expenditure_progress_gap_high": 20.0,

    # Project is more than 24 months beyond original target
    "schedule_slippage_high": 24.0,

    # Elapsed/planned duration ratio
    "schedule_pressure_high": 2.0,

    # Supporting warning
    "expenditure_progress_gap_medium": 0.0
}


# ============================================================
# RISK POINTS
# ============================================================
#
# Strong signals receive more points.
# Supporting signals receive fewer points.
# ============================================================

RISK_POINTS = {

    "expenditure_over_100": 35,

    "expenditure_progress_gap_high": 25,

    "schedule_slippage_high": 25,

    "schedule_pressure_high": 10,

    "expenditure_progress_gap_medium": 5
}


# ============================================================
# RISK LEVELS
# ============================================================

def get_risk_level(score):

    if score >= 60:
        return "HIGH"

    elif score >= 30:
        return "MEDIUM"

    else:
        return "LOW"


# ============================================================
# CALCULATE RISK FOR ONE PROJECT SNAPSHOT
# ============================================================

def calculate_cost_risk(row):

    score = 0

    reasons = []

    warnings = []

    # --------------------------------------------------------
    # Read values
    # --------------------------------------------------------

    expenditure_pct = float(
        row[
            "expenditure_pct_of_original_cost"
        ]
    )

    physical_progress = float(
        row[
            "physical_progress_pct"
        ]
    )

    months_to_target = float(
        row[
            "months_to_original_target"
        ]
    )

    elapsed_months = float(
        row[
            "elapsed_months"
        ]
    )

    planned_duration = float(
        row[
            "planned_duration_months"
        ]
    )

    # --------------------------------------------------------
    # Derived values
    # --------------------------------------------------------

    expenditure_progress_gap = (
        expenditure_pct
        -
        physical_progress
    )

    schedule_slippage = max(
        -months_to_target,
        0
    )

    if planned_duration > 0:

        schedule_pressure = (
            elapsed_months
            /
            planned_duration
        )

    else:

        schedule_pressure = np.nan

    # ========================================================
    # RULE 1
    # ========================================================

    if (
        expenditure_pct
        >
        RISK_THRESHOLDS[
            "expenditure_over_100"
        ]
    ):

        score += RISK_POINTS[
            "expenditure_over_100"
        ]

        reasons.append(
            "Expenditure has exceeded "
            "the original approved cost."
        )

    # ========================================================
    # RULE 2
    # ========================================================

    if (
        expenditure_progress_gap
        >
        RISK_THRESHOLDS[
            "expenditure_progress_gap_high"
        ]
    ):

        score += RISK_POINTS[
            "expenditure_progress_gap_high"
        ]

        reasons.append(
            "Expenditure is substantially "
            "ahead of physical progress."
        )

    # ========================================================
    # RULE 3
    # ========================================================

    if (
        schedule_slippage
        >
        RISK_THRESHOLDS[
            "schedule_slippage_high"
        ]
    ):

        score += RISK_POINTS[
            "schedule_slippage_high"
        ]

        reasons.append(
            "Project is significantly "
            "beyond its original schedule."
        )

    # ========================================================
    # RULE 4
    # ========================================================

    if (
        not np.isnan(
            schedule_pressure
        )
        and
        schedule_pressure
        >
        RISK_THRESHOLDS[
            "schedule_pressure_high"
        ]
    ):

        score += RISK_POINTS[
            "schedule_pressure_high"
        ]

        reasons.append(
            "Elapsed project duration is "
            "more than twice the planned duration."
        )

    # ========================================================
    # RULE 5
    # ========================================================

    if (
        expenditure_progress_gap
        >
        RISK_THRESHOLDS[
            "expenditure_progress_gap_medium"
        ]
        and
        expenditure_progress_gap
        <=
        RISK_THRESHOLDS[
            "expenditure_progress_gap_high"
        ]
    ):

        score += RISK_POINTS[
            "expenditure_progress_gap_medium"
        ]

        warnings.append(
            "Expenditure is currently "
            "ahead of physical progress."
        )

    # --------------------------------------------------------
    # Limit score
    # --------------------------------------------------------

    score = min(
        score,
        100
    )

    # --------------------------------------------------------
    # Risk level
    # --------------------------------------------------------

    risk_level = get_risk_level(
        score
    )

    # --------------------------------------------------------
    # If no reason exists
    # --------------------------------------------------------

    if not reasons:

        reasons.append(
            "No major cost-risk indicator "
            "was detected."
        )

    # --------------------------------------------------------
    # Return
    # --------------------------------------------------------

    return {

        "cost_risk_score": score,

        "cost_risk_level": risk_level,

        "expenditure_pct":
            expenditure_pct,

        "physical_progress_pct":
            physical_progress,

        "expenditure_progress_gap":
            expenditure_progress_gap,

        "schedule_slippage_months":
            schedule_slippage,

        "schedule_pressure_ratio":
            schedule_pressure,

        "risk_reasons":
            reasons,

        "risk_warnings":
            warnings
    }


# ============================================================
# APPLY ENGINE TO DATASET
# ============================================================

def evaluate_dataset(df):

    results = []

    for _, row in df.iterrows():

        result = calculate_cost_risk(
            row
        )

        result[
            "project_code"
        ] = row[
            "project_code"
        ]

        result[
            "snapshot_date"
        ] = row[
            "snapshot_date"
        ]

        result[
            "project_category"
        ] = row[
            "project_category"
        ]

        # Actual target is ONLY used for evaluation.
        # It will NOT be used by the risk engine itself.

        if (
            "target_cost_overrun_pct"
            in row
        ):

            result[
                "actual_cost_overrun_pct"
            ] = row[
                "target_cost_overrun_pct"
            ]

        results.append(
            result
        )

    return pd.DataFrame(
        results
    )


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # Load training data
    # --------------------------------------------------------

    print(
        "\n[1] Loading training data..."
    )

    train_path = (
        "data/train.csv"
    )

    train = pd.read_csv(
        train_path
    )

    print(
        f"Training rows : "
        f"{len(train)}"
    )

    print(
        f"Training projects : "
        f"{train['project_code'].nunique()}"
    )

    # --------------------------------------------------------
    # Evaluate
    # --------------------------------------------------------

    print(
        "\n[2] Calculating risk scores..."
    )

    results = evaluate_dataset(
        train
    )

    # --------------------------------------------------------
    # Latest snapshot per project
    # --------------------------------------------------------

    print(
        "\n[3] Selecting latest project snapshots..."
    )

    results[
        "snapshot_date"
    ] = pd.to_datetime(
        results[
            "snapshot_date"
        ],
        errors="coerce"
    )

    latest = (
        results
        .sort_values(
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

    # --------------------------------------------------------
    # Risk distribution
    # --------------------------------------------------------

    print("\n")
    print("=" * 75)
    print("RISK LEVEL DISTRIBUTION")
    print("=" * 75)

    print(
        latest[
            "cost_risk_level"
        ].value_counts()
    )

    # --------------------------------------------------------
    # Risk score statistics
    # --------------------------------------------------------

    print("\n")
    print("=" * 75)
    print("RISK SCORE STATISTICS")
    print("=" * 75)

    print(
        latest[
            "cost_risk_score"
        ].describe()
    )

    # --------------------------------------------------------
    # Actual overrun comparison
    # --------------------------------------------------------

    if (
        "actual_cost_overrun_pct"
        in latest.columns
    ):

        latest[
            "actual_overrun"
        ] = (
            latest[
                "actual_cost_overrun_pct"
            ] > 0
        )

        print("\n")
        print("=" * 75)
        print("RISK ENGINE vs ACTUAL TRAINING OUTCOME")
        print("=" * 75)

        comparison = (
            latest
            .groupby(
                "cost_risk_level"
            )
            .agg(
                projects=(
                    "project_code",
                    "count"
                ),
                average_risk_score=(
                    "cost_risk_score",
                    "mean"
                ),
                average_actual_overrun=(
                    "actual_cost_overrun_pct",
                    "mean"
                ),
                maximum_actual_overrun=(
                    "actual_cost_overrun_pct",
                    "max"
                ),
                actual_overrun_projects=(
                    "actual_overrun",
                    "sum"
                )
            )
            .reset_index()
        )

        print(
            comparison.to_string(
                index=False
            )
        )

    # --------------------------------------------------------
    # Actual positive projects
    # --------------------------------------------------------

    print("\n")
    print("=" * 75)
    print("KNOWN COST-OVERRUN PROJECTS")
    print("=" * 75)

    positive = latest[
        latest[
            "actual_cost_overrun_pct"
        ] > 0
    ].copy()

    if len(positive) > 0:

        display_columns = [
            "project_code",
            "cost_risk_score",
            "cost_risk_level",
            "actual_cost_overrun_pct",
            "expenditure_pct",
            "physical_progress_pct",
            "expenditure_progress_gap",
            "schedule_slippage_months",
            "schedule_pressure_ratio"
        ]

        print(
            positive[
                display_columns
            ]
            .sort_values(
                "actual_cost_overrun_pct",
                ascending=False
            )
            .to_string(
                index=False
            )
        )

    # --------------------------------------------------------
    # False positive / normal high risk projects
    # --------------------------------------------------------

    print("\n")
    print("=" * 75)
    print("HIGH-RISK NORMAL PROJECTS")
    print("=" * 75)

    false_positive = latest[
        (
            latest[
                "cost_risk_level"
            ]
            ==
            "HIGH"
        )
        &
        (
            latest[
                "actual_cost_overrun_pct"
            ]
            <=
            0
        )
    ]

    if len(false_positive) == 0:

        print(
            "No high-risk normal projects."
        )

    else:

        print(
            false_positive[
                [
                    "project_code",
                    "cost_risk_score",
                    "actual_cost_overrun_pct",
                    "expenditure_pct",
                    "physical_progress_pct",
                    "expenditure_progress_gap",
                    "schedule_slippage_months",
                    "schedule_pressure_ratio"
                ]
            ]
            .sort_values(
                "cost_risk_score",
                ascending=False
            )
            .to_string(
                index=False
            )
        )

    # --------------------------------------------------------
    # Example individual predictions
    # --------------------------------------------------------

    print("\n")
    print("=" * 75)
    print("SAMPLE PROJECT RISK RESULTS")
    print("=" * 75)

    sample_columns = [
        "project_code",
        "cost_risk_score",
        "cost_risk_level",
        "actual_cost_overrun_pct",
        "expenditure_pct",
        "physical_progress_pct",
        "expenditure_progress_gap",
        "schedule_slippage_months"
    ]

    print(
        latest[
            sample_columns
        ]
        .sort_values(
            "cost_risk_score",
            ascending=False
        )
        .head(15)
        .to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    print("\n")
    print("=" * 75)
    print("SAVING RISK ENGINE RESULTS")
    print("=" * 75)

    results.to_csv(
        "reports/cost_risk_engine_snapshots.csv",
        index=False
    )

    latest.to_csv(
        "reports/cost_risk_engine_projects.csv",
        index=False
    )

    print(
        "✓ reports/cost_risk_engine_snapshots.csv"
    )

    print(
        "✓ reports/cost_risk_engine_projects.csv"
    )

    # --------------------------------------------------------
    # Complete
    # --------------------------------------------------------

    print("\n")
    print("=" * 75)
    print("COST RISK ENGINE COMPLETED")
    print("=" * 75)


if __name__ == "__main__":
    main()