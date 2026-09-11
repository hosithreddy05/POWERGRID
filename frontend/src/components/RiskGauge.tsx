import React from 'react';

interface RiskGaugeProps {
  score: number;
  size?: number;
  label?: string;
}

export const RiskGauge: React.FC<RiskGaugeProps> = ({
  score,
  size = 160,
  label = 'Risk Score',
}) => {
  const safeScore = Math.max(0, Math.min(100, score));

  const radius = 50;
  const circumference = 2 * Math.PI * radius;
  const progress = (safeScore / 100) * circumference;

  const riskLevel =
    safeScore >= 66 ? 'HIGH' : safeScore >= 36 ? 'MEDIUM' : 'LOW';

  return (
    <div
      className="flex flex-col items-center justify-center"
      style={{ width: size }}
    >
      <div
        className="relative"
        style={{ width: size, height: size }}
      >
        <svg
          viewBox="0 0 120 120"
          className="w-full h-full -rotate-90"
        >
          <circle
            cx="60"
            cy="60"
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth="10"
            className="text-slate-200"
          />

          <circle
            cx="60"
            cy="60"
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth="10"
            strokeLinecap="round"
            className={
              safeScore >= 66
                ? 'text-rose-500'
                : safeScore >= 36
                  ? 'text-amber-500'
                  : 'text-emerald-500'
            }
            strokeDasharray={circumference}
            strokeDashoffset={circumference - progress}
          />
        </svg>

        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-extrabold font-mono text-slate-900">
            {Math.round(safeScore)}
          </span>

          <span className="text-[9px] uppercase tracking-wider font-bold text-slate-500 font-mono">
            / 100
          </span>
        </div>
      </div>

      <div className="mt-2 text-center">
        <div className="text-[10px] uppercase tracking-wider font-bold text-slate-500 font-mono">
          {label}
        </div>

        <div
          className={
            'mt-1 text-xs font-bold font-mono ' +
            (riskLevel === 'HIGH'
              ? 'text-rose-600'
              : riskLevel === 'MEDIUM'
                ? 'text-amber-600'
                : 'text-emerald-600')
          }
        >
          {riskLevel} RISK
        </div>
      </div>
    </div>
  );
};

export default RiskGauge;
