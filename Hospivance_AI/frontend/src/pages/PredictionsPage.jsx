import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import RiskBadge from '../components/RiskBadge';
import { TrendLineChart } from '../components/Charts';

const DEPARTMENTS = [
  'All Departments',
  'Emergency Room',
  'Intensive Care Unit (ICU)',
  'General Ward',
  'Pediatrics',
  'Cardiology',
  'Surgery',
];

export default function PredictionsPage() {
  const [horizon, setHorizon] = useState(1);
  const [department, setDepartment] = useState('All Departments');
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchForecast = async () => {
    try {
      setLoading(true);
      setError(null);
      const deptFilter = department === 'All Departments' ? null : department;
      const res = await api.getPredictions(horizon, deptFilter);
      setForecast(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchForecast();
  }, [horizon, department]);

  const summary = forecast?.summary || {};
  const timeline = forecast?.daily_timeline || [];
  const deptForecasts = forecast?.department_forecasts || [];

  return (
    <div>
      {/* Controls Bar */}
      <div className="dashboard-card" style={{ padding: '16px 24px', marginBottom: 20 }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ fontSize: 13, fontWeight: 600, color: '#475569' }}>Forecast Horizon:</span>
            <div style={{ display: 'flex', gap: 6 }}>
              {[
                { label: '24 Hours (Next Day)', val: 1 },
                { label: '3-Day Window', val: 3 },
                { label: '7-Day Outlook', val: 7 },
              ].map(opt => (
                <button
                  key={opt.val}
                  className={`btn btn-sm ${horizon === opt.val ? 'btn-primary' : 'btn-outline'}`}
                  onClick={() => setHorizon(opt.val)}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ fontSize: 13, fontWeight: 600, color: '#475569' }}>Department:</span>
            <select
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
              style={{
                padding: '6px 12px',
                borderRadius: 8,
                border: '1px solid #cbd5e1',
                fontSize: 13,
                fontWeight: 500,
                color: '#0f172a',
                outline: 'none',
              }}
            >
              {DEPARTMENTS.map(d => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
            <button className="btn btn-outline btn-sm" onClick={fetchForecast}>
              Refresh Forecast
            </button>
          </div>
        </div>
      </div>

      {loading ? (
        <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>Calculating AI admission predictions...</div>
      ) : error ? (
        <div style={{ padding: 20, background: '#fee2e2', color: '#991b1b', borderRadius: 8 }}>{error}</div>
      ) : (
        <>
          {/* Summary Cards */}
          <div className="kpi-grid">
            <div className="kpi-card">
              <div className="kpi-label">Total Projected Influx</div>
              <div className="kpi-value">{summary.total_projected_admissions} patients</div>
              <div className="kpi-subtext">Over {forecast.horizon_label}</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-label">Peak Occupancy Projection</div>
              <div className="kpi-value" style={{ color: summary.peak_occupancy_rate >= 90 ? '#ef4444' : '#0f172a' }}>
                {summary.peak_occupancy_rate}%
              </div>
              <div className="kpi-subtext">System risk: <RiskBadge level={summary.overall_risk_level} /></div>
            </div>
            <div className="kpi-card">
              <div className="kpi-label">Bottleneck Departments</div>
              <div className="kpi-value" style={{ fontSize: 20 }}>
                {summary.high_risk_departments?.length || 0} Critical Units
              </div>
              <div className="kpi-subtext">{summary.high_risk_departments?.join(', ') || 'No critical bottlenecks'}</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-label">Model Evaluation Metrics</div>
              <div className="kpi-value" style={{ fontSize: 22 }}>
                R² {summary.model_r2}
              </div>
              <div className="kpi-subtext">Holdout RMSE: ±{summary.model_rmse} patients</div>
            </div>
          </div>

          {/* Timeline Chart */}
          <div className="dashboard-card">
            <div className="card-header">
              <div>
                <h3>Day-by-Day Forecasted Admissions Timeline</h3>
                <p style={{ fontSize: 12, color: '#64748b' }}>Chronological predictions across the {forecast.horizon_label} window</p>
              </div>
            </div>
            <div className="data-table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Forecast Date</th>
                    <th>Horizon</th>
                    <th>Projected Admissions</th>
                    <th>Projected Bed Occupancy</th>
                    <th>Occupancy %</th>
                    <th>Projected Risk</th>
                  </tr>
                </thead>
                <tbody>
                  {timeline.map((t, idx) => (
                    <tr key={idx}>
                      <td style={{ fontWeight: 600 }}>{t.date}</td>
                      <td>{t.day_label}</td>
                      <td style={{ fontWeight: 700, color: '#0d9488' }}>{t.total_predicted_admissions} patients</td>
                      <td>{t.projected_occupied_beds} / {t.total_capacity} beds</td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <span style={{ fontWeight: 700 }}>{t.projected_occupancy_rate}%</span>
                          <div className="progress-bar-bg" style={{ width: 80 }}>
                            <div
                              className="progress-bar-fill"
                              style={{
                                width: `${Math.min(100, t.projected_occupancy_rate)}%`,
                                backgroundColor: t.overall_risk === 'HIGH' ? '#ef4444' : t.overall_risk === 'MODERATE' ? '#f59e0b' : '#10b981'
                              }}
                            />
                          </div>
                        </div>
                      </td>
                      <td><RiskBadge level={t.overall_risk} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Department Forecast Details */}
          <div className="dashboard-card">
            <div className="card-header">
              <div>
                <h3>Department-Specific Predictions & Confidence Intervals</h3>
                <p style={{ fontSize: 12, color: '#64748b' }}>Includes 95% confidence bounds (±1.96 × holdout RMSE)</p>
              </div>
            </div>
            <div className="data-table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Department</th>
                    <th>Predicted Admissions</th>
                    <th>95% Confidence Interval</th>
                    <th>Projected Occupancy</th>
                    <th>Expected Discharges</th>
                    <th>Available Beds</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {deptForecasts.map((df, i) => (
                    <tr key={i}>
                      <td>{df.date}</td>
                      <td style={{ fontWeight: 600 }}>{df.department}</td>
                      <td style={{ fontWeight: 700, color: '#0d9488' }}>{df.predicted_admissions}</td>
                      <td style={{ fontSize: 12, color: '#64748b' }}>[{df.ci_lower} – {df.ci_upper}]</td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <span style={{ fontWeight: 700 }}>{df.projected_occupancy_rate}%</span>
                          <span style={{ fontSize: 11, color: '#64748b' }}>({df.projected_occupied_beds}/{df.total_beds})</span>
                        </div>
                      </td>
                      <td>{df.expected_discharges} patients</td>
                      <td style={{ fontWeight: 600, color: df.available_beds <= 2 ? '#dc2626' : '#059669' }}>
                        {df.available_beds} beds
                      </td>
                      <td>
                        {df.bottleneck_warning ? (
                          <span style={{ color: '#dc2626', fontWeight: 700, fontSize: 11.5, textTransform: 'uppercase' }}>
                            ⚠️ Bottleneck Critical
                          </span>
                        ) : (
                          <RiskBadge level={df.risk_level} />
                        )}
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
