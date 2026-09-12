import type {
  DerivedFeatures,
  PowerGridProject,
  PredictionResult,
  WhatIfChanges,
  WhatIfComparison,
  RiskLevel,
} from '../types';

// ============================================================
// API BASE URL
// ============================================================

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ??
  'http://127.0.0.1:8000/api';

// ============================================================
// BACKEND TYPES
// ============================================================

interface BackendSnapshot {
  project_code?: string;
  project_name?: string;
  snapshot_date?: string;
  start_date?: string;

  original_doc?: string;

  original_cost_cr?: number;
  cumulative_expenditure_cr?: number;

  physical_progress_pct?: number;

  planned_duration_months?: number;
  elapsed_months?: number;

  months_to_original_target?: number;

  expenditure_pct_of_original_cost?: number;

  project_category?: string;

  target_cost_overrun_pct?: number;
  target_schedule_overrun_months?: number | null;

  delay_flag?: number;
  cost_overrun_flag?: number;

  progress_change?: number;
  expenditure_change_cr?: number;
  expenditure_pct_change?: number;
  elapsed_month_change?: number;

  progress_velocity?: number;
  expenditure_velocity?: number;

  expenditure_progress_gap?: number;

  cost_per_progress_pct?: number;

  schedule_slippage_months?: number;
  schedule_pressure_ratio?: number;

  budget_consumption_ratio?: number;
  progress_time_ratio?: number;
  progress_expenditure_ratio?: number;

  project_age_months?: number;

  progress_change_3?: number;
  expenditure_change_3?: number;

  progress_velocity_rolling?: number;
  expenditure_velocity_rolling?: number;
}

interface BackendPrediction {
  cost_prediction_pct?: number;

  schedule_prediction_months?: number;

  cost_risk_score?: number;

  cost_risk_level?: string;

  cost_risk_reasons?: string[];

  cost_risk_warnings?: string[];

  expenditure_pct?: number;

  physical_progress_pct?: number;

  expenditure_progress_gap?: number;

  schedule_slippage_months?: number;

  schedule_pressure_ratio?: number;
}

interface BackendProjectAnalysis {
  project_code?: string;

  project_name?: string;

  snapshot?: BackendSnapshot;

  trajectory_snapshot?: BackendSnapshot;

  model_input?: BackendSnapshot;

  prediction?: BackendPrediction;
}

// Lightweight response from GET /projects
interface BackendProjectListItem {
  project_code?: string;
  project_name?: string;
  snapshot?: BackendSnapshot;
}

// ============================================================
// BACKEND WHAT-IF TYPES
// ============================================================

interface BackendWhatIfResult {
  scenario?: BackendSnapshot;

  prediction?: BackendPrediction;
}

interface BackendWhatIfResponse {
  project_code: string;

  baseline: BackendWhatIfResult;

  scenario: BackendWhatIfResult;
}

// ============================================================
// API FETCH HELPER
// ============================================================

