/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 * POWERGRID Project Intelligence Platform
 */

export type ProjectCategory =
  | 'Transmission_System'
  | 'Substation_Grid_Equipment'
  | 'Rural_Electrification'
  | 'Renewable_Integration'
  | 'HVDC_Interconnector'
  | 'Grid_Modernization';

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH';

export type NavScreen =
  | 'dashboard'
  | 'new_prediction'
  | 'project_intelligence'
  | 'what_if'
  | 'reports'
  | 'methodology';

export interface ProjectSnapshot {
  snapshot_date: string;
  snapshot_num: number;

  physical_progress_pct: number;
  cumulative_expenditure: number;

  elapsed_duration_months: number;

  progress_velocity: number;
  expenditure_velocity: number;

  risk_score: number;

  predicted_cost_overrun_pct: number;
  predicted_schedule_overrun_months: number;
}

export interface PowerGridProject {
  project_code: string;
  project_name: string;

  project_category: ProjectCategory;
  region: string;

  original_approved_cost: number;
  cumulative_expenditure: number;

  physical_progress_pct: number;

  planned_duration_months: number;
  elapsed_duration_months: number;

  progress_velocity: number;
  expenditure_velocity: number;

  latest_snapshot_date: string;

  is_training_cost: boolean;
  is_training_schedule: boolean;
  is_unseen_test: boolean;

  snapshots: ProjectSnapshot[];
}

export interface DerivedFeatures {
  expenditure_pct: number;

  physical_progress_pct: number;

  expenditure_progress_gap: number;

  schedule_elapsed_pct: number;

  schedule_pressure: number;

  months_to_original_target: number;

  cost_burn_rate: number;

  expected_cost_at_completion: number;

  progress_velocity_ratio: number;

  expenditure_velocity_ratio: number;
}

export interface SupportingRiskIndicator {
  name: string;

  key: string;

  value: number;

  unit: string;

  interpretation: string;

  risk_contribution: RiskLevel;

  benchmark: string;

  explanation: string;

  normalized_score: number;
}

export interface ModelInputRow {
  feature: string;

  value: string | number;

  unit: string;

  source:
    | 'User Input'
    | 'Derived Engine'
    | 'V2 Model Pipeline';

  description: string;
}

export interface PredictionResult {
  cost_prediction_pct: number;

  schedule_prediction_months: number;

  risk_score: number;

  cost_risk_level: RiskLevel;

  schedule_risk_level: RiskLevel;

  overall_risk_level: RiskLevel;

  derived_features: DerivedFeatures;

  supporting_indicators: SupportingRiskIndicator[];

  model_inputs_table: ModelInputRow[];

  timestamp: string;
}

export interface WhatIfChanges {
  physical_progress_pct?: number;

  cumulative_expenditure?: number;

  planned_duration_months?: number;

  progress_velocity?: number;

  expenditure_velocity?: number;
}

export interface WhatIfComparison {
  project_code: string;

  project_name: string;

  project_category: ProjectCategory;

  baseline: {
    inputs: PowerGridProject;

    derived: DerivedFeatures;

    prediction: PredictionResult;
  };

  scenario: {
    inputs: PowerGridProject;

    changes: WhatIfChanges;

    derived: DerivedFeatures;

    prediction: PredictionResult;
  };

  baseline_prediction: PredictionResult;

  scenario_prediction: PredictionResult;

  deltas: {
    cost_diff_pct: number;

    schedule_diff_months: number;

    risk_score_diff: number;

    cost_overrun_pct_delta: number;

    schedule_delay_months_delta: number;

    risk_score_delta: number;

    cost_improved: boolean;

    schedule_improved: boolean;

    risk_improved: boolean;
  };
}

export interface PortfolioStats {
  total_projects: number;

  high_risk_count: number;

  medium_risk_count: number;

  low_risk_count: number;

  avg_cost_overrun_pct: number;

  avg_schedule_delay_months: number;

  validated_projects_count: number;

  cost_training_count: number;

  schedule_training_count: number;

  unseen_test_count: number;

  total_snapshots_count: number;
}

export interface NewProjectFormState {
  originalApprovedCost: string;

  projectCategory: ProjectCategory;

  cumulativeExpenditure: string;

  physicalProgressPct: string;

  plannedDurationMonths: string;

  elapsedDurationMonths: string;

  progressVelocity: string;

  expenditureVelocity: string;
}