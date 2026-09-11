import pandas as pd
import numpy as np

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.ensemble import (
    RandomForestRegressor,
    HistGradientBoostingRegressor,
)

from sklearn.model_selection import GroupKFold
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

from src.config import (
    TRAIN_DATA_PATH,
    TEST_DATA_PATH,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    COST_TARGET,
    SCHEDULE_TARGET,
    CV_SPLITS,
    RANDOM_STATE,
    RANDOM_FOREST_N_ESTIMATORS,
    RANDOM_FOREST_MIN_SAMPLES_LEAF,
    METRICS_DIR,
)


# ============================================================
# SIH 25192 - MODEL DEVELOPMENT
#
# Models:
#   1. Dummy
#   2. Ridge
#   3. Random Forest
#   4. HistGradientBoosting
#
# Validation:
#   GroupKFold by project_code
# ============================================================


# ============================================================
# PREPROCESSOR
# ============================================================

def build_preprocessor(scale_numeric=True):

    if scale_numeric:

        numerical_pipeline = Pipeline(
            steps=[
                (
                    "imputer",
                    SimpleImputer(strategy="median")
                ),
                (
                    "scaler",
                    StandardScaler()
                ),
            ]
        )

    else:

        numerical_pipeline = Pipeline(
            steps=[
                (
                    "imputer",
                    SimpleImputer(strategy="median")
                ),
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
            ),
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
            ),
        ],
        remainder="drop"
    )

    return preprocessor


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(y_true, y_pred):

    mae = mean_absolute_error(
        y_true,
        y_pred
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_true,
            y_pred
        )
    )

    r2 = r2_score(
        y_true,
        y_pred
    )

    return {
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2
    }


# ============================================================
# MODEL BUILDERS
# ============================================================

def build_dummy():

    return Pipeline(
        steps=[
            (
                "preprocessor",
                build_preprocessor(
                    scale_numeric=False
                )
            ),
            (
                "model",
                DummyRegressor(
                    strategy="mean"
                )
            )
        ]
    )


def build_ridge():

    return Pipeline(
        steps=[
            (
                "preprocessor",
                build_preprocessor(
                    scale_numeric=True
                )
            ),
            (
                "model",
                Ridge(
                    alpha=1.0
                )
            )
        ]
    )


def build_random_forest():

    return Pipeline(
        steps=[
            (
                "preprocessor",
                build_preprocessor(
                    scale_numeric=False
                )
            ),
            (
                "model",
                RandomForestRegressor(
                    n_estimators=RANDOM_FOREST_N_ESTIMATORS,
                    min_samples_leaf=RANDOM_FOREST_MIN_SAMPLES_LEAF,
                    random_state=RANDOM_STATE,
                    n_jobs=-1
                )
            )
        ]
    )


def build_hist_gradient_boosting():

    return Pipeline(
        steps=[
            (
                "preprocessor",
                build_preprocessor(
                    scale_numeric=False
                )
            ),
            (
                "model",
                HistGradientBoostingRegressor(
                    max_iter=200,
                    learning_rate=0.05,
                    max_leaf_nodes=15,
                    l2_regularization=1.0,
                    random_state=RANDOM_STATE
                )
            )
        ]
    )


# ============================================================
# MODEL DICTIONARY
# ============================================================

def get_models():

    return {
        "Dummy": build_dummy,
        "Ridge": build_ridge,
        "RandomForest": build_random_forest,
        "HistGradientBoosting": build_hist_gradient_boosting
    }


# ============================================================
# GROUP K-FOLD VALIDATION
# ============================================================

