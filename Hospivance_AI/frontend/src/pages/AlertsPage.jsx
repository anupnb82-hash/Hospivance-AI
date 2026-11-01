import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import RiskBadge from '../components/RiskBadge';

export default function AlertsPage() {
  const [alerts, setAlerts] = useState([]);
  const [riskFilter, setRiskFilter] = useState('ALL');
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);
  const [error, setError] = useState(null);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getAlerts(riskFilter);
      setAlerts(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAlerts();
  }, [riskFilter]);

  const handleAck = async (id) => {
    try {
      await api.ackAlert(id);
      loadAlerts();
    } catch (err) {
      alert(`Acknowledgment failed: ${err.message}`);
    }
  };

  const handleSimulateSurge = async () => {
    try {
      setSimulating(true);
      await api.simulateAlert({
        department: 'Emergency Room',
        risk_level: 'HIGH',
        metric_name: 'Occupancy Rate',
        metric_value: 98.4,
        threshold_value: 90.0,
        title: 'Emergency Multi-Casualty / Surge Drill Triggered',
        message: 'Simulated mass-influx drill: 14 ambulances incoming. Deploy surge holding area and activate charge nurse float protocol.',
      });
      loadAlerts();
    } catch (err) {
      alert(`Simulation failed: ${err.message}`);
    } finally {
      setSimulating(false);
    }
  };

  const activeCount = alerts.filter(a => !a.acknowledged).length;

  return (
    <div>
      {/* Top Filter and Actions Bar */}
      <div className="dashboard-card" style={{ padding: '16px 24px', marginBottom: 20 }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontSize: 13, fontWeight: 600, color: '#475569' }}>Filter Risk Level:</span>
            {['ALL', 'HIGH', 'MODERATE', 'LOW'].map(lvl => (
              <button
                key={lvl}
                className={`btn btn-sm ${riskFilter === lvl ? 'btn-primary' : 'btn-outline'}`}
                onClick={() => setRiskFilter(lvl)}
              >
                {lvl}
              </button>
            ))}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <button
              className="btn btn-outline btn-sm"
              style={{ color: '#dc2626', borderColor: '#fca5a5' }}
              onClick={handleSimulateSurge}
              disabled={simulating}
            >
              {simulating ? 'Simulating...' : '🚨 Trigger Surge Drill Alert'}
            </button>
            <button className="btn btn-outline btn-sm" onClick={loadAlerts}>
              Refresh Alerts
            </button>
          </div>
        </div>
      </div>

      {/* KPI Overview */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-label">Active Unresolved Alerts</div>
          <div className="kpi-value" style={{ color: activeCount > 0 ? '#dc2626' : '#059669' }}>
            {activeCount}
          </div>
          <div className="kpi-subtext">Requires clinical coordinator review</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">High-Risk Bottlenecks</div>
          <div className="kpi-value" style={{ color: '#dc2626' }}>
            {alerts.filter(a => a.risk_level === 'HIGH' && !a.acknowledged).length}
          </div>
          <div className="kpi-subtext">Occupancy ≥ 90% or severe wait times</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">Acknowledged Events</div>
          <div className="kpi-value">
            {alerts.filter(a => a.acknowledged).length}
          </div>
          <div className="kpi-subtext">Action protocol already initiated</div>
        </div>
      </div>

      {/* Alerts Stream */}
      <div className="dashboard-card">
        <div className="card-header">
          <div>
            <h3>Operational Alert Stream</h3>
            <p style={{ fontSize: 12, color: '#64748b' }}>Real-time notifications triggered by hospital capacity thresholds</p>
          </div>
        </div>

        {loading ? (
          <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>Loading alerts...</div>
        ) : error ? (
          <div style={{ padding: 20, background: '#fee2e2', color: '#991b1b', borderRadius: 8 }}>{error}</div>
        ) : alerts.length === 0 ? (
          <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>No alerts match the selected criteria.</div>
        ) : (
          <div>
            {alerts.map(a => (
              <div
                key={a.id}
                className={`alert-item ${a.acknowledged ? 'acknowledged' : 'unacknowledged'}`}
              >
                <div className="alert-content" style={{ flexGrow: 1, paddingRight: 20 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
                    <RiskBadge level={a.risk_level} />
                    <span style={{ fontSize: 13, fontWeight: 700, color: '#0f172a' }}>{a.department}</span>
                    <span style={{ fontSize: 12, color: '#64748b' }}>• {a.metric_name}: <strong>{a.metric_value}%</strong> (Threshold: {a.threshold_value}%)</span>
                  </div>
                  <h4>{a.title}</h4>
                  <p>{a.message}</p>
                  <div className="alert-meta">
                    <span>Triggered: {new Date(a.timestamp).toLocaleString()}</span>
                    {a.acknowledged && (
                      <span style={{ color: '#059669', fontWeight: 600 }}>
                        ✓ Acknowledged {a.acknowledged_at ? `at ${new Date(a.acknowledged_at).toLocaleTimeString()}` : ''}
                      </span>
                    )}
                  </div>
                </div>

                <div>
                  {!a.acknowledged ? (
                    <button
                      className="btn btn-primary btn-sm"
                      onClick={() => handleAck(a.id)}
                    >
                      Acknowledge
                    </button>
                  ) : (
                    <span style={{ fontSize: 12, color: '#64748b', fontWeight: 500, padding: '4px 8px', background: '#f1f5f9', borderRadius: 6 }}>
                      Resolved
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
