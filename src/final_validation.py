import pandas as pd
import numpy as np
import ast

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder

from sklearn.linear_model import Ridge
from sklearn.ensemble import (
    RandomForestRegressor,
    HistGradientBoostingRegressor
)

from sklearn.model_selection import GroupKFold

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from src.config import (
    TRAIN_DATA_PATH,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    COST_TARGET,
    SCHEDULE_TARGET,
    RANDOM_STATE,
    REPORTS_DIR
)


# ============================================================
# SIH 25192
# FINAL MODEL VALIDATION
# ============================================================

print("=" * 70)
print("       SIH 25192 - FINAL MODEL VALIDATION")
print("=" * 70)


# ============================================================
# PREPROCESSOR
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
                CATEGORICAL_FEATURES
            )
        ],
        remainder="drop"
    )


# ============================================================
# MODELS
# ============================================================

def build_cost_model():

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
                    random_state=RANDOM_STATE,
                    n_jobs=-1
                )
            )
        ]
    )


def build_schedule_rf():

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
                    min_samples_leaf=5,
                    max_features=1.0,
                    random_state=RANDOM_STATE,
                    n_jobs=-1
                )
            )
        ]
    )


def build_schedule_hgb():

    return Pipeline(
        steps=[
            (
                "preprocessor",
                create_preprocessor()
            ),
            (
                "model",
                HistGradientBoostingRegressor(
                    learning_rate=0.05,
                    max_iter=300,
                    max_leaf_nodes=15,
                    min_samples_leaf=30,
                    l2_regularization=2.0,
                    random_state=RANDOM_STATE
                )
            )
        ]
    )


def build_schedule_ridge():

    return Pipeline(
        steps=[
            (
                "preprocessor",
                create_preprocessor()
            ),
            (
                "model",
                Ridge(
                    alpha=10.0
                )
            )
        ]
    )


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(
    actual,
    predicted
):

    mae = mean_absolute_error(
        actual,
        predicted
    )

    rmse = np.sqrt(
        mean_squared_error(
            actual,
            predicted
        )
    )

    r2 = r2_score(
        actual,
        predicted
    )

    return {
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2
    }


# ============================================================
# PROJECT LEVEL METRICS
# ============================================================

def calculate_project_metrics(
    prediction_df,
    target
):

    project_rows = []

    for project_code, group in prediction_df.groupby(
        "project_code"
    ):

        actual = group[target].mean()

        predicted = group["prediction"].mean()

        absolute_error = abs(
            actual - predicted
        )

        project_rows.append(
            {
                "project_code": project_code,
                "project_name": group[
                    "project_name"
                ].iloc[0],
                "snapshots": len(group),
                "actual_mean": actual,
                "predicted_mean": predicted,
                "absolute_error": absolute_error
            }
        )

    project_df = pd.DataFrame(
        project_rows
    )

    project_mae = (
        project_df[
            "absolute_error"
        ].mean()
    )

    return project_df, project_mae


# ============================================================
# OUT-OF-FOLD VALIDATION
# ============================================================

