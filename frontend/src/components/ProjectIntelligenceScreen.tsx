import { useEffect, useState } from 'react';

import {
  AlertTriangle,
  ArrowLeft,
  CalendarDays,
  CircleDollarSign,
  Clock3,
  Gauge,
  Loader2,
  RefreshCw,
  ShieldAlert,
  TrendingUp,
} from 'lucide-react';

import type {
  NavScreen,
  PowerGridProject,
} from '../types';

import { fetchProject } from '../services/api';

import { RiskBadge } from './RiskBadge';
import { RiskGauge } from './RiskGauge';


interface ProjectIntelligenceScreenProps {
  onNavigate: (screen: NavScreen) => void;
  selectedProjectCode: string;
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


interface BackendSnapshot {
  project_code?: string;
  project_name?: string;
  original_cost_cr?: number;
  cumulative_expenditure_cr?: number;
  physical_progress_pct?: number;
  planned_duration_months?: number;
  elapsed_months?: number;
  progress_velocity?: number;
  expenditure_velocity?: number;
  expenditure_progress_gap?: number;
  schedule_slippage_months?: number;
  snapshot_date?: string;
  project_category?: string;
}


interface BackendProjectResponse {
  project_code?: string;
  project_name?: string;

  snapshot?: BackendSnapshot;

  trajectory_snapshot?: BackendSnapshot;

