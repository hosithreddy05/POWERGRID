from pathlib import Path


# ============================================================
# SIH 25192 - PROJECT CONFIGURATION
# ============================================================

# ------------------------------------------------------------
# PROJECT DIRECTORIES
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
METRICS_DIR = REPORTS_DIR / "metrics"


# ------------------------------------------------------------
# DATA FILES
# ------------------------------------------------------------

RAW_DATA_PATH = DATA_DIR / "POWERGRID.csv"

CLEANED_DATA_PATH = (
    DATA_DIR / "POWERGRID_cleaned.csv"
)

TRAIN_DATA_PATH = (
    DATA_DIR / "train.csv"
)

TEST_DATA_PATH = (
    DATA_DIR / "test.csv"
)


# ------------------------------------------------------------
# MODEL FEATURES
# ------------------------------------------------------------

NUMERICAL_FEATURES = [
    "original_cost_cr",
    "cumulative_expenditure_cr",
    "physical_progress_pct",
    "planned_duration_months",
    "elapsed_months",
    "months_to_original_target",
    "expenditure_pct_of_original_cost",
]


CATEGORICAL_FEATURES = [
    "project_category",
]


ALL_FEATURES = (
    NUMERICAL_FEATURES
    + CATEGORICAL_FEATURES
)


# ------------------------------------------------------------
# TARGETS
# ------------------------------------------------------------

COST_TARGET = (
    "target_cost_overrun_pct"
)

SCHEDULE_TARGET = (
    "target_schedule_overrun_months"
)


TARGETS = [
    COST_TARGET,
    SCHEDULE_TARGET,
]


# ------------------------------------------------------------
# COLUMNS THAT MUST NEVER BE USED AS FEATURES
# ------------------------------------------------------------

IDENTIFIER_COLUMNS = [
    "project_code",
    "project_name",
]


TIME_COLUMNS = [
    "snapshot_date",
    "start_date",
    "original_doc",
]


LEAKAGE_COLUMNS = [
    "target_cost_overrun_pct",
    "target_schedule_overrun_months",
    "delay_flag",
    "cost_overrun_flag",
]


# ------------------------------------------------------------
# TRAIN / TEST SETTINGS
# ------------------------------------------------------------

TEST_SIZE = 0.25

RANDOM_STATE = 42


# ------------------------------------------------------------
# CROSS-VALIDATION
# ------------------------------------------------------------

CV_SPLITS = 5


# ------------------------------------------------------------
# MODEL SETTINGS
# ------------------------------------------------------------

# Number of trees for Random Forest

RANDOM_FOREST_N_ESTIMATORS = 300

# Random Forest minimum samples per leaf.
#
# We intentionally keep this configurable because
# our dataset has only 69 independent training projects.

RANDOM_FOREST_MIN_SAMPLES_LEAF = 2


# ------------------------------------------------------------
# RISK THRESHOLDS
# ------------------------------------------------------------

# IMPORTANT:
# These are INITIAL project/demo thresholds.
# They are NOT official POWERGRID thresholds.

COST_LOW_THRESHOLD = 5.0

COST_MEDIUM_THRESHOLD = 15.0


SCHEDULE_LOW_THRESHOLD = 3.0

SCHEDULE_MEDIUM_THRESHOLD = 6.0


# ------------------------------------------------------------
# RISK LEVELS
# ------------------------------------------------------------

RISK_LOW = "Low"

RISK_MEDIUM = "Medium"

RISK_HIGH = "High"


# ------------------------------------------------------------
# SCHEDULE SENTINEL
# ------------------------------------------------------------

SCHEDULE_SENTINEL = 99


# ------------------------------------------------------------
# MODEL NAMES
# ------------------------------------------------------------

MODEL_DUMMY = "Dummy"

MODEL_RIDGE = "Ridge"

MODEL_RANDOM_FOREST = "RandomForest"

MODEL_HIST_GRADIENT_BOOSTING = (
    "HistGradientBoosting"
)


MODEL_NAMES = [
    MODEL_DUMMY,
    MODEL_RIDGE,
    MODEL_RANDOM_FOREST,
    MODEL_HIST_GRADIENT_BOOSTING,
]


# ------------------------------------------------------------
# METRICS
# ------------------------------------------------------------

EVALUATION_METRICS = [
    "MAE",
    "RMSE",
    "R2",
]


# ------------------------------------------------------------
# CREATE REQUIRED DIRECTORIES
# ------------------------------------------------------------

MODELS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

REPORTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

FIGURES_DIR.mkdir(
    parents=True,
    exist_ok=True
)

METRICS_DIR.mkdir(
    parents=True,
    exist_ok=True
)