def run_oof_validation(
    df,
    target,
    model_name,
    model_builder
):

    print("\n" + "=" * 70)

    print(
        f"MODEL: {model_name}"
    )

    print(
        f"TARGET: {target}"
    )

    print("=" * 70)

    data = df[
        df[target].notna()
    ].copy()

    X = data[
        NUMERICAL_FEATURES
        + CATEGORICAL_FEATURES
    ]

    y = data[target]

    groups = data["project_code"]

    n_projects = groups.nunique()

    cv = GroupKFold(
        n_splits=min(
            5,
            n_projects
        )
    )

    all_predictions = []

    fold_results = []

    for fold_number, (
        train_index,
        validation_index
    ) in enumerate(
        cv.split(
            X,
            y,
            groups
        ),
        start=1
    ):

        X_train = X.iloc[
            train_index
        ]

        X_validation = X.iloc[
            validation_index
        ]

        y_train = y.iloc[
            train_index
        ]

        y_validation = y.iloc[
            validation_index
        ]

        train_groups = set(
            groups.iloc[
                train_index
            ]
        )

        validation_groups = set(
            groups.iloc[
                validation_index
            ]
        )

        overlap = (
            train_groups
            & validation_groups
        )

        if overlap:

            raise RuntimeError(
                f"Project leakage detected "
                f"in fold {fold_number}"
            )

        model = model_builder()

        model.fit(
            X_train,
            y_train
        )

        predictions = model.predict(
            X_validation
        )

        metrics = calculate_metrics(
            y_validation,
            predictions
        )

        fold_results.append(
            {
                "fold": fold_number,
                **metrics,
                "train_projects": len(
                    train_groups
                ),
                "validation_projects": len(
                    validation_groups
                )
            }
        )

        fold_prediction_df = data.iloc[
            validation_index
        ][
            [
                "project_code",
                "project_name",
                "snapshot_date",
                target
            ]
        ].copy()

        fold_prediction_df[
            "prediction"
        ] = predictions

        fold_prediction_df[
            "fold"
        ] = fold_number

        all_predictions.append(
            fold_prediction_df
        )

        print(
            f"\nFold {fold_number}"
        )

        print(
            f"Train projects : "
            f"{len(train_groups)}"
        )

        print(
            f"Validation projects : "
            f"{len(validation_groups)}"
        )

        print(
            f"Project overlap : "
            f"{len(overlap)}"
        )

        print(
            f"MAE  : "
            f"{metrics['MAE']:.4f}"
        )

        print(
            f"RMSE : "
            f"{metrics['RMSE']:.4f}"
        )

        print(
            f"R²   : "
            f"{metrics['R2']:.4f}"
        )

    # --------------------------------------------------------
    # Combine OOF predictions
    # --------------------------------------------------------

    prediction_df = pd.concat(
        all_predictions,
        ignore_index=True
    )

    # --------------------------------------------------------
    # Overall snapshot metrics
    # --------------------------------------------------------

    snapshot_metrics = calculate_metrics(
        prediction_df[target],
        prediction_df["prediction"]
    )

    # --------------------------------------------------------
    # Project-level metrics
    # --------------------------------------------------------

    project_df, project_mae = (
        calculate_project_metrics(
            prediction_df,
            target
        )
    )

    # --------------------------------------------------------
    # Fold statistics
    # --------------------------------------------------------

    fold_df = pd.DataFrame(
        fold_results
    )

    print("\n" + "-" * 70)
    print("OUT-OF-FOLD SUMMARY")
    print("-" * 70)

    print(
        f"Snapshot MAE  : "
        f"{snapshot_metrics['MAE']:.4f}"
    )

    print(
        f"Snapshot RMSE : "
        f"{snapshot_metrics['RMSE']:.4f}"
    )

    print(
        f"Snapshot R²   : "
        f"{snapshot_metrics['R2']:.4f}"
    )

    print(
        f"Project MAE   : "
        f"{project_mae:.4f}"
    )

    print(
        f"Fold MAE mean : "
        f"{fold_df['MAE'].mean():.4f}"
    )

    print(
        f"Fold MAE std  : "
        f"{fold_df['MAE'].std():.4f}"
    )

    return {
        "prediction_df": prediction_df,
        "project_df": project_df,
        "fold_df": fold_df,
        "snapshot_metrics": snapshot_metrics,
        "project_mae": project_mae
    }


# ============================================================
# SAVE PREDICTIONS
# ============================================================

def save_predictions(
    result,
    target,
    model_name
):

    filename = (
        f"oof_"
        f"{target}_"
        f"{model_name}.csv"
    )

    path = (
        REPORTS_DIR
        / filename
    )

    result[
        "prediction_df"
    ].to_csv(
        path,
        index=False
    )

    print(
        f"\nOOF predictions saved:"
    )

    print(path)


# ============================================================
# MAIN
# ============================================================

