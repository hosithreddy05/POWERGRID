import { useEffect, useMemo, useState } from 'react';

import type {
  NavScreen,
  PowerGridProject,
  PredictionResult,
  WhatIfComparison,
} from '../types';

import {
  apiAnalyzeWhatIf,
  fetchProjects,
} from '../services/api';

import { RiskBadge } from './RiskBadge';

interface WhatIfScreenProps {
  onNavigate: (screen: NavScreen) => void;
  selectedProjectCode: string;
}

export const WhatIfScreen = ({
  onNavigate,
  selectedProjectCode,
}: WhatIfScreenProps) => {
  const [projects, setProjects] = useState<PowerGridProject[]>([]);
  const [loadingProjects, setLoadingProjects] = useState(true);
  const [projectError, setProjectError] = useState('');

  const [projectCode, setProjectCode] =
    useState(selectedProjectCode);

  const [physicalProgress, setPhysicalProgress] =
    useState('');

  const [cumulativeExpenditure, setCumulativeExpenditure] =
    useState('');

  const [plannedDuration, setPlannedDuration] =
    useState('');

  const [elapsedDuration, setElapsedDuration] =
    useState('');

  const [progressVelocity, setProgressVelocity] =
    useState('');

  const [expenditureVelocity, setExpenditureVelocity] =
    useState('');

  const [result, setResult] =
    useState<WhatIfComparison | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // ==========================================================
  // LOAD PROJECTS FROM BACKEND
  // ==========================================================

  useEffect(() => {
    let cancelled = false;

    const loadProjects = async () => {
      setLoadingProjects(true);
      setProjectError('');

      try {
        const data = await fetchProjects();

        if (cancelled) {
          return;
        }

        setProjects(data);

        if (data.length > 0) {
          const preferred =
            data.find(
              (p) =>
                p.project_code === selectedProjectCode,
            ) ?? data[0];

          setProjectCode(
            preferred.project_code,
          );
        }
      } catch (err) {
        if (!cancelled) {
          setProjectError(
            err instanceof Error
              ? err.message
              : 'Unable to load projects.',
          );
        }
      } finally {
        if (!cancelled) {
          setLoadingProjects(false);
        }
      }
    };

    loadProjects();

    return () => {
      cancelled = true;
    };
  }, [selectedProjectCode]);

  // ==========================================================
  // SELECTED PROJECT
  // ==========================================================

  const selectedProject =
    useMemo(
      () =>
        projects.find(
          (p) =>
            p.project_code === projectCode,
        ) ??
        projects.find(
          (p) =>
            p.project_code ===
            selectedProjectCode,
        ) ??
        projects[0],
      [
        projects,
        projectCode,
        selectedProjectCode,
      ],
    );

  // ==========================================================
  // PROJECT CHANGE
  // ==========================================================

  const loadProject = (
    code: string,
  ) => {
    setProjectCode(code);

    setPhysicalProgress('');
    setCumulativeExpenditure('');
    setPlannedDuration('');
    setElapsedDuration('');
    setProgressVelocity('');
    setExpenditureVelocity('');

    setResult(null);
    setError('');
  };

  // ==========================================================
  // RUN WHAT-IF
  // ==========================================================

  const runScenario = async () => {
    if (!selectedProject) {
      setError(
        'Please select a POWERGRID project.',
      );
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const changes: Record<string, number> = {};

      if (physicalProgress.trim() !== '') {
        changes.physical_progress_pct =
          Number(physicalProgress);
      }

      if (
        cumulativeExpenditure.trim() !== ''
      ) {
        changes.cumulative_expenditure =
          Number(cumulativeExpenditure);
      }

      if (plannedDuration.trim() !== '') {
        changes.planned_duration_months =
          Number(plannedDuration);
      }

      if (elapsedDuration.trim() !== '') {
        changes.elapsed_duration_months =
          Number(elapsedDuration);
      }

      if (progressVelocity.trim() !== '') {
        changes.progress_velocity =
          Number(progressVelocity);
      }

      if (
        expenditureVelocity.trim() !== ''
      ) {
        changes.expenditure_velocity =
          Number(expenditureVelocity);
      }

      for (const [key, value] of Object.entries(
        changes,
      )) {
        if (!Number.isFinite(value)) {
          delete changes[key];
        }
      }

      const analysis =
        await apiAnalyzeWhatIf(
          selectedProject.project_code,
          changes,
        );

      setResult(analysis);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'What-If analysis failed.',
      );
    } finally {
      setLoading(false);
    }
  };

  // ==========================================================
  // RESET
  // ==========================================================

  const resetScenario = () => {
    setPhysicalProgress('');
    setCumulativeExpenditure('');
    setPlannedDuration('');
    setElapsedDuration('');
    setProgressVelocity('');
    setExpenditureVelocity('');

    setResult(null);
    setError('');
  };

  const inputClass =
    'w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100';

  // ==========================================================
  // LOADING
  // ==========================================================

  if (loadingProjects) {
    return (
      <div className="flex min-h-[400px] items-center justify-center">
        <div className="text-sm text-slate-500">
          Loading POWERGRID projects...
        </div>
      </div>
    );
  }

  // ==========================================================
  // ERROR LOADING PROJECTS
  // ==========================================================

  if (
    projectError &&
    projects.length === 0
  ) {
    return (
      <div className="space-y-5">
        <div className="rounded-2xl border border-red-200 bg-red-50 p-6">
          <div className="font-bold text-red-700">
            Unable to load POWERGRID projects
          </div>

          <div className="mt-2 text-sm text-red-600">
            {projectError}
          </div>
        </div>

        <button
          type="button"
          onClick={() =>
            onNavigate('dashboard')
          }
          className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-bold text-white"
        >
          Back to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-12">

      {/* HEADER */}

      <div className="rounded-2xl bg-gradient-to-r from-[#091e3a] to-[#133363] p-6 text-white shadow-sm">
        <div className="text-[10px] font-bold uppercase tracking-widest text-blue-200 font-mono">
          POWERGRID PROJECT INTELLIGENCE
        </div>

        <h2 className="mt-2 text-2xl font-bold tracking-tight">
          What-If Simulator
        </h2>

        <p className="mt-1 max-w-3xl text-sm text-slate-300">
          Change project execution parameters and
          compare the scenario against the current
          baseline using the Python V2 risk engine.
        </p>
      </div>

      {/* PROJECT */}

      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <label className="mb-2 block text-xs font-bold uppercase tracking-wider text-slate-500">
          Select POWERGRID Project
        </label>

        <select
          value={
            selectedProject?.project_code ??
            ''
          }
          onChange={(e) =>
            loadProject(e.target.value)
          }
          className={inputClass}
        >
          {projects.map((project) => (
            <option
              key={project.project_code}
              value={project.project_code}
            >
              {project.project_code}
              {' — '}
              {project.project_name}
            </option>
          ))}
        </select>

        {selectedProject && (
          <div className="mt-3 flex flex-wrap gap-4 text-xs text-slate-500">
            <span>
              <strong>Category:</strong>{' '}
              {selectedProject.project_category}
            </span>

            <span>
              <strong>Region:</strong>{' '}
              {selectedProject.region}
            </span>

            <span>
              <strong>Progress:</strong>{' '}
              {selectedProject.physical_progress_pct.toFixed(
                1,
              )}
              %
            </span>

            <span>
              <strong>Cost:</strong> ₹{' '}
              {selectedProject.original_approved_cost.toFixed(
                2,
              )}{' '}
              Cr
            </span>
          </div>
        )}
      </div>

      {/* INPUTS */}

      <div className="rounded-2xl border border-slate-200 bg-white shadow-sm">

        <div className="border-b border-slate-100 p-6">
          <h3 className="text-lg font-bold text-slate-900">
            Scenario Changes
          </h3>

          <p className="mt-1 text-xs text-slate-500">
            Enter only the values you want to
            change. Empty fields keep the current
            project value.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-5 p-6 md:grid-cols-2">

          <InputField
            label="Physical Progress (%)"
            value={physicalProgress}
            onChange={setPhysicalProgress}
            placeholder={
              selectedProject
                ? selectedProject.physical_progress_pct.toFixed(
                    1,
                  )
                : '70'
            }
            min="0"
            max="100"
            step="0.1"
          />

          <InputField
            label="Cumulative Expenditure (₹ Cr)"
            value={cumulativeExpenditure}
            onChange={setCumulativeExpenditure}
            placeholder={
              selectedProject
                ? selectedProject.cumulative_expenditure.toFixed(
                    2,
                  )
                : '300'
            }
            min="0"
            step="0.01"
          />

          <InputField
            label="Planned Duration (Months)"
            value={plannedDuration}
            onChange={setPlannedDuration}
            placeholder={
              selectedProject
                ? selectedProject.planned_duration_months.toFixed(
                    1,
                  )
                : '30'
            }
            min="1"
            step="0.1"
          />

          <InputField
            label="Elapsed Duration (Months)"
            value={elapsedDuration}
            onChange={setElapsedDuration}
            placeholder={
              selectedProject
                ? selectedProject.elapsed_duration_months.toFixed(
                    1,
                  )
                : '20'
            }
            min="0"
            step="0.1"
          />

          <InputField
            label="Progress Velocity (% / Month)"
            value={progressVelocity}
            onChange={setProgressVelocity}
            placeholder={
              selectedProject
                ? selectedProject.progress_velocity.toFixed(
                    2,
                  )
                : '3.5'
            }
            min="0"
            step="0.01"
          />

          <InputField
            label="Expenditure Velocity (₹ Cr / Month)"
            value={expenditureVelocity}
            onChange={setExpenditureVelocity}
            placeholder={
              selectedProject
                ? selectedProject.expenditure_velocity.toFixed(
                    2,
                  )
                : '15'
            }
            min="0"
            step="0.01"
          />

        </div>

        <div className="flex flex-col gap-3 px-6 pb-6 sm:flex-row">

          <button
            type="button"
            onClick={runScenario}
            disabled={
              loading ||
              !selectedProject
            }
            className="flex-1 rounded-xl bg-blue-600 px-5 py-3 text-sm font-bold text-white hover:bg-blue-700 disabled:bg-blue-300"
          >
            {loading
              ? 'Running Python V2 Analysis...'
              : 'Run What-If Analysis'}
          </button>

          <button
            type="button"
            onClick={resetScenario}
            disabled={loading}
            className="rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-bold text-slate-700 hover:bg-slate-50"
          >
            Reset
          </button>

        </div>
      </div>

      {/* ERROR */}

      {error && (
        <div className="rounded-2xl border border-red-200 bg-red-50 p-5">
          <div className="font-bold text-red-700">
            What-If analysis failed
          </div>

          <div className="mt-1 text-sm text-red-600">
            {error}
          </div>
        </div>
      )}

      {/* RESULTS */}

      {result && (
        <div className="space-y-6">

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">

              <div>
                <div className="font-mono text-[10px] font-bold uppercase tracking-widest text-slate-400">
                  PYTHON V2 WHAT-IF RESULT
                </div>

                <h3 className="mt-1 text-xl font-bold text-slate-900">
                  {selectedProject?.project_name ??
                    result.project_code}
                </h3>

                <div className="mt-1 font-mono text-xs text-slate-500">
                  {result.project_code}
                </div>
              </div>

              <RiskBadge
                level={
                  result.scenario_prediction
                    .overall_risk_level
                }
              />

            </div>
          </div>

          {/* BASELINE / SCENARIO */}

          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">

            <ComparisonCard
              title="Baseline"
              prediction={
                result.baseline_prediction
              }
            />

            <ComparisonCard
              title="Scenario"
              prediction={
                result.scenario_prediction
              }
              highlighted
            />

          </div>

          {/* IMPACT */}

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

            <h3 className="text-lg font-bold text-slate-900">
              Scenario Impact
            </h3>

            <p className="mt-1 text-xs text-slate-500">
              Difference between scenario and
              baseline.
            </p>

            <div className="mt-5 grid grid-cols-1 gap-4 md:grid-cols-3">

              <DeltaCard
                label="Cost Change"
                value={`${formatSigned(
                  result.deltas.cost_diff_pct,
                )}%`}
                improved={
                  result.deltas.cost_improved
                }
              />

              <DeltaCard
                label="Schedule Change"
                value={`${formatSigned(
                  result.deltas.schedule_diff_months,
                )} months`}
                improved={
                  result.deltas.schedule_improved
                }
              />

              <DeltaCard
                label="Risk Score Change"
                value={formatSigned(
                  result.deltas.risk_score_diff,
                )}
                improved={
                  result.deltas.risk_improved
                }
              />

            </div>
          </div>

          {/* INDICATORS */}

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

            <h3 className="text-lg font-bold text-slate-900">
              Scenario Indicators
            </h3>

            <div className="mt-5 grid grid-cols-2 gap-5 md:grid-cols-4">

              <Metric
                label="Expenditure"
                value={`${result.scenario_prediction.derived_features.expenditure_pct.toFixed(
                  2,
                )}%`}
              />

              <Metric
                label="Physical Progress"
                value={`${result.scenario_prediction.derived_features.physical_progress_pct.toFixed(
                  2,
                )}%`}
              />

              <Metric
                label="Expenditure / Progress Gap"
                value={`${result.scenario_prediction.derived_features.expenditure_progress_gap.toFixed(
                  2,
                )}%`}
              />

              <Metric
                label="Schedule Pressure"
                value={`${result.scenario_prediction.derived_features.schedule_pressure.toFixed(
                  2,
                )}x`}
              />

            </div>
          </div>

          {/* RISK REASONS */}

          <RiskReasons
            prediction={
              result.scenario_prediction
            }
          />

          {/* NAVIGATION */}

          <div className="flex flex-col gap-3 sm:flex-row">

            <button
              type="button"
              onClick={() =>
                onNavigate('dashboard')
              }
              className="rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-bold text-slate-700 hover:bg-slate-50"
            >
              Back to Dashboard
            </button>

            <button
              type="button"
              onClick={() =>
                onNavigate(
                  'project_intelligence',
                )
              }
              className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-bold text-white hover:bg-slate-800"
            >
              Open Project Intelligence
            </button>

          </div>

        </div>
      )}
    </div>
  );
};


