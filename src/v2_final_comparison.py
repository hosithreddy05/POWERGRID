"""
===========================================================================
       SIH 25192 - FINAL V1 vs V2 MODEL COMPARISON
===========================================================================

Purpose:
    Compare the already-evaluated V1 and V2 models.

IMPORTANT:
    - No new training
    - No test-set tuning
    - No synthetic data
    - No PDF rows
    - V1 remains untouched
    - V2 remains untouched

This script is for final model-selection documentation.
===========================================================================
"""

from pathlib import Path
import json
import pandas as pd


# =========================================================================
# PATHS
# =========================================================================

ROOT = Path(__file__).resolve().parents[1]

REPORTS = ROOT / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)


# =========================================================================
# V1 RESULTS
#
# These values come from the previously completed V1 evaluations.
# =========================================================================

V1_COST = {
    "MAE": 2.2420,
    "RMSE": 7.0698,
    "R2": -0.6836,
    "Project_MAE": 3.2043,
}

V1_SCHEDULE = None


# =========================================================================
# V2 RESULTS
#
# Read directly from the final V2 evaluation report.
# =========================================================================

V2_SUMMARY_PATH = (
    REPORTS / "v2_unseen_final_summary.json"
)


def load_v2_results():

    if not V2_SUMMARY_PATH.exists():

        raise FileNotFoundError(
            f"Missing V2 summary file:\n"
            f"{V2_SUMMARY_PATH}\n\n"
            f"Run:\n"
            f"python -m src.v2_final_test\n"
            f"first."
        )

    with open(
        V2_SUMMARY_PATH,
        "r"
    ) as f:

        data = json.load(f)

    return data


# =========================================================================
# MAIN
# =========================================================================

