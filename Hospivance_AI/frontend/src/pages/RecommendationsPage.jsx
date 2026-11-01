import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import RiskBadge from '../components/RiskBadge';

export default function RecommendationsPage() {
  const [data, setData] = useState(null);
  const [horizon, setHorizon] = useState(1);
  const [loading, setLoading] = useState(true);
  const [appliedItems, setAppliedItems] = useState({});
  const [error, setError] = useState(null);

  const loadRecommendations = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getRecommendations(horizon);
      setData(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRecommendations();
  }, [horizon]);

  const toggleApply = (id) => {
    setAppliedItems(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const recs = data?.recommendations || [];

  return (
    <div>
      {/* Top Controls */}
      <div className="dashboard-card" style={{ padding: '16px 24px', marginBottom: 20 }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ fontSize: 13, fontWeight: 600, color: '#475569' }}>Optimization Horizon:</span>
            {[
              { label: 'Next 24h Surge', val: 1 },
              { label: '3-Day Operations', val: 3 },
              { label: '7-Day Strategic', val: 7 },
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

          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{
              fontSize: 12,
              padding: '4px 10px',
              backgroundColor: data?.ai_engine === 'gemini-api' ? '#e0f2fe' : '#f1f5f9',
              color: data?.ai_engine === 'gemini-api' ? '#0369a1' : '#334155',
              borderRadius: 6,
              fontWeight: 600,
            }}>
              Engine: {data?.ai_engine === 'gemini-api' ? 'Google Gemini AI' : data?.ai_engine === 'openai-api' ? 'OpenAI GPT' : 'Clinical Heuristics Rule Engine'}
            </span>
            <button className="btn btn-outline btn-sm" onClick={loadRecommendations}>
              Re-generate
            </button>
          </div>
        </div>
      </div>

      {loading ? (
        <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>Generating resource allocation strategies...</div>
      ) : error ? (
        <div style={{ padding: 20, background: '#fee2e2', color: '#991b1b', borderRadius: 8 }}>{error}</div>
      ) : (
        <>
          {/* Executive Briefing Card */}
          <div className="dashboard-card" style={{ background: '#f8fafc', borderLeft: '4px solid #0d9488' }}>
            <div className="card-header" style={{ borderBottom: 'none', paddingBottom: 0, marginBottom: 12 }}>
              <h3>AI Operational Intelligence Briefing</h3>
              <RiskBadge level={data?.forecast_summary?.overall_risk_level} />
            </div>
            <div style={{ fontSize: 14, color: '#334155', whiteSpace: 'pre-line', lineHeight: 1.6 }}>
              {data?.executive_briefing}
            </div>
          </div>

          {/* Actionable Recommendations List */}
          <div className="dashboard-card">
            <div className="card-header">
              <div>
                <h3>Prioritized Resource Allocation Actions ({recs.length})</h3>
                <p style={{ fontSize: 12, color: '#64748b' }}>Actionable interventions to prevent or relieve hospital bottlenecks</p>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {recs.map(rec => {
                const isApplied = appliedItems[rec.id];
                return (
                  <div
                    key={rec.id}
                    style={{
                      border: '1px solid #e2e8f0',
                      borderRadius: 10,
                      padding: 20,
                      backgroundColor: isApplied ? '#f0fdfa' : '#ffffff',
                      borderColor: isApplied ? '#0d9488' : '#e2e8f0',
                      transition: 'all 0.2s ease',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <span style={{
                          fontSize: 11,
                          fontWeight: 700,
                          padding: '3px 8px',
                          borderRadius: 4,
                          backgroundColor: rec.priority === 'HIGH' ? '#fee2e2' : '#fef3c7',
                          color: rec.priority === 'HIGH' ? '#991b1b' : '#92400e',
                        }}>
                          {rec.priority} PRIORITY
                        </span>
                        <span style={{ fontSize: 12, fontWeight: 600, color: '#0d9488' }}>{rec.category}</span>
                        <span style={{ fontSize: 12, color: '#64748b' }}>• {rec.department}</span>
                      </div>
                      <button
                        className={`btn btn-sm ${isApplied ? 'btn-primary' : 'btn-outline'}`}
                        onClick={() => toggleApply(rec.id)}
                      >
                        {isApplied ? '✓ Implemented' : 'Apply Protocol'}
                      </button>
                    </div>

                    <h4 style={{ fontSize: 15, fontWeight: 700, color: '#0f172a', marginBottom: 6 }}>
                      {rec.title}
                    </h4>
                    <p style={{ fontSize: 13.5, color: '#334155', marginBottom: 10 }}>
                      <strong>Action:</strong> {rec.action}
                    </p>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 12, fontSize: 12.5, backgroundColor: '#f8fafc', padding: 12, borderRadius: 6 }}>
                      <div>
                        <strong style={{ color: '#475569' }}>Clinical Rationale:</strong>
                        <p style={{ color: '#64748b', marginTop: 2 }}>{rec.rationale}</p>
                      </div>
                      <div>
                        <strong style={{ color: '#0f766e' }}>Expected Capacity Impact:</strong>
                        <p style={{ color: '#0f766e', marginTop: 2, fontWeight: 500 }}>{rec.expected_impact}</p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
