import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path

from sklearn.ensemble import RandomForestRegressor
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
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
    RANDOM_STATE,
    RANDOM_FOREST_N_ESTIMATORS,
    RANDOM_FOREST_MIN_SAMPLES_LEAF,
    REPORTS_DIR,
    FIGURES_DIR,
)


# ============================================================
# SIH 25192 - ERROR ANALYSIS
# ============================================================


def print_header(title):

    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


# ============================================================
# TARGET DISTRIBUTION
# ============================================================

def analyze_target_distribution(df, target):

    print_header(
        f"TARGET DISTRIBUTION: {target}"
    )

    data = df[
        df[target].notna()
    ].copy()

    print(
        f"Rows: {len(data)}"
    )

    print(
        f"Projects: "
        f"{data['project_code'].nunique()}"
    )

    print("\nBasic statistics:")

    print(
        data[target].describe()
    )

    # --------------------------------------------------------
    # Zero values
    # --------------------------------------------------------

    zero_count = (
        data[target] == 0
    ).sum()

    print(
        f"\nZero values: "
        f"{zero_count}"
    )

    print(
        f"Zero percentage: "
        f"{zero_count / len(data) * 100:.2f}%"
    )

    # --------------------------------------------------------
    # Negative values
    # --------------------------------------------------------

    negative_count = (
        data[target] < 0
    ).sum()

    print(
        f"Negative values: "
        f"{negative_count}"
    )

    # --------------------------------------------------------
    # Positive values
    # --------------------------------------------------------

    positive_count = (
        data[target] > 0
    ).sum()

    print(
        f"Positive values: "
        f"{positive_count}"
    )

    print(
        f"Positive percentage: "
        f"{positive_count / len(data) * 100:.2f}%"
    )


# ============================================================
# PROJECT-LEVEL TARGET ANALYSIS
# ============================================================

def analyze_project_targets(df, target):

    print_header(
        f"PROJECT-LEVEL ANALYSIS: {target}"
    )

    data = df[
        df[target].notna()
    ].copy()

    project_summary = (
        data
        .groupby("project_code")
        .agg(
            project_name=(
                "project_name",
                "first"
            ),
            snapshots=(
                target,
                "size"
            ),
            target_unique_values=(
                target,
                "nunique"
            ),
            target_mean=(
                target,
                "mean"
            ),
            target_min=(
                target,
                "min"
            ),
            target_max=(
                target,
                "max"
            ),
        )
        .reset_index()
    )

    print(
        "\nNumber of projects:"
    )

    print(
        len(project_summary)
    )

    # --------------------------------------------------------
    # Projects with changing target
    # --------------------------------------------------------

    changing = project_summary[
        project_summary[
            "target_unique_values"
        ] > 1
    ]

    print(
        "\nProjects with more than "
        "one target value:"
    )

    print(
        len(changing)
    )

    if len(changing) > 0:

        print(
            changing.to_string(
                index=False
            )
        )

    # --------------------------------------------------------
    # High target projects
    # --------------------------------------------------------

    print(
        "\nHighest target projects:"
    )

    highest = project_summary.sort_values(
        "target_max",
        ascending=False
    ).head(10)

    print(
        highest.to_string(
            index=False
        )
    )

    return project_summary


# ============================================================
# SNAPSHOTS PER PROJECT
# ============================================================

def analyze_snapshots(df):

    print_header(
        "SNAPSHOT DISTRIBUTION BY PROJECT"
    )

    summary = (
        df
        .groupby("project_code")
        .size()
        .describe()
    )

    print(summary)

    counts = (
        df["project_code"]
        .value_counts()
        .sort_values()
    )

    print(
        "\nProjects with fewest snapshots:"
    )

    print(
        counts.head(10)
    )

    print(
        "\nProjects with most snapshots:"
    )

    print(
        counts.tail(10)
    )


# ============================================================
# BUILD RANDOM FOREST PIPELINE
# ============================================================

