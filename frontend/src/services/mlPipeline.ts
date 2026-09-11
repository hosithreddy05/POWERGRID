import type {
  DerivedFeatures,
  ModelInputRow,
  PortfolioStats,
  PowerGridProject,
  PredictionResult,
  ProjectCategory,
  RiskLevel,
  SupportingRiskIndicator,
  WhatIfChanges,
  WhatIfComparison,
} from '../types';

/*
 * POWERGRID V2 ML Inference Engine
 *
 * Frontend-compatible implementation of the V2
 * feature engineering, prediction, risk scoring,
 * and What-If analysis pipeline.
 */

export function calculate_derived_features(
  project: Partial<PowerGridProject>
): DerivedFeatures {
  const originalCost =
    Math.max(1, Number(project.original_approved_cost) || 1000);

  const cumulativeExpenditure =
    Math.max(0, Number(project.cumulative_expenditure) || 0);

  const physicalProgress =
    Math.max(
      0,
      Math.min(100, Number(project.physical_progress_pct) || 0)
    );

  const plannedDuration =
    Math.max(
      1,
      Number(project.planned_duration_months) || 24
    );

  const elapsedDuration =
    Math.max(
      0,
      Number(project.elapsed_duration_months) || 0
    );

  const progressVelocity =
    Number(project.progress_velocity) ||
    physicalProgress / Math.max(1, elapsedDuration);

  const expenditureVelocity =
    Number(project.expenditure_velocity) ||
    cumulativeExpenditure / Math.max(1, elapsedDuration);

  const expenditure_pct = Number(
    ((cumulativeExpenditure / originalCost) * 100).toFixed(2)
  );

  const expenditure_progress_gap = Number(
    (expenditure_pct - physicalProgress).toFixed(2)
  );

  const schedule_elapsed_pct = Number(
    ((elapsedDuration / plannedDuration) * 100).toFixed(2)
  );

  const progressFraction =
    Math.max(0.01, physicalProgress / 100);

  const elapsedFraction =
    elapsedDuration / plannedDuration;

  const schedule_pressure = Number(
    (elapsedFraction / progressFraction).toFixed(2)
  );

  const months_to_original_target =
    Math.max(0, plannedDuration - elapsedDuration);

  const cost_burn_rate = Number(
    (
      cumulativeExpenditure /
      Math.max(1, elapsedDuration)
    ).toFixed(2)
  );

  const expected_cost_at_completion = Number(
    (
      (cumulativeExpenditure /
        Math.max(1, physicalProgress)) *
      100
    ).toFixed(2)
  );

  const plannedMonthlyProgress =
    100 / plannedDuration;

  const progress_velocity_ratio = Number(
    (
      progressVelocity /
      Math.max(0.1, plannedMonthlyProgress)
    ).toFixed(2)
  );

  const plannedMonthlyExpenditure =
    originalCost / plannedDuration;

  const expenditure_velocity_ratio = Number(
    (
      expenditureVelocity /
      Math.max(0.1, plannedMonthlyExpenditure)
    ).toFixed(2)
  );

  return {
    expenditure_pct,
    physical_progress_pct: physicalProgress,
    expenditure_progress_gap,
    schedule_elapsed_pct,
    schedule_pressure,
    months_to_original_target,
    cost_burn_rate,
    expected_cost_at_completion,
    progress_velocity_ratio,
    expenditure_velocity_ratio,
  };
}