// ============================================================
// INPUT FIELD
// ============================================================

function InputField({
  label,
  value,
  onChange,
  placeholder,
  min,
  max,
  step,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
  min?: string;
  max?: string;
  step?: string;
}) {
  return (
    <div>
      <label className="mb-2 block text-xs font-bold uppercase tracking-wider text-slate-500">
        {label}
      </label>

      <input
        type="number"
        value={value}
        onChange={(e) =>
          onChange(e.target.value)
        }
        placeholder={placeholder}
        min={min}
        max={max}
        step={step}
        className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
      />
    </div>
  );
}


// ============================================================
// COMPARISON CARD
// ============================================================

function ComparisonCard({
  title,
  prediction,
  highlighted = false,
}: {
  title: string;
  prediction: PredictionResult;
  highlighted?: boolean;
}) {
  return (
    <div
      className={`rounded-2xl border bg-white p-6 shadow-sm ${
        highlighted
          ? 'border-blue-200'
          : 'border-slate-200'
      }`}
    >

      <div
        className={`text-xs font-bold uppercase tracking-wider ${
          highlighted
            ? 'text-blue-600'
            : 'text-slate-400'
        }`}
      >
        {title}
      </div>

      <div className="mt-5 space-y-5">

        <Metric
          label="Cost Overrun"
          value={`${prediction.cost_prediction_pct.toFixed(
            2,
          )}%`}
        />

        <Metric
          label="Schedule Delay"
          value={`${prediction.schedule_prediction_months.toFixed(
            2,
          )} months`}
        />

        <Metric
          label="Risk Score"
          value={`${prediction.risk_score}`}
        />

        <RiskBadge
          level={
            prediction.overall_risk_level
          }
        />

      </div>
    </div>
  );
}


