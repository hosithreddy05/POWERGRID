"""
POWERGRID Project Intelligence Platform
FastAPI Backend

Connects the React/Vite frontend to the existing
POWERGRID Python application and V2 ML pipeline.
"""

from typing import Any

import pandas as pd

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.application_service import (
    analyze_project,
    analyze_what_if,
    predict_new_project,
)

from src.project_service import (
    load_project_data,
    load_trajectory_data,
)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="POWERGRID Project Intelligence API",
    description=(
        "Backend API for the POWERGRID V2 ML "
        "Project Intelligence Platform"
    ),
    version="2.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "https://powergrid-gb1a.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class PredictionRequest(BaseModel):
    original_approved_cost: float = Field(
        gt=0
    )

    project_category: str

    cumulative_expenditure: float = Field(
        ge=0
    )

    physical_progress_pct: float = Field(
        ge=0,
        le=100,
    )

    planned_duration_months: float = Field(
        gt=0
    )

    elapsed_duration_months: float = Field(
        ge=0
    )

    progress_velocity: float = Field(
        default=0,
        ge=0,
    )

    expenditure_velocity: float = Field(
        default=0,
        ge=0,
    )


class WhatIfRequest(BaseModel):
    project_code: str

    physical_progress_pct: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    cumulative_expenditure: float | None = Field(
        default=None,
        ge=0,
    )

    planned_duration_months: float | None = Field(
        default=None,
        gt=0,
    )

    elapsed_duration_months: float | None = Field(
        default=None,
        ge=0,
    )

    progress_velocity: float | None = Field(
        default=None,
        ge=0,
    )

    expenditure_velocity: float | None = Field(
        default=None,
        ge=0,
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
def health_check() -> dict[str, str]:
    """
    Check whether the POWERGRID backend is running.
    """

    return {
        "status": "ok",
        "service": "POWERGRID Project Intelligence API",
        "version": "2.0.0",
    }


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root() -> dict[str, str]:
    """
    API root endpoint.
    """

    return {
        "message": "POWERGRID Project Intelligence API",
        "status": "running",
        "docs": "/docs",
        "health": "/api/health",
    }


# ============================================================
# PROJECT LIST
# ============================================================

@app.get("/api/projects")
def project_list() -> Any:
    """
    Return the latest REAL POWERGRID snapshot for every project.

    This endpoint does not run ML predictions.
    Detailed prediction is handled by:
        /api/projects/{project_code}
    """

    try:

        # Load the real cleaned POWERGRID dataset.
        project_df = load_project_data()

        # Load the real trajectory dataset.
        trajectory_df = load_trajectory_data()

        # --------------------------------------------------------
        # Latest raw snapshot for each project
        # --------------------------------------------------------

        latest_projects = (
            project_df
            .sort_values(
                ["project_code", "snapshot_date"]
            )
            .drop_duplicates(
                subset=["project_code"],
                keep="last",
            )
            .copy()
        )

        # --------------------------------------------------------
        # Latest trajectory snapshot for each project
        # --------------------------------------------------------

        latest_trajectory = (
            trajectory_df
            .sort_values(
                ["project_code", "snapshot_date"]
            )
            .drop_duplicates(
                subset=["project_code"],
                keep="last",
            )
            .copy()
        )

        # --------------------------------------------------------
        # Convert trajectory data into a lookup dictionary.
        # This avoids merging and prevents any raw fields from
        # being overwritten.
        # --------------------------------------------------------

        trajectory_lookup = {}

        for _, row in latest_trajectory.iterrows():

            code = str(
                row["project_code"]
            ).strip()

            trajectory_lookup[code] = row

        # --------------------------------------------------------
        # Build response
        # --------------------------------------------------------

        result = []

        for _, row in latest_projects.iterrows():

            project_code = str(
                row["project_code"]
            ).strip()

            project_name = str(
                row["project_name"]
            )

            trajectory = trajectory_lookup.get(
                project_code
            )

            # ----------------------------------------------------
            # Real raw snapshot values
            # ----------------------------------------------------

            def safe_value(
                value,
                default=0,
            ):
                if pd.isna(value):
                    return default
                return value

            snapshot = {
                "project_code":
                    project_code,

                "project_name":
                    project_name,

                "snapshot_date":
                    str(
                        safe_value(
                            row["snapshot_date"],
                            "",
                        )
                    ),

                "original_cost_cr":
                    float(
                        safe_value(
                            row["original_cost_cr"]
                        )
                    ),

                "cumulative_expenditure_cr":
                    float(
                        safe_value(
                            row[
                                "cumulative_expenditure_cr"
                            ]
                        )
                    ),

                "physical_progress_pct":
                    float(
                        safe_value(
                            row[
                                "physical_progress_pct"
                            ]
                        )
                    ),

                "planned_duration_months":
                    float(
                        safe_value(
                            row[
                                "planned_duration_months"
                            ]
                        )
                    ),

                "elapsed_months":
                    float(
                        safe_value(
                            row["elapsed_months"]
                        )
                    ),

                "months_to_original_target":
                    float(
                        safe_value(
                            row[
                                "months_to_original_target"
                            ]
                        )
                    ),

                "expenditure_pct_of_original_cost":
                    float(
                        safe_value(
                            row[
                                "expenditure_pct_of_original_cost"
                            ]
                        )
                    ),

                "project_category":
                    str(
                        safe_value(
                            row[
                                "project_category"
                            ],
                            "Transmission_System",
                        )
                    ),
            }

            # ----------------------------------------------------
            # Add real trajectory features
            # ----------------------------------------------------

            if trajectory is not None:

                snapshot[
                    "progress_velocity"
                ] = float(
                    safe_value(
                        trajectory[
                            "progress_velocity"
                        ]
                    )
                )

                snapshot[
                    "expenditure_velocity"
                ] = float(
                    safe_value(
                        trajectory[
                            "expenditure_velocity"
                        ]
                    )
                )

                snapshot[
                    "expenditure_progress_gap"
                ] = float(
                    safe_value(
                        trajectory[
                            "expenditure_progress_gap"
                        ]
                    )
                )

                snapshot[
                    "schedule_slippage_months"
                ] = float(
                    safe_value(
                        trajectory[
                            "schedule_slippage_months"
                        ]
                    )
                )

            else:

                snapshot[
                    "progress_velocity"
                ] = 0.0

                snapshot[
                    "expenditure_velocity"
                ] = 0.0

                snapshot[
                    "expenditure_progress_gap"
                ] = 0.0

                snapshot[
                    "schedule_slippage_months"
                ] = 0.0

            result.append(
                {
                    "project_code":
                        project_code,

                    "project_name":
                        project_name,

                    "snapshot":
                        snapshot,
                }
            )

        return result

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to load POWERGRID projects: "
                f"{exc}"
            ),
        ) from exc


