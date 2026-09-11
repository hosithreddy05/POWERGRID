"""
===========================================================================
       SIH 25192 - V2 UNSEEN PROJECT FINAL EVALUATION
===========================================================================

FINAL V2 MODELS
    COST     -> Random Forest + Base + Trajectory
    SCHEDULE -> Extra Trees + Base + Trajectory

IMPORTANT:
    - Test projects are completely unseen during model selection.
    - No synthetic data.
    - No PDF rows.
    - V1 models are NOT modified.
    - Project-level leakage is checked.
=========================================================================== 
"""

from pathlib import Path

import json
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# =========================================================================
# PATHS
# =========================================================================

ROOT = Path(__file__).resolve().parents[1]

TRAIN_COST = ROOT / "data" / "v2" / "train_cost_v2.csv"
TEST_COST = ROOT / "data" / "v2" / "test_cost_v2.csv"

TRAIN_SCHEDULE = ROOT / "data" / "v2" / "train_schedule_v2.csv"
TEST_SCHEDULE = ROOT / "data" / "v2" / "test_schedule_v2.csv"

REPORT_DIR = ROOT / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================================
# FEATURES
# =========================================================================

NUMERICAL_FEATURES = [
    "original_cost_cr",
    "cumulative_expenditure_cr",
    "physical_progress_pct",
    "planned_duration_months",
    "elapsed_months",
    "months_to_original_target",
    "expenditure_pct_of_original_cost",
    "progress_velocity",
    "expenditure_velocity",
    "expenditure_progress_gap",
    "schedule_slippage_months",
]

CATEGORICAL_FEATURES = [
    "project_category"
]

ALL_FEATURES = (
    NUMERICAL_FEATURES
    + CATEGORICAL_FEATURES
)

COST_TARGET = "target_cost_overrun_pct"

SCHEDULE_TARGET = "target_schedule_overrun_months"


# =========================================================================
# MODELS
# =========================================================================

def build_preprocessor():

    numeric_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="median")
            )
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="most_frequent")
            ),
            (
                "onehot",
                OneHotEncoder(handle_unknown="ignore")
            )
        ]
    )

    return ColumnTransformer(
        transformers=[
            (
                "num",
                numeric_pipeline,
                NUMERICAL_FEATURES
            ),
            (
                "cat",
                categorical_pipeline,
                CATEGORICAL_FEATURES
            )
        ]
    )


def build_cost_model():

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=None,
        min_samples_leaf=3,
        max_features=1.0,
        random_state=42,
        n_jobs=-1
    )

    return Pipeline(
        steps=[
            (
                "preprocessor",
                build_preprocessor()
            ),
            (
                "model",
                model
            )
        ]
    )


def build_schedule_model():

    model = ExtraTreesRegressor(
        n_estimators=300,
        max_depth=None,
        min_samples_leaf=3,
        max_features=1.0,
        random_state=42,
        n_jobs=-1
    )

    return Pipeline(
        steps=[
            (
                "preprocessor",
                build_preprocessor()
            ),
            (
                "model",
                model
            )
        ]
    )


# =========================================================================
# VALIDATION
# =========================================================================

def validate_columns(df, target):

    required = (
        [
            "project_code",
            "project_name",
            "snapshot_date"
        ]
        + ALL_FEATURES
        + [target]
    )

    missing = [
        col
        for col in required
        if col not in df.columns
    ]

    if missing:

        raise ValueError(
            f"Missing columns: {missing}"
        )


def project_level_metrics(
    df,
    predictions,
    target
):

    temp = df[
        [
            "project_code",
            target
        ]
    ].copy()

    temp["prediction"] = predictions

    project_rows = []

    for project_code, group in temp.groupby(
        "project_code"
    ):

        actual = group[target].mean()

        prediction = group[
            "prediction"
        ].mean()

        error = abs(
            actual - prediction
        )

        project_rows.append(
            {
                "project_code": project_code,
                "actual": actual,
                "prediction": prediction,
                "absolute_error": error
            }
        )

    project_df = pd.DataFrame(
        project_rows
    )

    project_mae = (
        project_df["absolute_error"].mean()
    )

    return project_df, project_mae


# =========================================================================
# MAIN
# =========================================================================

