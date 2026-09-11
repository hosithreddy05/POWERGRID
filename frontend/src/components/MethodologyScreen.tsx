import {
  GitBranch,
  Calculator,
  Database,
  BarChart3,
  Ruler,
} from 'lucide-react';

import type { NavScreen } from '../types';

interface MethodologyScreenProps {
  onNavigate: (screen: NavScreen) => void;
}

export const MethodologyScreen = ({
  onNavigate,
}: MethodologyScreenProps) => {
  return (
    <div className="space-y-6 pb-12">

      {/* HEADER */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-[#091e3a] to-[#1e293b] text-white border border-slate-700/50 shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-md text-[10px] font-bold bg-blue-500/30 text-blue-200 uppercase tracking-widest font-mono border border-blue-400/30">
              Technical Documentation
            </span>

            <span className="text-xs text-slate-300 font-mono">
              ML Architecture Specifications
            </span>
          </div>

          <h2 className="text-xl font-bold tracking-tight">
            V2 Machine Learning Architecture & Methodology
          </h2>

          <p className="text-xs text-slate-300 max-w-2xl mt-1">
            Mathematical foundations, ensemble regression pipelines,
            feature engineering specifications, and validation integrity
            for the decision support platform.
          </p>
        </div>

        <button
          type="button"
          onClick={() => onNavigate('new_prediction')}
          className="px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs transition-all shadow-md flex items-center gap-2 font-mono"
        >
          <span className="material-symbols-outlined text-base">
            bolt
          </span>
          Run V2 Inference
        </button>
      </div>

      {/* SECTION 1 */}
      <section className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center gap-2">
          <GitBranch className="w-5 h-5 text-blue-600" />

          <div>
            <h3 className="font-bold text-sm text-slate-900 font-mono uppercase">
              1. Model Architecture & Core Ensembles
            </h3>

            <p className="text-xs text-slate-500 mt-0.5">
              Dual-regressor ensemble setup for cost and schedule prediction.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

          {/* COST REGRESSOR */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-3">

            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold text-blue-600 font-mono uppercase">
                Cost Regressor
              </span>

              <span className="material-symbols-outlined text-blue-600">
                forest
              </span>
            </div>

            <h4 className="font-bold text-sm text-slate-900 font-mono">
              Random Forest Regressor V2
            </h4>

            <p className="text-xs text-slate-600 leading-relaxed">
              Ensemble regression model targeting percentage cost overrun
              above the original sanctioned project budget.
            </p>

            <div className="pt-2 border-t border-slate-200 space-y-1 text-[10px] font-mono text-slate-600">
              <div>
                Target: <strong>Cost Overrun (%)</strong>
              </div>

              <div>
                Estimators: <strong>100 Decision Trees</strong>
              </div>

              <div>
                Key Driver: <strong>Expenditure-Progress Gap</strong>
              </div>
            </div>
          </div>

          {/* SCHEDULE REGRESSOR */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-3">

            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold text-indigo-600 font-mono uppercase">
                Schedule Regressor
              </span>

              <span className="material-symbols-outlined text-indigo-600">
                schedule
              </span>
            </div>

            <h4 className="font-bold text-sm text-slate-900 font-mono">
              Extra Trees Regressor V2
            </h4>

            <p className="text-xs text-slate-600 leading-relaxed">
              Extremely randomized trees ensemble predicting timeline
              delay in months beyond planned commissioning targets.
            </p>

            <div className="pt-2 border-t border-slate-200 space-y-1 text-[10px] font-mono text-slate-600">
              <div>
                Target: <strong>Schedule Delay (Months)</strong>
              </div>

              <div>
                Estimators: <strong>120 Decision Trees</strong>
              </div>

              <div>
                Key Driver: <strong>Schedule Pressure Ratio</strong>
              </div>
            </div>
          </div>

          {/* RISK ENGINE */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-3">

            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold text-emerald-600 font-mono uppercase">
                Explainable Risk Engine
              </span>

              <span className="material-symbols-outlined text-emerald-600">
                speed
              </span>
            </div>

            <h4 className="font-bold text-sm text-slate-900 font-mono">
              Multi-Factor Composite Score
            </h4>

            <p className="text-xs text-slate-600 leading-relaxed">
              Deterministic risk score from 0 to 100 combining cost,
              schedule, expenditure-progress, and schedule-pressure
              indicators.
            </p>

            <div className="pt-2 border-t border-slate-200 space-y-1 text-[10px] font-mono text-slate-600">
              <div>
                Scale: <strong>0–100</strong>
              </div>

              <div>
                Low: <strong>0–35</strong>
              </div>

              <div>
                Medium: <strong>36–65</strong>
              </div>

              <div>
                High: <strong>66–100</strong>
              </div>
            </div>
          </div>

        </div>
      </section>

      {/* SECTION 2 */}
      <section className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-4">

        <div className="flex items-center gap-2">
          <Calculator className="w-5 h-5 text-blue-600" />

          <div>
            <h3 className="font-bold text-sm text-slate-900 font-mono uppercase">
              2. Feature Engineering & Mathematical Formulas
            </h3>

            <p className="text-xs text-slate-500 mt-0.5">
              Derived indicators generated before model inference.
            </p>
          </div>
        </div>

        <div className="overflow-x-auto border border-slate-200 rounded-xl">

          <table className="w-full text-left text-xs font-mono">

            <thead className="bg-slate-50 text-slate-700 uppercase tracking-wider border-b border-slate-200 text-[10px]">

              <tr>
                <th className="py-3 px-3">
                  Feature
                </th>

                <th className="py-3 px-3">
                  Formula
                </th>

                <th className="py-3 px-3">
                  Unit
                </th>

                <th className="py-3 px-3">
                  Significance
                </th>
              </tr>

            </thead>

            <tbody className="divide-y divide-slate-100">

              <tr className="hover:bg-slate-50">
                <td className="py-3 px-3 font-bold text-blue-600">
                  expenditure_pct
                </td>

                <td className="py-3 px-3 text-slate-800">
                  (cumulative_expenditure / original_approved_cost) × 100
                </td>

                <td className="py-3 px-3 text-slate-500">
                  %
                </td>

                <td className="py-3 px-3 text-slate-600">
                  Proportion of sanctioned budget consumed.
                </td>
              </tr>

              <tr className="hover:bg-slate-50">
                <td className="py-3 px-3 font-bold text-blue-600">
                  expenditure_progress_gap
                </td>

                <td className="py-3 px-3 text-slate-800">
                  expenditure_pct − physical_progress_pct
                </td>

                <td className="py-3 px-3 text-slate-500">
                  % pts
                </td>

                <td className="py-3 px-3 text-slate-600">
                  Positive values indicate spending is ahead of physical work.
                </td>
              </tr>

              <tr className="hover:bg-slate-50">
                <td className="py-3 px-3 font-bold text-blue-600">
                  schedule_elapsed_pct
                </td>

                <td className="py-3 px-3 text-slate-800">
                  (elapsed_duration_months / planned_duration_months) × 100
                </td>

                <td className="py-3 px-3 text-slate-500">
                  %
                </td>

                <td className="py-3 px-3 text-slate-600">
                  Proportion of the approved execution window consumed.
                </td>
              </tr>

              <tr className="hover:bg-slate-50">
                <td className="py-3 px-3 font-bold text-blue-600">
                  schedule_pressure
                </td>

                <td className="py-3 px-3 text-slate-800">
                  elapsed_fraction / progress_fraction
                </td>

                <td className="py-3 px-3 text-slate-500">
                  x
                </td>

                <td className="py-3 px-3 text-slate-600">
                  Values above 1.0 indicate schedule drag.
                </td>
              </tr>

              <tr className="hover:bg-slate-50">
                <td className="py-3 px-3 font-bold text-blue-600">
                  progress_velocity_ratio
                </td>

                <td className="py-3 px-3 text-slate-800">
                  progress_velocity / (100 / planned_duration_months)
                </td>

                <td className="py-3 px-3 text-slate-500">
                  x
                </td>

                <td className="py-3 px-3 text-slate-600">
                  Actual execution velocity versus planned rate.
                </td>
              </tr>

              <tr className="hover:bg-slate-50">
                <td className="py-3 px-3 font-bold text-blue-600">
                  months_to_original_target
                </td>

                <td className="py-3 px-3 text-slate-800">
                  planned_duration_months − elapsed_duration_months
                </td>

                <td className="py-3 px-3 text-slate-500">
                  months
                </td>

                <td className="py-3 px-3 text-slate-600">
                  Remaining contractual calendar window.
                </td>
              </tr>

            </tbody>

          </table>

        </div>
      </section>

      {/* SECTION 3 */}
      <section className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-4">

        <div className="flex items-center gap-2">
          <Database className="w-5 h-5 text-blue-600" />

          <div>
            <h3 className="font-bold text-sm text-slate-900 font-mono uppercase">
              3. Dataset & Split Integrity
            </h3>

            <p className="text-xs text-slate-500 mt-0.5">
              Strict project-level partitioning prevents snapshot leakage.
            </p>
          </div>
        </div>

        <p className="text-xs text-slate-600 leading-relaxed">
          The validated corpus contains 92 projects and 668 snapshots.
          The project-level split contains 69 training projects and
          23 unseen evaluation projects.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
            <span className="text-[10px] text-slate-500 block font-mono">
              TOTAL CORPUS
            </span>

            <span className="text-lg font-bold text-slate-900 font-mono">
              92 Projects
            </span>

            <span className="text-[11px] text-slate-500 block">
              668 Snapshots
            </span>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
            <span className="text-[10px] text-slate-500 block font-mono">
              TRAINING
            </span>

            <span className="text-lg font-bold text-blue-600 font-mono">
              69 Projects
            </span>

            <span className="text-[11px] text-slate-500 block">
              75% project split
            </span>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
            <span className="text-[10px] text-slate-500 block font-mono">
              UNSEEN TEST
            </span>

            <span className="text-lg font-bold text-emerald-600 font-mono">
              23 Projects
            </span>

            <span className="text-[11px] text-slate-500 block">
              25% project split
            </span>
          </div>

        </div>
      </section>

      {/* SECTION 4 */}
      <section className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-4">

        <div className="flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-blue-600" />

          <div>
            <h3 className="font-bold text-sm text-slate-900 font-mono uppercase">
              4. Model Evaluation
            </h3>

            <p className="text-xs text-slate-500 mt-0.5">
              Out-of-sample evaluation across unseen projects.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

          {/* COST EVALUATION */}
          <div className="p-5 rounded-xl bg-slate-50 border border-slate-200">

            <span className="text-[10px] uppercase tracking-wider font-bold text-blue-600 font-mono">
              COST REGRESSION
            </span>

            <h4 className="font-bold text-sm text-slate-900 mt-1">
              Random Forest Regressor V2
            </h4>

            <div className="grid grid-cols-3 gap-2 mt-4">

              <div className="p-3 rounded-lg bg-white border border-slate-200">
                <span className="text-[9px] text-slate-500 block">
                  MAE
                </span>

                <strong className="text-sm font-mono">
                  ~2.51
                </strong>
              </div>

              <div className="p-3 rounded-lg bg-white border border-slate-200">
                <span className="text-[9px] text-slate-500 block">
                  RMSE
                </span>

                <strong className="text-sm font-mono">
                  ~6.91
                </strong>
              </div>

              <div className="p-3 rounded-lg bg-white border border-slate-200">
                <span className="text-[9px] text-slate-500 block">
                  R²
                </span>

                <strong className="text-sm font-mono">
                  ~-0.61
                </strong>
              </div>

            </div>
          </div>

          {/* SCHEDULE EVALUATION */}
          <div className="p-5 rounded-xl bg-slate-50 border border-slate-200">

            <span className="text-[10px] uppercase tracking-wider font-bold text-indigo-600 font-mono">
              SCHEDULE REGRESSION
            </span>

            <h4 className="font-bold text-sm text-slate-900 mt-1">
              Extra Trees Regressor V2
            </h4>

            <div className="grid grid-cols-3 gap-2 mt-4">

              <div className="p-3 rounded-lg bg-white border border-slate-200">
                <span className="text-[9px] text-slate-500 block">
                  MAE
                </span>

                <strong className="text-sm font-mono">
                  ~2.25
                </strong>
              </div>

              <div className="p-3 rounded-lg bg-white border border-slate-200">
                <span className="text-[9px] text-slate-500 block">
                  RMSE
                </span>

                <strong className="text-sm font-mono">
                  ~3.05
                </strong>
              </div>

              <div className="p-3 rounded-lg bg-white border border-slate-200">
                <span className="text-[9px] text-slate-500 block">
                  R²
                </span>

                <strong className="text-sm font-mono text-emerald-600">
                  ~0.94
                </strong>
              </div>

            </div>
          </div>

        </div>
      </section>

      {/* SECTION 5 */}
      <section className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-4">

        <div className="flex items-center gap-2">
          <Ruler className="w-5 h-5 text-blue-600" />

          <div>
            <h3 className="font-bold text-sm text-slate-900 font-mono uppercase">
              5. Explainable Risk Score Formulation
            </h3>

            <p className="text-xs text-slate-500 mt-0.5">
              Deterministic weighted composite score from 0–100.
            </p>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 font-mono">

          <h4 className="font-bold text-sm text-slate-900 mb-3">
            Composite Risk Score Components
          </h4>

          <ul className="space-y-2 text-xs text-slate-600 list-disc pl-5">

            <li>
              <strong>
                Predicted Cost Overrun — 35%
              </strong>
            </li>

            <li>
              <strong>
                Predicted Schedule Delay — 35%
              </strong>
            </li>

            <li>
              <strong>
                Expenditure-Progress Gap — 15%
              </strong>
            </li>

            <li>
              <strong>
                Schedule Pressure Ratio — 15%
              </strong>
            </li>

          </ul>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">

          <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs font-mono">
            <strong>LOW RISK</strong>
            <br />
            0–35
            <br />

            <span className="text-[10px]">
              Normal variance within standard buffers.
            </span>
          </div>

          <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs font-mono">
            <strong>MEDIUM RISK</strong>
            <br />
            36–65
            <br />

            <span className="text-[10px]">
              Moderate gap or schedule drift.
            </span>
          </div>

          <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-900 text-xs font-mono">
            <strong>HIGH RISK</strong>
            <br />
            66–100
            <br />

            <span className="text-[10px]">
              Severe overrun or schedule compression.
            </span>
          </div>

        </div>
      </section>

    </div>
  );
};
