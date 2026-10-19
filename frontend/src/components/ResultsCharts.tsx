import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { EvaluationResult } from '../types'

interface ResultsChartsProps {
  evaluation: EvaluationResult | null
}

export default function ResultsCharts({ evaluation }: ResultsChartsProps) {
  const chartData = evaluation
    ? evaluation.scenario_ids.map((id) => {
      const scenarioMetrics = evaluation.per_scenario_metrics[id]
      const name = evaluation.episode_records.find((record) => record.scenario_id === id)?.scenario_name ?? id
      return {
        scenario: name,
        'Baseline collisions': scenarioMetrics.baseline.collision_rate_pct,
        'Safety-aware collisions': scenarioMetrics.safety_aware.collision_rate_pct,
        'Baseline near-misses': scenarioMetrics.baseline.near_miss_rate_pct,
        'Safety-aware near-misses': scenarioMetrics.safety_aware.near_miss_rate_pct,
        'Baseline unnecessary braking': scenarioMetrics.baseline.unnecessary_braking_rate_pct,
        'Safety-aware unnecessary braking': scenarioMetrics.safety_aware.unnecessary_braking_rate_pct,
      }
    })
    : []

  return (
    <section className="panel chart-panel" id="analytics" aria-labelledby="analytics-title">
      <div className="panel-heading">
        <div><div className="eyebrow">EXPERIMENTAL OUTCOMES</div><h2 id="analytics-title">Safety analytics</h2></div>
        {evaluation && <span className="chart-unit">RATE · %</span>}
      </div>
      {evaluation ? (
        <div className="chart-wrap">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 16, right: 12, left: -18, bottom: 16 }}>
              <CartesianGrid stroke="#293138" strokeDasharray="3 5" vertical={false} />
              <XAxis dataKey="scenario" tick={{ fill: '#89969e', fontSize: 10 }} axisLine={{ stroke: '#39434a' }} tickLine={false} interval={0} angle={-12} textAnchor="end" height={52} />
              <YAxis tick={{ fill: '#75828b', fontSize: 10 }} axisLine={false} tickLine={false} domain={[0, 100]} unit="%" />
              <Tooltip
                contentStyle={{ background: '#171d22', border: '1px solid #354149', borderRadius: 8, color: '#eaf0f1' }}
                formatter={(value) => value == null ? ['Unavailable', ''] : [`${Number(value).toFixed(1)}%`, undefined]}
                labelStyle={{ color: '#bbc4c8', marginBottom: 4 }}
              />
              <Legend wrapperStyle={{ color: '#9aa6ad', fontSize: 11 }} />
              <Bar dataKey="Baseline collisions" fill="#d38b58" radius={[3, 3, 0, 0]} maxBarSize={16} />
              <Bar dataKey="Safety-aware collisions" fill="#45d59a" radius={[3, 3, 0, 0]} maxBarSize={16} />
              <Bar dataKey="Baseline near-misses" fill="#b6a170" radius={[3, 3, 0, 0]} maxBarSize={16} />
              <Bar dataKey="Safety-aware near-misses" fill="#4b9d7e" radius={[3, 3, 0, 0]} maxBarSize={16} />
              <Bar dataKey="Baseline unnecessary braking" fill="#c46e62" radius={[3, 3, 0, 0]} maxBarSize={16} />
              <Bar dataKey="Safety-aware unnecessary braking" fill="#78bd9e" radius={[3, 3, 0, 0]} maxBarSize={16} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="chart-empty">
          <span className="chart-empty-icon">▥</span>
          <strong>Analytics appear after evaluation</strong>
          <p>Charts use measured simulation records. No example results are preloaded.</p>
        </div>
      )}
      {evaluation && <p className="chart-caption">Null metrics remain unavailable, not zero. Rates use {evaluation.episodes_per_scenario} seeded input variations per scenario.</p>}
    </section>
  )
}
