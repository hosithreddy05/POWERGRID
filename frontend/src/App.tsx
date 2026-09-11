import { useEffect, useState } from 'react';

import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { ExecutiveDashboard } from './components/ExecutiveDashboard';
import { NewPredictionScreen } from './components/NewPredictionScreen';
import { ProjectIntelligenceScreen } from './components/ProjectIntelligenceScreen';
import { WhatIfScreen } from './components/WhatIfScreen';
import { ReportsScreen } from './components/ReportsScreen';
import { MethodologyScreen } from './components/MethodologyScreen';

import type {
  NavScreen,
  PortfolioStats,
  PowerGridProject,
} from './types';

import {
  fetchProjects,
  checkApiHealth,
} from './services/api';

import {
  get_portfolio_stats,
} from './services/mlPipeline';


export default function App() {
  const [activeScreen, setActiveScreen] =
    useState<NavScreen>('dashboard');

  const [selectedProjectCode, setSelectedProjectCode] =
    useState('');

  const [projects, setProjects] =
    useState<PowerGridProject[]>([]);

  const [stats, setStats] =
    useState<PortfolioStats>(
      get_portfolio_stats(),
    );

  const [loading, setLoading] =
    useState(true);

  const [apiError, setApiError] =
    useState('');

  /*
   * ----------------------------------------------------------
   * Load real POWERGRID data from FastAPI
   * ----------------------------------------------------------
   */

  useEffect(() => {
    let mounted = true;

    async function loadBackendData() {
      try {
        setLoading(true);
        setApiError('');

        const healthy =
          await checkApiHealth();

        if (!healthy) {
          throw new Error(
            'POWERGRID backend is not reachable.',
          );
        }

        const loadedProjects =
          await fetchProjects();

        if (!mounted) {
          return;
        }

        setProjects(
          loadedProjects,
        );

        /*
         * Build portfolio statistics from the
         * real project list when possible.
         *
         * The existing ML statistics remain the
         * fallback for fields not exposed by the API.
         */

        const fallbackStats =
          get_portfolio_stats();

        const highRisk =
          loadedProjects.filter(
            (project) => {
              const snapshot =
                project.snapshots[
                  project.snapshots.length - 1
                ];

              return (
                snapshot &&
                snapshot.risk_score >= 70
              );
            },
          ).length;

        const mediumRisk =
          loadedProjects.filter(
            (project) => {
              const snapshot =
                project.snapshots[
                  project.snapshots.length - 1
                ];

              return (
                snapshot &&
                snapshot.risk_score >= 40 &&
                snapshot.risk_score < 70
              );
            },
          ).length;

        const lowRisk =
          Math.max(
            loadedProjects.length -
              highRisk -
              mediumRisk,
            0,
          );

        setStats({
          ...fallbackStats,

          total_projects:
            loadedProjects.length ||
            fallbackStats.total_projects,

          validated_projects_count:
            loadedProjects.length ||
            fallbackStats.validated_projects_count,

          high_risk_count:
            highRisk,

          medium_risk_count:
            mediumRisk,

          low_risk_count:
            lowRisk,
        });

      } catch (error) {
        if (!mounted) {
          return;
        }

        console.error(
          'POWERGRID API error:',
          error,
        );

        setApiError(
          error instanceof Error
            ? error.message
            : 'Unable to connect to POWERGRID backend.',
        );

      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    loadBackendData();

    return () => {
      mounted = false;
    };
  }, []);


  /*
   * ----------------------------------------------------------
   * Navigation
   * ----------------------------------------------------------
   */

  const handleNavigate = (
    screen: NavScreen,
  ) => {
    setActiveScreen(screen);
  };


  /*
   * ----------------------------------------------------------
   * Project selection
   * ----------------------------------------------------------
   */

  const handleSelectProject = (
    projectCode: string,
  ) => {
    setSelectedProjectCode(
      projectCode,
    );

    /*
     * When a project is selected from the
     * header/dashboard, take the user to
     * Project Intelligence.
     */
    if (projectCode) {
      setActiveScreen(
        'project_intelligence',
      );
    }
  };


  /*
   * ----------------------------------------------------------
   * Screen rendering
   * ----------------------------------------------------------
   */

  const renderScreen = () => {
    switch (activeScreen) {

      case 'dashboard':
        return (
          <ExecutiveDashboard
            projects={projects}
            stats={stats}
            selectedProjectCode={
              selectedProjectCode
            }
            onNavigate={
              handleNavigate
            }
            onSelectProject={
              handleSelectProject
            }
          />
        );


      case 'new_prediction':
        return (
          <NewPredictionScreen
            onNavigate={
              handleNavigate
            }
          />
        );


      case 'project_intelligence':
        return (
          <ProjectIntelligenceScreen
            onNavigate={
              handleNavigate
            }
            selectedProjectCode={
              selectedProjectCode
            }
          />
        );


      case 'what_if':
        return (
          <WhatIfScreen
            onNavigate={
              handleNavigate
            }
            selectedProjectCode={
              selectedProjectCode
            }
          />
        );


      case 'reports':
        return (
          <ReportsScreen
            onNavigate={
              handleNavigate
            }
            onSelectProject={
              handleSelectProject
            }
            stats={stats}
          />
        );


      case 'methodology':
        return (
          <MethodologyScreen
            onNavigate={
              handleNavigate
            }
          />
        );


      default:
        return (
          <ExecutiveDashboard
            projects={projects}
            stats={stats}
            selectedProjectCode={
              selectedProjectCode
            }
            onNavigate={
              handleNavigate
            }
            onSelectProject={
              handleSelectProject
            }
          />
        );
    }
  };


  /*
   * ----------------------------------------------------------
   * Application layout
   * ----------------------------------------------------------
   */

  return (
    <div className="flex min-h-screen bg-[#f8fafc] text-slate-900 font-sans selection:bg-blue-600 selection:text-white">

      <Sidebar
        activeScreen={
          activeScreen
        }
        onNavigate={
          handleNavigate
        }
        stats={{
          total_projects:
            stats.total_projects,

          high_risk_count:
            stats.high_risk_count,

          cost_training_count:
            stats.cost_training_count,

          schedule_training_count:
            stats.schedule_training_count,

          unseen_test_count:
            stats.unseen_test_count,
        }}
      />


      <div className="flex-1 flex flex-col min-w-0">

        <Header
          onNavigate={
            handleNavigate
          }
          onSelectProject={
            handleSelectProject
          }
          projects={
            projects
          }
          activeScreen={
            activeScreen
          }
        />


        <main className="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto">

          {loading && (
            <div className="mb-6 rounded-xl border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-800">
              Connecting to POWERGRID ML backend...
            </div>
          )}


          {!loading && apiError && (
            <div className="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
              <div className="font-bold">
                POWERGRID backend connection failed
              </div>

              <div className="mt-1">
                {apiError}
              </div>

              <div className="mt-2 font-mono text-xs">
                Make sure FastAPI is running on
                http://127.0.0.1:8000
              </div>
            </div>
          )}


          <div className="animate-fadeIn">
            {renderScreen()}
          </div>

        </main>

      </div>

    </div>
  );
}
