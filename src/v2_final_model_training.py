"""
===========================================================================
       SIH 25192 - V2 FINAL MODEL TRAINING
===========================================================================

FINAL COST MODEL
    Random Forest + Base + Trajectory

FINAL SCHEDULE MODEL
    Extra Trees + Base + Trajectory

IMPORTANT:
    - Uses ONLY V2 training datasets
    - NO synthetic data
    - NO PDF rows
    - NO test data
    - V1 models are NOT overwritten
    - Saves separate V2 production models
=========================================================================== 
"""

from pathlib import Path
import json

import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# =========================================================================
# PATHS
# =========================================================================

ROOT = Path(__file__).resolve().parents[1]

TRAIN_COST_PATH = (
    ROOT
    / "data"
    / "v2"
    / "train_cost_v2.csv"
)

TRAIN_SCHEDULE_PATH = (
    ROOT
    / "data"
    / "v2"
    / "train_schedule_v2.csv"
)

MODEL_DIR = ROOT / "models"

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)


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


# =========================================================================
# TARGETS
# =========================================================================

COST_TARGET = (
    "target_cost_overrun_pct"
)

SCHEDULE_TARGET = (
    "target_schedule_overrun_months"
)


# =========================================================================
# PREPROCESSOR
# =========================================================================

def build_preprocessor():

    numerical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="median"
                )
            )
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="most_frequent"
                )
            ),
            (
                "onehot",
                OneHotEncoder(
                    handle_unknown="ignore"
                )
            )
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numerical",
                numerical_pipeline,
                NUMERICAL_FEATURES
            ),
            (
                "categorical",
                categorical_pipeline,
                CATEGORICAL_FEATURES
            )
        ]
    )

    return preprocessor


# =========================================================================
# COST MODEL
# =========================================================================

