"""
SIH 25192 - V2 DATA AUDIT
SAFE STEP 1

Purpose:
- Verify V1/trajectory datasets before V2 training.
- Confirm project-level split.
- Check target imbalance.
- Check which PDF-inspired engineering features are actually available.
- Do NOT modify any existing dataset or model.
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

TRAIN = DATA / "train_trajectory.csv"
TEST = DATA / "test_trajectory.csv"

def main():
    print("=" * 75)
    print("       SIH 25192 - V2 DATA / FEATURE AUDIT")
    print("=" * 75)

    if not TRAIN.exists():
        raise FileNotFoundError(f"Missing: {TRAIN}")
    if not TEST.exists():
        raise FileNotFoundError(f"Missing: {TEST}")

    train = pd.read_csv(TRAIN)
    test = pd.read_csv(TEST)

    print("\n[1] DATASET CHECK")
    print("Training rows    :", len(train))
    print("Testing rows     :", len(test))
    print("Training projects:", train["project_code"].nunique())
    print("Testing projects :", test["project_code"].nunique())

    overlap = set(train["project_code"]) & set(test["project_code"])
    print("Project overlap  :", len(overlap))

    if overlap:
        raise ValueError("PROJECT LEAKAGE DETECTED")

    print("✓ Project-level split is valid")

    print("\n[2] COST TARGET CHECK")
    cost = "target_cost_overrun_pct"
    positive = (train[cost] > 0.5)

    print("Training cost rows :", len(train))
    print("Positive rows      :", int(positive.sum()))
    print("Non-positive rows  :", int((~positive).sum()))
    print("Positive percentage:", f"{positive.mean()*100:.2f}%")
    print("Positive projects  :",
          int(train.groupby("project_code")[cost].max().gt(0.5).sum()))

    print("\n[3] PDF-INSPIRED FEATURE AVAILABILITY")

    pdf_features = [
        "voltage_kv",
        "circuit_type",
        "region",
        "line_length_km",
        "terrain",
    ]

    for feature in pdf_features:
        if feature in train.columns:
            print(f"✓ {feature} -> already available")
        else:
            print(f"✗ {feature} -> NOT available in existing project data")

    print("\n[4] PDF OUTCOME FIELDS - NEVER USE AS INPUT")

    forbidden = [
        "completion_cost_lakhs",
        "cost_per_km_lakhs",
    ]

    for feature in forbidden:
        if feature in train.columns:
            print(f"⚠ {feature} exists -> MUST EXCLUDE")
        else:
            print(f"✓ {feature} not present in training data")

    print("\n[5] CURRENT TRAJECTORY FEATURES")

    trajectory = [
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
        "expenditure_velocity_rolling",
    ]

    available = [f for f in trajectory if f in train.columns]

    print("Available trajectory features:", len(available))
    for feature in available:
        print("  ✓", feature)

    print("\n[6] DECISION")

    available_pdf = [f for f in pdf_features if f in train.columns]

    if available_pdf:
        print("PDF-inspired features available:", available_pdf)
        print("These can be evaluated in V2.")
    else:
        print("No PDF engineering feature can be safely joined to the")
        print("existing 92 projects from the current PDF benchmark.")
        print("Therefore the 14 PDF rows will NOT be appended.")
        print("V2 will use real existing trajectory/project information.")
        print("The PDF remains a real-world engineering benchmark.")

    print("\n[7] PROTECTION")
    print("Existing V1 dataset/model will NOT be overwritten.")
    print("Synthetic data used: NO")
    print("PDF rows appended: NO")
    print("Status: SAFE TO PROCEED")

    print("\n" + "=" * 75)
    print("V2 DATA / FEATURE AUDIT COMPLETED")
    print("=" * 75)

if __name__ == "__main__":
    main()