async function apiFetch<T>(
  endpoint: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    {
      ...options,

      headers: {
        'Content-Type': 'application/json',

        ...(options?.headers ?? {}),
      },
    },
  );

  if (!response.ok) {
    let message =
      `API request failed: ${response.status}`;

    try {
      const error =
        await response.json();

      if (
        error &&
        typeof error.detail === 'string'
      ) {
        message = error.detail;
      }
    } catch {
      // Keep default message.
    }

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

// ============================================================
// HEALTH
// ============================================================

export async function checkApiHealth(): Promise<boolean> {
  try {
    const result =
      await apiFetch<{
        status: string;
      }>('/health');

    return result.status === 'ok';
  } catch {
    return false;
  }
}

// ============================================================
// PROJECT LIST
// ============================================================

/**
 * Lightweight portfolio project list.
 *
 * IMPORTANT:
 * GET /projects intentionally does NOT return predictions.
 * Detailed V2 analysis is fetched through:
 *
 * GET /projects/{project_code}
 */
export async function fetchProjectList(): Promise<
  BackendProjectListItem[]
> {
  return apiFetch<BackendProjectListItem[]>(
    '/projects',
  );
}

/**
 * Backwards-compatible alias.
 *
 * Some existing screens may still call fetchProjectAnalyses().
 * The endpoint is now lightweight, so callers should not expect
 * prediction data from these records.
 */
export async function fetchProjectAnalyses(): Promise<
  BackendProjectListItem[]
> {
  return fetchProjectList();
}

// ============================================================
// CATEGORY NORMALIZATION
// ============================================================

function normalizeCategory(
  value?: string,
): PowerGridProject['project_category'] {
  const category =
    String(value ?? '').toLowerCase();

  if (category.includes('substation')) {
    return 'Substation_Grid_Equipment';
  }

  if (category.includes('rural')) {
    return 'Rural_Electrification';
  }

  if (
    category.includes('renewable') ||
    category.includes('solar') ||
    category.includes('wind')
  ) {
    return 'Renewable_Integration';
  }

  if (category.includes('hvdc')) {
    return 'HVDC_Interconnector';
  }

  if (category.includes('modern')) {
    return 'Grid_Modernization';
  }

  return 'Transmission_System';
}

// ============================================================
// REGION INFERENCE
// ============================================================

function inferRegion(
  projectName: string,
): string {
  const regions = [
    'Gujarat',
    'Rajasthan',
    'Karnataka',
    'Maharashtra',
    'Tamil Nadu',
    'Andhra Pradesh',
    'Telangana',
    'Kerala',
    'Odisha',
    'Jharkhand',
    'Bihar',
    'Assam',
    'Arunachal Pradesh',
    'Jammu',
    'Kashmir',
    'Ladakh',
    'Punjab',
    'Haryana',
    'Uttar Pradesh',
    'Madhya Pradesh',
    'West Bengal',
  ];

  const lowerName =
    projectName.toLowerCase();

  for (const region of regions) {
    if (
      lowerName.includes(
        region.toLowerCase(),
      )
    ) {
      return region;
    }
  }

  return 'India';
}

// ============================================================
// SAFE NUMBER
// ============================================================

function numberOrZero(
  value?: number,
): number {
  return Number.isFinite(value)
    ? Number(value)
    : 0;
}

// ============================================================
// DERIVED FEATURES
// ============================================================

function createDerivedFeatures(
  prediction?: BackendPrediction,
  snapshot?: BackendSnapshot,
): DerivedFeatures {
  const expenditurePct =
    numberOrZero(
      prediction?.expenditure_pct ??
      snapshot?.expenditure_pct_of_original_cost,
    );

  const physicalProgress =
    numberOrZero(
      prediction?.physical_progress_pct ??
      snapshot?.physical_progress_pct,
    );

  const gap =
    numberOrZero(
      prediction?.expenditure_progress_gap ??
      snapshot?.expenditure_progress_gap,
    );

  const planned =
    numberOrZero(
      snapshot?.planned_duration_months,
    );

  const elapsed =
    numberOrZero(
      snapshot?.elapsed_months,
    );

  const schedulePressure =
    numberOrZero(
      prediction?.schedule_pressure_ratio ??
      snapshot?.schedule_pressure_ratio,
    );

  const monthsToTarget =
    numberOrZero(
      snapshot?.months_to_original_target,
    );

  const expenditure =
    numberOrZero(
      snapshot?.cumulative_expenditure_cr,
    );

  const originalCost =
    numberOrZero(
      snapshot?.original_cost_cr,
    );

  const progressVelocity =
    numberOrZero(
      snapshot?.progress_velocity,
    );

  const expenditureVelocity =
    numberOrZero(
      snapshot?.expenditure_velocity,
    );

  const costBurnRate =
    originalCost > 0
      ? expenditure / originalCost
      : 0;

  const expectedCost =
    physicalProgress > 0
      ? expenditure *
        (100 / physicalProgress)
      : expenditure;

  const scheduleElapsedPct =
    planned > 0
      ? (elapsed / planned) * 100
      : 0;

  const progressVelocityRatio =
    planned > 0
      ? progressVelocity /
        (100 / planned)
      : 0;

  const expenditureVelocityRatio =
    originalCost > 0 &&
    planned > 0
      ? expenditureVelocity /
        (originalCost / planned)
      : 0;

  return {
    expenditure_pct:
      expenditurePct,

    physical_progress_pct:
      physicalProgress,

    expenditure_progress_gap:
      gap,

    schedule_elapsed_pct:
      scheduleElapsedPct,

    schedule_pressure:
      schedulePressure,

    months_to_original_target:
      monthsToTarget,

    cost_burn_rate:
      costBurnRate,

    expected_cost_at_completion:
      expectedCost,

    progress_velocity_ratio:
      progressVelocityRatio,

    expenditure_velocity_ratio:
      expenditureVelocityRatio,
  };
}

// ============================================================
// RISK LEVEL
// ============================================================

function normalizeRiskLevel(
  value?: string,
): RiskLevel {
  const level =
    String(value ?? '')
      .toUpperCase();

  if (level === 'HIGH') {
    return 'HIGH';
  }

  if (level === 'MEDIUM') {
    return 'MEDIUM';
  }

  return 'LOW';
}

// ============================================================
// SCHEDULE RISK
// ============================================================

function getScheduleRiskLevel(
  schedule: number,
): RiskLevel {
  if (schedule >= 12) {
    return 'HIGH';
  }

  if (schedule >= 3) {
    return 'MEDIUM';
  }

  return 'LOW';
}

// ============================================================
// CONVERT BACKEND PREDICTION
// ============================================================

function convertPrediction(
  prediction?: BackendPrediction,
  snapshot?: BackendSnapshot,
): PredictionResult {
  const cost =
    numberOrZero(
      prediction?.cost_prediction_pct,
    );

  const schedule =
    numberOrZero(
      prediction?.schedule_prediction_months,
    );

  const riskScore =
    numberOrZero(
      prediction?.cost_risk_score,
    );

  const riskLevel =
    normalizeRiskLevel(
      prediction?.cost_risk_level,
    );

  const scheduleRisk =
    getScheduleRiskLevel(
      schedule,
    );

  return {
    cost_prediction_pct:
      cost,

    schedule_prediction_months:
      schedule,

    risk_score:
      riskScore,

    cost_risk_level:
      riskLevel,

    schedule_risk_level:
      scheduleRisk,

    overall_risk_level:
      riskLevel,

    derived_features:
      createDerivedFeatures(
        prediction,
        snapshot,
      ),

    supporting_indicators: [],

    model_inputs_table: [],

    timestamp:
      new Date().toISOString(),
  };
}

// ============================================================
// CONVERT PROJECT
// ============================================================

function convertProject(
  item:
    BackendProjectAnalysis |
    BackendProjectListItem,
): PowerGridProject {
  const snapshot =
    item.snapshot ??
    ('trajectory_snapshot' in item
      ? item.trajectory_snapshot
      : undefined) ??
    ('model_input' in item
      ? item.model_input
      : undefined) ??
    {};

  const projectCode =
    item.project_code ??
    snapshot.project_code ??
    '';

  const projectName =
    item.project_name ??
    snapshot.project_name ??
    projectCode;

  const originalCost =
    numberOrZero(
      snapshot.original_cost_cr,
    );

  const expenditure =
    numberOrZero(
      snapshot.cumulative_expenditure_cr,
    );

  const physicalProgress =
    numberOrZero(
      snapshot.physical_progress_pct,
    );

  const plannedDuration =
    numberOrZero(
      snapshot.planned_duration_months,
    );

  const elapsedMonths =
    numberOrZero(
      snapshot.elapsed_months,
    );

  const progressVelocity =
    numberOrZero(
      snapshot.progress_velocity,
    );

  const expenditureVelocity =
    numberOrZero(
      snapshot.expenditure_velocity,
    );

  return {
    project_code:
      projectCode,

    project_name:
      projectName,

    project_category:
      normalizeCategory(
        snapshot.project_category,
      ),

    region:
      inferRegion(projectName),

    original_approved_cost:
      originalCost,

    cumulative_expenditure:
      expenditure,

    physical_progress_pct:
      physicalProgress,

    planned_duration_months:
      plannedDuration,

    elapsed_duration_months:
      elapsedMonths,

    progress_velocity:
      progressVelocity,

    expenditure_velocity:
      expenditureVelocity,

    latest_snapshot_date:
      snapshot.snapshot_date ??
      '',

    is_training_cost:
      false,

    is_training_schedule:
      false,

    is_unseen_test:
      false,

    snapshots: [],
  };
}

// ============================================================
// FETCH PROJECTS
// ============================================================

/**
 * Fetch all 92 projects using the fast lightweight endpoint.
 *
 * No predictions are expected here.
 */
export async function fetchProjects(): Promise<
  PowerGridProject[]
> {
  const projects =
    await fetchProjectList();

  return projects.map(
    convertProject,
  );
}

// ============================================================
// FETCH ONE PROJECT
// ============================================================

/**
 * Fetch one project with complete V2 analysis.
 *
 * This endpoint contains:
 * - project snapshot
 * - prediction
 * - risk score
 * - risk level
 * - derived features
 */
export async function fetchProject(
  projectCode: string,
): Promise<{
  project: PowerGridProject;
  prediction: PredictionResult;
  raw: BackendProjectAnalysis;
}> {
  const result =
    await apiFetch<BackendProjectAnalysis>(
      `/projects/${encodeURIComponent(
        projectCode,
      )}`,
    );

  const project =
    convertProject(result);

  const prediction =
    convertPrediction(
      result.prediction,
      result.snapshot ??
        result.trajectory_snapshot ??
        result.model_input,
    );

  return {
    project,
    prediction,
    raw: result,
  };
}

// ============================================================
// NEW PROJECT PREDICTION
// ============================================================

export async function apiPredictNewProject(
  input: {
    original_approved_cost: number;
    project_category: string;
    cumulative_expenditure: number;
    physical_progress_pct: number;
    planned_duration_months: number;
    elapsed_duration_months: number;
    progress_velocity: number;
    expenditure_velocity: number;
  },
): Promise<PredictionResult> {
  const result =
    await apiFetch<{
      input?: BackendSnapshot;
      prediction?: BackendPrediction;
    }>('/predict', {
      method: 'POST',

      body: JSON.stringify(input),
    });

  return convertPrediction(
    result.prediction,
    result.input,
  );
}

// ============================================================
// WHAT-IF ANALYSIS
// ============================================================

export async function apiAnalyzeWhatIf(
  projectCode: string,
  changes: WhatIfChanges,
): Promise<WhatIfComparison> {
  const result =
    await apiFetch<BackendWhatIfResponse>(
      '/what-if',
      {
        method: 'POST',

        body: JSON.stringify({
          project_code: projectCode,
          ...changes,
        }),
      },
    );

  const baseline =
    result.baseline;

  const scenario =
    result.scenario;

  const baselineSnapshot =
    baseline?.scenario;

  const scenarioSnapshot =
    scenario?.scenario;

  // ----------------------------------------------------------
  // BASELINE PREDICTION
  // ----------------------------------------------------------

  const baselinePrediction =
    convertPrediction(
      baseline?.prediction,
      baselineSnapshot,
    );

  // ----------------------------------------------------------
  // SCENARIO PREDICTION
  // ----------------------------------------------------------

  const scenarioPrediction =
    convertPrediction(
      scenario?.prediction,
      scenarioSnapshot,
    );

  // ----------------------------------------------------------
  // CALCULATE DIFFERENCES
  // ----------------------------------------------------------

  const costDiff =
    Number(
      (
        scenarioPrediction.cost_prediction_pct -
        baselinePrediction.cost_prediction_pct
      ).toFixed(2),
    );

  const scheduleDiff =
    Number(
      (
        scenarioPrediction.schedule_prediction_months -
        baselinePrediction.schedule_prediction_months
      ).toFixed(1),
    );

  const riskDiff =
    scenarioPrediction.risk_score -
    baselinePrediction.risk_score;

  // ----------------------------------------------------------
  // BASELINE INPUTS
  // ----------------------------------------------------------

  const baselineInputs = {
    project_code:
      result.project_code ??
      projectCode,

    project_name:
      `POWERGRID Project ${
        result.project_code ??
        projectCode
      }`,

    project_category:
      normalizeCategory(
        baselineSnapshot?.project_category,
      ),

    region:
      'India',

    original_approved_cost:
      numberOrZero(
        baselineSnapshot?.original_cost_cr,
      ),

    cumulative_expenditure:
      numberOrZero(
        baselineSnapshot?.cumulative_expenditure_cr,
      ),

    physical_progress_pct:
      numberOrZero(
        baselineSnapshot?.physical_progress_pct,
      ),

    planned_duration_months:
      numberOrZero(
        baselineSnapshot?.planned_duration_months,
      ),

    elapsed_duration_months:
      numberOrZero(
        baselineSnapshot?.elapsed_months,
      ),

    progress_velocity:
      numberOrZero(
        baselineSnapshot?.progress_velocity,
      ),

    expenditure_velocity:
      numberOrZero(
        baselineSnapshot?.expenditure_velocity,
      ),
  };

  // ----------------------------------------------------------
  // SCENARIO INPUTS
  // ----------------------------------------------------------

  const scenarioInputs = {
    project_code:
      result.project_code ??
      projectCode,

    project_name:
      `POWERGRID Project ${
        result.project_code ??
        projectCode
      }`,

    project_category:
      normalizeCategory(
        scenarioSnapshot?.project_category,
      ),

    region:
      'India',

    original_approved_cost:
      numberOrZero(
        scenarioSnapshot?.original_cost_cr,
      ),

    cumulative_expenditure:
      numberOrZero(
        scenarioSnapshot?.cumulative_expenditure_cr,
      ),

    physical_progress_pct:
      numberOrZero(
        scenarioSnapshot?.physical_progress_pct,
      ),

    planned_duration_months:
      numberOrZero(
        scenarioSnapshot?.planned_duration_months,
      ),

    elapsed_duration_months:
      numberOrZero(
        scenarioSnapshot?.elapsed_months,
      ),

    progress_velocity:
      numberOrZero(
        scenarioSnapshot?.progress_velocity,
      ),

    expenditure_velocity:
      numberOrZero(
        scenarioSnapshot?.expenditure_velocity,
      ),
  };

  // ----------------------------------------------------------
  // RETURN FRONTEND WHAT-IF RESULT
  // ----------------------------------------------------------

  return {
    project_code:
      result.project_code ??
      projectCode,

    project_name:
      `POWERGRID Project ${
        result.project_code ??
        projectCode
      }`,

    project_category:
      normalizeCategory(
        baselineSnapshot?.project_category,
      ),

    // --------------------------------------------------------
    // BASELINE
    // --------------------------------------------------------

    baseline: {
      inputs:
        baselineInputs,

      derived:
        createDerivedFeatures(
          baseline?.prediction,
          baselineSnapshot,
        ),

      prediction:
        baselinePrediction,
    },

    // --------------------------------------------------------
    // SCENARIO
    // --------------------------------------------------------

    scenario: {
      inputs:
        scenarioInputs,

      changes,

      derived:
        createDerivedFeatures(
          scenario?.prediction,
          scenarioSnapshot,
        ),

      prediction:
        scenarioPrediction,
    },

    // --------------------------------------------------------
    // PREDICTIONS
    // --------------------------------------------------------

    baseline_prediction:
      baselinePrediction,

    scenario_prediction:
      scenarioPrediction,

    // --------------------------------------------------------
    // DELTAS
    // --------------------------------------------------------

    deltas: {
      cost_diff_pct:
        costDiff,

      schedule_diff_months:
        scheduleDiff,

      risk_score_diff:
        riskDiff,

      cost_overrun_pct_delta:
        costDiff,

      schedule_delay_months_delta:
        scheduleDiff,

      risk_score_delta:
        riskDiff,

      cost_improved:
        costDiff < 0,

      schedule_improved:
        scheduleDiff < 0,

      risk_improved:
        riskDiff < 0,
    },
  };
}