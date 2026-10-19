interface HeaderProps {
  backendOnline: boolean
}

export default function Header({ backendOnline }: HeaderProps) {
  return (
    <header className="topbar">
      <a className="brand" href="#overview" aria-label="DriveGuard AI overview">
        <span className="brand-mark" aria-hidden="true">
          <span />
          <span />
          <span />
        </span>
        <span className="brand-name">DRIVEGUARD<span>AI</span></span>
      </a>
      <div className="topbar-meta">
        <div className={`connection-status ${backendOnline ? 'online' : 'offline'}`}>
          <span className="status-dot" />
          {backendOnline ? 'Backend connected' : 'Backend offline'}
        </div>
        <span className="topbar-divider" />
        <span className="mode-badge">EDUCATIONAL SIMULATION</span>
      </div>
    </header>
  )
}
