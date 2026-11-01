import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import RiskBadge from '../components/RiskBadge';

export default function DepartmentOvercrowdingPage() {
  const [data, setData] = useState(null);
  const [selectedDeptId, setSelectedDeptId] = useState(null);
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getDepartments(selectedDeptId, days);
      setData(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedDeptId, days]);

  const depts = data?.departments || [];
  const activeDept = depts.find(d => selectedDeptId ? d.department_id === selectedDeptId : true) || depts[0];

  return (
    <div>
      {/* Controls Bar */}
      <div className="dashboard-card" style={{ padding: '16px 24px', marginBottom: 20 }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontSize: 13, fontWeight: 600, color: '#475569' }}>Focus Department:</span>
            <select
              value={selectedDeptId || ''}
              onChange={(e) => setSelectedDeptId(e.target.value ? parseInt(e.target.value, 10) : null)}
              style={{
                padding: '6px 12px',
                borderRadius: 8,
                border: '1px solid #cbd5e1',
                fontSize: 13,
                fontWeight: 500,
                outline: 'none',
              }}
            >
              <option value="">All Departments Overview</option>
              {depts.map(d => (
                <option key={d.department_id} value={d.department_id}>{d.name}</option>
              ))}
            </select>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontSize: 13, fontWeight: 600, color: '#475569' }}>Window:</span>
            {[14, 30, 60].map(w => (
              <button
                key={w}
                className={`btn btn-sm ${days === w ? 'btn-primary' : 'btn-outline'}`}
                onClick={() => setDays(w)}
              >
                {w} Days
              </button>
            ))}
          </div>
        </div>
      </div>

      {loading ? (
        <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>Loading department bottleneck statistics...</div>
      ) : error ? (
        <div style={{ padding: 20, background: '#fee2e2', color: '#991b1b', borderRadius: 8 }}>{error}</div>
      ) : (
        <>
          {/* Overcrowding Risk Summary Cards */}
          <div className="kpi-grid">
            {depts.map((d, i) => (
              <div key={i} className="kpi-card" style={{
                borderTop: d.overcrowding_frequency_pct > 25 ? '4px solid #ef4444' : '4px solid #0d9488'
              }}>
                <div className="kpi-label">{d.name}</div>
                <div className="kpi-value" style={{ fontSize: 24 }}>
                  {d.average_occupancy_rate}% avg
                </div>
                <div className="kpi-subtext" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                  <span>Peak: <strong>{d.peak_occupancy_rate}%</strong></span>
                  <span>Overcrowding rate: <strong style={{ color: d.overcrowding_frequency_pct > 20 ? '#dc2626' : '#059669' }}>
                    {d.overcrowding_frequency_pct}% of days
                  </strong></span>
                </div>
              </div>
            ))}
          </div>

          {/* Department Deep-Dive Table */}
          <div className="dashboard-card">
            <div className="card-header">
              <div>
                <h3>{days}-Day Department Overcrowding Indices</h3>
                <p style={{ fontSize: 12, color: '#64748b' }}>Comparing patient throughput velocities and bottleneck severity</p>
              </div>
            </div>

            <div className="data-table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Department</th>
                    <th>Total Beds</th>
                    <th>Avg Occupancy</th>
                    <th>Peak Occupancy</th>
                    <th>Days in High-Risk (≥90%)</th>
                    <th>Avg Wait Time</th>
                    <th>Total Influx</th>
                    <th>Total Discharges</th>
                    <th>Net Influx Flow</th>
                  </tr>
                </thead>
                <tbody>
                  {depts.map((d, i) => (
                    <tr key={i}>
                      <td style={{ fontWeight: 600 }}>{d.name}</td>
                      <td>{d.total_beds}</td>
                      <td>{d.average_occupancy_rate}%</td>
                      <td style={{ fontWeight: 700, color: d.peak_occupancy_rate >= 95 ? '#dc2626' : '#0f172a' }}>
                        {d.peak_occupancy_rate}%
                      </td>
                      <td>
                        <span style={{
                          padding: '3px 8px',
                          borderRadius: 4,
                          fontSize: 12,
                          fontWeight: 700,
                          backgroundColor: d.high_risk_days_count > 5 ? '#fee2e2' : '#f1f5f9',
                          color: d.high_risk_days_count > 5 ? '#991b1b' : '#334155'
                        }}>
                          {d.high_risk_days_count} / {days} days ({d.overcrowding_frequency_pct}%)
                        </span>
                      </td>
                      <td>{d.average_wait_time} min</td>
                      <td style={{ fontWeight: 600 }}>{d.total_admissions}</td>
                      <td style={{ fontWeight: 600 }}>{d.total_discharges}</td>
                      <td style={{
                        fontWeight: 700,
                        color: d.net_flow > 0 ? '#dc2626' : '#059669'
                      }}>
                        {d.net_flow > 0 ? `+${d.net_flow} backlog` : `${d.net_flow} buffer`}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
