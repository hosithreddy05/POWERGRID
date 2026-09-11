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

from src.config import (
    TRAIN_DATA_PATH,
    TEST_DATA_PATH,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    COST_TARGET,
    SCHEDULE_TARGET,
    RANDOM_STATE,
    REPORTS_DIR,
    FIGURES_DIR
)


# ============================================================
# SIH 25192 - FINAL TEST EVALUATION
# ============================================================

print("=" * 70)
print("       SIH 25192 - FINAL TEST EVALUATION")
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
# FINAL RANDOM FOREST
# ============================================================

def build_model():

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


# ============================================================
# EVALUATION
# ============================================================

def evaluate(
    model,
    test_df,
    target
):

    data = test_df[
        test_df[target].notna()
    ].copy()

    X = data[
        NUMERICAL_FEATURES
        + CATEGORICAL_FEATURES
    ]

    y = data[target]

    predictions = model.predict(
        X
    )

    mae = mean_absolute_error(
        y,
        predictions
    )

    rmse = np.sqrt(
        mean_squared_error(
            y,
            predictions
        )
    )

    r2 = r2_score(
        y,
        predictions
    )

    result = data[
        [
            "project_code",
            "project_name",
            "snapshot_date",
            target
        ]
    ].copy()

    result[
        "prediction"
    ] = predictions

    result[
        "error"
    ] = (
        predictions - y
    )

    result[
        "absolute_error"
    ] = result[
        "error"
    ].abs()

    return (
        mae,
        rmse,
        r2,
        result
    )


# ============================================================
# PROJECT LEVEL
# ============================================================

def project_level_metrics(
    result,
    target
):

    project_summary = (
        result
        .groupby(
            [
                "project_code",
                "project_name"
            ]
        )
        .agg(
            actual=(
                target,
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

    project_summary[
        "absolute_error"
    ] = (
        project_summary[
            "predicted"
        ]
        -
        project_summary[
            "actual"
        ]
    ).abs()

    project_mae = (
        project_summary[
            "absolute_error"
        ].mean()
    )

    return (
        project_mae,
        project_summary
    )


# ============================================================
# MAIN
# ============================================================

def main():

    train_df = pd.read_csv(
        TRAIN_DATA_PATH
    )

    test_df = pd.read_csv(
        TEST_DATA_PATH
    )

    print("\nDATA")

    print(
        f"Training rows  : "
        f"{len(train_df)}"
    )

    print(
        f"Training projects : "
        f"{train_df['project_code'].nunique()}"
    )

    print(
        f"Testing rows : "
        f"{len(test_df)}"
    )

    print(
        f"Testing projects : "
        f"{test_df['project_code'].nunique()}"
    )

    overlap = (
        set(train_df["project_code"])
        &
        set(test_df["project_code"])
    )

    print(
        f"Project overlap : "
        f"{len(overlap)}"
    )

    if overlap:

        raise RuntimeError(
            "PROJECT LEAKAGE DETECTED"
        )

    # ========================================================
    # COST
    # ========================================================

    print("\n")
    print("#" * 70)
    print("FINAL COST MODEL")
    print("#" * 70)

    cost_train = train_df[
        train_df[COST_TARGET].notna()
    ].copy()

    cost_model = build_model()

    cost_model.fit(
        cost_train[
            NUMERICAL_FEATURES
            + CATEGORICAL_FEATURES
        ],
        cost_train[
            COST_TARGET
        ]
    )

    (
        cost_mae,
        cost_rmse,
        cost_r2,
        cost_predictions
    ) = evaluate(
        cost_model,
        test_df,
        COST_TARGET
    )

    (
        cost_project_mae,
        cost_project_summary
    ) = project_level_metrics(
        cost_predictions,
        COST_TARGET
    )

    print(
        f"\nTEST MAE  : "
        f"{cost_mae:.4f}%"
    )

    print(
        f"TEST RMSE : "
        f"{cost_rmse:.4f}%"
    )

    print(
        f"TEST R²   : "
        f"{cost_r2:.4f}"
    )

    print(
        f"PROJECT MAE : "
        f"{cost_project_mae:.4f}%"
    )

    print(
        "\nWorst cost predictions:"
    )

    print(
        cost_predictions
        .sort_values(
            "absolute_error",
            ascending=False
        )
        .head(10)
        .to_string(
            index=False
        )
    )

    cost_predictions.to_csv(
        REPORTS_DIR
        / "final_test_cost_predictions.csv",
        index=False
    )

    cost_project_summary.to_csv(
        REPORTS_DIR
        / "final_test_cost_project_summary.csv",
        index=False
    )

    # ========================================================
    # SCHEDULE
    # ========================================================

    print("\n")
    print("#" * 70)
    print("FINAL SCHEDULE MODEL")
    print("#" * 70)

    schedule_train = train_df[
        train_df[SCHEDULE_TARGET].notna()
    ].copy()

    schedule_model = build_model()

    schedule_model.fit(
        schedule_train[
            NUMERICAL_FEATURES
            + CATEGORICAL_FEATURES
        ],
        schedule_train[
            SCHEDULE_TARGET
        ]
    )

    (
        schedule_mae,
        schedule_rmse,
        schedule_r2,
        schedule_predictions
    ) = evaluate(
        schedule_model,
        test_df,
        SCHEDULE_TARGET
    )

    (
        schedule_project_mae,
        schedule_project_summary
    ) = project_level_metrics(
        schedule_predictions,
        SCHEDULE_TARGET
    )

    print(
        f"\nTEST MAE  : "
        f"{schedule_mae:.4f} months"
    )

    print(
        f"TEST RMSE : "
        f"{schedule_rmse:.4f} months"
    )

    print(
        f"TEST R²   : "
        f"{schedule_r2:.4f}"
    )

    print(
        f"PROJECT MAE : "
        f"{schedule_project_mae:.4f} months"
    )

    print(
        "\nWorst schedule predictions:"
    )

    print(
        schedule_predictions
        .sort_values(
            "absolute_error",
            ascending=False
        )
        .head(10)
        .to_string(
            index=False
        )
    )

    schedule_predictions.to_csv(
        REPORTS_DIR
        / "final_test_schedule_predictions.csv",
        index=False
    )

    schedule_project_summary.to_csv(
        REPORTS_DIR
        / "final_test_schedule_project_summary.csv",
        index=False
    )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print("\n")
    print("=" * 70)
    print("FINAL UNSEEN TEST RESULTS")
    print("=" * 70)

    print(
        "\nCOST MODEL"
    )

    print(
        f"MAE          : "
        f"{cost_mae:.4f}%"
    )

    print(
        f"RMSE         : "
        f"{cost_rmse:.4f}%"
    )

    print(
        f"R²           : "
        f"{cost_r2:.4f}"
    )

    print(
        f"Project MAE  : "
        f"{cost_project_mae:.4f}%"
    )

    print(
        "\nSCHEDULE MODEL"
    )

    print(
        f"MAE          : "
        f"{schedule_mae:.4f} months"
    )

    print(
        f"RMSE         : "
        f"{schedule_rmse:.4f} months"
    )

    print(
        f"R²           : "
        f"{schedule_r2:.4f}"
    )

    print(
        f"Project MAE  : "
        f"{schedule_project_mae:.4f} months"
    )

    print("\n")
    print("=" * 70)
    print("FINAL TEST EVALUATION COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()