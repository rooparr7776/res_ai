import type { CSSProperties } from 'react'
import type { SimulationResult } from '../types'

interface DecisionPanelProps {
  result: SimulationResult | null
}

export default function DecisionPanel({ result }: DecisionPanelProps) {
  if (!result) {
    return (
      <section className="panel decision-panel empty-state" aria-labelledby="decision-title">
        <div className="panel-heading">
          <div><div className="eyebrow">POLICY OUTPUT</div><h2 id="decision-title">Decision analysis</h2></div>
        </div>
        <div className="empty-content">
          <div className="empty-symbol">◎</div>
          <strong>Awaiting a simulation</strong>
          <p>Configure a scenario and run an episode to see the policy's reasoning and outcome.</p>
        </div>
      </section>
    )
  }

  const category = result.risk.risk_category
  return (
    <section className="panel decision-panel" aria-labelledby="decision-title">
      <div className="panel-heading">
        <div><div className="eyebrow">POLICY OUTPUT</div><h2 id="decision-title">Decision analysis</h2></div>
        <span className={`risk-pill ${category}`}>{category.toUpperCase()} RISK</span>
      </div>

      <div className="decision-summary">
        <div className={`risk-dial ${category}`} style={{ '--risk': `${result.risk.risk_score}%` } as CSSProperties}>
          <div className="risk-dial-inner"><strong>{result.risk.risk_score}</strong><span>/ 100</span></div>
        </div>
        <div className="decision-action">
          <span className="mini-label">COMMANDED ACTION</span>
          <strong className={`action-text ${result.action}`}>{result.action.replace('_', ' ')}</strong>
          <span className="policy-name">{result.inputs.policy === 'safety_aware' ? 'Safety-aware policy' : 'Baseline reference policy'}</span>
        </div>
      </div>

      <div className="explanation-box">
        <span className="explanation-icon">✳</span>
        <p>{result.explanation}</p>
      </div>
      <div className="decision-details">
        <div><span>Scenario</span><strong>{result.inputs.scenario_name}</strong></div>
        <div><span>Minimum separation</span><strong>{result.minimum_separation_m == null ? 'Not applicable' : `${result.minimum_separation_m.toFixed(1)} m`}</strong></div>
        <div><span>Reaction time</span><strong>{result.reaction_time_s == null ? 'No response' : `${result.reaction_time_s.toFixed(1)} s`}</strong></div>
        <div><span>Stopping distance</span><strong>{result.stopping_distance_m == null ? 'Vehicle did not stop' : `${result.stopping_distance_m.toFixed(1)} m`}</strong></div>
      </div>
      <div className="decision-disclaimer"><span>i</span>{result.risk.explanation}</div>
      <details className="decision-log">
        <summary>
          <span>Inspect decision log</span>
          <span className="decision-log-count">{result.decision_log.length} EVENTS</span>
        </summary>
        <div className="log-inputs">
          <div><span>Policy</span><strong>{result.inputs.policy === 'safety_aware' ? 'Safety-aware' : 'Baseline'}</strong></div>
          <div><span>Initial speed</span><strong>{result.inputs.speed_kmh} km/h</strong></div>
          <div><span>Obstacle distance</span><strong>{result.inputs.obstacle_distance_m} m</strong></div>
          <div><span>Visibility</span><strong>{Math.round(result.inputs.visibility * 100)}%</strong></div>
          <div><span>Closing speed</span><strong>{result.inputs.closing_speed_kmh} km/h</strong></div>
          <div><span>Perception confidence</span><strong>{Math.round(result.inputs.perception_confidence * 100)}%</strong></div>
          <div><span>Hazard severity</span><strong>{Math.round(result.inputs.hazard_severity * 100)}%</strong></div>
          <div><span>Obstacle in path</span><strong>{result.inputs.in_predicted_path ? 'Yes' : 'No'}</strong></div>
          <div><span>Obstacle present</span><strong>{result.inputs.obstacle_present ? 'Yes' : 'No'}</strong></div>
        </div>
        <ol className="decision-log-list">
          {result.decision_log.map((entry, index) => (
            <li key={`${entry.event}-${index}`}>
              <span className="log-time">{entry.time_s.toFixed(1)}s</span>
              <div>
                <strong>{entry.event.replace('_', ' ')}</strong>
                <p>{entry.explanation}</p>
                <small>Risk {entry.risk_score}/100 · {entry.action.replace('_', ' ')}</small>
              </div>
            </li>
          ))}
        </ol>
      </details>
    </section>
  )
}