# ============================================================
# ALL PROJECT ANALYSES + V2 PREDICTIONS
# ============================================================

@app.get("/api/project-analyses")
def project_analyses() -> Any:
    """
    Return the complete V2 analysis for every
    real POWERGRID project.

    This endpoint uses the same existing
    analyze_project() V2 pipeline used by
    the individual project endpoint.

    No synthetic data is created or used.
    """

    try:

        # Load the real POWERGRID project list
        project_df = load_project_data()

        # Get one project code for each real project
        project_codes = (
            project_df[
                "project_code"
            ]
            .astype(str)
            .str.strip()
            .drop_duplicates()
            .sort_values()
            .tolist()
        )

        results = []

        for project_code in project_codes:

            analysis = analyze_project(
                project_code
            )

            if analysis is not None:
                results.append(
                    analysis
                )

        return results

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to analyze POWERGRID projects: "
                f"{exc}"
            ),
        ) from exc

# ============================================================
# PROJECT DETAILS + V2 PREDICTION
# ============================================================

@app.get(
    "/api/projects/{project_code}"
)
def project_details(
    project_code: str,
) -> Any:
    """
    Return complete V2 analysis for one POWERGRID project.

    This endpoint performs the actual model prediction.
    """

    try:

        result = analyze_project(
            project_code
        )

        if result is None:

            raise HTTPException(
                status_code=404,
                detail=(
                    f"Project '{project_code}' "
                    "not found"
                ),
            )

        return result

    except HTTPException:

        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Unable to analyze project "
                f"'{project_code}': {exc}"
            ),
        ) from exc


# ============================================================
# NEW PROJECT PREDICTION
# ============================================================

@app.post("/api/predict")
def predict(
    request: PredictionRequest,
) -> Any:
    """
    Run the existing POWERGRID V2 prediction pipeline
    for a newly entered project.
    """

    project_data = {
        "original_approved_cost":
            request.original_approved_cost,

        "project_category":
            request.project_category,

        "cumulative_expenditure":
            request.cumulative_expenditure,

        "physical_progress_pct":
            request.physical_progress_pct,

        "planned_duration_months":
            request.planned_duration_months,

        "elapsed_duration_months":
            request.elapsed_duration_months,

        "progress_velocity":
            request.progress_velocity,

        "expenditure_velocity":
            request.expenditure_velocity,
    }

    try:

        result = predict_new_project(
            project_data
        )

        return result

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Prediction failed: "
                f"{exc}"
            ),
        ) from exc


# ============================================================
# WHAT-IF ANALYSIS
# ============================================================

@app.post("/api/what-if")
def what_if(
    request: WhatIfRequest,
) -> Any:
    """
    Run the existing POWERGRID V2 What-If analysis.

    API field names are converted to the internal
    V2 field names expected by the analysis engine.
    """

    changes: dict[str, float] = {}

    # --------------------------------------------------------
    # Physical progress
    # --------------------------------------------------------

    if (
        request.physical_progress_pct
        is not None
    ):

        changes[
            "physical_progress_pct"
        ] = (
            request.physical_progress_pct
        )

    # --------------------------------------------------------
    # Cumulative expenditure
    # --------------------------------------------------------

    if (
        request.cumulative_expenditure
        is not None
    ):

        changes[
            "cumulative_expenditure_cr"
        ] = (
            request.cumulative_expenditure
        )

    # --------------------------------------------------------
    # Planned duration
    # --------------------------------------------------------

    if (
        request.planned_duration_months
        is not None
    ):

        changes[
            "planned_duration_months"
        ] = (
            request.planned_duration_months
        )

    # --------------------------------------------------------
    # Elapsed duration
    # --------------------------------------------------------

    if (
        request.elapsed_duration_months
        is not None
    ):

        changes[
            "elapsed_months"
        ] = (
            request.elapsed_duration_months
        )

    # --------------------------------------------------------
    # Progress velocity
    # --------------------------------------------------------

    if (
        request.progress_velocity
        is not None
    ):

        changes[
            "progress_velocity"
        ] = (
            request.progress_velocity
        )

    # --------------------------------------------------------
    # Expenditure velocity
    # --------------------------------------------------------

    if (
        request.expenditure_velocity
        is not None
    ):

        changes[
            "expenditure_velocity"
        ] = (
            request.expenditure_velocity
        )

    # --------------------------------------------------------
    # Run V2 What-If analysis
    # --------------------------------------------------------

    try:

        result = analyze_what_if(
            request.project_code,
            changes,
        )

        return result

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail=(
                f"What-If analysis failed: "
                f"{exc}"
            ),
        ) from exc