// ============================================================
// METRIC
// ============================================================

function Metric({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div>
      <div className="text-xs text-slate-500">
        {label}
      </div>

      <div className="mt-1 font-mono text-lg font-bold text-slate-900">
        {value}
      </div>
    </div>
  );
}


// ============================================================
// DELTA
// ============================================================

function DeltaCard({
  label,
  value,
  improved,
}: {
  label: string;
  value: string;
  improved: boolean;
}) {
  return (
    <div className="rounded-xl border border-slate-100 bg-slate-50 p-4">

      <div className="text-xs text-slate-500">
        {label}
      </div>

      <div className="mt-2 font-mono text-xl font-extrabold text-slate-900">
        {value}
      </div>

      <div
        className={`mt-1 text-xs font-bold ${
          improved
            ? 'text-emerald-600'
            : 'text-red-600'
        }`}
      >
        {improved
          ? 'Improved'
          : 'Worsened'}
      </div>

    </div>
  );
}


// ============================================================
// RISK REASONS
// ============================================================

function RiskReasons({
  prediction,
}: {
  prediction: PredictionResult;
}) {
  const indicators =
    prediction.supporting_indicators ?? [];

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

      <h3 className="text-lg font-bold text-slate-900">
        Scenario Risk Assessment
      </h3>

      {indicators.length > 0 ? (
        <div className="mt-4 space-y-3">
          {indicators.map(
            (indicator) => (
              <div
                key={indicator.key}
                className="rounded-xl border border-slate-100 bg-slate-50 p-4"
              >
                <div className="text-sm font-bold text-slate-800">
                  {indicator.name}
                </div>

                <div className="mt-1 text-sm text-slate-600">
                  {indicator.interpretation}
                </div>
              </div>
            ),
          )}
        </div>
      ) : (
        <div className="mt-4 rounded-xl bg-emerald-50 p-4 text-sm text-emerald-700">
          No additional risk indicators are
          available for this scenario.
        </div>
      )}
    </div>
  );
}


// ============================================================
// FORMAT SIGNED
// ============================================================

function formatSigned(
  value: number,
): string {
  if (value > 0) {
    return `+${value.toFixed(2)}`;
  }

  if (value < 0) {
    return value.toFixed(2);
  }

  return '0.00';
}
