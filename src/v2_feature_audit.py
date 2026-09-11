"""
SIH 25192 - V2 FEATURE AUDIT

Purpose:
    Determine whether the selected trajectory features add useful
    information before training the final V2 models.

Rules:
    - Training data only.
    - Test targets are NEVER used.
    - No synthetic data.
    - V1 remains untouched.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

TRAIN_PATH = (
    ROOT
    / "data"
    / "v2"
    / "train_cost_v2.csv"
)

REPORT_DIR = ROOT / "reports"

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# FEATURES
# ============================================================

BASE_FEATURES = [
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
    "schedule_pressure_ratio",
    "budget_consumption_ratio",
]

CATEGORICAL_FEATURES = [
    "project_category"
]

TARGET = "target_cost_overrun_pct"


# ============================================================
# HELPER
# ============================================================

def correlation_table(df):

    numerical_features = (
        BASE_FEATURES
        + TRAJECTORY_FEATURES
    )

    rows = []

    for feature in numerical_features:

        corr = df[
            [feature, TARGET]
        ].corr(
            method="spearman"
        ).iloc[0, 1]

        rows.append(
            {
                "feature": feature,
                "spearman_correlation": corr
            }
        )

    result = pd.DataFrame(rows)

    result["absolute_correlation"] = (
        result["spearman_correlation"]
        .abs()
    )

    return result.sort_values(
        "absolute_correlation",
        ascending=False
    )


def build_model():

    numerical_features = (
        BASE_FEATURES
        + TRAJECTORY_FEATURES
    )

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
                CATEGORICAL_FEATURES
            )
        ]
    )

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
                preprocessor
            ),
            (
                "model",
                model
            )
        ]
    )

    return pipeline


def main():

    print("=" * 75)
    print("       SIH 25192 - V2 FEATURE AUDIT")
    print("=" * 75)

    # --------------------------------------------------------
    # 1. Load
    # --------------------------------------------------------

    print("\n[1] Loading V2 training data...")

    df = pd.read_csv(
        TRAIN_PATH
    )

    print(
        "Rows    :",
        len(df)
    )

    print(
        "Projects:",
        df["project_code"].nunique()
    )

    # --------------------------------------------------------
    # 2. Basic validation
    # --------------------------------------------------------

    print("\n[2] Feature validation")

    all_features = (
        BASE_FEATURES
        + TRAJECTORY_FEATURES
        + CATEGORICAL_FEATURES
    )

    missing = [
        feature
        for feature in all_features
        if feature not in df.columns
    ]

    if missing:

        raise ValueError(
            f"Missing features: {missing}"
        )

    print(
        "Base features      :",
        len(BASE_FEATURES)
    )

    print(
        "Trajectory features:",
        len(TRAJECTORY_FEATURES)
    )

    print(
        "Categorical        :",
        len(CATEGORICAL_FEATURES)
    )

    print(
        "Total input features:",
        len(all_features)
    )

    # --------------------------------------------------------
    # 3. Cost target
    # --------------------------------------------------------

    print("\n[3] Cost target distribution")

    positive = (
        df[TARGET] > 0.5
    )

    print(
        "Total rows:",
        len(df)
    )

    print(
        "Positive rows:",
        int(positive.sum())
    )

    print(
        "Non-positive rows:",
        int((~positive).sum())
    )

    print(
        "Positive projects:",
        df.loc[
            positive,
            "project_code"
        ].nunique()
    )

    # --------------------------------------------------------
    # 4. Correlation
    # --------------------------------------------------------

    print("\n[4] Spearman correlation with cost overrun")

    corr = correlation_table(
        df
    )

    print(
        corr[
            [
                "feature",
                "spearman_correlation"
            ]
        ].to_string(
            index=False
        )
    )

    corr.to_csv(
        REPORT_DIR
        / "v2_cost_feature_correlations.csv",
        index=False
    )

    # --------------------------------------------------------
    # 5. Compare normal vs risk projects
    # --------------------------------------------------------

    print("\n[5] Project-level feature comparison")

    project_latest = (
        df.sort_values(
            [
                "project_code",
                "snapshot_date"
            ]
        )
        .groupby(
            "project_code",
            as_index=False
        )
        .tail(1)
        .copy()
    )

    project_latest["risk"] = (
        project_latest[TARGET] > 0.5
    )

    comparison_rows = []

    for feature in BASE_FEATURES + TRAJECTORY_FEATURES:

        normal = project_latest.loc[
            ~project_latest["risk"],
            feature
        ].mean()

        risk = project_latest.loc[
            project_latest["risk"],
            feature
        ].mean()

        normal_median = project_latest.loc[
            ~project_latest["risk"],
            feature
        ].median()

        risk_median = project_latest.loc[
            project_latest["risk"],
            feature
        ].median()

        comparison_rows.append(
            {
                "feature": feature,
                "normal_mean": normal,
                "risk_mean": risk,
                "normal_median": normal_median,
                "risk_median": risk_median
            }
        )

    comparison = pd.DataFrame(
        comparison_rows
    )

    print(
        comparison.to_string(
            index=False
        )
    )

    comparison.to_csv(
        REPORT_DIR
        / "v2_project_feature_comparison.csv",
        index=False
    )

    # --------------------------------------------------------
    # 6. Baseline RF importance
    # --------------------------------------------------------

    print("\n[6] Training baseline V2 feature-importance model")

    X = df[
        BASE_FEATURES
        + TRAJECTORY_FEATURES
        + CATEGORICAL_FEATURES
    ]

    y = df[
        TARGET
    ]

    model = build_model()

    model.fit(
        X,
        y
    )

    print(
        "✓ Baseline model fitted"
    )

    # --------------------------------------------------------
    # 7. Permutation importance
    # --------------------------------------------------------

    print("\n[7] Calculating permutation importance")

    importance = permutation_importance(
        model,
        X,
        y,
        n_repeats=10,
        random_state=42,
        scoring="neg_mean_absolute_error",
        n_jobs=-1
    )

    importance_df = pd.DataFrame(
        {
            "feature": X.columns,
            "importance_mean": importance.importances_mean,
            "importance_std": importance.importances_std
        }
    )

    importance_df = (
        importance_df
        .sort_values(
            "importance_mean",
            ascending=False
        )
    )

    print(
        importance_df.to_string(
            index=False
        )
    )

    importance_df.to_csv(
        REPORT_DIR
        / "v2_cost_permutation_importance.csv",
        index=False
    )

    # --------------------------------------------------------
    # 8. Feature group importance
    # --------------------------------------------------------

    print("\n[8] Feature group summary")

    base_importance = importance_df[
        importance_df["feature"].isin(
            BASE_FEATURES
        )
    ]["importance_mean"].sum()

    trajectory_importance = importance_df[
        importance_df["feature"].isin(
            TRAJECTORY_FEATURES
        )
    ]["importance_mean"].sum()

    print(
        "Base feature importance sum      :",
        round(base_importance, 6)
    )

    print(
        "Trajectory feature importance sum:",
        round(trajectory_importance, 6)
    )

    # --------------------------------------------------------
    # 9. Highly correlated feature pairs
    # --------------------------------------------------------

    print("\n[9] Highly correlated input features")

    numeric = df[
        BASE_FEATURES
        + TRAJECTORY_FEATURES
    ]

    corr_matrix = numeric.corr(
        method="spearman"
    )

    pairs = []

    features = corr_matrix.columns

    for i in range(len(features)):

        for j in range(i + 1, len(features)):

            value = corr_matrix.iloc[
                i,
                j
            ]

            if abs(value) >= 0.90:

                pairs.append(
                    {
                        "feature_1": features[i],
                        "feature_2": features[j],
                        "spearman_correlation": value
                    }
                )

    if pairs:

        pair_df = pd.DataFrame(
            pairs
        )

        print(
            pair_df.to_string(
                index=False
            )
        )

        pair_df.to_csv(
            REPORT_DIR
            / "v2_high_correlation_pairs.csv",
            index=False
        )

    else:

        print(
            "No feature pairs with |correlation| >= 0.90"
        )

    # --------------------------------------------------------
    # 10. Final decision
    # --------------------------------------------------------

    print("\n" + "=" * 75)
    print("V2 FEATURE AUDIT COMPLETED")
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
        "V1 was not modified."
    )

    print(
        "\nReports saved in:"
    )

    print(
        REPORT_DIR
        / "v2_cost_feature_correlations.csv"
    )

    print(
        REPORT_DIR
        / "v2_project_feature_comparison.csv"
    )

    print(
        REPORT_DIR
        / "v2_cost_permutation_importance.csv"
    )

    print("\n" + "=" * 75)


if __name__ == "__main__":
    main()