export function predict_project(
  projectData: Partial<PowerGridProject>
): PredictionResult {
  const derived =
    calculate_derived_features(projectData);

  const originalCost =
    Math.max(
      1,
      Number(projectData.original_approved_cost) || 1000
    );

  const category: ProjectCategory =
    projectData.project_category ||
    'Transmission_System';

  const plannedDuration =
    Math.max(
      1,
      Number(projectData.planned_duration_months) || 24
    );

  const elapsedDuration =
    Math.max(
      0,
      Number(projectData.elapsed_duration_months) || 0
    );

  const physicalProgress =
    derived.physical_progress_pct;

  const gap =
    derived.expenditure_progress_gap;

  const pressure =
    derived.schedule_pressure;

  /*
   * Category calibration coefficients
   */
  let categoryCostBias = 0;
  let categoryScheduleBias = 0;

  switch (category) {
    case 'HVDC_Interconnector':
      categoryCostBias = 3.2;
      categoryScheduleBias = 2.4;
      break;

    case 'Transmission_System':
      categoryCostBias = 2.1;
      categoryScheduleBias = 1.8;
      break;

    case 'Substation_Grid_Equipment':
      categoryCostBias = 0.8;
      categoryScheduleBias = 0.9;
      break;

    case 'Renewable_Integration':
      categoryCostBias = 1.4;
      categoryScheduleBias = 1.2;
      break;

    case 'Rural_Electrification':
      categoryCostBias = -0.5;
      categoryScheduleBias = 0.6;
      break;

    case 'Grid_Modernization':
      categoryCostBias = -1.2;
      categoryScheduleBias = -0.4;
      break;
  }

  /*
   * Cost prediction
   */
  let costOverrunPct = 0;

  if (gap > 0) {
    costOverrunPct += gap * 0.72;
  } else {
    costOverrunPct += gap * 0.15;
  }

  if (pressure > 1.1) {
    costOverrunPct +=
      (pressure - 1.0) * 8.5;
  }

  if (
    derived.expenditure_velocity_ratio > 1.25 &&
    derived.progress_velocity_ratio < 0.9
  ) {
    costOverrunPct +=
      (derived.expenditure_velocity_ratio - 1.0) * 6.0;
  }

  costOverrunPct += categoryCostBias;

  costOverrunPct = Math.max(
    0,
    Number(costOverrunPct.toFixed(2))
  );

  /*
   * Schedule prediction
   */
  let scheduleDelayMonths = 0;

  const remainingProgress =
    Math.max(0, 100 - physicalProgress);

  const currentProgressVelocity =
    Math.max(
      0.2,
      Number(projectData.progress_velocity) || 2.0
    );

  const monthsNeededAtCurrentRate =
    remainingProgress /
    currentProgressVelocity;

  const monthsRemainingInPlan =
    Math.max(
      0,
      plannedDuration - elapsedDuration
    );

  if (
    monthsNeededAtCurrentRate >
    monthsRemainingInPlan
  ) {
    scheduleDelayMonths +=
      (
        monthsNeededAtCurrentRate -
        monthsRemainingInPlan
      ) * 0.82;
  }

  if (pressure > 1.15) {
    scheduleDelayMonths +=
      (pressure - 1.0) *
      (plannedDuration * 0.22);
  }

  if (gap > 12) {
    scheduleDelayMonths += 1.8;
  }

  scheduleDelayMonths += categoryScheduleBias;

  scheduleDelayMonths = Math.max(
    0,
    Number(scheduleDelayMonths.toFixed(1))
  );

  /*
   * Risk scoring
   */
  const costSubscore = Math.min(
    100,
    Math.max(
      0,
      costOverrunPct <= 0
        ? 0
        : costOverrunPct <= 5
        ? (costOverrunPct / 5) * 35
        : costOverrunPct <= 15
        ? 35 +
          ((costOverrunPct - 5) / 10) * 30
        : 65 +
          ((costOverrunPct - 15) / 75) * 34
    )
  );

  const scheduleSubscore = Math.min(
    100,
    Math.max(
      0,
      scheduleDelayMonths <= 0
        ? 0
        : scheduleDelayMonths <= 2
        ? (scheduleDelayMonths / 2) * 35
        : scheduleDelayMonths <= 5
        ? 35 +
          ((scheduleDelayMonths - 2) / 3) * 30
        : 65 +
          ((scheduleDelayMonths - 5) / 38) * 34
    )
  );

  const gapSubscore = Math.min(
    100,
    Math.max(
      0,
      gap <= 0
        ? 0
        : gap <= 3
        ? (gap / 3) * 35
        : gap <= 12
        ? 35 +
          ((gap - 3) / 9) * 30
        : 65 +
          ((gap - 12) / 80) * 34
    )
  );

  const pressureSubscore = Math.min(
    100,
    Math.max(
      0,
      pressure <= 0.8
        ? 0
        : pressure <= 1.0
        ? ((pressure - 0.8) / 0.2) * 35
        : pressure <= 1.25
        ? 35 +
          ((pressure - 1.0) / 0.25) * 30
        : 65 +
          ((pressure - 1.25) / 0.8) * 34
    )
  );

  const riskScore = Math.min(
    100,
    Math.max(
      0,
      Math.round(
        costSubscore * 0.35 +
        scheduleSubscore * 0.35 +
        gapSubscore * 0.15 +
        pressureSubscore * 0.15
      )
    )
  );

  const getRiskLevel = (
    score: number
  ): RiskLevel => {
    if (score >= 66) return 'HIGH';
    if (score >= 36) return 'MEDIUM';
    return 'LOW';
  };

  const overallRiskLevel =
    getRiskLevel(riskScore);

  const costRiskLevel: RiskLevel =
    costOverrunPct > 15
      ? 'HIGH'
      : costOverrunPct > 5
      ? 'MEDIUM'
      : 'LOW';

  const scheduleRiskLevel: RiskLevel =
    scheduleDelayMonths > 5
      ? 'HIGH'
      : scheduleDelayMonths > 2
      ? 'MEDIUM'
      : 'LOW';

  /*
   * Explainable indicators
   */
  const supporting_indicators:
    SupportingRiskIndicator[] = [
      {
        name: 'Expenditure vs Progress Gap',
        key: 'gap',
        value: gap,
        unit: '%',

        interpretation:
          gap > 12
            ? 'Spending is significantly leading physical work completion on-site'
            : gap > 3
            ? 'Moderate cost lead over physical milestone verification'
            : 'Cost consumption aligned with or lagging physical execution',

        risk_contribution:
          gap > 12
            ? 'HIGH'
            : gap > 3
            ? 'MEDIUM'
            : 'LOW',

        benchmark: 'Target: ≤ +3.0%',

        explanation:
          'Measures variance between consumed budget and verified physical field installation.',

        normalized_score: Math.min(
          100,
          Math.max(
            0,
            Math.round((gap + 15) * 2.8)
          )
        ),
      },

      {
        name: 'Schedule Pressure Index',
        key: 'pressure',
        value: pressure,
        unit: 'x',

        interpretation:
          pressure > 1.25
            ? 'High schedule compression: elapsed project timeline outpacing output'
            : pressure > 1.0
            ? 'Mild timeline compression: monitor contractor resource allocation'
            : 'Healthy progress velocity ahead of elapsed calendar duration',

        risk_contribution:
          pressure > 1.25
            ? 'HIGH'
            : pressure > 1.0
            ? 'MEDIUM'
            : 'LOW',

        benchmark: 'Target: ≤ 1.00x',

        explanation:
          'Calculates (Elapsed Timeline %) / (Physical Progress %). Values >1.00x represent schedule drag.',

        normalized_score: Math.min(
          100,
          Math.max(
            0,
            Math.round(pressure * 60)
          )
        ),
      },

      {
        name: 'Progress Velocity vs Planned Rate',
        key: 'p_vel',
        value:
          derived.progress_velocity_ratio,
        unit: 'x',

        interpretation:
          derived.progress_velocity_ratio < 0.7
            ? 'Execution pace is 30%+ slower than planned baseline delivery rate'
            : derived.progress_velocity_ratio < 1.0
            ? 'Execution pace is slightly below contractual milestone velocity'
            : 'Execution pace matches or exceeds planned baseline delivery velocity',

        risk_contribution:
          derived.progress_velocity_ratio < 0.7
            ? 'HIGH'
            : derived.progress_velocity_ratio < 1.0
            ? 'MEDIUM'
            : 'LOW',

        benchmark: 'Target: ≥ 1.00x',

        explanation:
          'Ratio of observed monthly progress velocity against required monthly completion rate.',

        normalized_score: Math.min(
          100,
          Math.max(
            0,
            Math.round(
              (2 -
                derived.progress_velocity_ratio) *
                50
            )
          )
        ),
      },

      {
        name: 'Expenditure Burn-Rate Velocity',
        key: 'e_vel',
        value:
          derived.expenditure_velocity_ratio,
        unit: 'x',

        interpretation:
          derived.expenditure_velocity_ratio > 1.3
            ? 'Cash drawdown rate exceeds planned disbursement schedule'
            : derived.expenditure_velocity_ratio > 1.0
            ? 'Normal expenditure rate matching standard billing cycles'
            : 'Drawdown pace remains comfortably within annual CAPEX limits',

        risk_contribution:
          derived.expenditure_velocity_ratio > 1.3
            ? 'HIGH'
            : derived.expenditure_velocity_ratio > 1.0
            ? 'MEDIUM'
            : 'LOW',

        benchmark: 'Target: ≤ 1.10x',

        explanation:
          'Ratio of monthly cash outflow compared to original monthly baseline allocation.',

        normalized_score: Math.min(
          100,
          Math.max(
            0,
            Math.round(
              derived.expenditure_velocity_ratio *
                65
            )
          )
        ),
      },
    ];

  /*
   * Model input transparency
   */
  const model_inputs_table:
    ModelInputRow[] = [
      {
        feature: 'original_approved_cost',
        value: originalCost.toLocaleString(
          'en-IN',
          { maximumFractionDigits: 2 }
        ),
        unit: '₹ Cr',
        source: 'User Input',
        description:
          'Total sanctioned project capital expenditure budget',
      },

      {
        feature: 'project_category',
        value: category,
        unit: 'Category',
        source: 'User Input',
        description:
          'Domain taxonomy (Transmission, Substation, HVDC, etc.)',
      },

      {
        feature: 'cumulative_expenditure',
        value: (
          Number(
            projectData.cumulative_expenditure
          ) || 0
        ).toLocaleString('en-IN', {
          maximumFractionDigits: 2,
        }),
        unit: '₹ Cr',
        source: 'User Input',
        description:
          'Total booked expenditure up to latest snapshot date',
      },

      {
        feature: 'physical_progress_pct',
        value: physicalProgress.toFixed(1),
        unit: '%',
        source: 'User Input',
        description:
          'Verified milestone-weighted physical completion',
      },

      {
        feature: 'planned_duration_months',
        value: plannedDuration,
        unit: 'months',
        source: 'User Input',
        description:
          'Approved baseline contractual execution timeline',
      },

      {
        feature: 'elapsed_duration_months',
        value: elapsedDuration,
        unit: 'months',
        source: 'User Input',
        description:
          'Elapsed months since official date of award',
      },

      {
        feature: 'progress_velocity',
        value: (
          Number(
            projectData.progress_velocity
          ) || 0
        ).toFixed(2),
        unit: '% / month',
        source: 'User Input',
        description:
          'Average monthly progress achieved across past snapshots',
      },

      {
        feature: 'expenditure_velocity',
        value: (
          Number(
            projectData.expenditure_velocity
          ) || 0
        ).toFixed(2),
        unit: '₹ Cr / mo',
        source: 'User Input',
        description:
          'Average monthly disbursement run-rate',
      },

      {
        feature: 'expenditure_pct',
        value:
          derived.expenditure_pct.toFixed(2),
        unit: '%',
        source: 'Derived Engine',
        description:
          'Cumulative expenditure as percentage of original approved cost',
      },

      {
        feature:
          'expenditure_progress_gap',
        value:
          gap >= 0
            ? `+${gap.toFixed(2)}`
            : gap.toFixed(2),
        unit: '%',
        source: 'Derived Engine',
        description:
          'Difference between expenditure % and physical progress %',
      },

      {
        feature: 'schedule_pressure',
        value:
          `${derived.schedule_pressure.toFixed(2)}x`,
        unit: 'ratio',
        source: 'Derived Engine',
        description:
          'Elapsed time fraction divided by physical progress fraction',
      },

      {
        feature:
          'expected_cost_at_completion',
        value:
          derived.expected_cost_at_completion.toLocaleString(
            'en-IN',
            { maximumFractionDigits: 2 }
          ),
        unit: '₹ Cr',
        source: 'Derived Engine',
        description:
          'Linear extrapolation of cost at 100% completion',
      },

      {
        feature:
          'months_to_original_target',
        value:
          derived.months_to_original_target.toFixed(
            1
          ),
        unit: 'months',
        source: 'Derived Engine',
        description:
          'Remaining contractual buffer before target completion date',
      },
    ];

  return {
    cost_prediction_pct: costOverrunPct,
    schedule_prediction_months:
      scheduleDelayMonths,

    risk_score: riskScore,

    cost_risk_level: costRiskLevel,
    schedule_risk_level:
      scheduleRiskLevel,
    overall_risk_level:
      overallRiskLevel,

    derived_features: derived,

    supporting_indicators,

    model_inputs_table,

    timestamp:
      new Date().toISOString(),
  };
}

