import pandas as pd

from pathlib import Path


# ============================================================
# SIH 25192 - PROJECT DATA SERVICE V2
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    ROOT
    / "data"
    / "POWERGRID_cleaned.csv"
)

TRAJECTORY_DATA_PATH = (
    ROOT
    / "data"
    / "POWERGRID_trajectory.csv"
)


# ============================================================
# LOAD CLEANED PROJECT DATA
# ============================================================

def load_project_data():

    df = pd.read_csv(
        DATA_PATH
    )

    df["snapshot_date"] = pd.to_datetime(
        df["snapshot_date"],
        errors="coerce"
    )

    df["project_code"] = (
        df["project_code"]
        .astype(str)
        .str.strip()
    )

    return df


# ============================================================
# LOAD TRAJECTORY DATA
# ============================================================

def load_trajectory_data():

    df = pd.read_csv(
        TRAJECTORY_DATA_PATH
    )

    df["snapshot_date"] = pd.to_datetime(
        df["snapshot_date"],
        errors="coerce"
    )

    df["project_code"] = (
        df["project_code"]
        .astype(str)
        .str.strip()
    )

    return df


# ============================================================
# GET PROJECT LIST
# ============================================================

def get_project_list():

    df = load_project_data()

    df = df.sort_values(
        [
            "project_code",
            "snapshot_date"
        ]
    )

    projects = (
        df[
            [
                "project_code",
                "project_name"
            ]
        ]
        .drop_duplicates(
            subset=["project_code"],
            keep="last"
        )
        .sort_values(
            "project_code"
        )
        .reset_index(
            drop=True
        )
    )

    return projects


# ============================================================
# GET ALL PROJECT SNAPSHOTS
# ============================================================

def get_project_snapshots(
    project_code
):

    df = load_project_data()

    project = df[
        df["project_code"]
        == str(project_code)
    ].copy()

    if project.empty:

        raise ValueError(
            f"Project not found: {project_code}"
        )

    project = project.sort_values(
        "snapshot_date"
    ).reset_index(
        drop=True
    )

    return project


# ============================================================
# GET ALL TRAJECTORY SNAPSHOTS
# ============================================================

def get_project_trajectory(
    project_code
):

    df = load_trajectory_data()

    project = df[
        df["project_code"]
        == str(project_code)
    ].copy()

    if project.empty:

        raise ValueError(
            f"Trajectory data not found for project: "
            f"{project_code}"
        )

    project = project.sort_values(
        "snapshot_date"
    ).reset_index(
        drop=True
    )

    return project


# ============================================================
# GET LATEST RAW SNAPSHOT
# ============================================================

def get_latest_snapshot(
    project_code
):

    project = get_project_snapshots(
        project_code
    )

    latest = project.iloc[-1]

    return latest.to_dict()


# ============================================================
# GET LATEST TRAJECTORY SNAPSHOT
# ============================================================

def get_latest_trajectory_snapshot(
    project_code
):

    project = get_project_trajectory(
        project_code
    )

    latest = project.iloc[-1]

    return latest.to_dict()


# ============================================================
# GET PROJECT NAME
# ============================================================

def get_project_name(
    project_code
):

    snapshot = get_latest_snapshot(
        project_code
    )

    return str(
        snapshot["project_name"]
    )


# ============================================================
# CONVERT TRAJECTORY SNAPSHOT
# TO V2 MODEL INPUT
# ============================================================

def snapshot_to_prediction_input(
    snapshot
):

    """
    Convert the latest engineered trajectory
    snapshot into the exact 12-feature structure
    expected by the frozen V2 models.
    """

    return {

        # ----------------------------------------------------
        # BASE FEATURES
        # ----------------------------------------------------

        "original_cost_cr":
            float(
                snapshot[
                    "original_cost_cr"
                ]
            ),

        "cumulative_expenditure_cr":
            float(
                snapshot[
                    "cumulative_expenditure_cr"
                ]
            ),

        "physical_progress_pct":
            float(
                snapshot[
                    "physical_progress_pct"
                ]
            ),

        "planned_duration_months":
            float(
                snapshot[
                    "planned_duration_months"
                ]
            ),

        "elapsed_months":
            float(
                snapshot[
                    "elapsed_months"
                ]
            ),

        "months_to_original_target":
            float(
                snapshot[
                    "months_to_original_target"
                ]
            ),

        "expenditure_pct_of_original_cost":
            float(
                snapshot[
                    "expenditure_pct_of_original_cost"
                ]
            ),

        "project_category":
            str(
                snapshot[
                    "project_category"
                ]
            ),

        # ----------------------------------------------------
        # TRAJECTORY FEATURES
        # ----------------------------------------------------

        "progress_velocity":
            float(
                snapshot[
                    "progress_velocity"
                ]
            ),

        "expenditure_velocity":
            float(
                snapshot[
                    "expenditure_velocity"
                ]
            ),

        "expenditure_progress_gap":
            float(
                snapshot[
                    "expenditure_progress_gap"
                ]
            ),

        "schedule_slippage_months":
            float(
                snapshot[
                    "schedule_slippage_months"
                ]
            ),
    }