def main():

    print("=" * 75)
    print("       SIH 25192 - V2 UNSEEN PROJECT FINAL EVALUATION")
    print("=" * 75)

    print("\nFINAL MODELS")
    print("  Cost     : Random Forest + Base + Trajectory")
    print("  Schedule : Extra Trees + Base + Trajectory")

    print("\nIMPORTANT")
    print("  ✓ No synthetic data")
    print("  ✓ No PDF rows")
    print("  ✓ V1 models untouched")
    print("  ✓ Test projects were not used for model selection")

    # =====================================================================
    # COST DATA
    # =====================================================================

    print("\n" + "=" * 75)
    print("[1] LOADING COST DATA")
    print("=" * 75)

    train_cost = pd.read_csv(
        TRAIN_COST
    )

    test_cost = pd.read_csv(
        TEST_COST
    )

    validate_columns(
        train_cost,
        COST_TARGET
    )

    validate_columns(
        test_cost,
        COST_TARGET
    )

    print(
        "Training rows   :",
        len(train_cost)
    )

    print(
        "Training projects:",
        train_cost["project_code"].nunique()
    )

    print(
        "Testing rows    :",
        len(test_cost)
    )

    print(
        "Testing projects:",
        test_cost["project_code"].nunique()
    )

    # =====================================================================
    # PROJECT LEAKAGE
    # =====================================================================

    train_projects = set(
        train_cost["project_code"]
    )

    test_projects = set(
        test_cost["project_code"]
    )

    overlap = (
        train_projects
        & test_projects
    )

    print(
        "\nProject overlap:",
        len(overlap)
    )

    if overlap:

        raise ValueError(
            f"PROJECT LEAKAGE DETECTED: {overlap}"
        )

    print(
        "✓ Cost project separation valid"
    )

    # =====================================================================
    # TRAIN COST
    # =====================================================================

    print("\n" + "=" * 75)
    print("[2] TRAINING FINAL COST V2 MODEL")
    print("=" * 75)

    X_train_cost = train_cost[
        ALL_FEATURES
    ]

    y_train_cost = train_cost[
        COST_TARGET
    ]

    X_test_cost = test_cost[
        ALL_FEATURES
    ]

    y_test_cost = test_cost[
        COST_TARGET
    ]

    cost_model = build_cost_model()

    cost_model.fit(
        X_train_cost,
        y_train_cost
    )

    print(
        "✓ Cost model trained"
    )

    cost_predictions = cost_model.predict(
        X_test_cost
    )

    # Cost metrics

    cost_mae = mean_absolute_error(
        y_test_cost,
        cost_predictions
    )

    cost_rmse = np.sqrt(
        mean_squared_error(
            y_test_cost,
            cost_predictions
        )
    )

    cost_r2 = r2_score(
        y_test_cost,
        cost_predictions
    )

    cost_project_df, cost_project_mae = (
        project_level_metrics(
            test_cost,
            cost_predictions,
            COST_TARGET
        )
    )

    # =====================================================================
    # SCHEDULE DATA
    # =====================================================================

    print("\n" + "=" * 75)
    print("[3] LOADING SCHEDULE DATA")
    print("=" * 75)

    train_schedule = pd.read_csv(
        TRAIN_SCHEDULE
    )

    test_schedule = pd.read_csv(
        TEST_SCHEDULE
    )

    validate_columns(
        train_schedule,
        SCHEDULE_TARGET
    )

    validate_columns(
        test_schedule,
        SCHEDULE_TARGET
    )

    print(
        "Training rows   :",
        len(train_schedule)
    )

    print(
        "Training projects:",
        train_schedule["project_code"].nunique()
    )

    print(
        "Testing rows    :",
        len(test_schedule)
    )

    print(
        "Testing projects:",
        test_schedule["project_code"].nunique()
    )

    # =====================================================================
    # SCHEDULE LEAKAGE
    # =====================================================================

    train_schedule_projects = set(
        train_schedule["project_code"]
    )

    test_schedule_projects = set(
        test_schedule["project_code"]
    )

    schedule_overlap = (
        train_schedule_projects
        & test_schedule_projects
    )

    print(
        "\nProject overlap:",
        len(schedule_overlap)
    )

    if schedule_overlap:

        raise ValueError(
            f"PROJECT LEAKAGE DETECTED: "
            f"{schedule_overlap}"
        )

    print(
        "✓ Schedule project separation valid"
    )

    # =====================================================================
    # TRAIN SCHEDULE
    # =====================================================================

    print("\n" + "=" * 75)
    print("[4] TRAINING FINAL SCHEDULE V2 MODEL")
    print("=" * 75)

    X_train_schedule = train_schedule[
        ALL_FEATURES
    ]

    y_train_schedule = train_schedule[
        SCHEDULE_TARGET
    ]

    X_test_schedule = test_schedule[
        ALL_FEATURES
    ]

    y_test_schedule = test_schedule[
        SCHEDULE_TARGET
    ]

    schedule_model = build_schedule_model()

    schedule_model.fit(
        X_train_schedule,
        y_train_schedule
    )

    print(
        "✓ Schedule model trained"
    )

    schedule_predictions = schedule_model.predict(
        X_test_schedule
    )

    # Schedule metrics

    schedule_mae = mean_absolute_error(
        y_test_schedule,
        schedule_predictions
    )

    schedule_rmse = np.sqrt(
        mean_squared_error(
            y_test_schedule,
            schedule_predictions
        )
    )

    schedule_r2 = r2_score(
        y_test_schedule,
        schedule_predictions
    )

    schedule_project_df, schedule_project_mae = (
        project_level_metrics(
            test_schedule,
            schedule_predictions,
            SCHEDULE_TARGET
        )
    )

    # =====================================================================
    # RESULTS
    # =====================================================================

    print("\n" + "=" * 75)
    print("V2 UNSEEN TEST RESULTS")
    print("=" * 75)

    print("\nCOST MODEL")
    print(
        f"Test MAE          : {cost_mae:.4f}%"
    )

    print(
        f"Test RMSE         : {cost_rmse:.4f}%"
    )

    print(
        f"Test R²           : {cost_r2:.4f}"
    )

    print(
        f"Project MAE       : {cost_project_mae:.4f}%"
    )

    print("\nSCHEDULE MODEL")

    print(
        f"Test MAE          : {schedule_mae:.4f} months"
    )

    print(
        f"Test RMSE         : {schedule_rmse:.4f} months"
    )

    print(
        f"Test R²           : {schedule_r2:.4f}"
    )

    print(
        f"Project MAE       : {schedule_project_mae:.4f} months"
    )

    # =====================================================================
    # COST PROJECT RESULTS
    # =====================================================================

    print("\n" + "=" * 75)
    print("UNSEEN COST PROJECT PREDICTIONS")
    print("=" * 75)

    cost_output = test_cost[
        [
            "project_code",
            "project_name",
            "snapshot_date",
            COST_TARGET
        ]
    ].copy()

    cost_output[
        "prediction"
    ] = cost_predictions

    cost_output[
        "absolute_error"
    ] = abs(
        cost_output[COST_TARGET]
        - cost_output["prediction"]
    )

    print(
        cost_output[
            [
                "project_code",
                COST_TARGET,
                "prediction",
                "absolute_error"
            ]
        ].to_string(
            index=False
        )
    )

    # =====================================================================
    # SCHEDULE PROJECT RESULTS
    # =====================================================================

    print("\n" + "=" * 75)
    print("UNSEEN SCHEDULE PROJECT PREDICTIONS")
    print("=" * 75)

    schedule_output = test_schedule[
        [
            "project_code",
            "project_name",
            "snapshot_date",
            SCHEDULE_TARGET
        ]
    ].copy()

    schedule_output[
        "prediction"
    ] = schedule_predictions

    schedule_output[
        "absolute_error"
    ] = abs(
        schedule_output[SCHEDULE_TARGET]
        - schedule_output["prediction"]
    )

    print(
        schedule_output[
            [
                "project_code",
                SCHEDULE_TARGET,
                "prediction",
                "absolute_error"
            ]
        ].to_string(
            index=False
        )
    )

    # =====================================================================
    # KNOWN COST OVERRUN
    # =====================================================================

    print("\n" + "=" * 75)
    print("UNSEEN COST-OVERRUN PROJECT CHECK")
    print("=" * 75)

    positive_mask = (
        test_cost[COST_TARGET] > 0.5
    )

    positive_projects = cost_output[
        positive_mask
    ]

    if len(positive_projects) == 0:

        print(
            "No positive cost-overrun projects "
            "in the test set."
        )

    else:

        print(
            positive_projects[
                [
                    "project_code",
                    COST_TARGET,
                    "prediction",
                    "absolute_error"
                ]
            ].to_string(
                index=False
            )
        )

    # =====================================================================
    # PROJECT LEVEL SUMMARY
    # =====================================================================

    print("\n" + "=" * 75)
    print("PROJECT-LEVEL TEST SUMMARY")
    print("=" * 75)

    print(
        f"Cost projects evaluated     : "
        f"{len(cost_project_df)}"
    )

    print(
        f"Schedule projects evaluated : "
        f"{len(schedule_project_df)}"
    )

    print(
        f"Cost project MAE             : "
        f"{cost_project_mae:.4f}%"
    )

    print(
        f"Schedule project MAE         : "
        f"{schedule_project_mae:.4f} months"
    )

    # =====================================================================
    # SAVE PREDICTIONS
    # =====================================================================

    print("\n" + "=" * 75)
    print("[5] SAVING FINAL V2 TEST REPORTS")
    print("=" * 75)

    cost_prediction_path = (
        REPORT_DIR
        / "v2_unseen_cost_predictions.csv"
    )

    schedule_prediction_path = (
        REPORT_DIR
        / "v2_unseen_schedule_predictions.csv"
    )

    cost_metrics_path = (
        REPORT_DIR
        / "v2_unseen_cost_metrics.csv"
    )

    schedule_metrics_path = (
        REPORT_DIR
        / "v2_unseen_schedule_metrics.csv"
    )

    cost_output.to_csv(
        cost_prediction_path,
        index=False
    )

    schedule_output.to_csv(
        schedule_prediction_path,
        index=False
    )

    pd.DataFrame(
        [
            {
                "metric": "MAE",
                "value": cost_mae,
                "unit": "percent"
            },
            {
                "metric": "RMSE",
                "value": cost_rmse,
                "unit": "percent"
            },
            {
                "metric": "R2",
                "value": cost_r2,
                "unit": "score"
            },
            {
                "metric": "Project_MAE",
                "value": cost_project_mae,
                "unit": "percent"
            }
        ]
    ).to_csv(
        cost_metrics_path,
        index=False
    )

    pd.DataFrame(
        [
            {
                "metric": "MAE",
                "value": schedule_mae,
                "unit": "months"
            },
            {
                "metric": "RMSE",
                "value": schedule_rmse,
                "unit": "months"
            },
            {
                "metric": "R2",
                "value": schedule_r2,
                "unit": "score"
            },
            {
                "metric": "Project_MAE",
                "value": schedule_project_mae,
                "unit": "months"
            }
        ]
    ).to_csv(
        schedule_metrics_path,
        index=False
    )

    print(
        "✓",
        cost_prediction_path
    )

    print(
        "✓",
        schedule_prediction_path
    )

    print(
        "✓",
        cost_metrics_path
    )

    print(
        "✓",
        schedule_metrics_path
    )

    # =====================================================================
    # FINAL SUMMARY JSON
    # =====================================================================

    summary = {

        "version": "V2",

        "synthetic_data": False,

        "pdf_rows_appended": False,

        "v1_modified": False,

        "test_projects": int(
            test_cost["project_code"].nunique()
        ),

        "cost_model": {
            "algorithm": "RandomForest",
            "features": ALL_FEATURES,
            "test_mae": float(cost_mae),
            "test_rmse": float(cost_rmse),
            "test_r2": float(cost_r2),
            "project_mae": float(cost_project_mae)
        },

        "schedule_model": {
            "algorithm": "ExtraTrees",
            "features": ALL_FEATURES,
            "test_mae": float(schedule_mae),
            "test_rmse": float(schedule_rmse),
            "test_r2": float(schedule_r2),
            "project_mae": float(schedule_project_mae)
        }
    }

    summary_path = (
        REPORT_DIR
        / "v2_unseen_final_summary.json"
    )

    with open(
        summary_path,
        "w"
    ) as f:

        json.dump(
            summary,
            f,
            indent=4
        )

    print(
        "✓",
        summary_path
    )

    # =====================================================================
    # COMPLETE
    # =====================================================================

    print("\n" + "=" * 75)
    print("V2 UNSEEN PROJECT FINAL EVALUATION COMPLETED")
    print("=" * 75)

    print(
        "\nThe 23 unseen projects were evaluated."
    )

    print(
        "No test result was used to select or tune the models."
    )

    print(
        "No synthetic data was used."
    )

    print(
        "No PDF rows were appended."
    )

    print(
        "V1 models were not modified."
    )

    print("\n" + "=" * 75)


if __name__ == "__main__":
    main()