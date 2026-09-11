import React from 'react';
import type { NavScreen, PowerGridProject } from '../types';

interface HeaderProps {
  onNavigate: (screen: NavScreen) => void;
  onSelectProject?: (code: string) => void;
  projects: PowerGridProject[];
  activeScreen: NavScreen;
}

const SCREEN_TITLES: Record<
  NavScreen,
  { title: string; subtitle: string }
> = {
  dashboard: {
    title: 'Executive Portfolio Dashboard',
    subtitle:
      'Cost overruns, schedule delays, and risk analytics across active packages',
  },
  new_prediction: {
    title: 'New Project Prediction',
    subtitle:
      'Machine learning cost, schedule, and risk inference on custom parameters',
  },
  project_intelligence: {
    title: 'Project Intelligence Deep-Dive',
    subtitle:
      'Detailed trajectory analysis, risk drivers, and historical performance snapshots',
  },
  what_if: {
    title: 'What-If Scenario Simulator',
    subtitle:
      'Interactive sensitivity analysis and management intervention simulation',
  },
  reports: {
    title: 'Project Intelligence Matrix',
    subtitle:
      'Comprehensive multi-parameter project data table and CSV export',
  },
  methodology: {
    title: 'Model & Methodology Specifications',
    subtitle:
      'Ensemble regression architectures, feature engineering, and validation integrity',
  },
};

export const Header: React.FC<HeaderProps> = ({
  onNavigate,
  onSelectProject,
  projects,
  activeScreen,
}) => {
  const info =
    SCREEN_TITLES[activeScreen] || SCREEN_TITLES.dashboard;

  return (
    <header className="sticky top-0 z-30 bg-white/95 backdrop-blur-md border-b border-slate-200 px-6 py-2.5 flex flex-col md:flex-row md:items-center md:justify-between gap-3 shadow-xs">
      <div className="space-y-0.5">
        <h1 className="text-base font-bold text-[#091e3a] tracking-tight font-mono">
          {info.title}
        </h1>

        <p className="text-[11px] text-slate-500 font-medium">
          {info.subtitle}
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        {onSelectProject && (
          <select
            aria-label="Quick Select Project"
            defaultValue=""
            onChange={(e) => {
              if (e.target.value) {
                onSelectProject(e.target.value);
                onNavigate('project_intelligence');
              }
            }}
            className="text-xs bg-slate-50 border border-slate-300 text-slate-700 font-medium rounded-xl px-2.5 py-1.5 pr-7 outline-none hover:bg-slate-100 focus:ring-2 focus:ring-blue-500 transition-all cursor-pointer font-mono"
          >
            <option value="" disabled>
              Select Project...
            </option>

            {projects.map((p) => (
              <option key={p.project_code} value={p.project_code}>
                [{p.project_code}] {p.project_name.slice(0, 28)}...
              </option>
            ))}
          </select>
        )}

        <button
          onClick={() => onNavigate('new_prediction')}
          className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer shadow-xs ${
            activeScreen === 'new_prediction'
              ? 'bg-blue-700 text-white ring-2 ring-blue-400/50'
              : 'bg-blue-600 hover:bg-blue-700 text-white'
          }`}
        >
          <span className="material-symbols-outlined text-base leading-none">
            add_chart
          </span>
          <span>New Project Prediction</span>
        </button>

        <button
          onClick={() => onNavigate('what_if')}
          className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer border shadow-xs ${
            activeScreen === 'what_if'
              ? 'bg-slate-800 text-white border-slate-800'
              : 'bg-white hover:bg-slate-50 text-slate-700 border-slate-300'
          }`}
        >
          <span className="material-symbols-outlined text-base leading-none text-blue-600">
            tune
          </span>
          <span>What-If Analysis</span>
        </button>
      </div>
    </header>
  );
};
