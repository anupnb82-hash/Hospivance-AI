import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import RiskBadge from '../components/RiskBadge';
import { OccupancyGauge } from '../components/Charts';

export default function BedMonitoringPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getBeds();
      setData(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>Loading bed availability data...</div>;
  }

  if (error) {
    return (
      <div style={{ padding: 20, background: '#fee2e2', color: '#991b1b', borderRadius: 8 }}>
        {error}
      </div>
    );
  }

  const summary = data?.summary || {};
  const depts = data?.department_beds || [];

  return (
    <div>
      {/* Top Capacity Summary */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-label">Total Hospital Capacity</div>
          <div className="kpi-value">{summary.total_hospital_beds} Beds</div>
          <div className="kpi-subtext">Across 6 specialized departments</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">Current Bed Census</div>
          <div className="kpi-value">{summary.total_occupied} Occupied</div>
          <div className="kpi-subtext">{summary.total_available} Empty Beds Available</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">Overall Bed Saturation</div>
          <div className="kpi-value" style={{ color: summary.overall_occupancy_rate >= 90 ? '#ef4444' : '#0f172a' }}>
            {summary.overall_occupancy_rate}%
          </div>
          <div className="kpi-subtext">
            {summary.critical_departments_count} departments at critical capacity
          </div>
        </div>
      </div>

      {/* Department Bed Matrix */}
      <div className="dashboard-card">
        <div className="card-header">
          <div>
            <h3>Hospital Bed Availability Matrix</h3>
            <p style={{ fontSize: 12, color: '#64748b' }}>Detailed breakdown of occupied, sanitizing, and admission-ready beds</p>
          </div>
          <button className="btn btn-outline btn-sm" onClick={loadData}>Refresh Census</button>
        </div>

        <div className="data-table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Department</th>
                <th>Total Beds</th>
                <th>Occupied</th>
                <th>Available</th>
                <th>Sanitizing / Turnover</th>
                <th>Admission Ready</th>
                <th>Occupancy %</th>
                <th>Risk Category</th>
                <th>Discharges Needed to Safety (&lt;85%)</th>
              </tr>
            </thead>
            <tbody>
              {depts.map((d, i) => (
                <tr key={i}>
                  <td style={{ fontWeight: 600 }}>{d.department}</td>
                  <td>{d.total_beds}</td>
                  <td style={{ fontWeight: 700 }}>{d.occupied_beds}</td>
                  <td style={{ fontWeight: 600, color: d.available_beds <= 2 ? '#dc2626' : '#059669' }}>
                    {d.available_beds}
                  </td>
                  <td style={{ color: '#64748b' }}>{d.maintenance_beds} beds</td>
                  <td style={{ fontWeight: 700, color: '#0d9488' }}>{d.ready_for_admission} ready</td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{ fontWeight: 700 }}>{d.occupancy_rate}%</span>
                      <div className="progress-bar-bg" style={{ width: 70 }}>
                        <div
                          className="progress-bar-fill"
                          style={{
                            width: `${Math.min(100, d.occupancy_rate)}%`,
                            backgroundColor: d.risk_level === 'HIGH' ? '#ef4444' : d.risk_level === 'MODERATE' ? '#f59e0b' : '#10b981'
                          }}
                        />
                      </div>
                    </div>
                  </td>
                  <td><RiskBadge level={d.risk_level} /></td>
                  <td>
                    {d.target_discharges_needed > 0 ? (
                      <span style={{
                        padding: '3px 8px',
                        backgroundColor: '#fee2e2',
                        color: '#991b1b',
                        borderRadius: 4,
                        fontSize: 12,
                        fontWeight: 700
                      }}>
                        ⚡ Expedite {d.target_discharges_needed} discharges
                      </span>
                    ) : (
                      <span style={{ color: '#059669', fontSize: 12 }}>Buffer adequate</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 14-Day Occupancy History Mini-Graphs */}
      <div className="dashboard-card">
        <div className="card-header">
          <div>
            <h3>14-Day Historical Occupancy Trend Curves</h3>
            <p style={{ fontSize: 12, color: '#64748b' }}>Tracking bed kinetics and stability trends over the prior 2 weeks</p>
          </div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 20 }}>
          {depts.map((d, i) => {
            const hist = d.occupancy_history_14d || [];
            return (
              <div key={i} style={{ border: '1px solid #e2e8f0', borderRadius: 8, padding: 16 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 10 }}>
                  <span style={{ fontWeight: 600, fontSize: 14 }}>{d.department}</span>
                  <RiskBadge level={d.risk_level} />
                </div>
                <div style={{ height: 60, display: 'flex', alignItems: 'flex-end', gap: 4, paddingBottom: 4, borderBottom: '1px solid #cbd5e1' }}>
                  {hist.map((h, hIdx) => {
                    const hRate = h.occupancy_rate || 50;
                    const barColor = hRate >= 90 ? '#ef4444' : hRate >= 75 ? '#f59e0b' : '#10b981';
                    return (
                      <div
                        key={hIdx}
                        title={`${h.date}: ${hRate}%`}
                        style={{
                          flex: 1,
                          height: `${Math.min(100, Math.max(15, hRate))}%`,
                          backgroundColor: barColor,
                          borderRadius: '2px 2px 0 0',
                          opacity: hIdx === hist.length - 1 ? 1 : 0.65,
                        }}
                      />
                    );
                  })}
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: '#64748b', marginTop: 4 }}>
                  <span>14 days ago</span>
                  <span>Today ({d.occupancy_rate}%)</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
