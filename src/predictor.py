from pathlib import Path
import joblib
import pandas as pd

from src.cost_risk_engine import calculate_cost_risk


# ============================================================
# PROJECT ROOT
# ============================================================

ROOT = Path(__file__).resolve().parents[1]


# ============================================================
# FINAL V2 MODELS
# ============================================================

COST_MODEL_PATH = ROOT / "models" / "v2_cost_model.joblib"
SCHEDULE_MODEL_PATH = ROOT / "models" / "v2_schedule_model.joblib"


# ============================================================
# LOAD MODELS
# ============================================================

cost_model = joblib.load(COST_MODEL_PATH)
schedule_model = joblib.load(SCHEDULE_MODEL_PATH)


# ============================================================
# FINAL V2 FEATURES
# ============================================================

FEATURES = [
    "original_cost_cr",
    "cumulative_expenditure_cr",
    "physical_progress_pct",
    "planned_duration_months",
    "elapsed_months",
    "months_to_original_target",
    "expenditure_pct_of_original_cost",
    "project_category",
    "progress_velocity",
    "expenditure_velocity",
    "expenditure_progress_gap",
    "schedule_slippage_months",
]


# ============================================================
# PREDICT ONE PROJECT
# ============================================================

def predict_project(project_data):

    row = pd.DataFrame([project_data])

    missing = [
        feature
        for feature in FEATURES
        if feature not in row.columns
    ]

    if missing:
        raise ValueError(
            "Missing required V2 features: "
            + str(missing)
        )

    # --------------------------------------------------------
    # COST PREDICTION
    # --------------------------------------------------------

    cost_prediction = float(
        cost_model.predict(
            row[FEATURES]
        )[0]
    )

    # --------------------------------------------------------
    # SCHEDULE PREDICTION
    # --------------------------------------------------------

    schedule_prediction = float(
        schedule_model.predict(
            row[FEATURES]
        )[0]
    )

    # --------------------------------------------------------
    # RISK ENGINE
    # --------------------------------------------------------

    risk = calculate_cost_risk(
        project_data
    )

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    return {

        "cost_prediction_pct":
            round(cost_prediction, 2),

        "schedule_prediction_months":
            round(schedule_prediction, 2),

        "cost_risk_score":
            risk["cost_risk_score"],

        "cost_risk_level":
            risk["cost_risk_level"],

        "cost_risk_reasons":
            risk["risk_reasons"],

        "cost_risk_warnings":
            risk["risk_warnings"],

        "expenditure_pct":
            round(
                risk["expenditure_pct"],
                2
            ),

        "physical_progress_pct":
            round(
                risk["physical_progress_pct"],
                2
            ),

        "expenditure_progress_gap":
            round(
                risk["expenditure_progress_gap"],
                2
            ),

        "schedule_slippage_months":
            round(
                risk["schedule_slippage_months"],
                2
            ),

        "schedule_pressure_ratio":
            round(
                risk["schedule_pressure_ratio"],
                2
            ),
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 75)
    print("       SIH 25192 - FINAL V2 UNIFIED PREDICTOR TEST")
    print("=" * 75)

    print("\n[1] Loading frozen V2 models...")

    print(
        "Cost model:",
        COST_MODEL_PATH
    )

    print(
        "Schedule model:",
        SCHEDULE_MODEL_PATH
    )

    print("✓ Cost model loaded")
    print("✓ Schedule model loaded")

    # --------------------------------------------------------
    # REAL PROJECT INPUT
    # --------------------------------------------------------

    example_project = {

        "original_cost_cr": 1931.39,

        "cumulative_expenditure_cr": 1972.44,

        "physical_progress_pct": 99.0,

        "planned_duration_months": 30.0,

        "elapsed_months": 89.0,

        "months_to_original_target": -59.0,

        "expenditure_pct_of_original_cost":
            102.12541226784856,

        "project_category":
            "Substation_Grid_Equipment",

        # ----------------------------------------------------
        # TRAJECTORY FEATURES
        # ----------------------------------------------------

        "progress_velocity": 0.2,

        "expenditure_velocity": 0.0,

        "expenditure_progress_gap":
            3.12541226784856,

        "schedule_slippage_months": 59.0,
    }

    print("\n[2] Running V2 prediction...")

    result = predict_project(
        example_project
    )

    print("\n[3] RESULT")

    for key, value in result.items():

        print(
            f"{key}: {value}"
        )

    print("\n" + "=" * 75)

    print(
        "FINAL V2 UNIFIED PREDICTOR TEST COMPLETED"
    )

    print("=" * 75)