def build_random_forest():

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
        ],
        remainder="drop"
    )

    model = RandomForestRegressor(
        n_estimators=RANDOM_FOREST_N_ESTIMATORS,
        min_samples_leaf=RANDOM_FOREST_MIN_SAMPLES_LEAF,
        random_state=RANDOM_STATE,
        n_jobs=-1
    )

    return Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor
            ),
            (
                "model",
                model
            )
        ]
    )


# ============================================================
# TRAIN RANDOM FOREST
# ============================================================

def train_random_forest(
    train_df,
    target
):

    data = train_df[
        train_df[target].notna()
    ].copy()

    X = data[
        NUMERICAL_FEATURES
        + CATEGORICAL_FEATURES
    ]

    y = data[target]

    model = build_random_forest()

    model.fit(
        X,
        y
    )

    return model


# ============================================================
# PREDICTION ERROR ANALYSIS
# ============================================================

def analyze_predictions(
    model,
    test_df,
    target
):

    print_header(
        f"RANDOM FOREST ERROR ANALYSIS: {target}"
    )

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

    results = data[
        [
            "project_code",
            "project_name",
            "snapshot_date",
            target,
        ]
    ].copy()

    results[
        "prediction"
    ] = predictions

    results[
        "error"
    ] = (
        results["prediction"]
        - results[target]
    )

    results[
        "absolute_error"
    ] = results["error"].abs()

    results[
        "squared_error"
    ] = results["error"] ** 2

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

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

    print(
        f"\nMAE  : {mae:.4f}"
    )

    print(
        f"RMSE : {rmse:.4f}"
    )

    print(
        f"R²   : {r2:.4f}"
    )

    # --------------------------------------------------------
    # Worst predictions
    # --------------------------------------------------------

    print(
        "\nWorst 15 predictions:"
    )

    worst = results.sort_values(
        "absolute_error",
        ascending=False
    ).head(15)

    print(
        worst.to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # Project-level error
    # --------------------------------------------------------

    project_errors = (
        results
        .groupby(
            [
                "project_code",
                "project_name"
            ]
        )
        .agg(
            snapshots=(
                "absolute_error",
                "size"
            ),
            mean_absolute_error=(
                "absolute_error",
                "mean"
            ),
            max_absolute_error=(
                "absolute_error",
                "max"
            ),
            actual_mean=(
                target,
                "mean"
            ),
            predicted_mean=(
                "prediction",
                "mean"
            )
        )
        .reset_index()
    )

    project_errors = project_errors.sort_values(
        "mean_absolute_error",
        ascending=False
    )

    print(
        "\nWorst projects by average error:"
    )

    print(
        project_errors.head(15).to_string(
            index=False
        )
    )

    return results, project_errors


# ============================================================
# PLOT: ACTUAL VS PREDICTED
# ============================================================

def plot_actual_vs_predicted(
    results,
    target
):

    plt.figure(
        figsize=(8, 6)
    )

    plt.scatter(
        results[target],
        results["prediction"],
        alpha=0.7
    )

    minimum = min(
        results[target].min(),
        results["prediction"].min()
    )

    maximum = max(
        results[target].max(),
        results["prediction"].max()
    )

    plt.plot(
        [minimum, maximum],
        [minimum, maximum],
        linestyle="--"
    )

    plt.xlabel(
        "Actual"
    )

    plt.ylabel(
        "Predicted"
    )

    plt.title(
        f"Actual vs Predicted - {target}"
    )

    plt.tight_layout()

    path = (
        FIGURES_DIR
        / f"actual_vs_predicted_{target}.png"
    )

    plt.savefig(
        path,
        dpi=150
    )

    plt.close()

    print(
        f"\nSaved plot:"
        f"\n{path}"
    )


# ============================================================
# PLOT: RESIDUALS
# ============================================================

def plot_residuals(
    results,
    target
):

    plt.figure(
        figsize=(8, 6)
    )

    plt.scatter(
        results["prediction"],
        results["error"],
        alpha=0.7
    )

    plt.axhline(
        0,
        linestyle="--"
    )

    plt.xlabel(
        "Predicted"
    )

    plt.ylabel(
        "Residual (Prediction - Actual)"
    )

    plt.title(
        f"Residual Plot - {target}"
    )

    plt.tight_layout()

    path = (
        FIGURES_DIR
        / f"residuals_{target}.png"
    )

    plt.savefig(
        path,
        dpi=150
    )

    plt.close()

    print(
        f"Saved plot:"
        f"\n{path}"
    )


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

def analyze_feature_importance(
    model,
    target
):

    print_header(
        f"FEATURE IMPORTANCE: {target}"
    )

    preprocessor = model.named_steps[
        "preprocessor"
    ]

    rf_model = model.named_steps[
        "model"
    ]

    feature_names = (
        preprocessor
        .get_feature_names_out()
    )

    importances = (
        rf_model.feature_importances_
    )

    importance_df = pd.DataFrame(
        {
            "feature": feature_names,
            "importance": importances
        }
    )

    importance_df = importance_df.sort_values(
        "importance",
        ascending=False
    )

    print(
        importance_df.head(15).to_string(
            index=False
        )
    )

    path = (
        REPORTS_DIR
        / f"feature_importance_{target}.csv"
    )

    importance_df.to_csv(
        path,
        index=False
    )

    print(
        f"\nSaved feature importance:"
        f"\n{path}"
    )

    return importance_df


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)

    print(
        "       SIH 25192 - ERROR ANALYSIS"
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

    print(
        f"\nTraining rows: "
        f"{len(train_df)}"
    )

    print(
        f"Testing rows: "
        f"{len(test_df)}"
    )

    # ========================================================
    # General analysis
    # ========================================================

    analyze_snapshots(
        train_df
    )

    cost_projects = (
        analyze_project_targets(
            train_df,
            COST_TARGET
        )
    )

    schedule_projects = (
        analyze_project_targets(
            train_df,
            SCHEDULE_TARGET
        )
    )

    analyze_target_distribution(
        train_df,
        COST_TARGET
    )

    analyze_target_distribution(
        train_df,
        SCHEDULE_TARGET
    )

    # ========================================================
    # Train RF for cost
    # ========================================================

    print_header(
        "TRAINING RANDOM FOREST - COST"
    )

    cost_model = train_random_forest(
        train_df,
        COST_TARGET
    )

    cost_predictions, cost_project_errors = (
        analyze_predictions(
            cost_model,
            test_df,
            COST_TARGET
        )
    )

    plot_actual_vs_predicted(
        cost_predictions,
        COST_TARGET
    )

    plot_residuals(
        cost_predictions,
        COST_TARGET
    )

    analyze_feature_importance(
        cost_model,
        COST_TARGET
    )

    # ========================================================
    # Train RF for schedule
    # ========================================================

    print_header(
        "TRAINING RANDOM FOREST - SCHEDULE"
    )

    schedule_model = train_random_forest(
        train_df,
        SCHEDULE_TARGET
    )

    schedule_predictions, schedule_project_errors = (
        analyze_predictions(
            schedule_model,
            test_df,
            SCHEDULE_TARGET
        )
    )

    plot_actual_vs_predicted(
        schedule_predictions,
        SCHEDULE_TARGET
    )

    plot_residuals(
        schedule_predictions,
        SCHEDULE_TARGET
    )

    analyze_feature_importance(
        schedule_model,
        SCHEDULE_TARGET
    )

    # ========================================================
    # Save project errors
    # ========================================================

    cost_project_errors.to_csv(
        REPORTS_DIR
        / "cost_project_errors.csv",
        index=False
    )

    schedule_project_errors.to_csv(
        REPORTS_DIR
        / "schedule_project_errors.csv",
        index=False
    )

    print_header(
        "ERROR ANALYSIS COMPLETED"
    )

    print(
        "\nReports created in:"
    )

    print(
        REPORTS_DIR
    )

    print(
        "\nFigures created in:"
    )

    print(
        FIGURES_DIR
    )


if __name__ == "__main__":
    main()