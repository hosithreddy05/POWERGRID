import os
import json
import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor


print("=" * 75)
print("       SIH 25192 - FINAL MODEL TRAINING")
print("=" * 75)


# ============================================================
# PATHS
# ============================================================

TRAIN_PATH = "data/train.csv"

MODEL_DIR = "models"

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)


# ============================================================
# FEATURES
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

CATEGORICAL_FEATURES = [
    "project_category"
]

ALL_FEATURES = (
    NUMERICAL_FEATURES
    +
    CATEGORICAL_FEATURES
)


# ============================================================
# TARGETS
# ============================================================

COST_TARGET = (
    "target_cost_overrun_pct"
)

SCHEDULE_TARGET = (
    "target_schedule_overrun_months"
)


# ============================================================
# LOAD DATA
# ============================================================

print("\n[1] Loading training data...")

df = pd.read_csv(
    TRAIN_PATH
)

print(
    f"Training rows   : {len(df)}"
)

print(
    f"Training projects: "
    f"{df['project_code'].nunique()}"
)


# ============================================================
# PREPROCESSOR
# ============================================================

print("\n[2] Creating preprocessing pipeline...")

preprocessor = ColumnTransformer(

    transformers=[

        (
            "num",
            "passthrough",
            NUMERICAL_FEATURES
        ),

        (
            "cat",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            CATEGORICAL_FEATURES
        )
    ]
)


# ============================================================
# COST MODEL
# ============================================================

print("\n[3] Training final COST model...")

cost_data = df[
    df[COST_TARGET].notna()
].copy()

X_cost = cost_data[
    ALL_FEATURES
]

y_cost = cost_data[
    COST_TARGET
]

cost_model = Pipeline(

    steps=[

        (
            "preprocessor",
            preprocessor
        ),

        (
            "model",
            RandomForestRegressor(

                n_estimators=300,

                max_depth=None,

                min_samples_leaf=3,

                max_features=1.0,

                random_state=42,

                n_jobs=-1
            )
        )
    ]
)

cost_model.fit(
    X_cost,
    y_cost
)

print(
    "✓ Cost model trained"
)


# ============================================================
# SCHEDULE MODEL
# ============================================================

print("\n[4] Training final SCHEDULE model...")

schedule_data = df[
    df[SCHEDULE_TARGET].notna()
].copy()

X_schedule = schedule_data[
    ALL_FEATURES
]

y_schedule = schedule_data[
    SCHEDULE_TARGET
]

schedule_model = Pipeline(

    steps=[

        (
            "preprocessor",
            preprocessor
        ),

        (
            "model",
            RandomForestRegressor(

                n_estimators=300,

                max_depth=None,

                min_samples_leaf=5,

                max_features=1.0,

                random_state=42,

                n_jobs=-1
            )
        )
    ]
)

schedule_model.fit(
    X_schedule,
    y_schedule
)

print(
    "✓ Schedule model trained"
)


# ============================================================
# SAVE MODELS
# ============================================================

print("\n[5] Saving models...")

cost_model_path = (
    "models/cost_model.joblib"
)

schedule_model_path = (
    "models/schedule_model.joblib"
)

joblib.dump(
    cost_model,
    cost_model_path
)

joblib.dump(
    schedule_model,
    schedule_model_path
)

print(
    f"✓ {cost_model_path}"
)

print(
    f"✓ {schedule_model_path}"
)


# ============================================================
# MODEL METADATA
# ============================================================

print("\n[6] Saving model metadata...")

metadata = {

    "project": "SIH 25192",

    "models": {

        "cost": {

            "model": "RandomForestRegressor",

            "n_estimators": 300,

            "min_samples_leaf": 3,

            "target":
                COST_TARGET
        },

        "schedule": {

            "model": "RandomForestRegressor",

            "n_estimators": 300,

            "min_samples_leaf": 5,

            "target":
                SCHEDULE_TARGET
        }
    },

    "features": {

        "numerical":
            NUMERICAL_FEATURES,

        "categorical":
            CATEGORICAL_FEATURES
    },

    "training_rows": len(df),

    "training_projects":
        int(
            df[
                "project_code"
            ].nunique()
        )
}

metadata_path = (
    "models/model_metadata.json"
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
    f"✓ {metadata_path}"
)


# ============================================================
# VERIFY FILES
# ============================================================

print("\n[7] Verifying saved models...")

assert os.path.exists(
    cost_model_path
)

assert os.path.exists(
    schedule_model_path
)

assert os.path.exists(
    metadata_path
)

print(
    "✓ All model files exist"
)


# ============================================================
# TEST MODEL LOADING
# ============================================================

print(
    "\n[8] Testing model loading..."
)

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


# ============================================================
# COMPLETE
# ============================================================

print("\n")
print("=" * 75)
print("FINAL MODEL TRAINING COMPLETED")
print("=" * 75)

print(
    "\nModels created:"
)

print(
    "  models/cost_model.joblib"
)

print(
    "  models/schedule_model.joblib"
)

print(
    "  models/model_metadata.json"
)

print("\n")