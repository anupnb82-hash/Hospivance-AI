import React from 'react';

export default function RiskBadge({ level }) {
  const normLevel = (level || 'LOW').toUpperCase();
  const label = normLevel === 'HIGH' ? 'High Risk' : normLevel === 'MODERATE' ? 'Moderate' : 'Low Risk';

  return (
    <span className={`badge-risk ${normLevel}`}>
      <span style={{
        width: 6,
        height: 6,
        borderRadius: '50%',
        backgroundColor: normLevel === 'HIGH' ? '#dc2626' : normLevel === 'MODERATE' ? '#d97706' : '#059669',
        display: 'inline-block'
      }} />
      {label}
    </span>
  );
}