def evaluate_model_cv(
    train_df,
    target,
    model_name,
    model_builder
):

    print("\n" + "=" * 70)

    print(
        f"{model_name.upper()} "
        f"GROUP CROSS-VALIDATION"
    )

    print(
        f"Target: {target}"
    )

    print("=" * 70)

    # --------------------------------------------------------
    # Remove missing target values
    # --------------------------------------------------------

    data = train_df[
        train_df[target].notna()
    ].copy()

    X = data[
        NUMERICAL_FEATURES
        + CATEGORICAL_FEATURES
    ]

    y = data[target]

    groups = data["project_code"]

    unique_projects = groups.nunique()

    n_splits = min(
        CV_SPLITS,
        unique_projects
    )

    print(
        f"\nRows available  : {len(data)}"
    )

    print(
        f"Projects        : {unique_projects}"
    )

    print(
        f"CV folds        : {n_splits}"
    )

    # --------------------------------------------------------
    # GroupKFold
    # --------------------------------------------------------

    cv = GroupKFold(
        n_splits=n_splits
    )

    fold_results = []

    for fold_number, (
        train_indices,
        validation_indices
    ) in enumerate(
        cv.split(
            X,
            y,
            groups=groups
        ),
        start=1
    ):

        X_train = X.iloc[
            train_indices
        ]

        X_validation = X.iloc[
            validation_indices
        ]

        y_train = y.iloc[
            train_indices
        ]

        y_validation = y.iloc[
            validation_indices
        ]

        train_groups = set(
            groups.iloc[
                train_indices
            ]
        )

        validation_groups = set(
            groups.iloc[
                validation_indices
            ]
        )

        overlap = (
            train_groups
            .intersection(
                validation_groups
            )
        )

        if overlap:

            raise RuntimeError(
                f"Project leakage detected "
                f"in fold {fold_number}"
            )

        # ----------------------------------------------------
        # New model for every fold
        # ----------------------------------------------------

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
            metrics
        )

        print(
            f"\nFold {fold_number}"
        )

        print(
            f"Train projects : "
            f"{len(train_groups)}"
        )

        print(
            f"Valid projects : "
            f"{len(validation_groups)}"
        )

        print(
            f"Overlap        : "
            f"{len(overlap)}"
        )

        print(
            f"MAE            : "
            f"{metrics['MAE']:.4f}"
        )

        print(
            f"RMSE           : "
            f"{metrics['RMSE']:.4f}"
        )

        print(
            f"R²             : "
            f"{metrics['R2']:.4f}"
        )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    results_df = pd.DataFrame(
        fold_results
    )

    mean_results = results_df.mean()

    std_results = results_df.std()

    print("\n" + "-" * 70)
    print("CROSS-VALIDATION SUMMARY")
    print("-" * 70)

    print(
        f"Mean MAE  : "
        f"{mean_results['MAE']:.4f}"
    )

    print(
        f"Std MAE   : "
        f"{std_results['MAE']:.4f}"
    )

    print(
        f"Mean RMSE : "
        f"{mean_results['RMSE']:.4f}"
    )

    print(
        f"Mean R²   : "
        f"{mean_results['R2']:.4f}"
    )

    return {
        "CV_MAE": mean_results["MAE"],
        "CV_RMSE": mean_results["RMSE"],
        "CV_R2": mean_results["R2"],
        "CV_MAE_STD": std_results["MAE"]
    }


# ============================================================
# TRAIN FINAL MODEL
# ============================================================

