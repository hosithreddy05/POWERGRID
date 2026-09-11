"""
===========================================================================
       SIH 25192 - V2 END-TO-END PROJECT TEST
===========================================================================

Flow:

    Project Service
          ↓
    Latest trajectory snapshot
          ↓
    V2 Predictor
          ↓
    Cost + Schedule prediction
          ↓
    Explainable Risk Engine

No training.
No synthetic data.
No PDF data.
=========================================================================== 
"""

from src.project_service import (
    get_project_information
)

from src.predictor import (
    predict_project
)


# ============================================================
# TEST PROJECT
# ============================================================

PROJECT_CODE = "N18000264"


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 75)
    print(
        "       SIH 25192 - V2 END-TO-END PROJECT TEST"
    )
    print("=" * 75)

    # --------------------------------------------------------
    # STEP 1
    # --------------------------------------------------------

    print(
        "\n[1] Loading project..."
    )

    information = (
        get_project_information(
            PROJECT_CODE
        )
    )

    snapshot = information[
        "snapshot"
    ]

    trajectory_snapshot = (
        information[
            "trajectory_snapshot"
        ]
    )

    model_input = information[
        "model_input"
    ]

    print(
        "✓ Project loaded:",
        PROJECT_CODE
    )

    # --------------------------------------------------------
    # STEP 2
    # --------------------------------------------------------

    print(
        "\n[2] Latest project snapshot"
    )

    print(
        "Project:",
        snapshot["project_name"]
    )

    print(
        "Snapshot date:",
        snapshot["snapshot_date"]
    )

    print(
        "Physical progress:",
        snapshot["physical_progress_pct"]
    )

    print(
        "Expenditure:",
        snapshot["cumulative_expenditure_cr"]
    )

    # --------------------------------------------------------
    # STEP 3
    # --------------------------------------------------------

    print(
        "\n[3] Trajectory features"
    )

    trajectory_features = [

        "progress_velocity",

        "expenditure_velocity",

        "expenditure_progress_gap",

        "schedule_slippage_months",
    ]

    for feature in trajectory_features:

        print(
            f"{feature}: "
            f"{trajectory_snapshot[feature]}"
        )

    # --------------------------------------------------------
    # STEP 4
    # --------------------------------------------------------

    print(
        "\n[4] Sending 12 features to V2 predictor..."
    )

    print(
        "Feature count:",
        len(model_input)
    )

    # --------------------------------------------------------
    # STEP 5
    # --------------------------------------------------------

    result = predict_project(
        model_input
    )

    # --------------------------------------------------------
    # STEP 6
    # --------------------------------------------------------

    print(
        "\n[5] FINAL V2 RESULT"
    )

    print(
        "Cost prediction:",
        result[
            "cost_prediction_pct"
        ],
        "%"
    )

    print(
        "Schedule prediction:",
        result[
            "schedule_prediction_months"
        ],
        "months"
    )

    print(
        "Risk score:",
        result[
            "cost_risk_score"
        ]
    )

    print(
        "Risk level:",
        result[
            "cost_risk_level"
        ]
    )

    # --------------------------------------------------------
    # RISK REASONS
    # --------------------------------------------------------

    print(
        "\nRisk reasons:"
    )

    for reason in result[
        "cost_risk_reasons"
    ]:

        print(
            "  •",
            reason
        )

    # --------------------------------------------------------
    # WARNINGS
    # --------------------------------------------------------

    print(
        "\nRisk warnings:"
    )

    for warning in result[
        "cost_risk_warnings"
    ]:

        print(
            "  •",
            warning
        )

    # --------------------------------------------------------
    # SUPPORTING INDICATORS
    # --------------------------------------------------------

    print(
        "\nSupporting indicators:"
    )

    print(
        "Expenditure %:",
        result[
            "expenditure_pct"
        ]
    )

    print(
        "Physical progress %:",
        result[
            "physical_progress_pct"
        ]
    )

    print(
        "Expenditure-progress gap:",
        result[
            "expenditure_progress_gap"
        ]
    )

    print(
        "Schedule slippage:",
        result[
            "schedule_slippage_months"
        ],
        "months"
    )

    print(
        "Schedule pressure ratio:",
        result[
            "schedule_pressure_ratio"
        ]
    )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    print(
        "\n[6] FINAL VALIDATION"
    )

    checks = {

        "Cost prediction exists":
            result[
                "cost_prediction_pct"
            ] is not None,

        "Schedule prediction exists":
            result[
                "schedule_prediction_months"
            ] is not None,

        "Risk score exists":
            result[
                "cost_risk_score"
            ] is not None,

        "Risk level exists":
            result[
                "cost_risk_level"
            ] in [
                "LOW",
                "MEDIUM",
                "HIGH"
            ],

        "12 V2 features supplied":
            len(model_input) == 12,
    }

    all_passed = True

    for name, passed in checks.items():

        if passed:

            print(
                "✓",
                name
            )

        else:

            print(
                "✗",
                name
            )

            all_passed = False

    # --------------------------------------------------------
    # FINAL STATUS
    # --------------------------------------------------------

    print(
        "\n" + "=" * 75
    )

    if all_passed:

        print(
            "✓ V2 END-TO-END PIPELINE VALIDATED"
        )

    else:

        print(
            "✗ V2 END-TO-END PIPELINE NEEDS REVIEW"
        )

    print("=" * 75)


if __name__ == "__main__":

    main()