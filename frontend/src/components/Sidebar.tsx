import React from 'react';
import type { NavScreen, PortfolioStats } from '../types';

interface SidebarProps {
  activeScreen: NavScreen;
  onNavigate: (screen: NavScreen) => void;
  stats: Pick<
    PortfolioStats,
    | 'total_projects'
    | 'high_risk_count'
    | 'cost_training_count'
    | 'schedule_training_count'
    | 'unseen_test_count'
  >;
}

const items: { id: NavScreen; label: string; icon: string }[] = [
  { id: 'dashboard', label: 'Executive Dashboard', icon: 'dashboard' },
  { id: 'new_prediction', label: 'New Prediction', icon: 'add_chart' },
  { id: 'project_intelligence', label: 'Project Intelligence', icon: 'analytics' },
  { id: 'what_if', label: 'What-If Simulator', icon: 'tune' },
  { id: 'reports', label: 'Project Matrix', icon: 'table_chart' },
  { id: 'methodology', label: 'Methodology', icon: 'account_tree' },
];

export const Sidebar: React.FC<SidebarProps> = ({
  activeScreen,
  onNavigate,
  stats,
}) => {
  return (
    <aside className="hidden lg:flex w-64 shrink-0 min-h-screen bg-[#091e3a] text-white flex-col border-r border-slate-800">
      <div className="px-5 py-5 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-900/30">
            <span className="material-symbols-outlined text-xl">
              bolt
            </span>
          </div>

          <div>
            <div className="font-bold text-sm tracking-tight">
              POWERGRID
            </div>
            <div className="text-[10px] text-blue-300 font-mono uppercase tracking-widest">
              Project Intelligence
            </div>
          </div>
        </div>
      </div>

      <nav className="flex-1 p-3 space-y-1">
        <div className="px-3 pt-3 pb-2 text-[10px] uppercase tracking-widest text-slate-500 font-mono font-bold">
          Intelligence Platform
        </div>

        {items.map((item) => {
          const active = activeScreen === item.id;

          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left text-xs font-semibold transition-all cursor-pointer ${
                active
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-950/30'
                  : 'text-slate-300 hover:bg-white/10 hover:text-white'
              }`}
            >
              <span className="material-symbols-outlined text-lg">
                {item.icon}
              </span>

              <span>{item.label}</span>

              {active && (
                <span className="ml-auto w-1.5 h-1.5 rounded-full bg-white" />
              )}
            </button>
          );
        })}
      </nav>

      <div className="p-4 border-t border-white/10 space-y-3">
        <div className="rounded-xl bg-white/5 border border-white/10 p-3">
          <div className="text-[10px] uppercase tracking-widest text-slate-500 font-mono">
            Portfolio
          </div>

          <div className="mt-1 text-xl font-extrabold font-mono">
            {stats.total_projects}
          </div>

          <div className="text-[10px] text-slate-400">
            Validated Projects
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <div className="rounded-lg bg-rose-500/10 border border-rose-500/20 p-2">
            <div className="text-[9px] uppercase text-rose-300 font-mono">
              High Risk
            </div>
            <div className="text-lg font-bold font-mono text-rose-300">
              {stats.high_risk_count}
            </div>
          </div>

          <div className="rounded-lg bg-emerald-500/10 border border-emerald-500/20 p-2">
            <div className="text-[9px] uppercase text-emerald-300 font-mono">
              Unseen
            </div>
            <div className="text-lg font-bold font-mono text-emerald-300">
              {stats.unseen_test_count}
            </div>
          </div>
        </div>

        <div className="text-[9px] text-slate-500 font-mono leading-relaxed">
          V2 COST / SCHEDULE RISK ENGINE
          <br />
          Project-level validation enforced
        </div>
      </div>
    </aside>
  );
};
