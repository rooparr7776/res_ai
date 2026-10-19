import type { EvaluationResult, PolicyMetrics } from '../types'

interface PolicyComparisonProps {
  evaluation: EvaluationResult | null
}

function metric(value: number | null, suffix = '%'): string {
  return value == null ? '—' : `${value.toFixed(value % 1 === 0 ? 0 : 1)}${suffix}`
}

function PolicyCard({
  title,
  subtitle,
  metrics,
  tone,
}: {
  title: string
  subtitle: string
  metrics: PolicyMetrics
  tone: 'neutral' | 'green'
}) {
  return (
    <article className={`policy-card ${tone}`}>
      <div className="policy-card-heading">
        <div className={`policy-symbol ${tone}`}>{tone === 'green' ? '✳' : '◌'}</div>
        <div><h3>{title}</h3><p>{subtitle}</p></div>
      </div>
      <div className="policy-metrics">
        <div><span>Collision rate</span><strong>{metric(metrics.collision_rate_pct)}</strong></div>
        <div><span>Near-miss rate</span><strong>{metric(metrics.near_miss_rate_pct)}</strong></div>
        <div><span>Unnecessary braking</span><strong>{metric(metrics.unnecessary_braking_rate_pct)}</strong></div>
        <div><span>Mean reaction time</span><strong>{metric(metrics.average_reaction_time_s, ' s')}</strong></div>
      </div>
      <div className="policy-sample-count">{metrics.total_episodes} simulated episodes</div>
    </article>
  )
}

export default function PolicyComparison({ evaluation }: PolicyComparisonProps) {
  return (
    <section className="panel comparison-panel" id="comparison" aria-labelledby="comparison-title">
      <div className="panel-heading">
        <div><div className="eyebrow">PAIRED EXPERIMENT</div><h2 id="comparison-title">Policy comparison</h2></div>
        {evaluation && <span className="seed-badge">SEED {evaluation.seed}</span>}
      </div>
      {evaluation ? (
        <>
          <div className="policy-cards">
            <PolicyCard title="Baseline" subtitle="Reference policy" metrics={evaluation.metrics_by_policy.baseline} tone="neutral" />
            <PolicyCard title="Safety-aware" subtitle="More cautious decision rules" metrics={evaluation.metrics_by_policy.safety_aware} tone="green" />
          </div>
          <p className="evaluation-note">{evaluation.variation_description}</p>
        </>
      ) : (
        <div className="comparison-placeholder">
          <div className="empty-symbol">⇄</div>
          <div><strong>No experiment results yet</strong><p>Run a policy evaluation to compare outcomes on paired scenarios.</p></div>
        </div>
      )}
    </section>
  )
}