# ============================================================
# GET COMPLETE PROJECT INFORMATION
# ============================================================

def get_project_information(
    project_code
):

    # --------------------------------------------------------
    # Raw latest snapshot
    # --------------------------------------------------------

    raw_snapshot = get_latest_snapshot(
        project_code
    )

    # --------------------------------------------------------
    # Latest trajectory snapshot
    # --------------------------------------------------------

    trajectory_snapshot = (
        get_latest_trajectory_snapshot(
            project_code
        )
    )

    # --------------------------------------------------------
    # Model input
    # --------------------------------------------------------

    model_input = (
        snapshot_to_prediction_input(
            trajectory_snapshot
        )
    )

    return {

        "snapshot":
            raw_snapshot,

        "trajectory_snapshot":
            trajectory_snapshot,

        "model_input":
            model_input
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 75)
    print(
        "       SIH 25192 - V2 PROJECT SERVICE TEST"
    )
    print("=" * 75)

    # --------------------------------------------------------
    # Load projects
    # --------------------------------------------------------

    print(
        "\n[1] Loading projects..."
    )

    projects = get_project_list()

    print(
        "Projects found:",
        len(projects)
    )

    if len(projects) == 92:

        print(
            "✓ Project count matches "
            "validated dataset: 92"
        )

    else:

        print(
            "⚠ WARNING:"
        )

        print(
            f"Expected 92 projects "
            f"but found {len(projects)}"
        )

    # --------------------------------------------------------
    # First five projects
    # --------------------------------------------------------

    print(
        "\n[2] First 5 projects:"
    )

    print(
        projects.head(5).to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # Test known real project
    # --------------------------------------------------------

    project_code = "N18000264"

    print(
        f"\n[3] Loading project: "
        f"{project_code}"
    )

    information = (
        get_project_information(
            project_code
        )
    )

    snapshot = information[
        "snapshot"
    ]

    trajectory_snapshot = (
        information[
            "trajectory_snapshot"
        ]
    )

    model_input = information[
        "model_input"
    ]

    # --------------------------------------------------------
    # Raw snapshot
    # --------------------------------------------------------

    print(
        "\nLatest raw snapshot:"
    )

    print(
        "Project:",
        snapshot[
            "project_name"
        ]
    )

    print(
        "Snapshot date:",
        snapshot[
            "snapshot_date"
        ]
    )

    print(
        "Physical progress:",
        snapshot[
            "physical_progress_pct"
        ]
    )

    print(
        "Expenditure:",
        snapshot[
            "cumulative_expenditure_cr"
        ]
    )

    # --------------------------------------------------------
    # Trajectory values
    # --------------------------------------------------------

    print(
        "\nLatest trajectory features:"
    )

    trajectory_features = [

        "progress_velocity",

        "expenditure_velocity",

        "expenditure_progress_gap",

        "schedule_slippage_months",
    ]

    for feature in trajectory_features:

        print(
            f"{feature}: "
            f"{trajectory_snapshot[feature]}"
        )

    # --------------------------------------------------------
    # Model input
    # --------------------------------------------------------

    print(
        "\n[4] FINAL V2 MODEL INPUT:"
    )

    for key, value in model_input.items():

        print(
            f"{key}: {value}"
        )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    print(
        "\n[5] Validation:"
    )

    expected_features = 12

    if len(model_input) == expected_features:

        print(
            "✓ 12 V2 features available"
        )

    else:

        print(
            "✗ Incorrect feature count:",
            len(model_input)
        )

    unique_codes = (
        projects[
            "project_code"
        ].nunique()
    )

    print(
        "Unique project codes:",
        unique_codes
    )

    if (
        len(projects) == 92
        and unique_codes == 92
        and len(model_input) == 12
    ):

        print(
            "✓ V2 PROJECT SERVICE VALIDATED"
        )

    else:

        print(
            "⚠ V2 PROJECT SERVICE NEEDS REVIEW"
        )

    print(
        "\n" + "=" * 75
    )

    print(
        "V2 PROJECT SERVICE TEST COMPLETED"
    )

    print("=" * 75)