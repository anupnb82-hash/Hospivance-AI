import React from 'react';

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Command Center', icon: '📊' },
  { id: 'predictions', label: 'Admission Forecasts', icon: '📈' },
  { id: 'beds', label: 'Bed Capacity Matrix', icon: '🛏️' },
  { id: 'departments', label: 'Department Bottlenecks', icon: '🏥' },
  { id: 'alerts', label: 'Overcrowding Alerts', icon: '🚨' },
  { id: 'recommendations', label: 'AI Recommendations', icon: '💡' },
  { id: 'analytics', label: 'Historical & ML Metrics', icon: '📉' },
  { id: 'settings', label: 'Settings & FHIR Export', icon: '⚙️' },
];

export default function Sidebar({ currentTab, onSelectTab }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="logo-badge">H</div>
        <div className="brand-text">
          <h1>Hospivance AI</h1>
          <span>Operations Intelligence</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item) => (
          <button
            key={item.id}
            className={`nav-link ${currentTab === item.id ? 'active' : ''}`}
            onClick={() => onSelectTab(item.id)}
          >
            <span style={{ fontSize: 16 }}>{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="synthetic-pill">
          <span className="status-dot" />
          <span>Synthetic Demo Model</span>
        </div>
        <div>Hospivance AI v1.0.0</div>
      </div>
    </aside>
  );
}
