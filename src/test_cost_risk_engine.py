import pandas as pd

from src.cost_risk_engine import (
    evaluate_dataset
)


print("=" * 75)
print("       SIH 25192 - UNSEEN COST RISK VALIDATION")
print("=" * 75)


# ============================================================
# 1. LOAD UNSEEN TEST DATA
# ============================================================

print("\n[1] Loading unseen test data...")

test = pd.read_csv(
    "data/test.csv"
)

print(
    f"Testing rows    : {len(test)}"
)

print(
    f"Testing projects: "
    f"{test['project_code'].nunique()}"
)


# ============================================================
# 2. APPLY FROZEN RISK ENGINE
# ============================================================

print(
    "\n[2] Applying frozen cost risk engine..."
)

results = evaluate_dataset(
    test
)


# ============================================================
# 3. SELECT LATEST SNAPSHOT
# ============================================================

print(
    "\n[3] Selecting latest snapshot per project..."
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


print(
    f"Projects evaluated: "
    f"{len(latest)}"
)


# ============================================================
# 4. RISK DISTRIBUTION
# ============================================================

print("\n")
print("=" * 75)
print("UNSEEN TEST RISK DISTRIBUTION")
print("=" * 75)

print(
    latest[
        "cost_risk_level"
    ].value_counts()
)


# ============================================================
# 5. RISK SCORE DISTRIBUTION
# ============================================================

print("\n")
print("=" * 75)
print("RISK SCORE STATISTICS")
print("=" * 75)

print(
    latest[
        "cost_risk_score"
    ].describe()
)


# ============================================================
# 6. ACTUAL TEST OUTCOMES
# ============================================================

print("\n")
print("=" * 75)
print("ACTUAL UNSEEN COST OUTCOMES")
print("=" * 75)

latest[
    "actual_overrun"
] = (
    latest[
        "actual_cost_overrun_pct"
    ] > 0
)

print(
    "Actual overrun projects:",
    int(
        latest[
            "actual_overrun"
        ].sum()
    )
)

print(
    "No-overrun projects:",
    int(
        (
            ~latest[
                "actual_overrun"
            ]
        ).sum()
    )
)


# ============================================================
# 7. RISK VS ACTUAL OUTCOME
# ============================================================

print("\n")
print("=" * 75)
print("RISK ENGINE vs UNSEEN TEST OUTCOME")
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


# ============================================================
# 8. ALL TEST PROJECTS
# ============================================================

print("\n")
print("=" * 75)
print("ALL UNSEEN TEST PROJECTS")
print("=" * 75)

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
    latest[
        display_columns
    ]
    .sort_values(
        "cost_risk_score",
        ascending=False
    )
    .to_string(
        index=False
    )
)


# ============================================================
# 9. ACTUAL POSITIVE TEST PROJECTS
# ============================================================

print("\n")
print("=" * 75)
print("ACTUAL COST-OVERRUN PROJECTS IN TEST SET")
print("=" * 75)

positive = latest[
    latest[
        "actual_cost_overrun_pct"
    ] > 0
].copy()

if len(positive) == 0:

    print(
        "No positive cost-overrun projects "
        "exist in the test set."
    )

else:

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


# ============================================================
# 10. HIGH-RISK TEST PROJECTS
# ============================================================

print("\n")
print("=" * 75)
print("HIGH-RISK TEST PROJECTS")
print("=" * 75)

high_risk = latest[
    latest[
        "cost_risk_level"
    ] == "HIGH"
].copy()

if len(high_risk) == 0:

    print(
        "No HIGH-risk projects."
    )

else:

    print(
        high_risk[
            display_columns
        ]
        .sort_values(
            "cost_risk_score",
            ascending=False
        )
        .to_string(
            index=False
        )
    )


# ============================================================
# 11. CONFUSION MATRIX STYLE SUMMARY
# ============================================================

print("\n")
print("=" * 75)
print("HIGH-RISK DETECTION SUMMARY")
print("=" * 75)

actual_positive = (
    latest[
        "actual_overrun"
    ]
)

predicted_high = (
    latest[
        "cost_risk_level"
    ] == "HIGH"
)

true_positive = int(
    (
        actual_positive
        &
        predicted_high
    ).sum()
)

false_positive = int(
    (
        ~actual_positive
        &
        predicted_high
    ).sum()
)

false_negative = int(
    (
        actual_positive
        &
        ~predicted_high
    ).sum()
)

true_negative = int(
    (
        ~actual_positive
        &
        ~predicted_high
    ).sum()
)

print(
    f"True Positive  : {true_positive}"
)

print(
    f"False Positive : {false_positive}"
)

print(
    f"False Negative : {false_negative}"
)

print(
    f"True Negative  : {true_negative}"
)


# ============================================================
# 12. IMPORTANT INTERPRETATION
# ============================================================

print("\n")
print("=" * 75)
print("IMPORTANT INTERPRETATION")
print("=" * 75)

print(
    """
The risk engine was developed using training projects only.

The thresholds were NOT modified using the test results.

Therefore this evaluation represents an unseen-project
validation of the frozen rule-based cost risk engine.

The risk score is NOT a probability.
It is an explainable relative risk score from 0 to 100.
"""
)


# ============================================================
# 13. SAVE
# ============================================================

results.to_csv(
    "reports/cost_risk_engine_test_snapshots.csv",
    index=False
)

latest.to_csv(
    "reports/cost_risk_engine_test_projects.csv",
    index=False
)

comparison.to_csv(
    "reports/cost_risk_engine_test_summary.csv",
    index=False
)

print("\n")
print("=" * 75)
print("FILES SAVED")
print("=" * 75)

print(
    "✓ reports/cost_risk_engine_test_snapshots.csv"
)

print(
    "✓ reports/cost_risk_engine_test_projects.csv"
)

print(
    "✓ reports/cost_risk_engine_test_summary.csv"
)


print("\n")
print("=" * 75)
print("UNSEEN COST RISK VALIDATION COMPLETED")
print("=" * 75)