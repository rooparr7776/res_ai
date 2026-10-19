import type { ChangeEvent } from 'react'
import type { Controls, PolicyName, Scenario } from '../types'

interface ScenarioControlsProps {
  scenarios: Scenario[]
  controls: Controls
  onChange: (next: Controls) => void
  onRunSimulation: () => void
  onRunEvaluation: () => void
  onReset: () => void
  simulationLoading: boolean
  evaluationLoading: boolean
}

export default function ScenarioControls({
  scenarios,
  controls,
  onChange,
  onRunSimulation,
  onRunEvaluation,
  onReset,
  simulationLoading,
  evaluationLoading,
}: ScenarioControlsProps) {
  const setNumber = (key: 'speedKmh' | 'obstacleDistanceM' | 'visibility') =>
    (event: ChangeEvent<HTMLInputElement>) => onChange({ ...controls, [key]: Number(event.target.value) })

  return (
    <section className="panel controls-panel" aria-labelledby="controls-title">
      <div className="panel-heading">
        <div>
          <div className="eyebrow">CONFIGURATION</div>
          <h2 id="controls-title">Scenario controls</h2>
        </div>
        <button className="icon-button reset-button" onClick={onReset} title="Reset settings" aria-label="Reset settings">↺</button>
      </div>

      <label className="field-label" htmlFor="scenario-select">Driving scenario</label>
      <select
        id="scenario-select"
        value={controls.scenarioId}
        onChange={(event) => onChange({ ...controls, scenarioId: event.target.value })}
      >
        {scenarios.map((scenario) => <option key={scenario.id} value={scenario.id}>{scenario.name}</option>)}
      </select>
      <p className="scenario-description">
        {scenarios.find((scenario) => scenario.id === controls.scenarioId)?.description}
      </p>

      <div className="control-range">
        <div className="range-heading">
          <label className="field-label" htmlFor="speed-range">Vehicle speed</label>
          <span className="range-value">{controls.speedKmh}<small> km/h</small></span>
        </div>
        <input id="speed-range" type="range" min="10" max="120" step="1" value={controls.speedKmh} onChange={setNumber('speedKmh')} />
        <div className="range-limits"><span>10</span><span>120 km/h</span></div>
      </div>

      <div className="control-range">
        <div className="range-heading">
          <label className="field-label" htmlFor="distance-range">Obstacle distance</label>
          <span className="range-value">{controls.obstacleDistanceM}<small> m</small></span>
        </div>
        <input id="distance-range" type="range" min="2" max="150" step="1" value={controls.obstacleDistanceM} onChange={setNumber('obstacleDistanceM')} />
        <div className="range-limits"><span>2 m</span><span>150 m</span></div>
      </div>

      <div className="control-range visibility-control">
        <div className="range-heading">
          <label className="field-label" htmlFor="visibility-range">Visibility</label>
          <span className="range-value">{Math.round(controls.visibility * 100)}<small>%</small></span>
        </div>
        <input id="visibility-range" type="range" min="0.1" max="1" step="0.05" value={controls.visibility} onChange={setNumber('visibility')} />
        <div className="range-limits"><span>Low</span><span>Clear</span></div>
      </div>

      <label className="field-label" htmlFor="policy-select">Decision policy</label>
      <select
        id="policy-select"
        value={controls.policy}
        onChange={(event) => onChange({ ...controls, policy: event.target.value as PolicyName })}
      >
        <option value="safety_aware">Safety-aware</option>
        <option value="baseline">Baseline reference</option>
      </select>

      <div className="control-actions">
        <button className="button button-primary" onClick={onRunSimulation} disabled={simulationLoading || !controls.scenarioId}>
          {simulationLoading ? <><span className="spinner" /> Running simulation</> : <><span>▶</span> Run simulation</>}
        </button>
        <button className="button button-secondary" onClick={onRunEvaluation} disabled={evaluationLoading || scenarios.length === 0}>
          {evaluationLoading ? <><span className="spinner" /> Evaluating</> : <><span>⇄</span> Run policy evaluation</>}
        </button>
      </div>
      <p className="control-footnote">Evaluation runs 20 reproducible episodes per scenario, paired across both policies.</p>
    </section>
  )
}
