interface MetricCardProps {
  label: string
  value: string
  unit?: string
  caption: string
  tone?: 'green' | 'amber' | 'red' | 'blue'
  icon: string
}

export default function MetricCard({
  label,
  value,
  unit,
  caption,
  tone = 'blue',
  icon,
}: MetricCardProps) {
  return (
    <article className="metric-card">
      <div className={`metric-icon ${tone}`}>{icon}</div>
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}<span>{unit}</span></div>
      <div className="metric-caption">{caption}</div>
    </article>
  )
}
