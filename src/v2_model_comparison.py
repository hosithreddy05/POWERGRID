"""
===========================================================================
       SIH 25192 - V2 CONTROLLED MODEL COMPARISON
===========================================================================

Purpose:
    Compare different ML models using ONLY the V2 training projects.

Important rules:
    - NO synthetic data
    - NO test-set target usage
    - NO project leakage
    - V1 models are NOT modified
    - Model selection uses GroupKFold by project
    - Compare BASE features vs BASE + TRAJECTORY features

Targets:
    1. target_cost_overrun_pct
    2. target_schedule_overrun_months

Metrics:
    MAE
    RMSE
    R2
    Project-level MAE

=========================================================================== 
"""

from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.base import clone

from sklearn.compose import ColumnTransformer

from sklearn.ensemble import (
    RandomForestRegressor,
    ExtraTreesRegressor,
    HistGradientBoostingRegressor,
    GradientBoostingRegressor
)

from sklearn.impute import SimpleImputer

from sklearn.linear_model import Ridge

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from sklearn.model_selection import GroupKFold

from sklearn.pipeline import Pipeline

from sklearn.preprocessing import OneHotEncoder


# =========================================================================
# PATHS
# =========================================================================

ROOT = Path(__file__).resolve().parents[1]

COST_TRAIN_PATH = (
    ROOT
    / "data"
    / "v2"
    / "train_cost_v2.csv"
)

SCHEDULE_TRAIN_PATH = (
    ROOT
    / "data"
    / "v2"
    / "train_schedule_v2.csv"
)

REPORT_DIR = ROOT / "reports"

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================================
# FEATURES
# =========================================================================

BASE_NUMERICAL_FEATURES = [
    "original_cost_cr",
    "cumulative_expenditure_cr",
    "physical_progress_pct",
    "planned_duration_months",
    "elapsed_months",
    "months_to_original_target",
    "expenditure_pct_of_original_cost",
]

TRAJECTORY_FEATURES = [
    "progress_velocity",
    "expenditure_velocity",
    "expenditure_progress_gap",
    "schedule_slippage_months",
]

CATEGORICAL_FEATURES = [
    "project_category"
]


# =========================================================================
# TARGETS
# =========================================================================

COST_TARGET = "target_cost_overrun_pct"

SCHEDULE_TARGET = "target_schedule_overrun_months"


# =========================================================================
# MODEL FACTORIES
# =========================================================================

def get_models():

    models = {

        "Ridge": Ridge(
            alpha=10.0
        ),

        "RandomForest": RandomForestRegressor(
            n_estimators=300,
            max_depth=None,
            min_samples_leaf=3,
            max_features=1.0,
            random_state=42,
            n_jobs=-1
        ),

        "ExtraTrees": ExtraTreesRegressor(
            n_estimators=300,
            max_depth=None,
            min_samples_leaf=3,
            max_features=1.0,
            random_state=42,
            n_jobs=-1
        ),

        "GradientBoosting": GradientBoostingRegressor(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=2,
            min_samples_leaf=5,
            random_state=42
        ),

        "HistGradientBoosting": HistGradientBoostingRegressor(
            max_iter=200,
            learning_rate=0.05,
            max_leaf_nodes=15,
            min_samples_leaf=10,
            l2_regularization=1.0,
            random_state=42
        )
    }

    return models


# =========================================================================
# PREPROCESSOR
# =========================================================================

def build_pipeline(
    model,
    numerical_features,
    categorical_features
):

    numeric_pipeline = Pipeline(
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
                "num",
                numeric_pipeline,
                numerical_features
            ),
            (
                "cat",
                categorical_pipeline,
                categorical_features
            )
        ]
    )

    pipeline = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor
            ),
            (
                "model",
                clone(model)
            )
        ]
    )

    return pipeline


# =========================================================================
# PROJECT MAE
# =========================================================================

def calculate_project_mae(
    validation_df,
    predictions,
    target
):

    temp = validation_df[
        [
            "project_code",
            target
        ]
    ].copy()

    temp["prediction"] = predictions

    project_values = []

    for project_code, group in temp.groupby(
        "project_code"
    ):

        actual = group[target].mean()
        predicted = group["prediction"].mean()

        error = abs(
            actual - predicted
        )

        project_values.append(error)

    if not project_values:
        return np.nan

    return float(
        np.mean(project_values)
    )


# =========================================================================
# EVALUATION
# =========================================================================

