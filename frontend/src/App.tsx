import { Suspense, lazy, useCallback, useEffect, useState } from 'react'
import DecisionPanel from './components/DecisionPanel'
import EthicalAnalysis from './components/EthicalAnalysis'
import Header from './components/Header'
import MetricCard from './components/MetricCard'
import PolicyComparison from './components/PolicyComparison'
import RoadSimulation from './components/RoadSimulation'
import ScenarioControls from './components/ScenarioControls'
import Sidebar from './components/Sidebar'
import { downloadEvaluation, getHealth, getScenarios, runEvaluation, runSimulation } from './services/api'
import type { Controls, EvaluationResult, Scenario, SimulationResult } from './types'

const ResultsCharts = lazy(() => import('./components/ResultsCharts'))

function initialControls(scenario: Scenario): Controls {
  return {
    scenarioId: scenario.id,
    speedKmh: scenario.default_speed_kmh,
    obstacleDistanceM: scenario.default_obstacle_distance_m,
    visibility: scenario.default_visibility,
    policy: 'safety_aware',
  }
}

function metricValue(value: number | null | undefined, suffix = '%'): string {
  return value == null ? '—' : `${value.toFixed(value % 1 === 0 ? 0 : 1)}${suffix}`
}

export default function App() {
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [controls, setControls] = useState<Controls | null>(null)
  const [simulation, setSimulation] = useState<SimulationResult | null>(null)
  const [evaluation, setEvaluation] = useState<EvaluationResult | null>(null)
  const [backendOnline, setBackendOnline] = useState(false)
  const [simulationLoading, setSimulationLoading] = useState(false)
  const [evaluationLoading, setEvaluationLoading] = useState(false)
  const [exportLoading, setExportLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadConnection = useCallback(async () => {
    try {
      await getHealth()
      setBackendOnline(true)
    } catch (loadError) {
      setBackendOnline(false)
      setError(loadError instanceof Error ? loadError.message : 'Backend health check failed.')
    }
  }, [])

  useEffect(() => {
    let active = true
    void Promise.all([getHealth(), getScenarios()])
      .then(([health, data]) => {
        if (!active) return
        setBackendOnline(health.status === 'ok')
        setScenarios(data)
        if (data.length > 0) setControls(initialControls(data[0]))
      })
      .catch((loadError: unknown) => {
        if (!active) return
        setBackendOnline(false)
        setError(loadError instanceof Error ? loadError.message : 'Could not load backend data.')
      })
    return () => { active = false }
  }, [])

  const handleControlsChange = (next: Controls) => {
    if (controls && next.scenarioId !== controls.scenarioId) {
      const scenario = scenarios.find((item) => item.id === next.scenarioId)
      if (scenario) {
        setControls({ ...initialControls(scenario), policy: next.policy })
        setSimulation(null)
        return
      }
    }
    setControls(next)
  }

  const handleSimulation = async () => {
    if (!controls) return
    setSimulationLoading(true)
    setError(null)
    try {
      const result = await runSimulation({
        scenario_id: controls.scenarioId,
        policy: controls.policy,
        speed_kmh: controls.speedKmh,
        obstacle_distance_m: controls.obstacleDistanceM,
        visibility: controls.visibility,
      })
      setSimulation(result)
      setBackendOnline(true)
    } catch (runError) {
      setBackendOnline(false)
      setError(runError instanceof Error ? runError.message : 'Simulation request failed.')
    } finally {
      setSimulationLoading(false)
    }
  }

  const handleEvaluation = async () => {
    setEvaluationLoading(true)
    setError(null)
    try {
      const result = await runEvaluation(42, 20)
      setEvaluation(result)
      setBackendOnline(true)
    } catch (runError) {
      setBackendOnline(false)
      setError(runError instanceof Error ? runError.message : 'Evaluation request failed.')
    } finally {
      setEvaluationLoading(false)
    }
  }

  const handleReset = () => {
    const scenario = scenarios.find((item) => item.id === controls?.scenarioId) ?? scenarios[0]
    if (scenario) setControls(initialControls(scenario))
    setSimulation(null)
    setEvaluation(null)
    setError(null)
  }

  const handleExport = async () => {
    setExportLoading(true)
    setError(null)
    try {
      await downloadEvaluation()
    } catch (downloadError) {
      setError(downloadError instanceof Error ? downloadError.message : 'CSV export failed.')
    } finally {
      setExportLoading(false)
    }
  }

  const metrics = evaluation?.metrics_by_policy.safety_aware

  return (
    <div className="app-shell">
      <Header backendOnline={backendOnline} />
      <Sidebar />
      <main className="main-content">
        <section className="page-intro" id="overview">
          <div>
            <div className="eyebrow page-eyebrow"><span className="intro-spark">✳</span> RESPONSIBLE AUTONOMOUS DRIVING</div>
            <h1>Safety, explained.</h1>
            <p>Explore how transparent driving policies respond to risk — and where their limits begin.</p>
          </div>
          <div className="intro-right">
            <span className="intro-index">LAB / 01</span>
            <span className="intro-line" />
            <span className="intro-version">DECISION SYSTEMS</span>
          </div>
        </section>

        {error && (
          <div className="error-banner" role="alert">
            <span>!</span><p>{error}</p>
            <button onClick={() => { setError(null); void loadConnection() }} aria-label="Dismiss error and retry connection">Retry connection</button>
          </div>
        )}

        <section className="metrics-grid" aria-label="Policy outcome overview">
          <MetricCard label="Collision rate" value={metricValue(metrics?.collision_rate_pct)} caption={metrics ? `${metrics.total_episodes} safety-aware episodes` : 'Run an evaluation to measure'} tone="red" icon="×" />
          <MetricCard label="Near-miss rate" value={metricValue(metrics?.near_miss_rate_pct)} caption="Minimum separation ≤ 3 m" tone="amber" icon="!" />
          <MetricCard label="Unnecessary braking" value={metricValue(metrics?.unnecessary_braking_rate_pct)} caption="Emergency stop with no in-path hazard" tone="blue" icon="↘" />
          <MetricCard label="Mean reaction time" value={metricValue(metrics?.average_reaction_time_s, ' s')} caption="For episodes with policy response" tone="green" icon="◷" />
        </section>

        <div className="primary-grid">
          <ScenarioControls
            scenarios={scenarios}
            controls={controls ?? { scenarioId: '', speedKmh: 60, obstacleDistanceM: 50, visibility: 1, policy: 'safety_aware' }}
            onChange={handleControlsChange}
            onRunSimulation={() => void handleSimulation()}
            onRunEvaluation={() => void handleEvaluation()}
            onReset={handleReset}
            simulationLoading={simulationLoading}
            evaluationLoading={evaluationLoading}
          />
          <RoadSimulation result={simulation} />
          <DecisionPanel result={simulation} />
        </div>

        <PolicyComparison evaluation={evaluation} />
        <div className="analytics-row">
          <Suspense fallback={<section className="panel chart-panel chart-loading">Loading analytics…</section>}>
            <ResultsCharts evaluation={evaluation} />
          </Suspense>
          <section className="panel experiment-panel">
            <div className="panel-heading">
              <div><div className="eyebrow">REPRODUCIBILITY</div><h2>Experiment record</h2></div>
              <span className="record-icon">⌁</span>
            </div>
            {evaluation ? (
              <>
                <div className="experiment-stats">
                  <div><span>Random seed</span><strong>{evaluation.seed}</strong></div>
                  <div><span>Scenarios tested</span><strong>{evaluation.scenario_ids.length}</strong></div>
                  <div><span>Episodes / policy</span><strong>{evaluation.total_episodes_per_policy}</strong></div>
                  <div><span>Total paired records</span><strong>{evaluation.episode_records.length}</strong></div>
                </div>
                <p className="experiment-description">{evaluation.variation_description}</p>
                <button className="button button-secondary export-button" onClick={() => void handleExport()} disabled={exportLoading}>
                  {exportLoading ? <><span className="spinner" /> Preparing CSV</> : '↓  Export episode records'}
                </button>
              </>
            ) : (
              <div className="experiment-empty"><span>⌁</span><strong>Waiting for an experiment</strong><p>Run policy evaluation to populate this record with real episode data.</p></div>
            )}
          </section>
        </div>
        <EthicalAnalysis />
        <footer className="page-footer">
          <span>DRIVEGUARD AI <b>·</b> EDUCATIONAL SIMULATOR</span>
          <span>Not Tesla software. Not validated for real-world driving.</span>
        </footer>
      </main>
    </div>
  )
}
