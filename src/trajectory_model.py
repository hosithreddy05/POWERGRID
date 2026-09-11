import pandas as pd
import numpy as np

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


print("=" * 75)
print("       SIH 25192 - TRAJECTORY COST MODEL")
print("=" * 75)


# ============================================================
# Paths
# ============================================================

TRAIN_PATH = "data/train_trajectory.csv"
TEST_PATH = "data/test_trajectory.csv"

TARGET = "target_cost_overrun_pct"


# ============================================================
# Original features
# ============================================================

ORIGINAL_NUMERICAL = [
    "original_cost_cr",
    "cumulative_expenditure_cr",
    "physical_progress_pct",
    "planned_duration_months",
    "elapsed_months",
    "months_to_original_target",
    "expenditure_pct_of_original_cost"
]


ORIGINAL_CATEGORICAL = [
    "project_category"
]


# ============================================================
# New trajectory features
# ============================================================

TRAJECTORY_FEATURES = [

    "progress_change",

    "expenditure_change_cr",

    "expenditure_pct_change",

    "elapsed_month_change",

    "progress_velocity",

    "expenditure_velocity",

    "expenditure_progress_gap",

    "cost_per_progress_pct",

    "schedule_slippage_months",

    "schedule_pressure_ratio",

    "budget_consumption_ratio",

    "progress_time_ratio",

    "progress_expenditure_ratio",

    "project_age_months",

    "progress_change_3",

    "expenditure_change_3",

    "progress_velocity_rolling",

    "expenditure_velocity_rolling"
]


NUMERICAL_FEATURES = (
    ORIGINAL_NUMERICAL
    +
    TRAJECTORY_FEATURES
)


# ============================================================
# Preprocessor
# ============================================================

def create_preprocessor():

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
                    handle_unknown="ignore",
                    sparse_output=False
                )
            )
        ]
    )

    return ColumnTransformer(
        transformers=[
            (
                "numerical",
                numerical_pipeline,
                NUMERICAL_FEATURES
            ),
            (
                "categorical",
                categorical_pipeline,
                ORIGINAL_CATEGORICAL
            )
        ]
    )


# ============================================================
# Model
# ============================================================