def main():

    train_df = pd.read_csv(
        TRAIN_DATA_PATH
    )

    print(
        f"\nTraining rows: "
        f"{len(train_df)}"
    )

    print(
        f"Training projects: "
        f"{train_df['project_code'].nunique()}"
    )

    final_results = []

    # ========================================================
    # COST
    # ========================================================

    print("\n")
    print("#" * 70)
    print("FINAL COST VALIDATION")
    print("#" * 70)

    cost_result = run_oof_validation(
        train_df,
        COST_TARGET,
        "Tuned Random Forest",
        build_cost_model
    )

    save_predictions(
        cost_result,
        COST_TARGET,
        "RandomForest"
    )

    final_results.append(
        {
            "Target": "Cost",
            "Model": "RandomForest",
            "Snapshot_MAE":
                cost_result[
                    "snapshot_metrics"
                ]["MAE"],
            "Snapshot_RMSE":
                cost_result[
                    "snapshot_metrics"
                ]["RMSE"],
            "Snapshot_R2":
                cost_result[
                    "snapshot_metrics"
                ]["R2"],
            "Project_MAE":
                cost_result[
                    "project_mae"
                ]
        }
    )

    # ========================================================
    # SCHEDULE RANDOM FOREST
    # ========================================================

    print("\n")
    print("#" * 70)
    print("SCHEDULE - RANDOM FOREST")
    print("#" * 70)

    schedule_rf_result = run_oof_validation(
        train_df,
        SCHEDULE_TARGET,
        "Tuned Random Forest",
        build_schedule_rf
    )

    save_predictions(
        schedule_rf_result,
        SCHEDULE_TARGET,
        "RandomForest"
    )

    final_results.append(
        {
            "Target": "Schedule",
            "Model": "RandomForest",
            "Snapshot_MAE":
                schedule_rf_result[
                    "snapshot_metrics"
                ]["MAE"],
            "Snapshot_RMSE":
                schedule_rf_result[
                    "snapshot_metrics"
                ]["RMSE"],
            "Snapshot_R2":
                schedule_rf_result[
                    "snapshot_metrics"
                ]["R2"],
            "Project_MAE":
                schedule_rf_result[
                    "project_mae"
                ]
        }
    )

    # ========================================================
    # SCHEDULE HGB
    # ========================================================

    print("\n")
    print("#" * 70)
    print("SCHEDULE - HISTGRADIENTBOOSTING")
    print("#" * 70)

    schedule_hgb_result = run_oof_validation(
        train_df,
        SCHEDULE_TARGET,
        "Tuned HistGradientBoosting",
        build_schedule_hgb
    )

    save_predictions(
        schedule_hgb_result,
        SCHEDULE_TARGET,
        "HistGradientBoosting"
    )

    final_results.append(
        {
            "Target": "Schedule",
            "Model": "HistGradientBoosting",
            "Snapshot_MAE":
                schedule_hgb_result[
                    "snapshot_metrics"
                ]["MAE"],
            "Snapshot_RMSE":
                schedule_hgb_result[
                    "snapshot_metrics"
                ]["RMSE"],
            "Snapshot_R2":
                schedule_hgb_result[
                    "snapshot_metrics"
                ]["R2"],
            "Project_MAE":
                schedule_hgb_result[
                    "project_mae"
                ]
        }
    )

    # ========================================================
    # SCHEDULE RIDGE
    # ========================================================

    print("\n")
    print("#" * 70)
    print("SCHEDULE - RIDGE")
    print("#" * 70)

    schedule_ridge_result = run_oof_validation(
        train_df,
        SCHEDULE_TARGET,
        "Ridge",
        build_schedule_ridge
    )

    save_predictions(
        schedule_ridge_result,
        SCHEDULE_TARGET,
        "Ridge"
    )

    final_results.append(
        {
            "Target": "Schedule",
            "Model": "Ridge",
            "Snapshot_MAE":
                schedule_ridge_result[
                    "snapshot_metrics"
                ]["MAE"],
            "Snapshot_RMSE":
                schedule_ridge_result[
                    "snapshot_metrics"
                ]["RMSE"],
            "Snapshot_R2":
                schedule_ridge_result[
                    "snapshot_metrics"
                ]["R2"],
            "Project_MAE":
                schedule_ridge_result[
                    "project_mae"
                ]
        }
    )

    # ========================================================
    # FINAL COMPARISON
    # ========================================================

    results_df = pd.DataFrame(
        final_results
    )

    print("\n")
    print("=" * 70)
    print("FINAL OUT-OF-FOLD MODEL COMPARISON")
    print("=" * 70)

    print(
        results_df.to_string(
            index=False
        )
    )

    output_path = (
        REPORTS_DIR
        / "final_oof_model_comparison.csv"
    )

    results_df.to_csv(
        output_path,
        index=False
    )

    print(
        "\nFinal comparison saved:"
    )

    print(output_path)

    print("\n")
    print("=" * 70)
    print("FINAL MODEL VALIDATION COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()