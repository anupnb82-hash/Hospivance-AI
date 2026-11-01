import React from 'react';

/**
 * Responsive SVG Line & Forecast Chart.
 */
export function TrendLineChart({ data = [], height = 260, title }) {
  if (!data || data.length === 0) {
    return <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#94a3b8' }}>No data available</div>;
  }

  const padding = { top: 20, right: 30, bottom: 40, left: 45 };
  const width = 640;
  const innerWidth = width - padding.left - padding.right;
  const innerHeight = height - padding.top - padding.bottom;

  const yValues = data.map(d => d.admissions || d.occupancy_rate || 0);
  const minY = Math.max(0, Math.min(...yValues) * 0.8);
  const maxY = Math.max(...yValues) * 1.15 || 100;

  const getX = (idx) => padding.left + (idx / Math.max(1, data.length - 1)) * innerWidth;
  const getY = (val) => padding.top + innerHeight - ((val - minY) / Math.max(1, maxY - minY)) * innerHeight;

  // Split points into actual vs forecast
  const points = data.map((d, i) => ({
    x: getX(i),
    y: getY(d.admissions || d.occupancy_rate || 0),
    val: d.admissions || d.occupancy_rate || 0,
    label: d.date ? d.date.slice(5) : `D${i+1}`,
    isForecast: d.type === 'forecast',
  }));

  const actualPoints = points.filter(p => !p.isForecast);
  const forecastPoints = points.slice(Math.max(0, actualPoints.length - 1));

  const actualPath = actualPoints.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
  const forecastPath = forecastPoints.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');

  return (
    <div style={{ width: '100%', overflowX: 'auto' }}>
      <svg viewBox={`0 0 ${width} ${height}`} style={{ width: '100%', height: 'auto', display: 'block' }}>
        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((pct, i) => {
          const y = padding.top + innerHeight * (1 - pct);
          const val = Math.round(minY + (maxY - minY) * pct);
          return (
            <g key={i}>
              <line x1={padding.left} y1={y} x2={width - padding.right} y2={y} stroke="#e2e8f0" strokeDasharray="3 3" />
              <text x={padding.left - 8} y={y + 4} fontSize="10" fill="#94a3b8" textAnchor="end">{val}</text>
            </g>
          );
        })}

        {/* Actual Line */}
        {actualPath && (
          <path d={actualPath} fill="none" stroke="#0d9488" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
        )}

        {/* Forecast Line */}
        {forecastPath && forecastPoints.length > 1 && (
          <path d={forecastPath} fill="none" stroke="#f59e0b" strokeWidth="3" strokeDasharray="5 4" strokeLinecap="round" />
        )}

        {/* Data points */}
        {points.map((p, i) => (
          <g key={i}>
            <circle cx={p.x} cy={p.y} r={p.isForecast ? 5 : 4} fill={p.isForecast ? '#f59e0b' : '#0d9488'} stroke="#ffffff" strokeWidth="2" />
            <text x={p.x} y={height - padding.bottom + 18} fontSize="11" fill="#64748b" textAnchor="middle">{p.label}</text>
            <text x={p.x} y={p.y - 10} fontSize="10.5" fontWeight="600" fill={p.isForecast ? '#b45309' : '#0f766e'} textAnchor="middle">
              {p.val}
            </text>
          </g>
        ))}
      </svg>
      <div style={{ display: 'flex', gap: 18, justifyContent: 'center', marginTop: 8, fontSize: 12 }}>
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
          <span style={{ width: 14, height: 3, backgroundColor: '#0d9488', display: 'inline-block' }} /> Historical Actuals
        </span>
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
          <span style={{ width: 14, height: 3, backgroundColor: '#f59e0b', borderTop: '2px dashed #f59e0b', display: 'inline-block' }} /> AI Model Forecast
        </span>
      </div>
    </div>
  );
}

/**
 * Bar Chart for Department comparison.
 */
export function DepartmentBarChart({ data = [], height = 240 }) {
  if (!data || data.length === 0) return null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14, marginTop: 10 }}>
      {data.map((item, idx) => {
        const rate = item.occupancy_rate || 0;
        const color = rate >= 90 ? '#ef4444' : rate >= 75 ? '#f59e0b' : '#10b981';
        return (
          <div key={idx}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, marginBottom: 5 }}>
              <span style={{ fontWeight: 600, color: '#0f172a' }}>{item.name || item.department}</span>
              <span style={{ fontWeight: 700, color }}>{rate}% ({item.occupied_beds || 0}/{item.total_beds || 0} beds)</span>
            </div>
            <div className="progress-bar-bg" style={{ height: 10 }}>
              <div className="progress-bar-fill" style={{ width: `${Math.min(100, rate)}%`, backgroundColor: color }} />
            </div>
          </div>
        );
      })}
    </div>
  );
}

/**
 * Gauge for Capacity Monitoring.
 */
export function OccupancyGauge({ value = 0, size = 160, label = 'System Occupancy' }) {
  const normVal = Math.min(100, Math.max(0, value));
  const stroke = 14;
  const radius = (size - stroke) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDashoffset = circumference - (normVal / 100) * circumference * 0.75;
  const color = normVal >= 90 ? '#ef4444' : normVal >= 75 ? '#f59e0b' : '#10b981';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ position: 'relative', width: size, height: size * 0.85 }}>
        <svg width={size} height={size} style={{ transform: 'rotate(135deg)', transformOrigin: '50% 50%' }}>
          <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="#e2e8f0" strokeWidth={stroke} strokeDasharray={circumference * 0.75 + ' ' + circumference * 0.25} />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={stroke}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 0.5s ease' }}
          />
        </svg>
        <div style={{ position: 'absolute', top: '38%', left: 0, right: 0, textAlign: 'center' }}>
          <div style={{ fontSize: 28, fontWeight: 800, color }}>{normVal}%</div>
          <div style={{ fontSize: 11, fontWeight: 700, color: '#64748b', textTransform: 'uppercase' }}>
            {normVal >= 90 ? 'CRITICAL' : normVal >= 75 ? 'WARNING' : 'NORMAL'}
          </div>
        </div>
      </div>
      <div style={{ fontSize: 13, fontWeight: 600, color: '#475569', marginTop: -6 }}>{label}</div>
    </div>
  );
}
