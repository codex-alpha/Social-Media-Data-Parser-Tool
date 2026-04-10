import { Shield, BarChart3, Brain, Search, Network, Clock, AlertTriangle, Activity, Terminal } from 'lucide-react';

const NAV_SECTIONS = [
  {
    title: 'Intelligence',
    items: [
      { id: 'overview', label: 'Dashboard', icon: BarChart3 },
      { id: 'manual', label: 'Manual Input', icon: Terminal },
      { id: 'sentiment', label: 'Sentiment Analysis', icon: Brain },
      { id: 'threats', label: 'Threat Detection', icon: AlertTriangle, badge: null },
    ],
  },
  {
    title: 'Forensics',
    items: [
      { id: 'forensics', label: 'Digital Forensics', icon: Shield },
      { id: 'graph', label: 'Social Graph', icon: Network },
      { id: 'timeline', label: 'Event Timeline', icon: Clock },
    ],
  },
];

export function Sidebar({ activePage, onNavigate }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <div className="logo-icon">⚡</div>
          <div>
            <div className="logo-text">Hawkeye</div>
            <div className="logo-sub">Intelligence Platform</div>
          </div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {NAV_SECTIONS.map(section => (
          <div key={section.title} className="nav-section">
            <div className="nav-section-title">{section.title}</div>
            {section.items.map(item => {
              const Icon = item.icon;
              return (
                <div
                  key={item.id}
                  className={`nav-item ${activePage === item.id ? 'active' : ''}`}
                  onClick={() => onNavigate(item.id)}
                >
                  <Icon className="nav-icon" size={18} />
                  <span>{item.label}</span>
                  {item.badge != null && <span className="nav-badge">{item.badge}</span>}
                </div>
              );
            })}
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="system-status">
          <div className="status-dot" />
          <span>System Operational</span>
          <Activity size={12} style={{ marginLeft: 'auto', opacity: 0.5 }} />
        </div>
      </div>
    </aside>
  );
}
