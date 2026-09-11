from src.predictor import predict_project


# ============================================================
# SIH 25192 - V2 WHAT-IF SIMULATOR
# ============================================================


def calculate_derived_features(project):
    """
    Recalculate features that are directly derived from
    scenario values.

    This is scenario analysis only.
    No scenario data is used for model training.
    """

    scenario = project.copy()

    # --------------------------------------------------------
    # Original cost
    # --------------------------------------------------------

    original_cost = float(
        scenario["original_cost_cr"]
    )

    if original_cost <= 0:
        raise ValueError(
            "Original cost must be greater than zero."
        )

    # --------------------------------------------------------
    # Expenditure
    # --------------------------------------------------------

    expenditure = float(
        scenario["cumulative_expenditure_cr"]
    )

    # --------------------------------------------------------
    # Expenditure percentage
    # --------------------------------------------------------

    scenario[
        "expenditure_pct_of_original_cost"
    ] = (
        expenditure
        / original_cost
        * 100
    )

    # --------------------------------------------------------
    # Planned duration
    # --------------------------------------------------------

    planned_duration = float(
        scenario["planned_duration_months"]
    )

    # --------------------------------------------------------
    # Elapsed duration
    # --------------------------------------------------------

    elapsed_months = float(
        scenario["elapsed_months"]
    )

    # --------------------------------------------------------
    # Months to original target
    # --------------------------------------------------------

    scenario[
        "months_to_original_target"
    ] = (
        planned_duration
        - elapsed_months
    )

    # --------------------------------------------------------
    # Schedule slippage
    # --------------------------------------------------------

    scenario[
        "schedule_slippage_months"
    ] = max(
        0,
        elapsed_months - planned_duration
    )

    # --------------------------------------------------------
    # Expenditure-progress gap
    #
    # This is directly derived from the scenario's
    # expenditure percentage and physical progress.
    # --------------------------------------------------------

    physical_progress = float(
        scenario["physical_progress_pct"]
    )

    scenario[
        "expenditure_progress_gap"
    ] = (
        scenario[
            "expenditure_pct_of_original_cost"
        ]
        - physical_progress
    )

    return scenario


# ============================================================
# RUN WHAT-IF SCENARIO
# ============================================================

def run_what_if(
    project_data,
    changes
):

    """
    Apply user-defined scenario changes and
    run the frozen V2 prediction models.

    Example:

        changes = {
            "cumulative_expenditure_cr": 2200
        }

    Important:
        This does NOT retrain the model.
    """

    # --------------------------------------------------------
    # Create independent scenario
    # --------------------------------------------------------

    scenario = project_data.copy()

    # --------------------------------------------------------
    # Apply changes
    # --------------------------------------------------------

    for key, value in changes.items():

        if key not in scenario:

            raise ValueError(
                f"Unknown project field: {key}"
            )

        scenario[key] = value

    # --------------------------------------------------------
    # Recalculate directly derived features
    # --------------------------------------------------------

    scenario = calculate_derived_features(
        scenario
    )

    # --------------------------------------------------------
    # Run frozen V2 models
    # --------------------------------------------------------

    result = predict_project(
        scenario
    )

    return {

        "scenario":
            scenario,

        "prediction":
            result
    }


# ============================================================
# PRINT PREDICTION
# ============================================================

def print_prediction(
    label,
    result
):

    prediction = result[
        "prediction"
    ]

    scenario = result[
        "scenario"
    ]

    print()

    print(
        f"--- {label} ---"
    )

    print(
        "Expenditure:",
        round(
            scenario[
                "cumulative_expenditure_cr"
            ],
            2
        ),
        "Cr"
    )

    print(
        "Expenditure %:",
        round(
            scenario[
                "expenditure_pct_of_original_cost"
            ],
            2
        ),
        "%"
    )

    print(
        "Physical progress:",
        round(
            scenario[
                "physical_progress_pct"
            ],
            2
        ),
        "%"
    )

    print(
        "Expenditure-progress gap:",
        round(
            scenario[
                "expenditure_progress_gap"
            ],
            2
        )
    )

    print(
        "Months to original target:",
        round(
            scenario[
                "months_to_original_target"
            ],
            2
        )
    )

    print(
        "Schedule slippage:",
        round(
            scenario[
                "schedule_slippage_months"
            ],
            2
        ),
        "months"
    )

    print(
        "Cost prediction:",
        prediction[
            "cost_prediction_pct"
        ],
        "%"
    )

    print(
        "Schedule prediction:",
        prediction[
            "schedule_prediction_months"
        ],
        "months"
    )

    print(
        "Risk score:",
        prediction[
            "cost_risk_score"
        ]
    )

    print(
        "Risk level:",
        prediction[
            "cost_risk_level"
        ]
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 75)
    print(
        "       SIH 25192 - V2 WHAT-IF SIMULATOR TEST"
    )
    print("=" * 75)

    # --------------------------------------------------------
    # REAL PROJECT BASELINE
    # --------------------------------------------------------

    project = {

        "original_cost_cr":
            1931.39,

        "cumulative_expenditure_cr":
            1972.44,

        "physical_progress_pct":
            99.0,

        "planned_duration_months":
            30.0,

        "elapsed_months":
            89.0,

        "months_to_original_target":
            -59.0,

        "expenditure_pct_of_original_cost":
            102.125412,

        "project_category":
            "Substation_Grid_Equipment",

        # ----------------------------------------------------
        # REAL TRAJECTORY FEATURES
        # ----------------------------------------------------

        "progress_velocity":
            0.0,

        "expenditure_velocity":
            0.0,

        "expenditure_progress_gap":
            3.125412,

        "schedule_slippage_months":
            59.0,
    }

    # --------------------------------------------------------
    # BASELINE
    # --------------------------------------------------------

    baseline = run_what_if(
        project,
        {}
    )

    print_prediction(
        "BASELINE",
        baseline
    )

    # --------------------------------------------------------
    # SCENARIO 1
    # --------------------------------------------------------

    scenario_1 = run_what_if(

        project,

        {
            "cumulative_expenditure_cr":
                2200
        }
    )

    print_prediction(
        "WHAT-IF: EXPENDITURE INCREASED",
        scenario_1
    )

    # --------------------------------------------------------
    # SCENARIO 2
    # --------------------------------------------------------

    scenario_2 = run_what_if(

        project,

        {
            "cumulative_expenditure_cr":
                1800
        }
    )

    print_prediction(
        "WHAT-IF: LOWER EXPENDITURE",
        scenario_2
    )

    # --------------------------------------------------------
    # SCENARIO 3
    # --------------------------------------------------------

    scenario_3 = run_what_if(

        project,

        {
            "elapsed_months":
                100
        }
    )

    print_prediction(
        "WHAT-IF: ADDITIONAL DELAY",
        scenario_3
    )

    print()

    print("=" * 75)

    print(
        "V2 WHAT-IF SIMULATOR TEST COMPLETED"
    )

    print("=" * 75)