import pandas as pd
import numpy as np

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
# SIH 25192 - MODEL TUNING
# ============================================================

print("=" * 70)
print("       SIH 25192 - MODEL TUNING")
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
# MODEL BUILDERS
# ============================================================

def build_ridge():

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


def build_random_forest(
    n_estimators=300,
    max_depth=None,
    min_samples_leaf=1,
    max_features=1.0
):

    return Pipeline(
        steps=[
            (
                "preprocessor",
                create_preprocessor()
            ),
            (
                "model",
                RandomForestRegressor(
                    n_estimators=n_estimators,
                    max_depth=max_depth,
                    min_samples_leaf=min_samples_leaf,
                    max_features=max_features,
                    random_state=RANDOM_STATE,
                    n_jobs=-1
                )
            )
        ]
    )


def build_hist_gradient_boosting(
    learning_rate=0.05,
    max_iter=300,
    max_leaf_nodes=15,
    min_samples_leaf=20,
    l2_regularization=1.0
):

    return Pipeline(
        steps=[
            (
                "preprocessor",
                create_preprocessor()
            ),
            (
                "model",
                HistGradientBoostingRegressor(
                    learning_rate=learning_rate,
                    max_iter=max_iter,
                    max_leaf_nodes=max_leaf_nodes,
                    min_samples_leaf=min_samples_leaf,
                    l2_regularization=l2_regularization,
                    random_state=RANDOM_STATE
                )
            )
        ]
    )


# ============================================================
# CROSS VALIDATION
# ============================================================

