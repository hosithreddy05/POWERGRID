import { useState } from 'react';

import type {
  NavScreen,
  ProjectCategory,
  PredictionResult,
} from '../types';

import { apiPredictNewProject } from '../services/api';

import { RiskBadge } from './RiskBadge';
import { RiskGauge } from './RiskGauge';

interface NewPredictionScreenProps {
  onNavigate: (screen: NavScreen) => void;
}

export const NewPredictionScreen = ({
  onNavigate,
}: NewPredictionScreenProps) => {
  const [form, setForm] = useState({
    project_code: '',
    project_name: '',
    project_category:
      'Transmission_System' as ProjectCategory,

    original_approved_cost: '',
    cumulative_expenditure: '',
    physical_progress_pct: '',
    planned_duration_months: '',
    elapsed_duration_months: '',
    progress_velocity: '',
    expenditure_velocity: '',
  });

  const [result, setResult] =
    useState<PredictionResult | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState('');

  const updateField = (
    field: keyof typeof form,
    value: string,
  ) => {
    setForm((previous) => ({
      ...previous,
      [field]: value,
    }));
  };

  // ========================================================
  // RUN REAL BACKEND PREDICTION
  // ========================================================

  const handlePredict = async () => {
    setError('');
    setResult(null);
    setLoading(true);

    try {
      const input = {
        original_approved_cost:
          Number(form.original_approved_cost) || 1000,

        project_category:
          form.project_category,

        cumulative_expenditure:
          Number(form.cumulative_expenditure) || 0,

        physical_progress_pct:
          Number(form.physical_progress_pct) || 0,

        planned_duration_months:
          Number(form.planned_duration_months) || 24,

        elapsed_duration_months:
          Number(form.elapsed_duration_months) || 0,

        progress_velocity:
          Number(form.progress_velocity) || 0,

        expenditure_velocity:
          Number(form.expenditure_velocity) || 0,
      };

      const prediction =
        await apiPredictNewProject(input);

      setResult(prediction);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to generate prediction.',
      );
    } finally {
      setLoading(false);
    }
  };

  // ========================================================
  // RESET
  // ========================================================

  const resetForm = () => {
    setForm({
      project_code: '',
      project_name: '',
      project_category:
        'Transmission_System',

      original_approved_cost: '',
      cumulative_expenditure: '',
      physical_progress_pct: '',
      planned_duration_months: '',
      elapsed_duration_months: '',
      progress_velocity: '',
      expenditure_velocity: '',
    });

    setResult(null);
    setError('');
  };

  const inputClass =
    'w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100';

  return (
    <div className="space-y-6 pb-12">

      {/* ================================================== */}
      {/* HEADER */}
      {/* ================================================== */}

      <div className="p-6 rounded-2xl bg-gradient-to-r from-[#091e3a] to-[#133363] text-white border border-slate-700/50 shadow-sm">

        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">

          <div>
            <div className="text-[10px] font-bold uppercase tracking-widest text-blue-200 font-mono">
              POWERGRID PROJECT INTELLIGENCE
            </div>

            <h2 className="text-2xl font-bold tracking-tight mt-2">
              New Project Prediction
            </h2>

            <p className="text-sm text-slate-300 mt-1 max-w-2xl">
              Enter current project execution parameters
              to generate a V2 ML cost, schedule and risk
              prediction.
            </p>
          </div>

          <div className="px-3 py-2 rounded-xl bg-white/10 border border-white/10 text-xs font-mono text-blue-100">
            V2 ML ENGINE
          </div>

        </div>
      </div>

      {/* ================================================== */}
      {/* INPUT FORM */}
      {/* ================================================== */}

      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm">

        <div className="p-6 border-b border-slate-100">
          <h3 className="text-lg font-bold text-slate-900">
            Project Parameters
          </h3>

          <p className="text-xs text-slate-500 mt-1">
            Provide the current execution state of the
            project.
          </p>
        </div>

        <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-5">

          {/* PROJECT CODE */}

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
              Project Code
            </label>

            <input
              value={form.project_code}
              onChange={(event) =>
                updateField(
                  'project_code',
                  event.target.value,
                )
              }
              placeholder="NEW-PROJECT"
              className={inputClass}
            />
          </div>

          {/* PROJECT NAME */}

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
              Project Name
            </label>

            <input
              value={form.project_name}
              onChange={(event) =>
                updateField(
                  'project_name',
                  event.target.value,
                )
              }
              placeholder="New POWERGRID Project"
              className={inputClass}
            />
          </div>

          {/* CATEGORY */}

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
              Project Category
            </label>

            <select
              value={form.project_category}
              onChange={(event) =>
                updateField(
                  'project_category',
                  event.target.value,
                )
              }
              className={inputClass}
            >
              <option value="Transmission_System">
                Transmission System
              </option>

              <option value="Substation_Grid_Equipment">
                Substation / Grid Equipment
              </option>

              <option value="Rural_Electrification">
                Rural Electrification
              </option>

              <option value="Renewable_Integration">
                Renewable Integration
              </option>

              <option value="HVDC_Interconnector">
                HVDC Interconnector
              </option>

              <option value="Grid_Modernization">
                Grid Modernization
              </option>
            </select>
          </div>

          {/* APPROVED COST */}

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
              Original Approved Cost (₹ Cr)
            </label>

            <input
              type="number"
              min="0"
              value={form.original_approved_cost}
              onChange={(event) =>
                updateField(
                  'original_approved_cost',
                  event.target.value,
                )
              }
              placeholder="500"
              className={inputClass}
            />
          </div>

          {/* EXPENDITURE */}

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
              Cumulative Expenditure (₹ Cr)
            </label>

            <input
              type="number"
              min="0"
              value={form.cumulative_expenditure}
              onChange={(event) =>
                updateField(
                  'cumulative_expenditure',
                  event.target.value,
                )
              }
              placeholder="250"
              className={inputClass}
            />
          </div>

          {/* PHYSICAL PROGRESS */}

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
              Physical Progress (%)
            </label>

            <input
              type="number"
              min="0"
              max="100"
              value={form.physical_progress_pct}
              onChange={(event) =>
                updateField(
                  'physical_progress_pct',
                  event.target.value,
                )
              }
              placeholder="50"
              className={inputClass}
            />
          </div>

          {/* PLANNED DURATION */}

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
              Planned Duration (Months)
            </label>

            <input
              type="number"
              min="1"
              value={form.planned_duration_months}
              onChange={(event) =>
                updateField(
                  'planned_duration_months',
                  event.target.value,
                )
              }
              placeholder="24"
              className={inputClass}
            />
          </div>

          {/* ELAPSED DURATION */}

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
              Elapsed Duration (Months)
            </label>

            <input
              type="number"
              min="0"
              value={form.elapsed_duration_months}
              onChange={(event) =>
                updateField(
                  'elapsed_duration_months',
                  event.target.value,
                )
              }
              placeholder="12"
              className={inputClass}
            />
          </div>

          {/* PROGRESS VELOCITY */}

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
              Progress Velocity (% / Month)
            </label>

            <input
              type="number"
              min="0"
              step="0.1"
              value={form.progress_velocity}
              onChange={(event) =>
                updateField(
                  'progress_velocity',
                  event.target.value,
                )
              }
              placeholder="4.2"
              className={inputClass}
            />
          </div>

          {/* EXPENDITURE VELOCITY */}

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
              Expenditure Velocity (₹ Cr / Month)
            </label>

            <input
              type="number"
              min="0"
              step="0.1"
              value={form.expenditure_velocity}
              onChange={(event) =>
                updateField(
                  'expenditure_velocity',
                  event.target.value,
                )
              }
              placeholder="20"
              className={inputClass}
            />
          </div>

        </div>

        {/* BUTTONS */}

        <div className="px-6 pb-6 flex flex-col sm:flex-row gap-3">

          <button
            type="button"
            onClick={handlePredict}
            disabled={loading}
            className="flex-1 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-bold py-3 px-5 transition"
          >
            {loading
              ? 'Running V2 Prediction...'
              : 'Generate Prediction'}
          </button>

          <button
            type="button"
            onClick={resetForm}
            disabled={loading}
            className="rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 font-bold py-3 px-5 transition"
          >
            Reset
          </button>

        </div>

      </div>

      {/* ================================================== */}
      {/* ERROR */}
      {/* ================================================== */}

      {error && (
        <div className="p-4 rounded-xl border border-red-200 bg-red-50 text-red-700 text-sm">
          <div className="font-bold">
            Prediction failed
          </div>

          <div className="mt-1">
            {error}
          </div>
        </div>
      )}

      {/* ================================================== */}
      {/* RESULT */}
      {/* ================================================== */}

      {result && (
        <div className="space-y-6">

          {/* RESULT HEADER */}

          <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm">

            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">

              <div>
                <div className="text-[10px] font-bold uppercase tracking-widest text-slate-400 font-mono">
                  V2 PREDICTION RESULT
                </div>

                <h3 className="text-xl font-bold text-slate-900 mt-1">
                  {form.project_name ||
                    'New POWERGRID Project'}
                </h3>

                <p className="text-xs text-slate-500 mt-1 font-mono">
                  {form.project_code ||
                    'NEW-PROJECT'}
                </p>
              </div>

              <RiskBadge
                level={result.overall_risk_level}
              />

            </div>
          </div>

          {/* PRIMARY METRICS */}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

            {/* COST */}

            <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm">

              <div className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Predicted Cost Overrun
              </div>

              <div className="mt-3 text-3xl font-extrabold font-mono text-slate-900">
                {result.cost_prediction_pct.toFixed(2)}%
              </div>

              <div className="mt-2 text-xs text-slate-500">
                V2 model prediction
              </div>

            </div>

            {/* SCHEDULE */}

            <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm">

              <div className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Predicted Schedule Delay
              </div>

              <div className="mt-3 text-3xl font-extrabold font-mono text-slate-900">
                {result.schedule_prediction_months.toFixed(2)}
              </div>

              <div className="mt-2 text-xs text-slate-500">
                months
              </div>

            </div>

            {/* RISK */}

            <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm">

              <div className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Overall Risk
              </div>

              <div className="mt-3 flex items-center gap-4">

                <RiskGauge
                  score={result.risk_score}
                />

                <div>
                  <div className="text-2xl font-extrabold font-mono text-slate-900">
                    {result.risk_score}
                  </div>

                  <div className="text-xs text-slate-500">
                    Risk score
                  </div>
                </div>

              </div>

            </div>

          </div>

          {/* RISK LEVELS */}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

            <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm">

              <div className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">
                Cost Risk
              </div>

              <RiskBadge
                level={result.cost_risk_level}
              />

            </div>

            <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm">

              <div className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">
                Schedule Risk
              </div>

              <RiskBadge
                level={result.schedule_risk_level}
              />

            </div>

            <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm">

              <div className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">
                Overall Risk
              </div>

              <RiskBadge
                level={result.overall_risk_level}
              />

            </div>

          </div>

          {/* DERIVED FEATURES */}

          <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm">

            <div className="mb-5">

              <h3 className="text-lg font-bold text-slate-900">
                Derived Execution Indicators
              </h3>

              <p className="text-xs text-slate-500 mt-1">
                Features calculated by the POWERGRID V2
                pipeline.
              </p>

            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">

              <div>
                <div className="text-xs text-slate-500">
                  Expenditure
                </div>

                <div className="font-bold font-mono mt-1">
                  {result.derived_features.expenditure_pct.toFixed(2)}%
                </div>
              </div>

              <div>
                <div className="text-xs text-slate-500">
                  Physical Progress
                </div>

                <div className="font-bold font-mono mt-1">
                  {result.derived_features.physical_progress_pct.toFixed(2)}%
                </div>
              </div>

              <div>
                <div className="text-xs text-slate-500">
                  Expenditure / Progress Gap
                </div>

                <div className="font-bold font-mono mt-1">
                  {result.derived_features.expenditure_progress_gap.toFixed(2)}%
                </div>
              </div>

              <div>
                <div className="text-xs text-slate-500">
                  Schedule Pressure
                </div>

                <div className="font-bold font-mono mt-1">
                  {result.derived_features.schedule_pressure.toFixed(2)}x
                </div>
              </div>

            </div>

          </div>

          {/* RISK REASONS */}

          <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm">

            <h3 className="text-lg font-bold text-slate-900">
              Risk Assessment
            </h3>

            <div className="mt-4">

              {result.supporting_indicators.length === 0 ? (
                <div className="text-sm text-slate-500">
                  The V2 backend returned no additional
                  supporting indicators.
                </div>
              ) : (
                <div className="space-y-3">
                  {result.supporting_indicators.map(
                    (indicator) => (
                      <div
                        key={indicator.key}
                        className="p-4 rounded-xl bg-slate-50 border border-slate-100"
                      >
                        <div className="font-bold text-sm">
                          {indicator.name}
                        </div>

                        <div className="text-xs text-slate-500 mt-1">
                          {indicator.explanation}
                        </div>
                      </div>
                    ),
                  )}
                </div>
              )}

            </div>

          </div>

          {/* NAVIGATION */}

          <div className="flex flex-col sm:flex-row gap-3">

            <button
              type="button"
              onClick={() =>
                onNavigate('dashboard')
              }
              className="rounded-xl border border-slate-200 bg-white hover:bg-slate-50 px-5 py-3 text-sm font-bold text-slate-700"
            >
              Back to Dashboard
            </button>

            <button
              type="button"
              onClick={() =>
                onNavigate('project_intelligence')
              }
              className="rounded-xl bg-slate-900 hover:bg-slate-800 px-5 py-3 text-sm font-bold text-white"
            >
              Open Project Intelligence
            </button>

          </div>

        </div>
      )}

    </div>
  );
};
