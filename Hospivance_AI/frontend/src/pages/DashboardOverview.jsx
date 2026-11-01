import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import StatCard from '../components/StatCard';
import RiskBadge from '../components/RiskBadge';
import { TrendLineChart, DepartmentBarChart, OccupancyGauge } from '../components/Charts';

export default function DashboardOverview({ onNavigate }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getDashboard();
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
    return <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>Loading hospital command center data...</div>;
  }

  if (error) {
    return (
      <div style={{ padding: 30, background: '#fee2e2', color: '#991b1b', borderRadius: 8 }}>
        <h4>Failed to connect to Hospivance AI API</h4>
        <p>{error}</p>
        <button className="btn btn-primary" style={{ marginTop: 12 }} onClick={loadData}>Retry</button>
      </div>
    );
  }

  const kpis = data?.kpis || {};
  const depts = data?.departments || [];

  return (
    <div>
      {/* Top Notification Banner if high risk */}
      {kpis.overall_risk_level === 'HIGH' && (
        <div style={{
          padding: '12px 20px',
          backgroundColor: '#fee2e2',
          borderLeft: '4px solid #ef4444',
          borderRadius: 8,
          marginBottom: 24,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <strong style={{ color: '#991b1b' }}>High Bottleneck Alert: </strong>
            <span style={{ color: '#7f1d1d', fontSize: 13.5 }}>
              Overall hospital occupancy is at {kpis.overall_occupancy_rate}%. Immediate clinical mitigation recommended.
            </span>
          </div>
          <button className="btn btn-primary btn-sm" onClick={() => onNavigate('recommendations')}>
            View AI Recommendations
          </button>
        </div>
      )}

      {/* KPI Cards Grid */}
      <div className="kpi-grid">
        <StatCard
          label="Total Bed Occupancy"
          value={`${kpis.overall_occupancy_rate || 0}%`}
          subtext={`${kpis.total_occupied_beds || 0} / ${kpis.total_beds || 0} Beds Occupied`}
          alertLevel={kpis.overall_risk_level}
        />
        <StatCard
          label="24h Forecasted Admissions"
          value={kpis.projected_24h_admissions || 0}
          subtext="Random Forest ML Model Prediction"
        />
        <StatCard
          label="Available Hospital Beds"
          value={kpis.total_available_beds || 0}
          subtext="Across all 6 inpatient units"
        />
        <StatCard
          label="Active Bottleneck Alerts"
          value={kpis.active_high_risk_alerts || 0}
          subtext="Unacknowledged Critical Events"
          alertLevel={kpis.active_high_risk_alerts > 0 ? 'HIGH' : 'LOW'}
        />
        <StatCard
          label="ER Average Wait Time"
          value={`${kpis.er_avg_wait_minutes || 0} min`}
          subtext="Door-to-provider triage time"
          alertLevel={kpis.er_avg_wait_minutes > 60 ? 'HIGH' : 'LOW'}
        />
      </div>

      {/* Main Charts Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: 24, marginBottom: 24 }}>
        {/* 7-Day Trend Chart */}
        <div className="dashboard-card" style={{ marginBottom: 0 }}>
          <div className="card-header">
            <div>
              <h3>7-Day Patient Admissions Trend & 24h AI Forecast</h3>
              <p style={{ fontSize: 12, color: '#64748b' }}>Comparing recent historical admissions with next-day projection</p>
            </div>
            <button className="btn btn-outline btn-sm" onClick={() => onNavigate('predictions')}>
              Multi-Day Forecasts
            </button>
          </div>
          <TrendLineChart data={data?.trend_7day || []} height={250} />
        </div>

        {/* System Occupancy Gauge & Department Risk */}
        <div className="dashboard-card" style={{ marginBottom: 0 }}>
          <div className="card-header">
            <div>
              <h3>Current Hospital Capacity Gauge</h3>
              <p style={{ fontSize: 12, color: '#64748b' }}>Real-time saturation index</p>
            </div>
            <RiskBadge level={kpis.overall_risk_level} />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-around', paddingTop: 10 }}>
            <OccupancyGauge value={kpis.overall_occupancy_rate} size={170} label="System Capacity" />
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10, fontSize: 13 }}>
              <div><strong>Total Staff on Duty:</strong> 158 clinicians</div>
              <div><strong>Ambulance Diversions:</strong> {depts.reduce((acc, d) => acc + (d.diverted_ambulances || 0), 0)} active</div>
              <div><strong>Model RMSE:</strong> {data?.model_performance?.rmse || 7.5} patients</div>
              <button className="btn btn-outline btn-sm" onClick={() => onNavigate('beds')}>
                Inspect Bed Availability
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Department Bottleneck Risk Table */}
      <div className="dashboard-card">
        <div className="card-header">
          <div>
            <h3>Department-Wise Overcrowding & Capacity Grid</h3>
            <p style={{ fontSize: 12, color: '#64748b' }}>Sorted by risk priority and occupancy percentage</p>
          </div>
          <button className="btn btn-outline btn-sm" onClick={() => onNavigate('departments')}>
            Detailed Analytics
          </button>
        </div>
        <div className="data-table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Department</th>
                <th>Total Beds</th>
                <th>Occupied</th>
                <th>Available</th>
                <th>Occupancy %</th>
                <th>Risk Level</th>
                <th>Avg Wait Time</th>
                <th>Ambulance Diversions</th>
                <th>Staffing</th>
              </tr>
            </thead>
            <tbody>
              {depts.map((d, i) => (
                <tr key={i}>
                  <td style={{ fontWeight: 600 }}>{d.name}</td>
                  <td>{d.total_beds}</td>
                  <td style={{ fontWeight: 600 }}>{d.occupied_beds}</td>
                  <td style={{ color: d.available_beds <= 3 ? '#dc2626' : '#059669', fontWeight: 600 }}>
                    {d.available_beds}
                  </td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{ minWidth: 42, fontWeight: 700 }}>{d.occupancy_rate}%</span>
                      <div className="progress-bar-bg" style={{ width: 80 }}>
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
                  <td>{d.avg_wait_time} min</td>
                  <td>{d.diverted_ambulances > 0 ? <span style={{ color: '#dc2626', fontWeight: 700 }}>{d.diverted_ambulances} redirected</span> : 'None'}</td>
                  <td>{d.staff_on_duty} staff</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
