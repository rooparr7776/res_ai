const topics = [
  {
    number: '01',
    title: 'Safety & reliability',
    text: 'Collision and near-miss rates describe only this simplified simulator. A favorable result does not establish real-world safety or cover untested road conditions.',
    tag: 'OUTCOMES',
  },
  {
    number: '02',
    title: 'Transparency',
    text: 'The policy uses documented rules and a visible risk score. Clear rules can still encode poor assumptions, miss hazards, or produce incorrect judgments.',
    tag: 'EXPLAINABILITY',
  },
  {
    number: '03',
    title: 'Robustness',
    text: 'Seeded changes to speed, distance, visibility, and perception confidence help probe sensitivity. This narrow parameter sweep is not a substitute for diverse field tests.',
    tag: 'VARIATION',
  },
  {
    number: '04',
    title: 'Human oversight',
    text: 'Driver-assistance tools need clear limits and attentive human oversight. This educational simulator must never guide actual driving or replace a qualified driver.',
    tag: 'OVERSIGHT',
  },
  {
    number: '05',
    title: 'Accountability & fairness',
    text: 'Decision logs support investigation. Synthetic scenarios cannot establish fairness across people or road users; responsibility in real failures can involve developers, operators, manufacturers, and regulators.',
    tag: 'GOVERNANCE',
  },
  {
    number: '06',
    title: 'Ethical trade-offs',
    text: 'More conservative braking may reduce some simulated risks while increasing unnecessary interventions. Uncertain perception, traffic disruption, and user trust involve competing values, not one universally correct answer.',
    tag: 'TRADE-OFFS',
  },
]

export default function EthicalAnalysis() {
  return (
    <section className="panel ethics-panel" id="ethics" aria-labelledby="ethics-title">
      <div className="panel-heading">
        <div><div className="eyebrow">RESPONSIBLE AI</div><h2 id="ethics-title">Ethical analysis</h2></div>
        <span className="ethics-mark">✳</span>
      </div>
      <div className="ethics-grid">
        {topics.map((topic) => (
          <article className="ethics-item" key={topic.number}>
            <span className="ethics-number">{topic.number}</span>
            <div><div className="ethics-tag">{topic.tag}</div><h3>{topic.title}</h3><p>{topic.text}</p></div>
          </article>
        ))}
      </div>
      <div className="ethics-callout"><span>!</span><p><strong>Scope boundary:</strong> DriveGuard AI is an educational rule-based demonstration inspired by autonomous-driving ethics. It is not Tesla Autopilot, does not reproduce proprietary software, and is not a validated vehicle controller.</p></div>
    </section>
  )
}
