import { useEffect, useMemo, useState } from 'react';

import {
  FileBarChart,
  Database,
  ShieldCheck,
  TrendingUp,
} from 'lucide-react';

import type {
  NavScreen,
  PortfolioStats,
} from '../types';

import {
  fetchProjectAnalyses,
} from '../services/api';


// ============================================================
// PROPS
// ============================================================

interface ReportsScreenProps {
  onNavigate: (
    screen: NavScreen,
  ) => void;

  onSelectProject?: (
    projectCode: string,
  ) => void;

  stats: PortfolioStats;
}


// ============================================================
// BACKEND TYPE
// ============================================================

interface BackendProjectAnalysis {
  project_code?: string;

  prediction?: {
    cost_risk_level?: string;
    cost_risk_score?: number;
  };
}


// ============================================================
// RISK NORMALIZATION
// ============================================================

function normalizeRisk(
  value?: string,
): 'LOW' | 'MEDIUM' | 'HIGH' {

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
// COMPONENT
// ============================================================

export const ReportsScreen = ({
  onNavigate,
  stats,
}: ReportsScreenProps) => {

  const [
    backendProjects,
    setBackendProjects,
  ] = useState<
    BackendProjectAnalysis[]
  >([]);

  const [
    loadingRisk,
    setLoadingRisk,
  ] = useState(true);

  const [
    riskError,
    setRiskError,
  ] = useState('');


  // ==========================================================
  // LOAD REAL BACKEND RISK RESULTS
  // ==========================================================

  useEffect(() => {

    let cancelled = false;

    const loadRiskData = async () => {

      try {

        setLoadingRisk(true);
        setRiskError('');

        const result =
          await fetchProjectAnalyses();

        if (!cancelled) {
          setBackendProjects(
            result as BackendProjectAnalysis[],
          );
        }

      } catch (error) {

        if (!cancelled) {

          setRiskError(
            error instanceof Error
              ? error.message
              : 'Unable to load backend risk data.',
          );
        }

      } finally {

        if (!cancelled) {
          setLoadingRisk(false);
        }
      }
    };

    loadRiskData();

    return () => {
      cancelled = true;
    };

  }, []);


  // ==========================================================
  // BACKEND RISK DISTRIBUTION
  // ==========================================================

  const riskStats = useMemo(() => {

    let low = 0;
    let medium = 0;
    let high = 0;

    for (
      const project of backendProjects
    ) {

      const risk =
        normalizeRisk(
          project.prediction?.cost_risk_level,
        );

      if (risk === 'HIGH') {
        high += 1;
      } else if (risk === 'MEDIUM') {
        medium += 1;
      } else {
        low += 1;
      }
    }

    const total =
      backendProjects.length;

    return {
      total,
      low,
      medium,
      high,
    };

  }, [
    backendProjects,
  ]);


  const displayedRiskStats =
    backendProjects.length > 0
      ? riskStats
      : {
          total:
            stats.validated_projects_count,
          low:
            stats.low_risk_count,
          medium:
            stats.medium_risk_count,
          high:
            stats.high_risk_count,
        };


  return (
    <div className="space-y-6 pb-12">

      {/* ================================================== */}
      {/* HEADER */}
      {/* ================================================== */}

      <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm">

        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">

          <div>

            <div className="flex items-center gap-2 mb-2">

              <span className="material-symbols-outlined text-blue-600">
                table_chart
              </span>

              <span className="text-[10px] font-bold uppercase tracking-widest text-blue-600 font-mono">
                Portfolio Intelligence
              </span>

            </div>

            <h2 className="text-xl font-bold text-slate-900">
              Project Intelligence Matrix
            </h2>

            <p className="text-xs text-slate-500 mt-1">
              Portfolio-level validation, model coverage,
              and project intelligence summary.
            </p>

          </div>


          <button
            type="button"
            onClick={() =>
              onNavigate('dashboard')
            }
            className="px-4 py-2 rounded-xl bg-slate-900 text-white text-xs font-semibold hover:bg-slate-800 transition-colors"
          >
            Back to Dashboard
          </button>

        </div>

      </div>


      {/* ================================================== */}
      {/* MODEL COVERAGE */}
      {/* ================================================== */}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">

        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm">

          <div className="flex items-center justify-between">

            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 font-mono">
              Validated Projects
            </span>

            <FileBarChart className="w-5 h-5 text-blue-600" />

          </div>

          <div className="mt-3 text-3xl font-extrabold font-mono text-slate-900">
            {stats.validated_projects_count}
          </div>

          <p className="text-[10px] text-slate-400 mt-1">
            Total validated POWERGRID project corpus
          </p>

        </div>


        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm">

          <div className="flex items-center justify-between">

            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 font-mono">
              Cost Training
            </span>

            <TrendingUp className="w-5 h-5 text-blue-600" />

          </div>

          <div className="mt-3 text-3xl font-extrabold font-mono text-slate-900">
            {stats.cost_training_count}
          </div>

          <p className="text-[10px] text-slate-400 mt-1">
            Projects available for cost model training
          </p>

        </div>


        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm">

          <div className="flex items-center justify-between">

            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 font-mono">
              Schedule Training
            </span>

            <Database className="w-5 h-5 text-indigo-600" />

          </div>

          <div className="mt-3 text-3xl font-extrabold font-mono text-slate-900">
            {stats.schedule_training_count}
          </div>

          <p className="text-[10px] text-slate-400 mt-1">
            Projects available for schedule modeling
          </p>

        </div>


        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm">

          <div className="flex items-center justify-between">

            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 font-mono">
              Unseen Evaluation
            </span>

            <ShieldCheck className="w-5 h-5 text-emerald-600" />

          </div>

          <div className="mt-3 text-3xl font-extrabold font-mono text-slate-900">
            {stats.unseen_test_count}
          </div>

          <p className="text-[10px] text-slate-400 mt-1">
            Project-level out-of-sample evaluation set
          </p>

        </div>

      </div>


      {/* ================================================== */}
      {/* RISK DISTRIBUTION */}
      {/* ================================================== */}

      <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm">

        <div className="flex items-center justify-between">

          <div>

            <h3 className="text-sm font-bold uppercase tracking-tight text-slate-900 font-mono">
              Risk Distribution
            </h3>

            <p className="text-xs text-slate-500 mt-1 mb-5">
              Current portfolio risk classification generated
              directly from the POWERGRID V2 backend.
            </p>

          </div>

          {loadingRisk && (
            <span className="text-[10px] font-mono text-blue-600">
              Syncing...
            </span>
          )}

        </div>


        {riskError && (
          <div className="mb-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-xs text-amber-800">
            Backend risk sync warning: {riskError}
          </div>
        )}


        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

          {/* LOW */}

          <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200">

            <span className="text-[10px] uppercase tracking-wider font-bold text-emerald-700 font-mono">
              Low Risk
            </span>

            <div className="text-2xl font-extrabold font-mono text-emerald-900 mt-2">
              {displayedRiskStats.low}
            </div>

            <p className="text-[10px] text-emerald-700 mt-1">
              Scores from 0–35
            </p>

          </div>


          {/* MEDIUM */}

          <div className="p-4 rounded-xl bg-amber-50 border border-amber-200">

            <span className="text-[10px] uppercase tracking-wider font-bold text-amber-700 font-mono">
              Medium Risk
            </span>

            <div className="text-2xl font-extrabold font-mono text-amber-900 mt-2">
              {displayedRiskStats.medium}
            </div>

            <p className="text-[10px] text-amber-700 mt-1">
              Scores from 36–65
            </p>

          </div>


          {/* HIGH */}

          <div className="p-4 rounded-xl bg-rose-50 border border-rose-200">

            <span className="text-[10px] uppercase tracking-wider font-bold text-rose-700 font-mono">
              High Risk
            </span>

            <div className="text-2xl font-extrabold font-mono text-rose-900 mt-2">
              {displayedRiskStats.high}
            </div>

            <p className="text-[10px] text-rose-700 mt-1">
              Scores from 66–100
            </p>

          </div>

        </div>

      </div>


      {/* ================================================== */}
      {/* VALIDATION INTEGRITY */}
      {/* ================================================== */}

      <div className="p-6 rounded-2xl bg-slate-50 border border-slate-200">

        <div className="flex items-start gap-3">

          <ShieldCheck className="w-5 h-5 text-blue-600 mt-0.5 shrink-0" />

          <div>

            <h3 className="text-sm font-bold text-slate-900 font-mono">
              Project-Level Validation Integrity
            </h3>

            <p className="text-xs text-slate-600 leading-relaxed mt-2">
              The POWERGRID V2 methodology uses
              project-level separation between training
              and unseen evaluation projects. This prevents
              snapshots from the same project appearing
              across both partitions.
            </p>


            <div className="flex flex-wrap gap-2 mt-4">

              <span className="px-2.5 py-1 rounded-lg bg-white border border-slate-200 text-[10px] font-mono text-slate-600">
                {stats.validated_projects_count}
                {' '}validated projects
              </span>

              <span className="px-2.5 py-1 rounded-lg bg-white border border-slate-200 text-[10px] font-mono text-slate-600">
                {stats.total_snapshots_count}
                {' '}snapshots
              </span>

              <span className="px-2.5 py-1 rounded-lg bg-white border border-slate-200 text-[10px] font-mono text-slate-600">
                {stats.unseen_test_count}
                {' '}unseen projects
              </span>

            </div>

          </div>

        </div>

      </div>

    </div>
  );
};