def main():

    print("=" * 75)
    print(
        "       SIH 25192 - FINAL V1 vs V2 MODEL COMPARISON"
    )
    print("=" * 75)

    print("\nIMPORTANT")
    print("  ✓ No new model training")
    print("  ✓ No test-set tuning")
    print("  ✓ No synthetic data")
    print("  ✓ No PDF rows")
    print("  ✓ V1 untouched")
    print("  ✓ V2 untouched")

    # =====================================================================
    # LOAD V2
    # =====================================================================

    print("\n[1] Loading V2 evaluation results...")

    v2 = load_v2_results()

    v2_cost = v2["cost_model"]
    v2_schedule = v2["schedule_model"]

    print("✓ V2 results loaded")

    # =====================================================================
    # COST COMPARISON
    # =====================================================================

    print("\n" + "=" * 75)
    print("COST MODEL COMPARISON")
    print("=" * 75)

    cost_comparison = pd.DataFrame(
        [
            {
                "Metric": "MAE (%)",
                "V1": V1_COST["MAE"],
                "V2": v2_cost["test_mae"],
                "Lower_Better": True,
            },
            {
                "Metric": "RMSE (%)",
                "V1": V1_COST["RMSE"],
                "V2": v2_cost["test_rmse"],
                "Lower_Better": True,
            },
            {
                "Metric": "R2",
                "V1": V1_COST["R2"],
                "V2": v2_cost["test_r2"],
                "Lower_Better": False,
            },
            {
                "Metric": "Project MAE (%)",
                "V1": V1_COST["Project_MAE"],
                "V2": v2_cost["project_mae"],
                "Lower_Better": True,
            },
        ]
    )

    print(
        cost_comparison[
            [
                "Metric",
                "V1",
                "V2"
            ]
        ].to_string(
            index=False
        )
    )

    # =====================================================================
    # DETERMINE COST WINNER
    # =====================================================================

    cost_wins = 0
    cost_losses = 0

    for _, row in cost_comparison.iterrows():

        if row["Lower_Better"]:

            if row["V2"] < row["V1"]:
                cost_wins += 1

            elif row["V2"] > row["V1"]:
                cost_losses += 1

        else:

            if row["V2"] > row["V1"]:
                cost_wins += 1

            elif row["V2"] < row["V1"]:
                cost_losses += 1

    if cost_wins > cost_losses:

        cost_winner = "V2"

    elif cost_losses > cost_wins:

        cost_winner = "V1"

    else:

        cost_winner = "TIE"

    print(
        "\nCost model winner:",
        cost_winner
    )

    # =====================================================================
    # SCHEDULE
    # =====================================================================

    print("\n" + "=" * 75)
    print("SCHEDULE MODEL")
    print("=" * 75)

    print(
        "V2 Schedule Model:"
    )

    print(
        "  Algorithm :",
        v2_schedule["algorithm"]
    )

    print(
        f"  MAE       : "
        f"{v2_schedule['test_mae']:.4f} months"
    )

    print(
        f"  RMSE      : "
        f"{v2_schedule['test_rmse']:.4f} months"
    )

    print(
        f"  R2        : "
        f"{v2_schedule['test_r2']:.4f}"
    )

    print(
        f"  Project MAE: "
        f"{v2_schedule['project_mae']:.4f} months"
    )

    print(
        "\nNote:"
    )

    print(
        "The current V2 schedule evaluation is the "
        "final unseen-project schedule evaluation."
    )

    # =====================================================================
    # FINAL DECISION
    # =====================================================================

    print("\n" + "=" * 75)
    print("FINAL MODEL DECISION")
    print("=" * 75)

    if cost_winner == "V2":

        final_cost = (
            "V2 Random Forest "
            "(Base + Trajectory)"
        )

    elif cost_winner == "V1":

        final_cost = (
            "V1 Cost Model"
        )

    else:

        final_cost = (
            "V2 Random Forest "
            "(Base + Trajectory)"
        )

    final_schedule = (
        "V2 Extra Trees "
        "(Base + Trajectory)"
    )

    print(
        "\nFINAL COST MODEL:"
    )

    print(
        " ",
        final_cost
    )

    print(
        "\nFINAL SCHEDULE MODEL:"
    )

    print(
        " ",
        final_schedule
    )

    # =====================================================================
    # IMPORTANT SYSTEM ARCHITECTURE DECISION
    # =====================================================================

    print("\n" + "=" * 75)
    print("FINAL SYSTEM ARCHITECTURE")
    print("=" * 75)

    print(
        """
                    PROJECT DATA
                         |
                         v
              +----------------------+
              | Trajectory Features  |
              +----------------------+
                         |
                         v
              +----------------------+
              |   COST ML MODEL      |
              |   Random Forest      |
              +----------------------+
                         |
                         v
                 Cost Overrun %
                         
              +----------------------+
              | SCHEDULE ML MODEL    |
              | Extra Trees          |
              +----------------------+
                         |
                         v
                 Schedule Delay
                         |
                         v
              +----------------------+
              |  EXPLAINABLE RISK    |
              |      ENGINE           |
              +----------------------+
                         |
                         v
                 Risk Score 0-100
                 LOW / MEDIUM / HIGH
                         |
                         v
                    DASHBOARD
        """
    )

    # =====================================================================
    # SAVE COMPARISON
    # =====================================================================

    print("\n" + "=" * 75)
    print("[2] SAVING FINAL COMPARISON")
    print("=" * 75)

    cost_path = (
        REPORTS
        / "final_v1_v2_cost_comparison.csv"
    )

    cost_comparison.to_csv(
        cost_path,
        index=False
    )

    final_summary = {

        "final_cost_model": final_cost,

        "final_schedule_model": final_schedule,

        "cost_model_selection": {
            "winner": cost_winner,
            "v1": V1_COST,
            "v2": {
                "MAE": v2_cost["test_mae"],
                "RMSE": v2_cost["test_rmse"],
                "R2": v2_cost["test_r2"],
                "Project_MAE": v2_cost["project_mae"],
            },
        },

        "schedule_model": {
            "algorithm": v2_schedule["algorithm"],
            "MAE": v2_schedule["test_mae"],
            "RMSE": v2_schedule["test_rmse"],
            "R2": v2_schedule["test_r2"],
            "Project_MAE": v2_schedule["project_mae"],
        },

        "data_policy": {
            "synthetic_data": False,
            "pdf_rows_appended": False,
            "v1_modified": False,
            "test_set_used_for_tuning": False,
        },

        "decision": (
            "Use ML models for numerical prediction "
            "and the explainable risk engine for "
            "risk classification."
        ),
    }

    summary_path = (
        REPORTS
        / "final_v1_v2_model_decision.json"
    )

    with open(
        summary_path,
        "w"
    ) as f:

        json.dump(
            final_summary,
            f,
            indent=4
        )

    print(
        "✓",
        cost_path
    )

    print(
        "✓",
        summary_path
    )

    # =====================================================================
    # END
    # =====================================================================

    print("\n" + "=" * 75)
    print(
        "FINAL V1 vs V2 MODEL COMPARISON COMPLETED"
    )
    print("=" * 75)


if __name__ == "__main__":
    main()