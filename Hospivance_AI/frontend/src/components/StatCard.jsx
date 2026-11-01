import React from 'react';

export default function StatCard({ label, value, subtext, alertLevel, icon }) {
  return (
    <div className="kpi-card">
      <div className="kpi-label">
        <span>{label}</span>
        {icon && <span>{icon}</span>}
      </div>
      <div className="kpi-value" style={{
        color: alertLevel === 'HIGH' ? '#dc2626' : alertLevel === 'MODERATE' ? '#d97706' : '#0f172a'
      }}>
        {value}
      </div>
      {subtext && <div className="kpi-subtext">{subtext}</div>}
    </div>
  );
}