def evaluate_model(
    df,
    target,
    feature_set_name,
    numerical_features,
    categorical_features,
    model_name,
    model
):

    X = df[
        numerical_features
        + categorical_features
    ].copy()

    y = df[
        target
    ].copy()

    groups = df[
        "project_code"
    ].copy()

    n_projects = groups.nunique()

    n_splits = min(
        5,
        n_projects
    )

    if n_splits < 2:

        raise ValueError(
            "Not enough projects for GroupKFold."
        )

    cv = GroupKFold(
        n_splits=n_splits
    )

    fold_mae = []
    fold_rmse = []
    fold_r2 = []
    fold_project_mae = []

    oof_predictions = np.full(
        len(df),
        np.nan
    )

    print(
        f"\n{feature_set_name} | "
        f"{model_name}"
    )

    for fold, (
        train_idx,
        validation_idx
    ) in enumerate(
        cv.split(
            X,
            y,
            groups
        ),
        start=1
    ):

        X_train = X.iloc[
            train_idx
        ]

        X_validation = X.iloc[
            validation_idx
        ]

        y_train = y.iloc[
            train_idx
        ]

        y_validation = y.iloc[
            validation_idx
        ]

        train_projects = set(
            groups.iloc[
                train_idx
            ]
        )

        validation_projects = set(
            groups.iloc[
                validation_idx
            ]
        )

        overlap = (
            train_projects
            & validation_projects
        )

        if overlap:

            raise ValueError(
                f"PROJECT LEAKAGE in fold {fold}: "
                f"{overlap}"
            )

        pipeline = build_pipeline(
            model=model,
            numerical_features=numerical_features,
            categorical_features=categorical_features
        )

        pipeline.fit(
            X_train,
            y_train
        )

        predictions = pipeline.predict(
            X_validation
        )

        oof_predictions[
            validation_idx
        ] = predictions

        mae = mean_absolute_error(
            y_validation,
            predictions
        )

        rmse = np.sqrt(
            mean_squared_error(
                y_validation,
                predictions
            )
        )

        r2 = r2_score(
            y_validation,
            predictions
        )

        validation_df = df.iloc[
            validation_idx
        ].copy()

        project_mae = calculate_project_mae(
            validation_df,
            predictions,
            target
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

        fold_project_mae.append(
            project_mae
        )

        print(
            f"  Fold {fold}: "
            f"MAE={mae:.4f} | "
            f"RMSE={rmse:.4f} | "
            f"R²={r2:.4f} | "
            f"Project MAE={project_mae:.4f} | "
            f"Overlap={len(overlap)}"
        )

    valid = ~np.isnan(
        oof_predictions
    )

    oof_actual = y.iloc[
        np.where(valid)[0]
    ]

    oof_pred = oof_predictions[
        valid
    ]

    snapshot_mae = mean_absolute_error(
        oof_actual,
        oof_pred
    )

    snapshot_rmse = np.sqrt(
        mean_squared_error(
            oof_actual,
            oof_pred
        )
    )

    snapshot_r2 = r2_score(
        oof_actual,
        oof_pred
    )

    result = {

        "target": target,

        "feature_set": feature_set_name,

        "model": model_name,

        "rows": len(df),

        "projects": df[
            "project_code"
        ].nunique(),

        "CV_MAE": np.mean(
            fold_mae
        ),

        "CV_MAE_STD": np.std(
            fold_mae
        ),

        "CV_RMSE": np.mean(
            fold_rmse
        ),

        "CV_R2": np.mean(
            fold_r2
        ),

        "CV_PROJECT_MAE": np.mean(
            fold_project_mae
        ),

        "OOF_MAE": snapshot_mae,

        "OOF_RMSE": snapshot_rmse,

        "OOF_R2": snapshot_r2,

        "OOF_PROJECT_MAE": calculate_project_mae(
            df.loc[valid].copy(),
            oof_pred,
            target
        )
    }

    return result


# =========================================================================
# DATA VALIDATION
# =========================================================================

def validate_dataset(
    df,
    target,
    dataset_name
):

    print(
        f"\n[{dataset_name}]"
    )

    print(
        "Rows:",
        len(df)
    )

    print(
        "Projects:",
        df[
            "project_code"
        ].nunique()
    )

    required = (
        [
            "project_code",
            "project_name",
            "snapshot_date"
        ]
        + BASE_NUMERICAL_FEATURES
        + TRAJECTORY_FEATURES
        + CATEGORICAL_FEATURES
        + [target]
    )

    missing = [
        col
        for col in required
        if col not in df.columns
    ]

    if missing:

        raise ValueError(
            f"Missing columns in {dataset_name}: "
            f"{missing}"
        )

    if df[target].isna().any():

        raise ValueError(
            f"Target contains missing values: "
            f"{target}"
        )

    print(
        "✓ Required columns present"
    )

    print(
        "✓ Target contains no missing values"
    )


# =========================================================================
# MAIN
# =========================================================================

def main():

    print("=" * 75)
    print("       SIH 25192 - V2 CONTROLLED MODEL COMPARISON")
    print("=" * 75)

    print(
        "\nIMPORTANT:"
    )

    print(
        "  Test data is NOT used."
    )

    print(
        "  Synthetic data is NOT used."
    )

    print(
        "  PDF rows are NOT used."
    )

    print(
        "  V1 models are NOT modified."
    )

    # =====================================================================
    # 1. LOAD COST
    # =====================================================================

    print("\n" + "=" * 75)
    print("[1] LOADING COST TRAINING DATA")
    print("=" * 75)

    cost_df = pd.read_csv(
        COST_TRAIN_PATH
    )

    cost_df["snapshot_date"] = pd.to_datetime(
        cost_df["snapshot_date"],
        errors="coerce"
    )

    validate_dataset(
        cost_df,
        COST_TARGET,
        "COST"
    )

    # =====================================================================
    # 2. LOAD SCHEDULE
    # =====================================================================

    print("\n" + "=" * 75)
    print("[2] LOADING SCHEDULE TRAINING DATA")
    print("=" * 75)

    schedule_df = pd.read_csv(
        SCHEDULE_TRAIN_PATH
    )

    schedule_df["snapshot_date"] = pd.to_datetime(
        schedule_df["snapshot_date"],
        errors="coerce"
    )

    validate_dataset(
        schedule_df,
        SCHEDULE_TARGET,
        "SCHEDULE"
    )

    # =====================================================================
    # 3. FEATURE SETS
    # =====================================================================

    base_features = (
        BASE_NUMERICAL_FEATURES
    )

    base_plus_trajectory = (
        BASE_NUMERICAL_FEATURES
        + TRAJECTORY_FEATURES
    )

    feature_sets = {

        "BASE": base_features,

        "BASE_PLUS_TRAJECTORY":
            base_plus_trajectory
    }

    print("\n" + "=" * 75)
    print("[3] FEATURE SETS")
    print("=" * 75)

    print(
        "\nBASE features:",
        len(base_features)
    )

    for feature in base_features:
        print(
            "  ✓",
            feature
        )

    print(
        "\nBASE + TRAJECTORY:",
        len(base_plus_trajectory)
    )

    for feature in TRAJECTORY_FEATURES:
        print(
            "  +",
            feature
        )

    # =====================================================================
    # 4. MODELS
    # =====================================================================

    models = get_models()

    print("\n" + "=" * 75)
    print("[4] MODELS TO COMPARE")
    print("=" * 75)

    for name in models:
        print(
            "  ✓",
            name
        )

    # =====================================================================
    # 5. COST COMPARISON
    # =====================================================================

    print("\n" + "=" * 75)
    print("[5] COST MODEL COMPARISON")
    print("=" * 75)

    cost_results = []

    for feature_set_name, numerical_features in feature_sets.items():

        for model_name, model in models.items():

            result = evaluate_model(
                df=cost_df,
                target=COST_TARGET,
                feature_set_name=feature_set_name,
                numerical_features=numerical_features,
                categorical_features=CATEGORICAL_FEATURES,
                model_name=model_name,
                model=model
            )

            cost_results.append(
                result
            )

    cost_results_df = pd.DataFrame(
        cost_results
    )

    cost_results_df = (
        cost_results_df
        .sort_values(
            [
                "OOF_PROJECT_MAE",
                "OOF_MAE"
            ]
        )
    )

    # =====================================================================
    # 6. SCHEDULE COMPARISON
    # =====================================================================

    print("\n" + "=" * 75)
    print("[6] SCHEDULE MODEL COMPARISON")
    print("=" * 75)

    schedule_results = []

    for feature_set_name, numerical_features in feature_sets.items():

        for model_name, model in models.items():

            result = evaluate_model(
                df=schedule_df,
                target=SCHEDULE_TARGET,
                feature_set_name=feature_set_name,
                numerical_features=numerical_features,
                categorical_features=CATEGORICAL_FEATURES,
                model_name=model_name,
                model=model
            )

            schedule_results.append(
                result
            )

    schedule_results_df = pd.DataFrame(
        schedule_results
    )

    schedule_results_df = (
        schedule_results_df
        .sort_values(
            [
                "OOF_PROJECT_MAE",
                "OOF_MAE"
            ]
        )
    )

    # =====================================================================
    # 7. PRINT COST RESULTS
    # =====================================================================

    print("\n" + "=" * 75)
    print("COST MODEL RESULTS")
    print("=" * 75)

    print(
        cost_results_df[
            [
                "feature_set",
                "model",
                "CV_MAE",
                "CV_MAE_STD",
                "CV_RMSE",
                "CV_R2",
                "CV_PROJECT_MAE",
                "OOF_MAE",
                "OOF_RMSE",
                "OOF_R2",
                "OOF_PROJECT_MAE"
            ]
        ].to_string(
            index=False
        )
    )

    # =====================================================================
    # 8. PRINT SCHEDULE RESULTS
    # =====================================================================

    print("\n" + "=" * 75)
    print("SCHEDULE MODEL RESULTS")
    print("=" * 75)

    print(
        schedule_results_df[
            [
                "feature_set",
                "model",
                "CV_MAE",
                "CV_MAE_STD",
                "CV_RMSE",
                "CV_R2",
                "CV_PROJECT_MAE",
                "OOF_MAE",
                "OOF_RMSE",
                "OOF_R2",
                "OOF_PROJECT_MAE"
            ]
        ].to_string(
            index=False
        )
    )

    # =====================================================================
    # 9. BEST CANDIDATES
    # =====================================================================

    print("\n" + "=" * 75)
    print("BEST COST CANDIDATES")
    print("=" * 75)

    print(
        cost_results_df.head(
            5
        ).to_string(
            index=False
        )
    )

    print("\n" + "=" * 75)
    print("BEST SCHEDULE CANDIDATES")
    print("=" * 75)

    print(
        schedule_results_df.head(
            5
        ).to_string(
            index=False
        )
    )

    # =====================================================================
    # 10. TRAJECTORY BENEFIT
    # =====================================================================

    print("\n" + "=" * 75)
    print("TRAJECTORY FEATURE BENEFIT")
    print("=" * 75)

    for target_name, results_df in [
        ("COST", cost_results_df),
        ("SCHEDULE", schedule_results_df)
    ]:

        print(
            f"\n{target_name}"
        )

        for model_name in models.keys():

            base_row = results_df[
                (
                    results_df["feature_set"]
                    == "BASE"
                )
                &
                (
                    results_df["model"]
                    == model_name
                )
            ]

            trajectory_row = results_df[
                (
                    results_df["feature_set"]
                    == "BASE_PLUS_TRAJECTORY"
                )
                &
                (
                    results_df["model"]
                    == model_name
                )
            ]

            if (
                len(base_row) == 1
                and len(trajectory_row) == 1
            ):

                base_mae = float(
                    base_row[
                        "OOF_PROJECT_MAE"
                    ].iloc[0]
                )

                trajectory_mae = float(
                    trajectory_row[
                        "OOF_PROJECT_MAE"
                    ].iloc[0]
                )

                improvement = (
                    base_mae
                    - trajectory_mae
                )

                print(
                    f"  {model_name}: "
                    f"Project MAE change = "
                    f"{improvement:+.4f}"
                )

    # =====================================================================
    # 11. SAVE
    # =====================================================================

    print("\n" + "=" * 75)
    print("[7] SAVING MODEL COMPARISON REPORTS")
    print("=" * 75)

    cost_output = (
        REPORT_DIR
        / "v2_cost_model_comparison.csv"
    )

    schedule_output = (
        REPORT_DIR
        / "v2_schedule_model_comparison.csv"
    )

    cost_results_df.to_csv(
        cost_output,
        index=False
    )

    schedule_results_df.to_csv(
        schedule_output,
        index=False
    )

    print(
        "✓",
        cost_output
    )

    print(
        "✓",
        schedule_output
    )

    # =====================================================================
    # 12. FINAL STATUS
    # =====================================================================

    print("\n" + "=" * 75)
    print("V2 CONTROLLED MODEL COMPARISON COMPLETED")
    print("=" * 75)

    print(
        "\nNo test data was used."
    )

    print(
        "No synthetic data was used."
    )

    print(
        "No PDF rows were appended."
    )

    print(
        "No V1 model was modified."
    )

    print(
        "\nNext step:"
    )

    print(
        "Use these results to select the final V2"
    )

    print(
        "cost and schedule models before testing"
    )

    print(
        "on the 23 completely unseen projects."
    )

    print("\n" + "=" * 75)


if __name__ == "__main__":
    main()