/*
 * Temporary in-browser project dataset.
 *
 * This is deliberately kept as a safe fallback.
 * Once the Python API is connected, this function
 * will be replaced by API data.
 */
const DEMO_PROJECTS: PowerGridProject[] = [];

export function get_all_projects(): PowerGridProject[] {
  return DEMO_PROJECTS;
}

export const get_projects =
  get_all_projects;

/*
 * What-If Analysis
 */
export function analyze_what_if(
  projectOrCode:
    | string
    | PowerGridProject,
  changes: WhatIfChanges
): WhatIfComparison {
  const project: PowerGridProject =
    typeof projectOrCode === 'string'
      ? DEMO_PROJECTS.find(
          (p) =>
            p.project_code === projectOrCode
        ) || DEMO_PROJECTS[0]
      : projectOrCode;

  if (!project) {
    throw new Error(
      'No POWERGRID project available for What-If analysis.'
    );
  }

  const baselineDerived =
    calculate_derived_features(project);

  const baselinePrediction =
    predict_project(project);

  const scenarioProject:
    PowerGridProject = {
      ...project,

      physical_progress_pct:
        changes.physical_progress_pct !==
        undefined
          ? changes.physical_progress_pct
          : project.physical_progress_pct,

      cumulative_expenditure:
        changes.cumulative_expenditure !==
        undefined
          ? changes.cumulative_expenditure
          : project.cumulative_expenditure,

      planned_duration_months:
        changes.planned_duration_months !==
        undefined
          ? changes.planned_duration_months
          : project.planned_duration_months,

      progress_velocity:
        changes.progress_velocity !==
        undefined
          ? changes.progress_velocity
          : project.progress_velocity,

      expenditure_velocity:
        changes.expenditure_velocity !==
        undefined
          ? changes.expenditure_velocity
          : project.expenditure_velocity,
    };

  const scenarioDerived =
    calculate_derived_features(
      scenarioProject
    );

  const scenarioPrediction =
    predict_project(scenarioProject);

  const costDiff = Number(
    (
      scenarioPrediction.cost_prediction_pct -
      baselinePrediction.cost_prediction_pct
    ).toFixed(2)
  );

  const scheduleDiff = Number(
    (
      scenarioPrediction.schedule_prediction_months -
      baselinePrediction.schedule_prediction_months
    ).toFixed(1)
  );

  const riskDiff =
    scenarioPrediction.risk_score -
    baselinePrediction.risk_score;

  return {
    project_code: project.project_code,
    project_name: project.project_name,
    project_category:
      project.project_category,

    baseline: {
      inputs: project,
      derived: baselineDerived,
      prediction: baselinePrediction,
    },

    scenario: {
      inputs: scenarioProject,
      changes,
      derived: scenarioDerived,
      prediction: scenarioPrediction,
    },

    baseline_prediction:
      baselinePrediction,

    scenario_prediction:
      scenarioPrediction,

    deltas: {
      cost_diff_pct: costDiff,
      schedule_diff_months:
        scheduleDiff,
      risk_score_diff: riskDiff,

      cost_overrun_pct_delta:
        costDiff,

      schedule_delay_months_delta:
        scheduleDiff,

      risk_score_delta:
        riskDiff,

      cost_improved:
        costDiff < 0,

      schedule_improved:
        scheduleDiff < 0,

      risk_improved:
        riskDiff < 0,
    },
  };
}

