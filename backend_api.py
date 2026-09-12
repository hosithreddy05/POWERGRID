"""
POWERGRID Project Intelligence Platform
FastAPI Backend

Connects the React/Vite frontend to the existing
POWERGRID Python application and V2 ML pipeline.
"""

from typing import Any
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.application_service import (
    get_projects,
    analyze_project,
    analyze_what_if,
    predict_new_project,
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



# ============================================================
# PROJECT ANALYSIS
# ============================================================

@app.get("/api/projects/{project_code}")
def project_analysis(
    project_code: str,
) -> Any:
    """
    Return detailed project intelligence and
    V2 prediction for a selected project.
    """

    try:

        result = analyze_project(
            project_code
        )

        return result

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

    The API accepts frontend-friendly field names.
    application_service.py converts them to the exact
    field names required by the V2 Python engine.
    """

    project_data = {
        "original_approved_cost": (
            request.original_approved_cost
        ),

        "project_category": (
            request.project_category
        ),

        "cumulative_expenditure": (
            request.cumulative_expenditure
        ),

        "physical_progress_pct": (
            request.physical_progress_pct
        ),

        "planned_duration_months": (
            request.planned_duration_months
        ),

        "elapsed_duration_months": (
            request.elapsed_duration_months
        ),

        "progress_velocity": (
            request.progress_velocity
        ),

        "expenditure_velocity": (
            request.expenditure_velocity
        ),
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
    Run the existing POWERGRID What-If analysis engine.

    The frontend uses friendly API field names while the
    underlying Python V2 engine uses its internal field names.

    API field                         V2 field
    ---------------------------------------------------------
    cumulative_expenditure       ->  cumulative_expenditure_cr
    elapsed_duration_months      ->  elapsed_months
    physical_progress_pct        ->  physical_progress_pct
    planned_duration_months      ->  planned_duration_months
    progress_velocity            ->  progress_velocity
    expenditure_velocity         ->  expenditure_velocity
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
    #
    # API:
    #     cumulative_expenditure
    #
    # V2:
    #     cumulative_expenditure_cr
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
    #
    # API:
    #     elapsed_duration_months
    #
    # V2:
    #     elapsed_months
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
    # Run Python What-If analysis
    # --------------------------------------------------------

    try:

        result = analyze_what_if(
            request.project_code,
            changes,
        )

        return {
            "project_code":
                request.project_code,

            "baseline":
                result["baseline"],

            "scenario":
                result["scenario"],
        }

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail=(
                f"What-If analysis failed: "
                f"{exc}"
            ),
        ) from exc
# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class PredictionRequest(BaseModel):
    original_approved_cost: float = Field(gt=0)

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
    Return a lightweight list of all POWERGRID projects.

    Detailed V2 prediction and trajectory analysis is handled
    by /api/projects/{project_code}.
    """

    try:
        projects = get_projects()

        if hasattr(projects, "to_dict"):
            records = projects.to_dict(
                orient="records"
            )
        else:
            records = projects

        result = []

        for record in records:

            project_code = str(
                record.get(
                    "project_code",
                    "",
                )
            ).strip()

            if not project_code:
                continue

            project_name = record.get(
                "project_name",
                project_code,
            )

            project_category = record.get(
                "project_category",
                "Transmission_System",
            )

            result.append(
                {
                    "project_code": project_code,
                    "project_name": project_name,
                    "snapshot": {
                        "project_code": project_code,
                        "project_name": project_name,
                        "original_cost_cr": record.get(
                            "original_cost_cr",
                            record.get(
                                "original_approved_cost",
                                0,
                            ),
                        ),
                        "cumulative_expenditure_cr": record.get(
                            "cumulative_expenditure_cr",
                            record.get(
                                "cumulative_expenditure",
                                0,
                            ),
                        ),
                        "physical_progress_pct": record.get(
                            "physical_progress_pct",
                            0,
                        ),
                        "planned_duration_months": record.get(
                            "planned_duration_months",
                            0,
                        ),
                        "elapsed_months": record.get(
                            "elapsed_months",
                            record.get(
                                "elapsed_duration_months",
                                0,
                            ),
                        ),
                        "project_category": project_category,
                    },
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
# PROJECT DETAILS
# ============================================================

@app.get(
    "/api/projects/{project_code}"
)
def project_details(
    project_code: str,
) -> Any:
    """
    Return complete analysis for one POWERGRID project.
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
        "original_approved_cost": (
            request.original_approved_cost
        ),

        "project_category": (
            request.project_category
        ),

        "cumulative_expenditure": (
            request.cumulative_expenditure
        ),

        "physical_progress_pct": (
            request.physical_progress_pct
        ),

        "planned_duration_months": (
            request.planned_duration_months
        ),

        "elapsed_duration_months": (
            request.elapsed_duration_months
        ),

        "progress_velocity": (
            request.progress_velocity
        ),

        "expenditure_velocity": (
            request.expenditure_velocity
        ),
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
                f"Prediction failed: {exc}"
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
    Run the existing POWERGRID What-If analysis engine.
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
            "cumulative_expenditure"
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
            "elapsed_duration_months"
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
    # Run analysis
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
