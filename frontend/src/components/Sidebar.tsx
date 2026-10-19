const items = [
  { href: '#overview', label: 'Overview', icon: '◫' },
  { href: '#simulation', label: 'Live simulation', icon: '⌁' },
  { href: '#comparison', label: 'Policy comparison', icon: '⇄' },
  { href: '#analytics', label: 'Safety analytics', icon: '▥' },
  { href: '#ethics', label: 'Ethical analysis', icon: '◇' },
]

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-label">WORKSPACE</div>
      <nav aria-label="Main navigation">
        {items.map((item, index) => (
          <a className={`nav-item ${index === 0 ? 'active' : ''}`} href={item.href} key={item.href}>
            <span className="nav-icon" aria-hidden="true">{item.icon}</span>
            <span>{item.label}</span>
            {index === 0 && <span className="nav-indicator" />}
          </a>
        ))}
      </nav>
      <div className="sidebar-bottom">
        <div className="sidebar-note-icon">i</div>
        <div>
          <strong>Simulation only</strong>
          <p>Not for real-world driving decisions.</p>
        </div>
      </div>
    </aside>
  )
}
