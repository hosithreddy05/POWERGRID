/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 * POWERGRID Project Intelligence
 * Executive Dashboard
 */

import React, {
  useEffect,
  useMemo,
  useState,
} from 'react';

import {
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from 'recharts';

import {
  fetchProjectAnalyses,
} from '../services/api';

import type {
  NavScreen,
  PortfolioStats,
  PowerGridProject,
  RiskLevel,
  PredictionResult,
  DerivedFeatures,
} from '../types';

import { RiskBadge } from './RiskBadge';


// ============================================================
// PROPS
// ============================================================

interface ExecutiveDashboardProps {
  projects: PowerGridProject[];
  stats: PortfolioStats;

  onNavigate: (
    screen: NavScreen,
  ) => void;

  onSelectProject: (
    code: string,
  ) => void;

  selectedProjectCode:
    string | null;
}


// ============================================================
// BACKEND TYPES
// ============================================================

interface BackendSnapshot {
  project_code?: string;
  project_name?: string;

  original_cost_cr?: number;
  cumulative_expenditure_cr?: number;

  physical_progress_pct?: number;

  planned_duration_months?: number;
  elapsed_months?: number;

  months_to_original_target?: number;

  expenditure_pct_of_original_cost?: number;

  project_category?: string;

  progress_velocity?: number;
  expenditure_velocity?: number;

  expenditure_progress_gap?: number;

  schedule_slippage_months?: number;
  schedule_pressure_ratio?: number;

  snapshot_date?: string;
}

interface BackendPrediction {
  cost_prediction_pct?: number;
  schedule_prediction_months?: number;

  cost_risk_score?: number;
  cost_risk_level?: string;

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


// ============================================================
// HELPERS
// ============================================================

function safeNumber(
  value: number | undefined,
): number {
  return Number.isFinite(value)
    ? Number(value)
    : 0;
}


function normalizeRisk(
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


function normalizeCategory(
  value?: string,
): PowerGridProject['project_category'] {

  const category =
    String(value ?? '')
      .toLowerCase();

  if (
    category.includes('substation')
  ) {
    return 'Substation_Grid_Equipment';
  }

  if (
    category.includes('rural')
  ) {
    return 'Rural_Electrification';
  }

  if (
    category.includes('renewable') ||
    category.includes('solar') ||
    category.includes('wind')
  ) {
    return 'Renewable_Integration';
  }

  if (
    category.includes('hvdc')
  ) {
    return 'HVDC_Interconnector';
  }

  if (
    category.includes('modern')
  ) {
    return 'Grid_Modernization';
  }

  return 'Transmission_System';
}


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

  for (
    const region of regions
  ) {

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
// BUILD DERIVED FEATURES
// ============================================================

function buildDerivedFeatures(
  snapshot: BackendSnapshot,
  prediction: BackendPrediction,
): DerivedFeatures {

  const expenditure =
    safeNumber(
      snapshot.cumulative_expenditure_cr,
    );

  const originalCost =
    safeNumber(
      snapshot.original_cost_cr,
    );

  const physicalProgress =
    safeNumber(
      prediction.physical_progress_pct ??
        snapshot.physical_progress_pct,
    );

  const expenditurePct =
    safeNumber(
      prediction.expenditure_pct ??
        snapshot.expenditure_pct_of_original_cost ??
        (
          originalCost > 0
            ? (
                expenditure /
                originalCost
              ) * 100
            : 0
        ),
    );

  const progressGap =
    safeNumber(
      prediction.expenditure_progress_gap ??
        snapshot.expenditure_progress_gap ??
        (
          expenditurePct -
          physicalProgress
        ),
    );

  const planned =
    safeNumber(
      snapshot.planned_duration_months,
    );

  const elapsed =
    safeNumber(
      snapshot.elapsed_months,
    );

  const schedulePressure =
    safeNumber(
      prediction.schedule_pressure_ratio ??
        snapshot.schedule_pressure_ratio ??
        (
          planned > 0
            ? elapsed / planned
            : 0
        ),
    );

  const progressVelocity =
    safeNumber(
      snapshot.progress_velocity,
    );

  const expenditureVelocity =
    safeNumber(
      snapshot.expenditure_velocity,
    );

  return {

    expenditure_pct:
      expenditurePct,

    physical_progress_pct:
      physicalProgress,

    expenditure_progress_gap:
      progressGap,

    schedule_elapsed_pct:
      planned > 0
        ? (
            elapsed /
            planned
          ) * 100
        : 0,

    schedule_pressure:
      schedulePressure,

    months_to_original_target:
      safeNumber(
        snapshot.months_to_original_target ??
          planned -
            elapsed,
      ),

    cost_burn_rate:
      elapsed > 0
        ? expenditure / elapsed
        : 0,

    expected_cost_at_completion:
      physicalProgress > 0
        ? expenditure /
          (physicalProgress / 100)
        : expenditure,

    progress_velocity_ratio:
      planned > 0
        ? progressVelocity /
          (100 / planned)
        : 0,

    expenditure_velocity_ratio:
      planned > 0 &&
      expenditure > 0
        ? expenditureVelocity /
          (expenditure / planned)
        : 0,
  };
}


// ============================================================
// BUILD PREDICTION
// ============================================================

function buildPrediction(
  snapshot: BackendSnapshot,
  prediction: BackendPrediction,
): PredictionResult {

  const risk =
    normalizeRisk(
      prediction.cost_risk_level,
    );

  const schedule =
    safeNumber(
      prediction.schedule_prediction_months,
    );

  const derived =
    buildDerivedFeatures(
      snapshot,
      prediction,
    );

  return {

    cost_prediction_pct:
      safeNumber(
        prediction.cost_prediction_pct,
      ),

    schedule_prediction_months:
      schedule,

    risk_score:
      safeNumber(
        prediction.cost_risk_score,
      ),

    cost_risk_level:
      risk,

    schedule_risk_level:
      schedule >= 12
        ? 'HIGH'
        : schedule >= 6
          ? 'MEDIUM'
          : 'LOW',

    overall_risk_level:
      risk,

    derived_features:
      derived,

    supporting_indicators: [],

    model_inputs_table: [],

    timestamp:
      new Date().toISOString(),
  };
}


// ============================================================
// COMPONENT
// ============================================================

export const ExecutiveDashboard:
  React.FC<ExecutiveDashboardProps> = ({
    projects,
    stats,
    onNavigate,
    onSelectProject,
    selectedProjectCode,
  }) => {

  const [
    filterRisk,
    setFilterRisk,
  ] = useState<
    'ALL' | RiskLevel
  >('ALL');

  const [
    filterCategory,
    setFilterCategory,
  ] = useState<string>('ALL');


  const [
    backendData,
    setBackendData,
  ] = useState<
    BackendProjectAnalysis[]
  >([]);


  const [
    backendLoading,
    setBackendLoading,
  ] = useState(true);


  const [
    backendError,
    setBackendError,
  ] = useState('');


  // ==========================================================
  // LOAD BACKEND DATA
  // ==========================================================

  useEffect(() => {

    let cancelled = false;

    async function load() {

      try {

        setBackendLoading(true);
        setBackendError('');

        const result =
          await fetchProjectAnalyses();

        if (!cancelled) {
          setBackendData(result);
        }

      } catch (error) {

        if (!cancelled) {

          setBackendError(
            error instanceof Error
              ? error.message
              : 'Unable to load POWERGRID backend data.',
          );
        }

      } finally {

        if (!cancelled) {
          setBackendLoading(false);
        }
      }
    }

    load();

    return () => {
      cancelled = true;
    };

  }, []);


  // ==========================================================
  // COMBINE PROJECTS WITH BACKEND PREDICTIONS
  // ==========================================================

  const analyzedProjects =
    useMemo(() => {

      const backendMap =
        new Map<
          string,
          BackendProjectAnalysis
        >();

      for (
        const item of backendData
      ) {

        if (
          item.project_code
        ) {
          backendMap.set(
            item.project_code,
            item,
          );
        }
      }


      return projects
        .map((project) => {

          const backend =
            backendMap.get(
              project.project_code,
            );

          if (!backend) {
            return null;
          }


          const snapshot =
            backend.snapshot ??
            backend.trajectory_snapshot ??
            backend.model_input ??
            {};


          const backendPrediction =
            backend.prediction ??
            {};


          const derived =
            buildDerivedFeatures(
              snapshot,
              backendPrediction,
            );


          const prediction =
            buildPrediction(
              snapshot,
              backendPrediction,
            );


          return {

            ...project,

            project_name:
              backend.project_name ??
              snapshot.project_name ??
              project.project_name,

            project_category:
              normalizeCategory(
                snapshot.project_category,
              ),

            region:
              inferRegion(
                backend.project_name ??
                snapshot.project_name ??
                project.project_name,
              ),

            original_approved_cost:
              safeNumber(
                snapshot.original_cost_cr,
              ),

            cumulative_expenditure:
              safeNumber(
                snapshot.cumulative_expenditure_cr,
              ),

            physical_progress_pct:
              safeNumber(
                snapshot.physical_progress_pct,
              ),

            planned_duration_months:
              safeNumber(
                snapshot.planned_duration_months,
              ),

            elapsed_duration_months:
              safeNumber(
                snapshot.elapsed_months,
              ),

            progress_velocity:
              safeNumber(
                snapshot.progress_velocity,
              ),

            expenditure_velocity:
              safeNumber(
                snapshot.expenditure_velocity,
              ),

            latest_snapshot_date:
              snapshot.snapshot_date ??
              project.latest_snapshot_date,

            derived,

            prediction,
          };

        })
        .filter(
          (
            item,
          ): item is NonNullable<
            typeof item
          > =>
            item !== null,
        );

    }, [
      backendData,
      projects,
    ]);


  // ==========================================================
  // DASHBOARD STATS
  // ==========================================================

  const dashboardStats =
    useMemo(() => {

      const total =
        analyzedProjects.length;

      if (total === 0) {
        return stats;
      }


      const high =
        analyzedProjects.filter(
          (item) =>
            item.prediction
              .overall_risk_level ===
            'HIGH',
        ).length;


      const medium =
        analyzedProjects.filter(
          (item) =>
            item.prediction
              .overall_risk_level ===
            'MEDIUM',
        ).length;


      const low =
        analyzedProjects.filter(
          (item) =>
            item.prediction
              .overall_risk_level ===
            'LOW',
        ).length;


      const avgCost =
        analyzedProjects.reduce(
          (sum, item) =>
            sum +
            item.prediction
              .cost_prediction_pct,
          0,
        ) / total;


      const avgSchedule =
        analyzedProjects.reduce(
          (sum, item) =>
            sum +
            item.prediction
              .schedule_prediction_months,
          0,
        ) / total;


      return {

        ...stats,

        total_projects:
          total,

        high_risk_count:
          high,

        medium_risk_count:
          medium,

        low_risk_count:
          low,

        avg_cost_overrun_pct:
          Number(
            avgCost.toFixed(2),
          ),

        avg_schedule_delay_months:
          Number(
            avgSchedule.toFixed(2),
          ),
      };

    }, [
      analyzedProjects,
      stats,
    ]);


  // ==========================================================
  // RISK DONUT
  // ==========================================================

  const riskDonutData =
    useMemo(() => {

      const total =
        dashboardStats.total_projects;

      return [

        {
          name: 'Low Risk',
          value:
            dashboardStats.low_risk_count,
          pct:
            total > 0
              ? Number(
                  (
                    dashboardStats
                      .low_risk_count /
                    total *
                    100
                  ).toFixed(1),
                )
              : 0,
          color: '#10b981',
        },

        {
          name: 'Medium Risk',
          value:
            dashboardStats.medium_risk_count,
          pct:
            total > 0
              ? Number(
                  (
                    dashboardStats
                      .medium_risk_count /
                    total *
                    100
                  ).toFixed(1),
                )
              : 0,
          color: '#f59e0b',
        },

        {
          name: 'High Risk',
          value:
            dashboardStats.high_risk_count,
          pct:
            total > 0
              ? Number(
                  (
                    dashboardStats
                      .high_risk_count /
                    total *
                    100
                  ).toFixed(1),
                )
              : 0,
          color: '#e11d48',
        },

      ];

    }, [
      dashboardStats,
    ]);


  // ==========================================================
  // SCATTER DATA
  // ==========================================================

  const scatterData =
    useMemo(() => {

      return analyzedProjects.map(
        (project) => ({

          code:
            project.project_code,

          name:
            project.project_name,

          category:
            project.project_category,

          x:
            project.physical_progress_pct,

          y:
            project.prediction
              .derived_features
              .expenditure_pct,

          costOverrun:
            project.prediction
              .cost_prediction_pct,

          scheduleDelay:
            project.prediction
              .schedule_prediction_months,

          riskScore:
            project.prediction
              .risk_score,

          riskLevel:
            project.prediction
              .overall_risk_level,

          isSelected:
            project.project_code ===
            selectedProjectCode,

        }),
      );

    }, [
      analyzedProjects,
      selectedProjectCode,
    ]);


  // ==========================================================
  // FILTERED ATTENTION PROJECTS
  // ==========================================================

  const filteredProjects =
    useMemo(() => {

      return analyzedProjects
        .filter((project) => {

          if (
            filterRisk !== 'ALL' &&
            project.prediction
              .overall_risk_level !==
            filterRisk
          ) {
            return false;
          }


          if (
            filterCategory !== 'ALL' &&
            project.project_category !==
            filterCategory
          ) {
            return false;
          }


          return true;
        })
        .sort(
          (a, b) =>
            b.prediction.risk_score -
            a.prediction.risk_score,
        );

    }, [
      analyzedProjects,
      filterRisk,
      filterCategory,
    ]);


  // ==========================================================
  // RENDER
  // ==========================================================

  return (
    <div className="space-y-6 pb-12">

      {backendLoading && (
        <div className="rounded-xl border border-blue-100 bg-blue-50 px-4 py-3 text-xs text-blue-700">
          Syncing portfolio predictions from the POWERGRID V2 backend...
        </div>
      )}

      {backendError && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-xs text-amber-800">
          Backend portfolio sync warning: {backendError}
        </div>
      )}


      {/* ================================================== */}
      {/* HEADER */}
      {/* ================================================== */}

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl bg-gradient-to-r from-[#091e3a] to-[#133363] text-white shadow-sm border border-slate-700/50">

        <div className="space-y-1">

          <div className="flex items-center gap-2">

            <span className="px-2.5 py-0.5 rounded-md text-[10px] font-bold bg-blue-500/30 text-blue-200 uppercase tracking-widest font-mono border border-blue-400/30">
              Executive Overview
            </span>

            <span className="text-xs text-slate-300 font-mono">
              Aug 2024 – Jun 2026 Snapshot Baseline
            </span>

          </div>

          <h2 className="text-xl font-bold tracking-tight text-white">
            Transmission & Substation Portfolio Overview
          </h2>

          <p className="text-xs text-slate-300 max-w-2xl">
            Machine learning monitoring of cost overruns,
            timeline delays, and risk trajectories across{' '}
            {dashboardStats.total_projects}
            {' '}validated infrastructure projects.
          </p>

        </div>


        <div className="flex items-center gap-3">

          <button
            onClick={() =>
              onNavigate(
                'new_prediction',
              )
            }
            className="px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs transition-all shadow-md shadow-blue-900/40 flex items-center gap-2 cursor-pointer"
          >
            <span className="material-symbols-outlined text-base">
              add_chart
            </span>
            <span>
              Predict New Project
            </span>
          </button>


          <button
            onClick={() =>
              onNavigate(
                'what_if',
              )
            }
            className="px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white border border-white/20 font-semibold text-xs transition-all flex items-center gap-2 cursor-pointer"
          >
            <span className="material-symbols-outlined text-base">
              tune
            </span>
            <span>
              What-If Simulator
            </span>
          </button>

        </div>

      </div>


      {/* ================================================== */}
      {/* KPI CARDS */}
      {/* ================================================== */}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">

        {/* Total Projects */}

        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs">

          <div className="flex items-center justify-between text-slate-500">

            <span className="text-xs font-bold uppercase tracking-wider font-mono">
              Total Projects
            </span>

            <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
              <span className="material-symbols-outlined text-lg">
                folder_open
              </span>
            </div>

          </div>

          <div className="mt-3 flex items-baseline gap-2">

            <span className="text-3xl font-extrabold font-mono text-slate-900">
              {dashboardStats.total_projects}
            </span>

            <span className="text-xs text-slate-500">
              validated
            </span>

          </div>

          <p className="text-xs text-slate-500 mt-1">
            Across 6 categories (
            {dashboardStats.total_snapshots_count}
            {' '}snapshots)
          </p>

          <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-600 font-mono">

            <span>
              Training Projects:{' '}
              {dashboardStats.cost_training_count}
            </span>

            <span>
              Unseen:{' '}
              {dashboardStats.unseen_test_count}
            </span>

          </div>

        </div>


        {/* High Risk */}

        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs">

          <div className="flex items-center justify-between">

            <span className="text-xs font-bold uppercase tracking-wider font-mono text-rose-600">
              High Risk Projects
            </span>

            <div className="w-8 h-8 rounded-lg bg-rose-50 text-rose-600 flex items-center justify-center">
              <span className="material-symbols-outlined text-lg">
                warning
              </span>
            </div>

          </div>

          <div className="mt-3 flex items-baseline gap-2">

            <span className="text-3xl font-extrabold font-mono text-rose-600">
              {dashboardStats.high_risk_count}
            </span>

            <span className="text-xs text-rose-500">
              (
              {dashboardStats.total_projects > 0
                ? (
                    dashboardStats.high_risk_count /
                    dashboardStats.total_projects *
                    100
                  ).toFixed(1)
                : '0.0'}
              %)
            </span>

          </div>

          <p className="text-xs text-slate-500 mt-1">
            Requires active managerial intervention
          </p>

          <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-600 font-mono">

            <span>
              Medium:{' '}
              {dashboardStats.medium_risk_count}
            </span>

            <span>
              Low:{' '}
              {dashboardStats.low_risk_count}
            </span>

          </div>

        </div>


        {/* Cost */}

        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs">

          <div className="flex items-center justify-between">

            <span className="text-xs font-bold uppercase tracking-wider font-mono">
              Portfolio Cost Overrun
            </span>

            <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
              <span className="material-symbols-outlined text-lg">
                currency_rupee
              </span>
            </div>

          </div>

          <div className="mt-3 flex items-baseline gap-1">

            <span className="text-3xl font-extrabold font-mono text-slate-900">
              {dashboardStats.avg_cost_overrun_pct}%
            </span>

            <span className="text-xs text-amber-600 font-semibold">
              avg
            </span>

          </div>

          <p className="text-xs text-slate-500 mt-1">
            Predicted additional cost above sanctioned budget
          </p>

        </div>


        {/* Schedule */}

        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs">

          <div className="flex items-center justify-between">

            <span className="text-xs font-bold uppercase tracking-wider font-mono">
              Portfolio Schedule Delay
            </span>

            <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
              <span className="material-symbols-outlined text-lg">
                schedule
              </span>
            </div>

          </div>

          <div className="mt-3 flex items-baseline gap-1">

            <span className="text-3xl font-extrabold font-mono text-slate-900">
              {dashboardStats.avg_schedule_delay_months}
            </span>

            <span className="text-xs text-slate-600">
              months
            </span>

          </div>

          <p className="text-xs text-slate-500 mt-1">
            Average delay drift beyond planned milestone targets
          </p>

        </div>

      </div>


      {/* ================================================== */}
      {/* CHARTS */}
      {/* ================================================== */}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Risk Distribution */}

        <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-xs">

          <div className="flex items-center justify-between mb-2">

            <h3 className="font-bold text-sm text-slate-900 font-mono uppercase">
              Portfolio Risk Distribution
            </h3>

            <span className="text-[11px] font-mono text-slate-500">
              {dashboardStats.total_projects}
              {' '}Projects
            </span>

          </div>

          <p className="text-xs text-slate-500">
            Risk classifications from the POWERGRID V2 backend.
          </p>


          <div className="my-3 h-52 relative flex items-center justify-center">

            <ResponsiveContainer
              width="100%"
              height="100%"
            >

              <PieChart>

                <Pie
                  data={riskDonutData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={78}
                  paddingAngle={4}
                  dataKey="value"
                >

                  {riskDonutData.map(
                    (
                      entry,
                      index,
                    ) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={entry.color}
                        stroke="#ffffff"
                        strokeWidth={2}
                      />
                    ),
                  )}

                </Pie>


                <Tooltip
                  formatter={(value, name) => [
                    `${Number(value ?? 0)} projects`,
                    String(name ?? ''),
                  ]}
                />

              </PieChart>

            </ResponsiveContainer>


            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">

              <span className="text-2xl font-extrabold font-mono text-slate-900">
                {dashboardStats.total_projects}
              </span>

              <span className="text-[10px] uppercase font-bold text-slate-400 font-mono">
                Projects
              </span>

            </div>

          </div>


          <div className="space-y-2 pt-3 border-t border-slate-100">

            {riskDonutData.map(
              (entry) => (

                <button
                  key={entry.name}
                  type="button"
                  onClick={() => {

                    const level =
                      entry.name
                        .split(' ')[0]
                        .toUpperCase() as RiskLevel;

                    setFilterRisk(
                      filterRisk === level
                        ? 'ALL'
                        : level,
                    );

                  }}
                  className="w-full flex items-center justify-between text-xs p-1.5 rounded-lg hover:bg-slate-50 cursor-pointer"
                >

                  <div className="flex items-center gap-2">

                    <span
                      className="w-3 h-3 rounded-md"
                      style={{
                        backgroundColor:
                          entry.color,
                      }}
                    />

                    <span className="font-semibold text-slate-700">
                      {entry.name}
                    </span>

                  </div>

                  <div className="flex items-center gap-3 font-mono">

                    <span className="font-bold text-slate-900">
                      {entry.value}
                    </span>

                    <span className="text-slate-500">
                      {entry.pct}%
                    </span>

                  </div>

                </button>

              ),
            )}

          </div>

        </div>


        {/* Scatter */}

        <div className="lg:col-span-2 p-6 rounded-2xl bg-white border border-slate-200 shadow-xs">

          <div className="flex items-center justify-between mb-3">

            <div>

              <h3 className="font-bold text-sm text-slate-900 font-mono uppercase">
                Portfolio Risk Landscape
              </h3>

              <p className="text-xs text-slate-500 mt-0.5">
                Physical Progress vs Expenditure / Approved Cost
              </p>

            </div>

          </div>


          <div className="h-72 w-full">

            <ResponsiveContainer
              width="100%"
              height="100%"
            >

              <ScatterChart
                margin={{
                  top: 15,
                  right: 20,
                  bottom: 20,
                  left: 10,
                }}
              >

                <XAxis
                  type="number"
                  dataKey="x"
                  domain={[0, 100]}
                  name="Physical Progress"
                  unit="%"
                />

                <YAxis
                  type="number"
                  dataKey="y"
                  domain={[0, 120]}
                  name="Expenditure"
                  unit="%"
                />

                <ZAxis
                  range={[50, 160]}
                />


                <Tooltip
                  cursor={{
                    strokeDasharray: '3 3',
                  }}
                  content={({
                    payload,
                  }) => {

                    if (
                      !payload ||
                      payload.length === 0
                    ) {
                      return null;
                    }

                    const data =
                      payload[0]
                        .payload;

                    return (

                      <div className="bg-[#091e3a] border border-slate-700 text-white p-3 rounded-xl shadow-xl text-xs space-y-1 max-w-xs font-mono">

                        <div className="font-bold text-blue-300">
                          [{data.code}]
                        </div>

                        <div>
                          {data.name}
                        </div>

                        <div className="text-slate-400">
                          {data.category}
                        </div>

                        <div>
                          Physical Progress:
                          {' '}
                          {data.x}%
                        </div>

                        <div>
                          Expenditure:
                          {' '}
                          {data.y}%
                        </div>

                        <div>
                          Cost Overrun:
                          {' '}
                          {data.costOverrun}%
                        </div>

                        <div>
                          Risk:
                          {' '}
                          {data.riskScore}/100
                        </div>

                      </div>
                    );
                  }}
                />


                <Scatter
                  name="Validated Projects"
                  data={scatterData}
                  onClick={(node) => {
                    const point = node as {
                      code?: string;
                    };

                    if (point.code) {
                      onSelectProject(point.code);
                      onNavigate('project_intelligence');
                    }
                  }}
                >

                  {scatterData.map(
                    (
                      entry,
                      index,
                    ) => {

                      const fill =
                        entry.riskLevel ===
                        'HIGH'
                          ? '#e11d48'
                          : entry.riskLevel ===
                            'MEDIUM'
                            ? '#f59e0b'
                            : '#10b981';

                      return (
                        <Cell
                          key={`scatter-${index}`}
                          fill={fill}
                          stroke={
                            entry.isSelected
                              ? '#091e3a'
                              : '#ffffff'
                          }
                          strokeWidth={
                            entry.isSelected
                              ? 3
                              : 1.5
                          }
                        />
                      );

                    },
                  )}

                </Scatter>

              </ScatterChart>

            </ResponsiveContainer>

          </div>

        </div>

      </div>


      {/* ================================================== */}
      {/* PROJECTS REQUIRING ATTENTION */}
      {/* ================================================== */}

      <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-4">

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">

          <div>

            <h3 className="font-bold text-base text-slate-900 font-mono uppercase flex items-center gap-2">

              <span>
                Projects Requiring Attention
              </span>

              <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-mono">
                {filteredProjects.length}
                {' '}projects
              </span>

            </h3>

            <p className="text-xs text-slate-500 mt-0.5">
              Ranked by backend explainable risk score and forecasted impact.
            </p>

          </div>


          <div className="flex flex-wrap items-center gap-2 text-xs">

            <div className="flex items-center rounded-xl bg-slate-100 p-1 border border-slate-200">

              {(
                [
                  'ALL',
                  'HIGH',
                  'MEDIUM',
                  'LOW',
                ] as const
              ).map(
                (level) => (

                  <button
                    key={level}
                    type="button"
                    onClick={() =>
                      setFilterRisk(
                        level,
                      )
                    }
                    className={`px-2.5 py-1 rounded-lg font-mono font-semibold cursor-pointer ${
                      filterRisk === level
                        ? 'bg-white text-slate-900 shadow-xs'
                        : 'text-slate-500 hover:text-slate-800'
                    }`}
                  >
                    {level}
                  </button>

                ),
              )}

            </div>


            <select
              aria-label="Filter Projects by Category"
              value={filterCategory}
              onChange={(event) =>
                setFilterCategory(
                  event.target.value,
                )
              }
              className="px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-300 text-slate-700 text-xs font-medium outline-none cursor-pointer"
            >

              <option value="ALL">
                All Categories
              </option>

              <option value="Transmission_System">
                Transmission System
              </option>

              <option value="Substation_Grid_Equipment">
                Substation Equipment
              </option>

              <option value="Renewable_Integration">
                Renewable Integration
              </option>

              <option value="HVDC_Interconnector">
                HVDC Interconnector
              </option>

              <option value="Rural_Electrification">
                Rural Electrification
              </option>

              <option value="Grid_Modernization">
                Grid Modernization
              </option>

            </select>

          </div>

        </div>


        <div className="overflow-x-auto border border-slate-200 rounded-xl">

          <table className="w-full text-left text-xs">

            <thead className="bg-slate-50 text-slate-700 font-mono font-bold uppercase tracking-wider border-b border-slate-200">

              <tr>

                <th className="py-3 px-4">
                  Project
                </th>

                <th className="py-3 px-3">
                  Category
                </th>

                <th className="py-3 px-3">
                  Risk Level
                </th>

                <th className="py-3 px-3 text-right">
                  Physical Progress
                </th>

                <th className="py-3 px-3 text-right">
                  Cost Overrun
                </th>

                <th className="py-3 px-3 text-right">
                  Schedule Delay
                </th>

                <th className="py-3 px-4 text-center">
                  Action
                </th>

              </tr>

            </thead>


            <tbody className="divide-y divide-slate-100">

              {filteredProjects
                .slice(0, 10)
                .map(
                  (project) => (

                    <tr
                      key={
                        project.project_code
                      }
                      className="hover:bg-slate-50/80"
                    >

                      <td className="py-3.5 px-4">

                        <div className="font-mono font-bold text-blue-600">
                          [
                          {project.project_code}
                          ]
                        </div>

                        <div className="font-medium text-slate-900 max-w-sm truncate mt-0.5">
                          {project.project_name}
                        </div>

                        <div className="text-[10px] text-slate-500 font-mono">
                          Approved: ₹
                          {
                            project
                              .original_approved_cost
                          }
                          {' '}Cr •{' '}
                          {project.region}
                        </div>

                      </td>


                      <td className="py-3.5 px-3">

                        <span className="text-[11px] px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-mono">
                          {project
                            .project_category
                            .replace(
                              /_/g,
                              ' ',
                            )}
                        </span>

                      </td>


                      <td className="py-3.5 px-3">

                        <RiskBadge
                          level={
                            project
                              .prediction
                              .overall_risk_level
                          }
                          size="sm"
                        />

                        <div className="text-[10px] font-mono text-slate-400 mt-1">
                          Score:{' '}
                          {
                            project
                              .prediction
                              .risk_score
                          }
                          /100
                        </div>

                      </td>


                      <td className="py-3.5 px-3 text-right font-mono">

                        <div className="font-bold text-slate-900">
                          {
                            project
                              .physical_progress_pct
                          }%
                        </div>

                        <div className="text-[10px] text-slate-400">
                          Exp:{' '}
                          {
                            project
                              .prediction
                              .derived_features
                              .expenditure_pct
                          }%
                        </div>

                      </td>


                      <td className="py-3.5 px-3 text-right font-mono">

                        <span
                          className={`font-bold ${
                            project
                              .prediction
                              .cost_prediction_pct > 10
                              ? 'text-rose-600'
                              : project
                                  .prediction
                                  .cost_prediction_pct > 3
                                ? 'text-amber-600'
                                : 'text-emerald-600'
                          }`}
                        >
                          +
                          {
                            project
                              .prediction
                              .cost_prediction_pct
                          }%
                        </span>

                        <div className="text-[10px] text-slate-400">
                          Gap:{' '}
                          {
                            project
                              .prediction
                              .derived_features
                              .expenditure_progress_gap
                          }%
                        </div>

                      </td>


                      <td className="py-3.5 px-3 text-right font-mono">

                        <span
                          className={`font-bold ${
                            project
                              .prediction
                              .schedule_prediction_months > 4
                              ? 'text-rose-600'
                              : project
                                  .prediction
                                  .schedule_prediction_months > 1
                                ? 'text-amber-600'
                                : 'text-emerald-600'
                          }`}
                        >
                          +
                          {
                            project
                              .prediction
                              .schedule_prediction_months
                          }
                          {' '}mo
                        </span>

                        <div className="text-[10px] text-slate-400">
                          {
                            project
                              .elapsed_duration_months
                          }
                          /
                          {
                            project
                              .planned_duration_months
                          }
                          {' '}mo
                        </div>

                      </td>


                      <td className="py-3.5 px-4 text-center">

                        <button
                          type="button"
                          onClick={() => {

                            onSelectProject(
                              project.project_code,
                            );

                            onNavigate(
                              'project_intelligence',
                            );

                          }}
                          className="px-3 py-1.5 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-700 font-semibold text-[11px] font-mono border border-blue-200 cursor-pointer"
                        >
                          View Project
                        </button>

                      </td>

                    </tr>

                  ),
                )}

            </tbody>

          </table>

        </div>


        <div className="flex items-center justify-between pt-2 text-xs text-slate-500">

          <span>
            Showing top{' '}
            {Math.min(
              10,
              filteredProjects.length,
            )}
            {' '}of{' '}
            {filteredProjects.length}
          </span>

          <button
            type="button"
            onClick={() =>
              onNavigate(
                'reports',
              )
            }
            className="text-blue-600 font-semibold hover:underline font-mono cursor-pointer"
          >
            View all 92 validated projects in Portfolio Matrix →
          </button>

        </div>

      </div>

    </div>
  );
};/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 *
 * POWERGRID Project Intelligence
 * Screen 1: Executive Dashboard
 */