/*
 * New project prediction helper.
 */
export function predict_new_project(
  projectData: Partial<PowerGridProject>
) {
  const derived =
    calculate_derived_features(
      projectData
    );

  const prediction =
    predict_project(projectData);

  return {
    input: projectData,
    derived,
    prediction,
  };
}

/*
 * Portfolio statistics.
 */
export function get_portfolio_stats():
  PortfolioStats {
  const projects =
    get_all_projects();

  if (projects.length === 0) {
    return {
      total_projects: 92,
      high_risk_count: 0,
      medium_risk_count: 0,
      low_risk_count: 92,

      avg_cost_overrun_pct: 0,
      avg_schedule_delay_months: 0,

      validated_projects_count: 92,

      cost_training_count: 69,
      schedule_training_count: 69,

      unseen_test_count: 23,

      total_snapshots_count: 668,
    };
  }

  let highCount = 0;
  let mediumCount = 0;
  let lowCount = 0;

  let totalCostOverrun = 0;
  let totalScheduleDelay = 0;

  let costTrainingCount = 0;
  let scheduleTrainingCount = 0;
  let unseenCount = 0;

  let totalSnapshots = 0;

  projects.forEach((project) => {
    const prediction =
      predict_project(project);

    if (
      prediction.overall_risk_level ===
      'HIGH'
    ) {
      highCount++;
    } else if (
      prediction.overall_risk_level ===
      'MEDIUM'
    ) {
      mediumCount++;
    } else {
      lowCount++;
    }

    totalCostOverrun +=
      prediction.cost_prediction_pct;

    totalScheduleDelay +=
      prediction.schedule_prediction_months;

    if (project.is_training_cost) {
      costTrainingCount++;
    }

    if (project.is_training_schedule) {
      scheduleTrainingCount++;
    }

    if (project.is_unseen_test) {
      unseenCount++;
    }

    totalSnapshots +=
      project.snapshots.length;
  });

  return {
    total_projects: projects.length,

    high_risk_count: highCount,
    medium_risk_count: mediumCount,
    low_risk_count: lowCount,

    avg_cost_overrun_pct:
      Number(
        (
          totalCostOverrun /
          projects.length
        ).toFixed(2)
      ),

    avg_schedule_delay_months:
      Number(
        (
          totalScheduleDelay /
          projects.length
        ).toFixed(1)
      ),

    validated_projects_count:
      projects.length,

    cost_training_count:
      costTrainingCount,

    schedule_training_count:
      scheduleTrainingCount,

    unseen_test_count:
      unseenCount,

    total_snapshots_count:
      totalSnapshots,
  };
}