def train_final_model(
    train_df,
    test_df,
    target,
    model_name,
    model_builder
):

    print("\n" + "=" * 70)

    print(
        f"FINAL {model_name.upper()} MODEL"
    )

    print(
        f"Target: {target}"
    )

    print("=" * 70)

    train_data = train_df[
        train_df[target].notna()
    ].copy()

    test_data = test_df[
        test_df[target].notna()
    ].copy()

    X_train = train_data[
        NUMERICAL_FEATURES
        + CATEGORICAL_FEATURES
    ]

    y_train = train_data[target]

    X_test = test_data[
        NUMERICAL_FEATURES
        + CATEGORICAL_FEATURES
    ]

    y_test = test_data[target]

    train_projects = set(
        train_data["project_code"]
    )

    test_projects = set(
        test_data["project_code"]
    )

    overlap = (
        train_projects
        .intersection(test_projects)
    )

    if overlap:

        raise RuntimeError(
            "Project leakage detected "
            "between train and test!"
        )

    model = model_builder()

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(
        X_test
    )

    metrics = calculate_metrics(
        y_test,
        predictions
    )

    print(
        f"\nTraining rows : "
        f"{len(train_data)}"
    )

    print(
        f"Testing rows  : "
        f"{len(test_data)}"
    )

    print(
        f"Train projects: "
        f"{len(train_projects)}"
    )

    print(
        f"Test projects : "
        f"{len(test_projects)}"
    )

    print(
        f"Overlap       : "
        f"{len(overlap)}"
    )

    print("\nTEST RESULTS")

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

    return model, metrics


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)

    print(
        "       SIH 25192 - MODEL COMPARISON"
    )

    print("=" * 70)

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    train_df = pd.read_csv(
        TRAIN_DATA_PATH
    )

    test_df = pd.read_csv(
        TEST_DATA_PATH
    )

    print("\nDATA")

    print(
        f"Training rows    : "
        f"{len(train_df)}"
    )

    print(
        f"Testing rows     : "
        f"{len(test_df)}"
    )

    print(
        f"Training projects: "
        f"{train_df['project_code'].nunique()}"
    )

    print(
        f"Testing projects : "
        f"{test_df['project_code'].nunique()}"
    )

    models = get_models()

    all_results = []

    # ========================================================
    # COST
    # ========================================================

    print("\n\n")
    print("#" * 70)
    print("COST OVERRUN PREDICTION")
    print("#" * 70)

    for model_name, model_builder in models.items():

        cv_metrics = evaluate_model_cv(
            train_df,
            COST_TARGET,
            model_name,
            model_builder
        )

        all_results.append(
            {
                "Target": "Cost",
                "Model": model_name,
                **cv_metrics
            }
        )

    # ========================================================
    # SCHEDULE
    # ========================================================

    print("\n\n")
    print("#" * 70)
    print("SCHEDULE OVERRUN PREDICTION")
    print("#" * 70)

    for model_name, model_builder in models.items():

        cv_metrics = evaluate_model_cv(
            train_df,
            SCHEDULE_TARGET,
            model_name,
            model_builder
        )

        all_results.append(
            {
                "Target": "Schedule",
                "Model": model_name,
                **cv_metrics
            }
        )

    # ========================================================
    # Comparison table
    # ========================================================

    results_df = pd.DataFrame(
        all_results
    )

    print("\n\n")

    print("=" * 70)
    print("GROUP CROSS-VALIDATION MODEL COMPARISON")
    print("=" * 70)

    display_columns = [
        "Target",
        "Model",
        "CV_MAE",
        "CV_MAE_STD",
        "CV_RMSE",
        "CV_R2"
    ]

    print(
        results_df[
            display_columns
        ].to_string(
            index=False
        )
    )

    # ========================================================
    # Determine best model by MAE
    # ========================================================

    print("\n" + "=" * 70)
    print("BEST MODELS BASED ON CV MAE")
    print("=" * 70)

    for target_name in [
        "Cost",
        "Schedule"
    ]:

        target_results = results_df[
            results_df["Target"]
            == target_name
        ].copy()

        best_row = target_results.loc[
            target_results["CV_MAE"].idxmin()
        ]

        print(
            f"\n{target_name}: "
            f"{best_row['Model']}"
        )

        print(
            f"CV MAE: "
            f"{best_row['CV_MAE']:.4f}"
        )

        print(
            f"CV RMSE: "
            f"{best_row['CV_RMSE']:.4f}"
        )

        print(
            f"CV R²: "
            f"{best_row['CV_R2']:.4f}"
        )

    # ========================================================
    # Save CV results
    # ========================================================

    results_path = (
        METRICS_DIR
        / "model_comparison_cv.csv"
    )

    results_df.to_csv(
        results_path,
        index=False
    )

    print("\n" + "=" * 70)

    print(
        "CV RESULTS SAVED"
    )

    print(
        results_path
    )

    print("=" * 70)


if __name__ == "__main__":
    main()