def evaluate_model(
    model,
    df,
    target,
    model_name,
    params
):

    data = df[
        df[target].notna()
    ].copy()

    X = data[
        NUMERICAL_FEATURES
        + CATEGORICAL_FEATURES
    ]

    y = data[target]

    groups = data["project_code"]

    unique_projects = groups.nunique()

    n_splits = min(
        5,
        unique_projects
    )

    cv = GroupKFold(
        n_splits=n_splits
    )

    fold_mae = []
    fold_rmse = []
    fold_r2 = []

    for fold, (
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

        X_val = X.iloc[
            validation_index
        ]

        y_train = y.iloc[
            train_index
        ]

        y_val = y.iloc[
            validation_index
        ]

        train_projects = set(
            groups.iloc[
                train_index
            ]
        )

        val_projects = set(
            groups.iloc[
                validation_index
            ]
        )

        overlap = (
            train_projects
            & val_projects
        )

        if overlap:
            raise RuntimeError(
                "PROJECT LEAKAGE DETECTED"
            )

        model.fit(
            X_train,
            y_train
        )

        predictions = model.predict(
            X_val
        )

        mae = mean_absolute_error(
            y_val,
            predictions
        )

        rmse = np.sqrt(
            mean_squared_error(
                y_val,
                predictions
            )
        )

        r2 = r2_score(
            y_val,
            predictions
        )

        fold_mae.append(
            mae
        )

        fold_rmse.append(
            rmse
        )

        fold_r2.append(
            r2
        )

    return {
        "model": model_name,
        "target": target,
        "CV_MAE": np.mean(fold_mae),
        "CV_MAE_STD": np.std(fold_mae),
        "CV_RMSE": np.mean(fold_rmse),
        "CV_R2": np.mean(fold_r2),
        "params": str(params)
    }


# ============================================================
# MAIN TUNING
# ============================================================

def tune_target(
    train_df,
    target
):

    print("\n")
    print("#" * 70)

    print(
        f"TUNING TARGET: {target}"
    )

    print("#" * 70)

    results = []

    # --------------------------------------------------------
    # RIDGE BASELINE
    # --------------------------------------------------------

    print(
        "\nEvaluating Ridge..."
    )

    ridge_result = evaluate_model(
        build_ridge(),
        train_df,
        target,
        "Ridge",
        {
            "alpha": 10.0
        }
    )

    results.append(
        ridge_result
    )

    print(
        f"Ridge MAE: "
        f"{ridge_result['CV_MAE']:.4f}"
    )

    # ========================================================
    # RANDOM FOREST
    # ========================================================

    rf_configs = [

        {
            "n_estimators": 300,
            "max_depth": None,
            "min_samples_leaf": 1,
            "max_features": 1.0
        },

        {
            "n_estimators": 300,
            "max_depth": 10,
            "min_samples_leaf": 1,
            "max_features": 1.0
        },

        {
            "n_estimators": 300,
            "max_depth": 15,
            "min_samples_leaf": 1,
            "max_features": 1.0
        },

        {
            "n_estimators": 300,
            "max_depth": None,
            "min_samples_leaf": 2,
            "max_features": 1.0
        },

        {
            "n_estimators": 300,
            "max_depth": None,
            "min_samples_leaf": 3,
            "max_features": 1.0
        },

        {
            "n_estimators": 300,
            "max_depth": None,
            "min_samples_leaf": 5,
            "max_features": 1.0
        },

        {
            "n_estimators": 500,
            "max_depth": None,
            "min_samples_leaf": 2,
            "max_features": 0.8
        },

        {
            "n_estimators": 500,
            "max_depth": 10,
            "min_samples_leaf": 2,
            "max_features": 0.8
        }
    ]

    for i, params in enumerate(
        rf_configs,
        start=1
    ):

        print(
            f"\nRandom Forest "
            f"configuration {i}/"
            f"{len(rf_configs)}"
        )

        result = evaluate_model(
            build_random_forest(
                **params
            ),
            train_df,
            target,
            "RandomForest",
            params
        )

        results.append(
            result
        )

        print(
            f"CV MAE  : "
            f"{result['CV_MAE']:.4f}"
        )

        print(
            f"CV RMSE : "
            f"{result['CV_RMSE']:.4f}"
        )

        print(
            f"CV R²   : "
            f"{result['CV_R2']:.4f}"
        )

    # ========================================================
    # HISTOGRAM GRADIENT BOOSTING
    # ========================================================

    hgb_configs = [

        {
            "learning_rate": 0.05,
            "max_iter": 300,
            "max_leaf_nodes": 15,
            "min_samples_leaf": 20,
            "l2_regularization": 1.0
        },

        {
            "learning_rate": 0.05,
            "max_iter": 500,
            "max_leaf_nodes": 15,
            "min_samples_leaf": 20,
            "l2_regularization": 1.0
        },

        {
            "learning_rate": 0.03,
            "max_iter": 500,
            "max_leaf_nodes": 15,
            "min_samples_leaf": 20,
            "l2_regularization": 1.0
        },

        {
            "learning_rate": 0.05,
            "max_iter": 300,
            "max_leaf_nodes": 31,
            "min_samples_leaf": 20,
            "l2_regularization": 1.0
        },

        {
            "learning_rate": 0.05,
            "max_iter": 300,
            "max_leaf_nodes": 15,
            "min_samples_leaf": 10,
            "l2_regularization": 1.0
        },

        {
            "learning_rate": 0.05,
            "max_iter": 300,
            "max_leaf_nodes": 15,
            "min_samples_leaf": 30,
            "l2_regularization": 2.0
        }
    ]

    for i, params in enumerate(
        hgb_configs,
        start=1
    ):

        print(
            f"\nHistGradientBoosting "
            f"configuration {i}/"
            f"{len(hgb_configs)}"
        )

        result = evaluate_model(
            build_hist_gradient_boosting(
                **params
            ),
            train_df,
            target,
            "HistGradientBoosting",
            params
        )

        results.append(
            result
        )

        print(
            f"CV MAE  : "
            f"{result['CV_MAE']:.4f}"
        )

        print(
            f"CV RMSE : "
            f"{result['CV_RMSE']:.4f}"
        )

        print(
            f"CV R²   : "
            f"{result['CV_R2']:.4f}"
        )

    return pd.DataFrame(
        results
    )


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

    # --------------------------------------------------------
    # COST
    # --------------------------------------------------------

    cost_results = tune_target(
        train_df,
        COST_TARGET
    )

    # --------------------------------------------------------
    # SCHEDULE
    # --------------------------------------------------------

    schedule_results = tune_target(
        train_df,
        SCHEDULE_TARGET
    )

    # --------------------------------------------------------
    # Combine
    # --------------------------------------------------------

    all_results = pd.concat(
        [
            cost_results,
            schedule_results
        ],
        ignore_index=True
    )

    # --------------------------------------------------------
    # Sort by target and MAE
    # --------------------------------------------------------

    all_results = all_results.sort_values(
        [
            "target",
            "CV_MAE"
        ]
    )

    print("\n")
    print("=" * 70)
    print("FINAL TUNING RESULTS")
    print("=" * 70)

    print(
        all_results[
            [
                "target",
                "model",
                "CV_MAE",
                "CV_MAE_STD",
                "CV_RMSE",
                "CV_R2"
            ]
        ].to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # Best models
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("BEST CANDIDATES")
    print("=" * 70)

    for target in [
        COST_TARGET,
        SCHEDULE_TARGET
    ]:

        target_results = all_results[
            all_results["target"]
            == target
        ]

        best = target_results.iloc[
            target_results["CV_MAE"].argmin()
        ]

        print(
            f"\n{target}"
        )

        print(
            f"Model       : "
            f"{best['model']}"
        )

        print(
            f"CV MAE      : "
            f"{best['CV_MAE']:.4f}"
        )

        print(
            f"CV RMSE     : "
            f"{best['CV_RMSE']:.4f}"
        )

        print(
            f"CV R²       : "
            f"{best['CV_R2']:.4f}"
        )

        print(
            f"Parameters  : "
            f"{best['params']}"
        )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    output_path = (
        REPORTS_DIR
        / "model_tuning_results.csv"
    )

    all_results.to_csv(
        output_path,
        index=False
    )

    print(
        "\nResults saved to:"
    )

    print(
        output_path
    )

    print("\n")
    print("=" * 70)
    print("MODEL TUNING COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()