  prediction?: BackendPrediction;
}


function formatNumber(
  value: number,
  digits = 2,
): string {
  if (!Number.isFinite(value)) {
    return '0';
  }

  return value.toLocaleString(
    'en-IN',
    {
      minimumFractionDigits: digits,
      maximumFractionDigits: digits,
    },
  );
}


/*
 * V2 portfolio risk bands.
 *
 * 0 - 35   = LOW
 * 36 - 65  = MEDIUM
 * 66 - 100 = HIGH
 */
function riskFromScore(
  score: number,
): 'LOW' | 'MEDIUM' | 'HIGH' {
  if (score >= 66) {
    return 'HIGH';
  }

  if (score >= 36) {
    return 'MEDIUM';
  }

  return 'LOW';
}


function scheduleRisk(
  months: number,
): 'LOW' | 'MEDIUM' | 'HIGH' {
  if (months >= 24) {
    return 'HIGH';
  }

  if (months >= 12) {
    return 'MEDIUM';
  }

  return 'LOW';
}


export function ProjectIntelligenceScreen({
  onNavigate,
  selectedProjectCode,
}: ProjectIntelligenceScreenProps) {

  const [project, setProject] =
    useState<PowerGridProject | null>(null);

  const [backendData, setBackendData] =
    useState<BackendProjectResponse | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState('');

  const [reloadKey, setReloadKey] =
    useState(0);


  /*
   * ----------------------------------------------------------
   * Load project from POWERGRID backend
   * ----------------------------------------------------------
   */

  useEffect(() => {
    let cancelled = false;

    async function loadProject() {

      if (!selectedProjectCode) {
        setProject(null);
        setBackendData(null);
        return;
      }

      try {
        setLoading(true);
        setError('');

        /*
         * fetchProject() uses the configured API base URL.
         */
        const result =
          await fetchProject(
            selectedProjectCode,
          );

        if (cancelled) {
          return;
        }

        setProject(result.project);


        /*
         * Load the detailed backend response so that
         * trajectory values and V2 prediction values come
         * directly from FastAPI.
         */
        try {
          const apiBase =
            import.meta.env.VITE_API_BASE_URL ??
            'http://127.0.0.1:8000/api';

          const response =
            await fetch(
              `${apiBase}/projects/${encodeURIComponent(
                selectedProjectCode,
              )}`,
            );

          if (!response.ok) {
            throw new Error(
              `Backend returned ${response.status}`,
            );
          }

          const data =
            (await response.json()) as BackendProjectResponse;

          if (!cancelled) {
            setBackendData(data);
          }

        } catch (backendError) {

          if (!cancelled) {
            console.error(
              'Unable to load detailed backend project data:',
              backendError,
            );
          }
        }

      } catch (err) {

        if (cancelled) {
          return;
        }

        setError(
          err instanceof Error
            ? err.message
            : 'Unable to load project intelligence.',
        );

        setProject(null);
        setBackendData(null);

      } finally {

        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadProject();

    return () => {
      cancelled = true;
    };

  }, [
    selectedProjectCode,
    reloadKey,
  ]);


  /*
   * ----------------------------------------------------------
   * Backend snapshot
   * ----------------------------------------------------------
   *
   * Prefer trajectory_snapshot because it contains the
   * real trajectory features used by V2.
   */
  const backendSnapshot =
    backendData?.trajectory_snapshot ??
    backendData?.snapshot;


  /*
   * ----------------------------------------------------------
   * Prediction values
   * ----------------------------------------------------------
   */

  const costPrediction =
    Number(
      backendData?.prediction
        ?.cost_prediction_pct ??
        0,
    );


  const schedulePrediction =
    Number(
      backendData?.prediction
        ?.schedule_prediction_months ??
        0,
    );


  const riskScore =
    Number(
      backendData?.prediction
        ?.cost_risk_score ??
        0,
    );


  const riskLevel =
    riskFromScore(riskScore);


  const scheduleRiskLevel =
    scheduleRisk(
      schedulePrediction,
    );


  /*
   * ----------------------------------------------------------
   * Current project values
   * ----------------------------------------------------------
   *
   * Backend trajectory snapshot is preferred.
   * Project object is used only as a fallback.
   */

  const expenditure =
    Number(
      backendSnapshot
        ?.cumulative_expenditure_cr ??
        project?.cumulative_expenditure ??
        0,
    );


  const approvedCost =
    Number(
      backendSnapshot
        ?.original_cost_cr ??
        project?.original_approved_cost ??
        0,
    );


  const physicalProgress =
    Number(
      backendSnapshot
        ?.physical_progress_pct ??
        project?.physical_progress_pct ??
        0,
    );


  const plannedDuration =
    Number(
      backendSnapshot
        ?.planned_duration_months ??
        project?.planned_duration_months ??
        0,
    );


  const elapsedDuration =
    Number(
      backendSnapshot
        ?.elapsed_months ??
        project?.elapsed_duration_months ??
        0,
    );


  /*
   * IMPORTANT:
   *
   * These now come directly from the real POWERGRID
   * trajectory data returned by FastAPI.
   */
  const progressVelocity =
    Number(
      backendSnapshot
        ?.progress_velocity ??
        0,
    );


  const expenditureVelocity =
    Number(
      backendSnapshot
        ?.expenditure_velocity ??
        0,
    );


  const expenditurePct =
    Number(
      backendData?.prediction
        ?.expenditure_pct ??
        (
          approvedCost > 0
            ? (expenditure / approvedCost) * 100
            : 0
        ),
    );


  const gap =
    Number(
      backendData?.prediction
        ?.expenditure_progress_gap ??
        backendSnapshot
          ?.expenditure_progress_gap ??
        expenditurePct -
          physicalProgress,
    );


  const schedulePressure =
    Number(
      backendData?.prediction
        ?.schedule_pressure_ratio ??
        0,
    );


  /*
   * ----------------------------------------------------------
   * No project selected
   * ----------------------------------------------------------
   */

  if (!selectedProjectCode) {
    return (
      <div className="space-y-6">

        <section className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">

          <div className="flex flex-col items-center justify-center py-16 text-center">

            <div className="mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-50 text-blue-600">
              <TrendingUp className="h-8 w-8" />
            </div>

            <h1 className="text-2xl font-bold text-slate-900">
              Project Intelligence
            </h1>

            <p className="mt-2 max-w-xl text-sm text-slate-500">
              Select a POWERGRID project from the
              project selector above to view detailed
              cost, schedule and risk intelligence.
            </p>

            <button
              type="button"
              onClick={() =>
                onNavigate('dashboard')
              }
              className="mt-6 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-700"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Dashboard
            </button>

          </div>

        </section>

      </div>
    );
  }


  /*
   * ----------------------------------------------------------
   * Loading
   * ----------------------------------------------------------
   */

  if (loading) {
    return (
      <div className="flex min-h-[500px] items-center justify-center">

        <div className="rounded-2xl border border-slate-200 bg-white px-8 py-10 text-center shadow-sm">

          <Loader2 className="mx-auto h-8 w-8 animate-spin text-blue-600" />

          <h2 className="mt-4 text-lg font-bold text-slate-900">
            Loading project intelligence
          </h2>

          <p className="mt-2 text-sm text-slate-500">
            Running the POWERGRID V2 analysis engine...
          </p>

        </div>

      </div>
    );
  }


  /*
   * ----------------------------------------------------------
   * Error
   * ----------------------------------------------------------
   */

  if (error || !project) {
    return (
      <section className="rounded-2xl border border-red-200 bg-red-50 p-8">

        <div className="flex items-start gap-4">

          <AlertTriangle className="mt-1 h-6 w-6 text-red-600" />

          <div>

            <h2 className="font-bold text-red-900">
              Unable to load project
            </h2>

            <p className="mt-1 text-sm text-red-700">
              {error ||
                'The selected project could not be loaded.'}
            </p>

            <button
              type="button"
              onClick={() =>
                setReloadKey(
                  (value) => value + 1,
                )
              }
              className="mt-4 inline-flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white"
            >
              <RefreshCw className="h-4 w-4" />
              Retry
            </button>

          </div>

        </div>

      </section>
    );
  }


  /*
   * ----------------------------------------------------------
   * Main Project Intelligence
   * ----------------------------------------------------------
   */

  return (
    <div className="space-y-6">

      {/* HEADER */}

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">

          <div className="min-w-0">

            <div className="mb-2 flex flex-wrap items-center gap-2">

              <span className="rounded-md bg-blue-50 px-2.5 py-1 font-mono text-[10px] font-bold uppercase tracking-widest text-blue-700">
                PROJECT INTELLIGENCE
              </span>

              <span className="font-mono text-xs text-slate-400">
                {project.project_code}
              </span>

            </div>

            <h1 className="text-2xl font-bold tracking-tight text-slate-900">
              {project.project_name}
            </h1>

            <p className="mt-2 text-sm text-slate-500">
              Detailed AI-powered cost, schedule and
              project-risk assessment.
            </p>

          </div>


          <div className="flex shrink-0 items-center gap-3">

            <button
              type="button"
              onClick={() =>
                setReloadKey(
                  (value) => value + 1,
                )
              }
              className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50"
            >
              <RefreshCw className="h-4 w-4" />
              Refresh
            </button>

            <RiskBadge
              level={riskLevel}
            />

          </div>

        </div>

      </section>


      {/* KEY METRICS */}

      <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">

        <MetricCard
          icon={
            <CircleDollarSign className="h-5 w-5" />
          }
          label="Approved Cost"
          value={`₹ ${formatNumber(
            approvedCost,
            2,
          )} Cr`}
          subtext="Original approved project cost"
        />


        <MetricCard
          icon={
            <CircleDollarSign className="h-5 w-5" />
          }
          label="Expenditure"
          value={`₹ ${formatNumber(
            expenditure,
            2,
          )} Cr`}
          subtext={`${formatNumber(
            expenditurePct,
            1,
          )}% of approved cost`}
        />


        <MetricCard
          icon={
            <TrendingUp className="h-5 w-5" />
          }
          label="Physical Progress"
          value={`${formatNumber(
            physicalProgress,
            1,
          )}%`}
          subtext={`Gap ${formatNumber(
            gap,
            1,
          )} percentage points`}
        />


        <MetricCard
          icon={
            <Clock3 className="h-5 w-5" />
          }
          label="Schedule Pressure"
          value={
            schedulePressure > 0
              ? `${formatNumber(
                  schedulePressure,
                  2,
                )}x`
              : `${formatNumber(
                  schedulePrediction,
                  1,
                )} mo`
          }
          subtext="Predicted schedule pressure"
        />

      </section>


      {/* RISK + PREDICTION */}

      <section className="grid grid-cols-1 gap-6 xl:grid-cols-3">

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

          <div className="mb-5 flex items-center justify-between">

            <div>

              <h2 className="font-bold text-slate-900">
                Project Risk
              </h2>

              <p className="text-xs text-slate-500">
                Current V2 model risk score
              </p>

            </div>

            <ShieldAlert className="h-5 w-5 text-slate-400" />

          </div>

          <RiskGauge
            score={riskScore}
          />

          <div className="mt-5 flex items-center justify-between border-t border-slate-100 pt-4">

            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Overall Risk
            </span>

            <RiskBadge
              level={riskLevel}
            />

          </div>

        </div>


        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm xl:col-span-2">

          <div className="mb-5 flex items-center justify-between">

            <div>

              <h2 className="font-bold text-slate-900">
                AI Prediction
              </h2>

              <p className="text-xs text-slate-500">
                POWERGRID V2 model output
              </p>

            </div>

            <Gauge className="h-5 w-5 text-blue-600" />

          </div>


          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">

            <PredictionCard
              title="Predicted Cost Overrun"
              value={`${formatNumber(
                costPrediction,
                2,
              )}%`}
              level={riskLevel}
              description="Expected cost deviation from the approved baseline."
            />


            <PredictionCard
              title="Predicted Schedule Delay"
              value={`${formatNumber(
                schedulePrediction,
                1,
              )} months`}
              level={scheduleRiskLevel}
              description="Expected schedule overrun relative to the planned duration."
            />

          </div>

        </div>

      </section>


      {/* PROJECT STATUS */}

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

        <div className="mb-6 flex items-center gap-3">

          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
            <CalendarDays className="h-5 w-5" />
          </div>

          <div>

            <h2 className="font-bold text-slate-900">
              Project Status
            </h2>

            <p className="text-xs text-slate-500">
              Current execution indicators from real project trajectory
            </p>

          </div>

        </div>


        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">

          <StatusItem
            label="Planned Duration"
            value={`${formatNumber(
              plannedDuration,
              1,
            )} months`}
          />


          <StatusItem
            label="Elapsed Duration"
            value={`${formatNumber(
              elapsedDuration,
              1,
            )} months`}
          />


          <StatusItem
            label="Progress Velocity"
            value={`${formatNumber(
              progressVelocity,
              2,
            )}% / month`}
          />


          <StatusItem
            label="Expenditure Velocity"
            value={`₹ ${formatNumber(
              expenditureVelocity,
              2,
            )} Cr / month`}
          />

        </div>

      </section>


      {/* EXECUTION BAR */}

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

        <div className="mb-4 flex items-center justify-between">

          <div>

            <h2 className="font-bold text-slate-900">
              Physical Progress
            </h2>

            <p className="text-xs text-slate-500">
              Current project execution progress
            </p>

          </div>

          <span className="font-mono text-lg font-bold text-blue-700">
            {formatNumber(
              physicalProgress,
              1,
            )}
            %
          </span>

        </div>


        <div className="h-4 overflow-hidden rounded-full bg-slate-100">

          <div
            className="h-full rounded-full bg-blue-600 transition-all duration-700"
            style={{
              width: `${Math.min(
                Math.max(
                  physicalProgress,
                  0,
                ),
                100,
              )}%`,
            }}
          />

        </div>

      </section>


      {/* RISK INTERPRETATION */}

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

        <div className="mb-5 flex items-center gap-3">

          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-50 text-amber-600">
            <AlertTriangle className="h-5 w-5" />
          </div>

          <div>

            <h2 className="font-bold text-slate-900">
              Risk Interpretation
            </h2>

            <p className="text-xs text-slate-500">
              Key indicators affecting project risk
            </p>

          </div>

        </div>


        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">

          <RiskIndicator
            label="Cost Exposure"
            value={`${formatNumber(
              costPrediction,
              2,
            )}%`}
            description="Predicted deviation from the approved cost."
            high={costPrediction >= 20}
          />


          <RiskIndicator
            label="Progress / Expenditure Gap"
            value={`${formatNumber(
              gap,
              2,
            )}%`}
            description="Difference between expenditure consumption and physical progress."
            high={gap >= 15}
          />


          <RiskIndicator
            label="Schedule Pressure"
            value={
              schedulePressure > 0
                ? `${formatNumber(
                    schedulePressure,
                    2,
                  )}x`
                : `${formatNumber(
                    schedulePrediction,
                    1,
                  )} mo`
            }
            description="Indicates pressure against the planned project schedule."
            high={
              schedulePressure >= 1.2 ||
              schedulePrediction >= 12
            }
          />

        </div>

      </section>


      {/* ACTIONS */}

      <section className="flex flex-col gap-3 sm:flex-row">

        <button
          type="button"
          onClick={() =>
            onNavigate('what_if')
          }
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700"
        >
          Run What-If Analysis
          <ChevronRightIcon />
        </button>


        <button
          type="button"
          onClick={() =>
            onNavigate('reports')
          }
          className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
        >
          Open Project Matrix
          <ChevronRightIcon />
        </button>

      </section>

    </div>
  );
}


/*
 * ============================================================
 * SUPPORTING COMPONENTS
 * ============================================================
 */


function MetricCard({
  icon,
  label,
  value,
  subtext,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  subtext: string;
}) {

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

      <div className="flex items-center justify-between">

        <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
          {label}
        </span>

        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
          {icon}
        </div>

      </div>


      <div className="mt-4 text-2xl font-extrabold tracking-tight text-slate-900">
        {value}
      </div>


      <div className="mt-1 text-xs text-slate-500">
        {subtext}
      </div>

    </div>
  );
}


function PredictionCard({
  title,
  value,
  level,
  description,
}: {
  title: string;
  value: string;
  level: 'LOW' | 'MEDIUM' | 'HIGH';
  description: string;
}) {

  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-5">

      <div className="flex items-center justify-between gap-3">

        <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
          {title}
        </span>

        <RiskBadge
          level={level}
        />

      </div>


      <div className="mt-4 font-mono text-3xl font-extrabold text-slate-900">
        {value}
      </div>


      <p className="mt-2 text-xs leading-5 text-slate-500">
        {description}
      </p>

    </div>
  );
}


function StatusItem({
  label,
  value,
}: {
  label: string;
  value: string;
}) {

  return (
    <div className="rounded-xl bg-slate-50 p-4">

      <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
        {label}
      </div>

      <div className="mt-2 font-mono text-sm font-bold text-slate-900">
        {value}
      </div>

    </div>
  );
}


function RiskIndicator({
  label,
  value,
  description,
  high,
}: {
  label: string;
  value: string;
  description: string;
  high: boolean;
}) {

  return (
    <div className="rounded-xl border border-slate-200 p-4">

      <div className="flex items-center justify-between gap-3">

        <span className="text-xs font-bold text-slate-700">
          {label}
        </span>

        <span
          className={
            high
              ? 'rounded-md bg-red-50 px-2 py-1 font-mono text-xs font-bold text-red-700'
              : 'rounded-md bg-emerald-50 px-2 py-1 font-mono text-xs font-bold text-emerald-700'
          }
        >
          {value}
        </span>

      </div>


      <p className="mt-3 text-xs leading-5 text-slate-500">
        {description}
      </p>

    </div>
  );
}


function ChevronRightIcon() {
  return (
    <span className="text-base">
      →
    </span>
  );
}