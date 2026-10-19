import { useEffect, useMemo, useState } from 'react'
import type { SimulationResult } from '../types'

interface RoadSimulationProps {
  result: SimulationResult | null
}

function vehicle(x: number, y: number, color: string, label: string) {
  return (
    <g transform={`translate(${x} ${y})`}>
      <rect x="-19" y="-30" width="38" height="60" rx="10" fill={color} stroke="#e9f2f5" strokeOpacity=".55" strokeWidth="1.5" />
      <path d="M-12 -14 Q0 -23 12 -14 L14 1 L-14 1Z" fill="#bdd9df" fillOpacity=".62" />
      <rect x="-14" y="10" width="28" height="10" rx="3" fill="#182329" />
      <circle cx="-12" cy="-19" r="3" fill="#d6fbff" />
      <circle cx="12" cy="-19" r="3" fill="#d6fbff" />
      <text x="0" y="43" textAnchor="middle" className="svg-car-label">{label}</text>
    </g>
  )
}

export default function RoadSimulation({ result }: RoadSimulationProps) {
  const [frameIndex, setFrameIndex] = useState(0)
  const timeline = result?.timeline ?? []
  useEffect(() => {
    setFrameIndex(0)
    if (!result || timeline.length < 2) return
    const interval = window.setInterval(() => {
      setFrameIndex((index) => index >= timeline.length - 1 ? 0 : index + 1)
    }, 80)
    return () => window.clearInterval(interval)
  }, [result, timeline.length])

  const step = timeline[frameIndex]
  const layout = useMemo(() => {
    if (!step || timeline.length < 2) return { egoY: 326, hazardY: 120 }
    const last = timeline[timeline.length - 1]
    const totalDistance = Math.max(20, last.vehicle_position_m)
    const scale = 145 / totalDistance
    const egoY = 330 - Math.min(145, step.vehicle_position_m * scale)
    const hazardY = result?.inputs.obstacle_present
      ? 330 - (step.obstacle_position_m ?? result.inputs.obstacle_distance_m) * scale
      : 110
    return { egoY, hazardY }
  }, [result, step, timeline])

  const speedKmh = step ? Math.round(step.vehicle_speed_mps * 3.6) : result?.inputs.speed_kmh
  const action = result?.action.replace('_', ' ') ?? 'awaiting simulation'
  const outcome = result?.outcome.replace('_', ' ') ?? 'No episode loaded'

  return (
    <section className="panel simulation-panel" id="simulation" aria-labelledby="simulation-title">
      <div className="panel-heading simulation-heading">
        <div>
          <div className="eyebrow">LIVE SCENARIO</div>
          <h2 id="simulation-title">Road simulation</h2>
        </div>
        <div className={`simulation-live ${result ? 'is-live' : ''}`}><span />{result ? 'EPISODE PLAYBACK' : 'STANDBY'}</div>
      </div>
      <div className="road-stage">
        <div className="road-overlay-label top"><span className="road-dot amber-dot" /> HAZARD TRACK</div>
        <div className="road-overlay-label bottom"><span className="road-dot green-dot" /> EGO VEHICLE</div>
        <svg className="road-svg" viewBox="0 0 460 400" role="img" aria-label={result ? `${result.inputs.scenario_name} simulation showing ${action}` : 'Road simulation waiting for an episode'}>
          <defs>
            <linearGradient id="roadFade" x1="0" x2="0" y1="0" y2="1">
              <stop offset="0%" stopColor="#252c32" />
              <stop offset="100%" stopColor="#171c21" />
            </linearGradient>
            <pattern id="roadGrid" width="32" height="32" patternUnits="userSpaceOnUse">
              <path d="M32 0H0V32" fill="none" stroke="#ffffff" strokeOpacity=".025" />
            </pattern>
          </defs>
          <rect width="460" height="400" fill="#111519" />
          <path d="M98 0H362L420 400H40Z" fill="url(#roadFade)" stroke="#323b42" strokeWidth="2" />
          <path d="M98 0H362L420 400H40Z" fill="url(#roadGrid)" />
          <path d="M230 0V400" stroke="#e1e8e5" strokeOpacity=".28" strokeWidth="3" strokeDasharray="22 18" />
          <path d="M137 0L83 400M323 0L377 400" stroke="#d3dbdc" strokeOpacity=".18" strokeWidth="2" />
          <path d={`M230 368V${Math.max(50, layout.egoY + 20)}`} stroke="#48dfa2" strokeOpacity=".35" strokeDasharray="5 7" />
          {result?.inputs.obstacle_present && (
            <g transform={`translate(230 ${Math.max(48, Math.min(260, layout.hazardY))})`}>
              <circle r="34" fill="#ffb84e" fillOpacity=".09" stroke="#ffb84e" strokeOpacity=".28" strokeDasharray="4 5" />
              <path d="M0 -20L19 14H-19Z" fill="#f5a846" stroke="#ffe0a9" strokeWidth="1.5" />
              <text x="0" y="7" textAnchor="middle" fontSize="14" fontWeight="700" fill="#282018">!</text>
              {vehicle(0, 68, '#a76854', 'OBJECT')}
            </g>
          )}
          {vehicle(230, layout.egoY, '#3e9b7a', 'EGO')}
          <text x="24" y="28" className="svg-small-label">{result ? `T+${step?.time_s.toFixed(1) ?? '0.0'} SEC` : 'SIMULATION READY'}</text>
        </svg>
        <div className="road-metric speed">
          <span className="mini-label">SPEED</span>
          <strong>{speedKmh ?? '—'}<small> km/h</small></strong>
        </div>
        <div className="road-metric separation">
          <span className="mini-label">SEPARATION</span>
          <strong>{step?.separation_m != null ? `${Math.max(0, step.separation_m).toFixed(1)} m` : result?.inputs.obstacle_present ? '—' : 'CLEAR'}</strong>
        </div>
      </div>
      <div className="simulation-footer">
        <div><span className="footer-label">CURRENT ACTION</span><strong className={`action-text ${result?.action ?? ''}`}>{action}</strong></div>
        <div className="footer-outcome"><span className="footer-label">EPISODE OUTCOME</span><strong className={`outcome-text ${result?.outcome ?? ''}`}>{outcome}</strong></div>
        <span className="simulation-time">{step ? `${step.time_s.toFixed(1)}s` : '—'}</span>
      </div>
    </section>
  )
}
