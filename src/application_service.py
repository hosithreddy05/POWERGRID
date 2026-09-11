from src.project_service import (
    get_project_list,
    get_project_information,
)

from src.predictor import (
    predict_project,
)

from src.what_if import (
    run_what_if,
    calculate_derived_features,
)


# ============================================================
# SIH 25192 - APPLICATION SERVICE
# ============================================================


# ============================================================
# PROJECT LIST
# ============================================================

def get_projects():
    """
    Return the complete POWERGRID project list.
    """

    return get_project_list()


# ============================================================
# GET PROJECT DETAILS + PREDICTION
# ============================================================

def analyze_project(project_code):
    """
    Get one POWERGRID project and run the V2
    prediction pipeline.
    """

    information = get_project_information(
        project_code
    )

    model_input = information[
        "model_input"
    ]

    prediction = predict_project(
        model_input
    )

    return {
        "project_code": project_code,

        "snapshot": information[
            "snapshot"
        ],

        "trajectory_snapshot": information[
            "trajectory_snapshot"
        ],

        "model_input": model_input,

        "prediction": prediction,
    }


# ============================================================
# WHAT-IF ANALYSIS
# ============================================================

def analyze_what_if(
    project_code,
    changes,
):
    """
    Run baseline and scenario analysis using
    the frozen V2 prediction models.
    """

    information = get_project_information(
        project_code
    )

    model_input = information[
        "model_input"
    ]

    # --------------------------------------------------------
    # Baseline
    # --------------------------------------------------------

    baseline = run_what_if(
        model_input,
        {},
    )

    # --------------------------------------------------------
    # Scenario
    # --------------------------------------------------------

    scenario = run_what_if(
        model_input,
        changes,
    )

    return {
        "project_code": project_code,
        "baseline": baseline,
        "scenario": scenario,
    }


# ============================================================
# NEW PROJECT PREDICTION
# ============================================================

def predict_new_project(project_data):
    """
    Convert frontend/API field names into the exact
    field names expected by the POWERGRID V2 pipeline.

    Frontend/API names:
        original_approved_cost
        cumulative_expenditure
        elapsed_duration_months

    V2 names:
        original_cost_cr
        cumulative_expenditure_cr
        elapsed_months
    """

    # ========================================================
    # MAP API INPUT -> V2 INPUT
    # ========================================================

    original_cost = float(
        project_data[
            "original_approved_cost"
        ]
    )

    cumulative_expenditure = float(
        project_data[
            "cumulative_expenditure"
        ]
    )

    physical_progress = float(
        project_data[
            "physical_progress_pct"
        ]
    )

    planned_duration = float(
        project_data[
            "planned_duration_months"
        ]
    )

    elapsed_months = float(
        project_data[
            "elapsed_duration_months"
        ]
    )

    progress_velocity = float(
        project_data.get(
            "progress_velocity",
            0,
        )
    )

    expenditure_velocity = float(
        project_data.get(
            "expenditure_velocity",
            0,
        )
    )

    project_category = project_data[
        "project_category"
    ]

    # ========================================================
    # BUILD EXACT V2 PROJECT STRUCTURE
    # ========================================================

    v2_project = {

        "original_cost_cr":
            original_cost,

        "cumulative_expenditure_cr":
            cumulative_expenditure,

        "physical_progress_pct":
            physical_progress,

        "planned_duration_months":
            planned_duration,

        "elapsed_months":
            elapsed_months,

        "project_category":
            project_category,

        "progress_velocity":
            progress_velocity,

        "expenditure_velocity":
            expenditure_velocity,
    }

    # ========================================================
    # CALCULATE DERIVED V2 FEATURES
    # ========================================================

    prepared_data = calculate_derived_features(
        v2_project
    )

    # ========================================================
    # RUN FROZEN V2 PREDICTION
    # ========================================================

    prediction = predict_project(
        prepared_data
    )

    # ========================================================
    # RETURN RESULT
    # ========================================================

    return {
        "input": prepared_data,
        "prediction": prediction,
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 75)
    print(
        "       SIH 25192 - APPLICATION SERVICE TEST"
    )
    print("=" * 75)

    # --------------------------------------------------------
    # Test project list
    # --------------------------------------------------------

    print("\n[1] Testing project list...")

    try:

        projects = get_projects()

        print(
            "Project list loaded successfully."
        )

        print(
            "Number of projects:",
            len(projects),
        )

    except Exception as e:

        print(
            "Project list test failed:",
            e,
        )

    # --------------------------------------------------------
    # Test new project prediction
    # --------------------------------------------------------

    print(
        "\n[2] Testing new project prediction..."
    )

    test_project = {

        "original_approved_cost": 500,

        "project_category":
            "Transmission_System",

        "cumulative_expenditure": 250,

        "physical_progress_pct": 50,

        "planned_duration_months": 24,

        "elapsed_duration_months": 12,

        "progress_velocity": 4.2,

        "expenditure_velocity": 20,
    }

    try:

        result = predict_new_project(
            test_project
        )

        print(
            "New project prediction successful."
        )

        print(
            "Prediction:",
            result["prediction"],
        )

    except Exception as e:

        print(
            "New project prediction failed:",
            e,
        )

    print("\n" + "=" * 75)

    print(
        "APPLICATION SERVICE TEST COMPLETED"
    )

    print("=" * 75)