def create_model():

    return Pipeline(
        steps=[
            (
                "preprocessor",
                create_preprocessor()
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


# ============================================================
# Main
# ============================================================

def main():

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    print("\n[1] Loading trajectory data...")

    train = pd.read_csv(
        TRAIN_PATH
    )

    test = pd.read_csv(
        TEST_PATH
    )

    print(
        f"Training rows : {len(train)}"
    )

    print(
        f"Testing rows  : {len(test)}"
    )

    print(
        f"Training projects : "
        f"{train['project_code'].nunique()}"
    )

    print(
        f"Testing projects : "
        f"{test['project_code'].nunique()}"
    )

    # --------------------------------------------------------
    # Leakage check
    # --------------------------------------------------------

    print(
        "\n[2] Checking project leakage..."
    )

    overlap = (
        set(train["project_code"])
        &
        set(test["project_code"])
    )

    print(
        f"Project overlap: {len(overlap)}"
    )

    if overlap:

        raise RuntimeError(
            "PROJECT LEAKAGE DETECTED!"
        )

    print(
        "Leakage check: PASSED"
    )

    # --------------------------------------------------------
    # Remove rows without target
    # --------------------------------------------------------

    train = train[
        train[TARGET].notna()
    ].copy()

    test = test[
        test[TARGET].notna()
    ].copy()

    print(
        "\n[3] Target availability"
    )

    print(
        f"Training target rows: "
        f"{len(train)}"
    )

    print(
        f"Testing target rows: "
        f"{len(test)}"
    )

    # --------------------------------------------------------
    # Features
    # --------------------------------------------------------

    X_train = train[
        NUMERICAL_FEATURES
        +
        ORIGINAL_CATEGORICAL
    ]

    y_train = train[
        TARGET
    ]

    X_test = test[
        NUMERICAL_FEATURES
        +
        ORIGINAL_CATEGORICAL
    ]

    y_test = test[
        TARGET
    ]

    print(
        "\n[4] Features"
    )

    print(
        f"Original numerical features : "
        f"{len(ORIGINAL_NUMERICAL)}"
    )

    print(
        f"Trajectory features : "
        f"{len(TRAJECTORY_FEATURES)}"
    )

    print(
        f"Categorical features : "
        f"{len(ORIGINAL_CATEGORICAL)}"
    )

    print(
        f"Total features before encoding : "
        f"{len(NUMERICAL_FEATURES) + len(ORIGINAL_CATEGORICAL)}"
    )

    # --------------------------------------------------------
    # Train
    # --------------------------------------------------------

    print(
        "\n[5] Training Random Forest..."
    )

    model = create_model()

    model.fit(
        X_train,
        y_train
    )

    print(
        "Training completed."
    )

    # --------------------------------------------------------
    # Predict
    # --------------------------------------------------------

    print(
        "\n[6] Generating predictions..."
    )

    predictions = model.predict(
        X_test
    )

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            predictions
        )
    )

    r2 = r2_score(
        y_test,
        predictions
    )

    # --------------------------------------------------------
    # Prediction dataframe
    # --------------------------------------------------------

    results = test[
        [
            "project_code",
            "project_name",
            "snapshot_date",
            TARGET
        ]
    ].copy()

    results[
        "prediction"
    ] = predictions

    results[
        "error"
    ] = (
        predictions
        -
        y_test.values
    )

    results[
        "absolute_error"
    ] = (
        results["error"]
        .abs()
    )

    # --------------------------------------------------------
    # Project level metrics
    # --------------------------------------------------------

    project_results = (
        results
        .groupby(
            [
                "project_code",
                "project_name"
            ]
        )
        .agg(
            actual=(
                TARGET,
                "mean"
            ),
            predicted=(
                "prediction",
                "mean"
            ),
            snapshots=(
                "prediction",
                "size"
            )
        )
        .reset_index()
    )

    project_results[
        "absolute_error"
    ] = (
        project_results[
            "predicted"
        ]
        -
        project_results[
            "actual"
        ]
    ).abs()

    project_mae = (
        project_results[
            "absolute_error"
        ].mean()
    )

    # --------------------------------------------------------
    # Print results
    # --------------------------------------------------------

    print("\n")
    print("=" * 75)
    print("TRAJECTORY MODEL TEST RESULTS")
    print("=" * 75)

    print(
        f"\nTEST MAE       : "
        f"{mae:.4f}%"
    )

    print(
        f"TEST RMSE      : "
        f"{rmse:.4f}%"
    )

    print(
        f"TEST R²        : "
        f"{r2:.4f}"
    )

    print(
        f"PROJECT MAE    : "
        f"{project_mae:.4f}%"
    )

    # --------------------------------------------------------
    # Compare with old model
    # --------------------------------------------------------

    OLD_MAE = 2.2009
    OLD_RMSE = 6.7527
    OLD_R2 = -0.5359
    OLD_PROJECT_MAE = 2.9169

    print("\n")
    print("=" * 75)
    print("OLD MODEL vs TRAJECTORY MODEL")
    print("=" * 75)

    print(
        f"\n{'Metric':<20}"
        f"{'Old RF':>15}"
        f"{'Trajectory RF':>20}"
    )

    print("-" * 55)

    print(
        f"{'MAE':<20}"
        f"{OLD_MAE:>15.4f}"
        f"{mae:>20.4f}"
    )

    print(
        f"{'RMSE':<20}"
        f"{OLD_RMSE:>15.4f}"
        f"{rmse:>20.4f}"
    )

    print(
        f"{'R²':<20}"
        f"{OLD_R2:>15.4f}"
        f"{r2:>20.4f}"
    )

    print(
        f"{'Project MAE':<20}"
        f"{OLD_PROJECT_MAE:>15.4f}"
        f"{project_mae:>20.4f}"
    )

    # --------------------------------------------------------
    # Improvement
    # --------------------------------------------------------

    print("\n")
    print("=" * 75)
    print("IMPROVEMENT ANALYSIS")
    print("=" * 75)

    mae_improvement = (
        OLD_MAE - mae
    )

    project_improvement = (
        OLD_PROJECT_MAE
        -
        project_mae
    )

    r2_improvement = (
        r2
        -
        OLD_R2
    )

    print(
        f"\nMAE improvement: "
        f"{mae_improvement:.4f}"
    )

    print(
        f"Project MAE improvement: "
        f"{project_improvement:.4f}"
    )

    print(
        f"R² improvement: "
        f"{r2_improvement:.4f}"
    )

    # --------------------------------------------------------
    # Worst predictions
    # --------------------------------------------------------

    print("\n")
    print("=" * 75)
    print("WORST TRAJECTORY MODEL PREDICTIONS")
    print("=" * 75)

    print(
        results
        .sort_values(
            "absolute_error",
            ascending=False
        )
        .head(10)
        .to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # Save results
    # --------------------------------------------------------

    results.to_csv(
        "reports/trajectory_cost_predictions.csv",
        index=False
    )

    project_results.to_csv(
        "reports/trajectory_cost_project_results.csv",
        index=False
    )

    print("\n")
    print("=" * 75)
    print(
        "TRAJECTORY COST MODEL COMPLETED"
    )
    print("=" * 75)


if __name__ == "__main__":
    main()