def build_cost_model():

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=None,
        min_samples_leaf=3,
        max_features=1.0,
        random_state=42,
        n_jobs=-1
    )

    pipeline = Pipeline(
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

    return pipeline


# =========================================================================
# SCHEDULE MODEL
# =========================================================================

def build_schedule_model():

    model = ExtraTreesRegressor(
        n_estimators=300,
        max_depth=None,
        min_samples_leaf=3,
        max_features=1.0,
        random_state=42,
        n_jobs=-1
    )

    pipeline = Pipeline(
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

    return pipeline


# =========================================================================
# VALIDATION
# =========================================================================

def validate_dataset(
    df,
    target,
    name
):

    print(
        f"\n{name}"
    )

    print(
        "Rows    :",
        len(df)
    )

    print(
        "Projects:",
        df[
            "project_code"
        ].nunique()
    )

    missing_columns = [
        column
        for column in (
            ALL_FEATURES
            + [
                "project_code",
                target
            ]
        )
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            f"Missing columns: "
            f"{missing_columns}"
        )

    missing_target = df[
        target
    ].isna().sum()

    print(
        "Missing target rows:",
        missing_target
    )

    if missing_target > 0:

        raise ValueError(
            f"Target contains missing values: "
            f"{target}"
        )

    print(
        "✓ Dataset validated"
    )


# =========================================================================
# MAIN
# =========================================================================

def main():

    print("=" * 75)
    print(
        "       SIH 25192 - V2 FINAL MODEL TRAINING"
    )
    print("=" * 75)

    print(
        "\nFINAL COST MODEL:"
    )

    print(
        "  Random Forest"
    )

    print(
        "  Base + selected trajectory features"
    )

    print(
        "\nFINAL SCHEDULE MODEL:"
    )

    print(
        "  Extra Trees"
    )

    print(
        "  Base + selected trajectory features"
    )

    print("\nDATA POLICY")

    print(
        "  ✓ Real data only"
    )

    print(
        "  ✓ No synthetic data"
    )

    print(
        "  ✓ No PDF rows"
    )

    print(
        "  ✓ No test data"
    )

    print(
        "  ✓ V1 models will NOT be overwritten"
    )

    # =====================================================================
    # LOAD COST DATA
    # =====================================================================

    print("\n" + "=" * 75)
    print("[1] LOADING COST TRAINING DATA")
    print("=" * 75)

    cost_df = pd.read_csv(
        TRAIN_COST_PATH
    )

    validate_dataset(
        cost_df,
        COST_TARGET,
        "COST DATASET"
    )

    # =====================================================================
    # LOAD SCHEDULE DATA
    # =====================================================================

    print("\n" + "=" * 75)
    print("[2] LOADING SCHEDULE TRAINING DATA")
    print("=" * 75)

    schedule_df = pd.read_csv(
        TRAIN_SCHEDULE_PATH
    )

    validate_dataset(
        schedule_df,
        SCHEDULE_TARGET,
        "SCHEDULE DATASET"
    )

    # =====================================================================
    # CHECK PROJECT COUNTS
    # =====================================================================

    print("\n" + "=" * 75)
    print("[3] PROJECT VALIDATION")
    print("=" * 75)

    cost_projects = set(
        cost_df[
            "project_code"
        ]
    )

    schedule_projects = set(
        schedule_df[
            "project_code"
        ]
    )

    print(
        "Cost projects    :",
        len(cost_projects)
    )

    print(
        "Schedule projects:",
        len(schedule_projects)
    )

    print(
        "Cost/Schedule difference:",
        len(
            cost_projects
            - schedule_projects
        )
    )

    print(
        "\nNote:"
    )

    print(
        "The schedule dataset legitimately has fewer"
    )

    print(
        "projects because some schedule target values"
    )

    print(
        "were unavailable."
    )

    # =====================================================================
    # TRAIN COST
    # =====================================================================

    print("\n" + "=" * 75)
    print("[4] TRAINING FINAL COST MODEL")
    print("=" * 75)

    X_cost = cost_df[
        ALL_FEATURES
    ]

    y_cost = cost_df[
        COST_TARGET
    ]

    print(
        "Features:",
        len(ALL_FEATURES)
    )

    print(
        "Training rows:",
        len(X_cost)
    )

    cost_model = build_cost_model()

    cost_model.fit(
        X_cost,
        y_cost
    )

    print(
        "✓ Final cost model trained"
    )

    # =====================================================================
    # TRAIN SCHEDULE
    # =====================================================================

    print("\n" + "=" * 75)
    print("[5] TRAINING FINAL SCHEDULE MODEL")
    print("=" * 75)

    X_schedule = schedule_df[
        ALL_FEATURES
    ]

    y_schedule = schedule_df[
        SCHEDULE_TARGET
    ]

    print(
        "Features:",
        len(ALL_FEATURES)
    )

    print(
        "Training rows:",
        len(X_schedule)
    )

    schedule_model = build_schedule_model()

    schedule_model.fit(
        X_schedule,
        y_schedule
    )

    print(
        "✓ Final schedule model trained"
    )

    # =====================================================================
    # SAVE MODELS
    # =====================================================================

    print("\n" + "=" * 75)
    print("[6] SAVING FINAL V2 MODELS")
    print("=" * 75)

    cost_model_path = (
        MODEL_DIR
        / "v2_cost_model.joblib"
    )

    schedule_model_path = (
        MODEL_DIR
        / "v2_schedule_model.joblib"
    )

    import joblib

    joblib.dump(
        cost_model,
        cost_model_path
    )

    joblib.dump(
        schedule_model,
        schedule_model_path
    )

    print(
        "✓",
        cost_model_path
    )

    print(
        "✓",
        schedule_model_path
    )

    # =====================================================================
    # SAVE METADATA
    # =====================================================================

    print("\n" + "=" * 75)
    print("[7] SAVING MODEL METADATA")
    print("=" * 75)

    metadata = {

        "version": "V2",

        "status": "FINAL",

        "synthetic_data": False,

        "pdf_rows_appended": False,

        "test_data_used_for_training": False,

        "v1_models_overwritten": False,

        "cost_model": {

            "algorithm":
                "RandomForestRegressor",

            "n_estimators": 300,

            "min_samples_leaf": 3,

            "random_state": 42,

            "target":
                COST_TARGET
        },

        "schedule_model": {

            "algorithm":
                "ExtraTreesRegressor",

            "n_estimators": 300,

            "min_samples_leaf": 3,

            "random_state": 42,

            "target":
                SCHEDULE_TARGET
        },

        "features": {

            "numerical":
                NUMERICAL_FEATURES,

            "categorical":
                CATEGORICAL_FEATURES,

            "total":
                len(ALL_FEATURES)
        },

        "training_data": {

            "cost_rows":
                len(cost_df),

            "cost_projects":
                len(cost_projects),

            "schedule_rows":
                len(schedule_df),

            "schedule_projects":
                len(schedule_projects)
        }
    }

    metadata_path = (
        MODEL_DIR
        / "v2_model_metadata.json"
    )

    with open(
        metadata_path,
        "w"
    ) as f:

        json.dump(
            metadata,
            f,
            indent=4
        )

    print(
        "✓",
        metadata_path
    )

    # =====================================================================
    # VERIFY FILES
    # =====================================================================

    print("\n" + "=" * 75)
    print("[8] VERIFYING SAVED MODELS")
    print("=" * 75)

    files_to_check = [
        cost_model_path,
        schedule_model_path,
        metadata_path
    ]

    for file_path in files_to_check:

        if file_path.exists():

            print(
                "✓",
                file_path.name
            )

        else:

            raise FileNotFoundError(
                f"Expected file not found: "
                f"{file_path}"
            )

    # =====================================================================
    # TEST MODEL LOADING
    # =====================================================================

    print("\n" + "=" * 75)
    print("[9] TESTING MODEL LOADING")
    print("=" * 75)

    loaded_cost_model = joblib.load(
        cost_model_path
    )

    loaded_schedule_model = joblib.load(
        schedule_model_path
    )

    print(
        "✓ Cost model loaded successfully"
    )

    print(
        "✓ Schedule model loaded successfully"
    )

    # =====================================================================
    # TEST PREDICTION
    # =====================================================================

    print("\n" + "=" * 75)
    print("[10] TESTING SAVED MODEL PREDICTIONS")
    print("=" * 75)

    # Use training rows ONLY to verify that the saved pipeline
    # can accept the expected feature structure.
    # This is NOT an evaluation.

    cost_sample = X_cost.iloc[
        :1
    ]

    schedule_sample = X_schedule.iloc[
        :1
    ]

    cost_prediction = (
        loaded_cost_model.predict(
            cost_sample
        )
    )

    schedule_prediction = (
        loaded_schedule_model.predict(
            schedule_sample
        )
    )

    print(
        "Sample cost prediction:",
        round(
            float(
                cost_prediction[0]
            ),
            4
        ),
        "%"
    )

    print(
        "Sample schedule prediction:",
        round(
            float(
                schedule_prediction[0]
            ),
            4
        ),
        "months"
    )

    print(
        "\n✓ Saved models accept the expected input structure"
    )

    # =====================================================================
    # FINAL SUMMARY
    # =====================================================================

    print("\n" + "=" * 75)
    print(
        "V2 FINAL MODEL TRAINING COMPLETED"
    )
    print("=" * 75)

    print(
        "\nFINAL MODELS:"
    )

    print(
        "  models/v2_cost_model.joblib"
    )

    print(
        "  models/v2_schedule_model.joblib"
    )

    print(
        "  models/v2_model_metadata.json"
    )

    print(
        "\nMODEL STATUS:"
    )

    print(
        "  ✓ Cost model frozen"
    )

    print(
        "  ✓ Schedule model frozen"
    )

    print(
        "  ✓ V1 models preserved"
    )

    print(
        "  ✓ No synthetic data"
    )

    print(
        "  ✓ No PDF rows"
    )

    print(
        "  ✓ Test data not used for training"
    )

    print(
        "\nNEXT STEP:"
    )

    print(
        "Update the predictor/service layer to use"
    )

    print(
        "these frozen V2 models."
    )

    print("=" * 75)


if __name__ == "__main__":
    main()