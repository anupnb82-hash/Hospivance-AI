import React, { useState, useEffect } from 'react';
import { api } from '../api/client';

export default function AnalyticsPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [retraining, setRetraining] = useState(false);
  const [error, setError] = useState(null);
  const [retrainMsg, setRetrainMsg] = useState(null);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getAnalytics();
      setData(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAnalytics();
  }, []);

  const handleRetrain = async () => {
    try {
      setRetraining(true);
      setRetrainMsg(null);
      const res = await api.retrainModel();
      setRetrainMsg('ML Pipeline re-trained and re-evaluated on chronological split.');
      loadAnalytics();
    } catch (err) {
      alert(`Retraining failed: ${err.message}`);
    } finally {
      setRetraining(false);
    }
  };

  if (loading) {
    return <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>Loading historical analytics and ML scorecard...</div>;
  }

  if (error) {
    return <div style={{ padding: 20, background: '#fee2e2', color: '#991b1b', borderRadius: 8 }}>{error}</div>;
  }

  const scorecard = data?.ml_model_scorecard || {};
  const dow = data?.dow_breakdown || [];
  const deptDist = data?.department_distribution || [];
  const featImportances = scorecard?.feature_importances || {};

  return (
    <div>
      {retrainMsg && (
        <div style={{ padding: '12px 20px', background: '#d1fae5', color: '#065f46', borderRadius: 8, marginBottom: 20, fontWeight: 600 }}>
          ✓ {retrainMsg}
        </div>
      )}

      {/* ML Evaluation Scorecard */}
      <div className="dashboard-card" style={{ borderTop: '4px solid #0d9488' }}>
        <div className="card-header">
          <div>
            <h3>Machine Learning Model Evaluation Scorecard</h3>
            <p style={{ fontSize: 12, color: '#64748b' }}>
              Rigorous chronological train/test split • Evaluated on holdout data without lookahead leakage
            </p>
          </div>
          <button
            className="btn btn-primary btn-sm"
            onClick={handleRetrain}
            disabled={retraining}
          >
            {retraining ? 'Re-training Pipeline...' : '🔄 Retrain Model'}
          </button>
        </div>

        <div className="kpi-grid" style={{ marginBottom: 20 }}>
          <div className="kpi-card" style={{ background: '#f8fafc' }}>
            <div className="kpi-label">R² Fit Score</div>
            <div className="kpi-value" style={{ color: '#0d9488' }}>{scorecard.r2_score}</div>
            <div className="kpi-subtext">Variance explained on test set</div>
          </div>
          <div className="kpi-card" style={{ background: '#f8fafc' }}>
            <div className="kpi-label">Mean Absolute Error (MAE)</div>
            <div className="kpi-value">{scorecard.mae}</div>
            <div className="kpi-subtext">Avg prediction error in patients</div>
          </div>
          <div className="kpi-card" style={{ background: '#f8fafc' }}>
            <div className="kpi-label">Root Mean Squared Error (RMSE)</div>
            <div className="kpi-value">±{scorecard.rmse}</div>
            <div className="kpi-subtext">Standard deviation of residuals</div>
          </div>
          <div className="kpi-card" style={{ background: '#f8fafc' }}>
            <div className="kpi-label">Mean Absolute % Error (MAPE)</div>
            <div className="kpi-value">{scorecard.mape}%</div>
            <div className="kpi-subtext">Relative percentage error</div>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16, fontSize: 13, backgroundColor: '#f1f5f9', padding: 16, borderRadius: 8 }}>
          <div><strong>Algorithm:</strong> {scorecard.algorithm || 'RandomForestRegressor'}</div>
          <div><strong>Data Splitting:</strong> {scorecard.data_split || 'Strict Chronological Split'}</div>
          <div><strong>Training Samples:</strong> {scorecard.train_samples} days</div>
          <div><strong>Test Holdout:</strong> {scorecard.test_samples} days (from {scorecard.split_date})</div>
        </div>
      </div>

      {/* Feature Importances */}
      {Object.keys(featImportances).length > 0 && (
        <div className="dashboard-card">
          <div className="card-header">
            <div>
              <h3>Predictive Feature Importance Ranking</h3>
              <p style={{ fontSize: 12, color: '#64748b' }}>Top variables driving admission volume predictions</p>
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {Object.entries(featImportances).map(([feat, imp], i) => (
              <div key={i}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12.5, marginBottom: 4 }}>
                  <span style={{ fontWeight: 600, color: '#0f172a' }}>{feat}</span>
                  <span style={{ color: '#0f766e', fontWeight: 700 }}>{(imp * 100).toFixed(2)}%</span>
                </div>
                <div className="progress-bar-bg" style={{ height: 6 }}>
                  <div className="progress-bar-fill" style={{ width: `${Math.min(100, imp * 300)}%`, backgroundColor: '#0d9488' }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Day of Week Seasonality Breakdown */}
      <div className="dashboard-card">
        <div className="card-header">
          <div>
            <h3>Day-of-Week Influx & Capacity Patterns</h3>
            <p style={{ fontSize: 12, color: '#64748b' }}>Aggregated over 90-day operational window</p>
          </div>
        </div>

        <div className="data-table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Day of Week</th>
                <th>Avg Admissions / Day</th>
                <th>Avg Hospital Occupancy %</th>
                <th>Peak Flow Intensity</th>
              </tr>
            </thead>
            <tbody>
              {dow.map((d, i) => (
                <tr key={i}>
                  <td style={{ fontWeight: 600 }}>{d.day_name}</td>
                  <td style={{ fontWeight: 700, color: '#0d9488' }}>{d.avg_admissions} patients</td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{ fontWeight: 600 }}>{d.avg_occupancy_rate}%</span>
                      <div className="progress-bar-bg" style={{ width: 60 }}>
                        <div
                          className="progress-bar-fill"
                          style={{
                            width: `${d.avg_occupancy_rate}%`,
                            backgroundColor: d.avg_occupancy_rate >= 90 ? '#ef4444' : d.avg_occupancy_rate >= 75 ? '#f59e0b' : '#10b981'
                          }}
                        />
                      </div>
                    </div>
                  </td>
                  <td>
                    {d.day_name === 'Saturday' || d.day_name === 'Sunday' ? (
                      <span style={{ color: '#d97706', fontWeight: 600 }}>Weekend Influx Spikes (ER heavy)</span>
                    ) : (
                      <span style={{ color: '#0f766e' }}>Elective & Scheduled Volume</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
