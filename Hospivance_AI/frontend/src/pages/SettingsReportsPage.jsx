import React, { useState, useEffect } from 'react';
import { api } from '../api/client';

export default function SettingsReportsPage() {
  const [organizerStatus, setOrganizerStatus] = useState(null);
  const [testResult, setTestResult] = useState(null);
  const [syncResult, setSyncResult] = useState(null);
  const [testing, setTesting] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [health, setHealth] = useState(null);

  useEffect(() => {
    api.getOrganizerStatus().then(setOrganizerStatus).catch(console.error);
    api.getHealth().then(setHealth).catch(console.error);
  }, []);

  const handleTestOrganizer = async () => {
    try {
      setTesting(true);
      setTestResult(null);
      const res = await api.testOrganizer();
      setTestResult(res);
    } catch (err) {
      setTestResult({ success: false, message: err.message });
    } finally {
      setTesting(false);
    }
  };

  const handleSyncOrganizer = async () => {
    try {
      setSyncing(true);
      setSyncResult(null);
      const res = await api.syncOrganizer();
      setSyncResult(res);
    } catch (err) {
      setSyncResult({ success: false, message: err.message });
    } finally {
      setSyncing(false);
    }
  };

  return (
    <div>
      {/* Synthetic Data Notice Banner */}
      <div className="dashboard-card" style={{ borderLeft: '4px solid #0d9488', backgroundColor: '#f0fdfa' }}>
        <h3 style={{ color: '#0f766e', marginBottom: 6 }}>Synthetic Demonstration Dataset Notice</h3>
        <p style={{ fontSize: 13.5, color: '#134e4a', lineHeight: 1.6 }}>
          Hospivance AI uses <strong>100% synthetic, non-PHI department-day time series data</strong> for demonstration and capacity planning modeling.
          No real patient names, Medical Record Numbers (MRNs), or protected health information (PHI) are accessed or stored.
          Forecasts represent operational planning indicators and do not constitute clinical diagnostic decisions.
        </p>
      </div>

      {/* Reports and FHIR Export Section */}
      <div className="dashboard-card">
        <div className="card-header">
          <div>
            <h3>Reports & HL7 FHIR Interoperability</h3>
            <p style={{ fontSize: 12, color: '#64748b' }}>Download comprehensive operational census reports or query FHIR endpoints</p>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
          <div style={{ border: '1px solid #e2e8f0', borderRadius: 8, padding: 16 }}>
            <h4 style={{ fontSize: 14, fontWeight: 700, marginBottom: 4 }}>Full Hospital Operations Report</h4>
            <p style={{ fontSize: 12.5, color: '#64748b', marginBottom: 14 }}>
              Exports current capacity, bed census, 24h forecast, and active recommendations as a downloadable JSON document.
            </p>
            <a
              href={api.getExportReportUrl()}
              className="btn btn-primary btn-sm"
              target="_blank"
              rel="noreferrer"
            >
              📥 Download Operations Report (JSON)
            </a>
          </div>

          <div style={{ border: '1px solid #e2e8f0', borderRadius: 8, padding: 16 }}>
            <h4 style={{ fontSize: 14, fontWeight: 700, marginBottom: 4 }}>HL7 FHIR R4 Encounter Bundle</h4>
            <p style={{ fontSize: 12.5, color: '#64748b', marginBottom: 14 }}>
              Compliant FHIR R4 Bundle containing synthetic patient encounter resources for EHR/interoperability testing.
            </p>
            <a
              href="/api/fhir/Bundle/encounters"
              className="btn btn-outline btn-sm"
              target="_blank"
              rel="noreferrer"
            >
              🔗 View FHIR Encounters Bundle
            </a>
          </div>

          <div style={{ border: '1px solid #e2e8f0', borderRadius: 8, padding: 16 }}>
            <h4 style={{ fontSize: 14, fontWeight: 700, marginBottom: 4 }}>FHIR Capability Statement</h4>
            <p style={{ fontSize: 12.5, color: '#64748b', marginBottom: 14 }}>
              Conformance metadata describing supported FHIR interactions and resource definitions.
            </p>
            <a
              href="/api/fhir/metadata"
              className="btn btn-outline btn-sm"
              target="_blank"
              rel="noreferrer"
            >
              📋 View FHIR Metadata
            </a>
          </div>
        </div>
      </div>

      {/* Hackathon Organizer Integration Hook */}
      <div className="dashboard-card">
        <div className="card-header">
          <div>
            <h3>Hackathon Organizer Integration Hook</h3>
            <p style={{ fontSize: 12, color: '#64748b' }}>Configure external organizer hospital REST APIs in backend/.env</p>
          </div>
          <span style={{
            fontSize: 12,
            fontWeight: 700,
            padding: '4px 8px',
            borderRadius: 6,
            backgroundColor: organizerStatus?.configured ? '#d1fae5' : '#f1f5f9',
            color: organizerStatus?.configured ? '#065f46' : '#64748b',
          }}>
            {organizerStatus?.configured ? 'ORGANIZER CONNECTED' : 'LOCAL SYNTHETIC MODE'}
          </span>
        </div>

        <div style={{ backgroundColor: '#f8fafc', padding: 16, borderRadius: 8, marginBottom: 16, fontSize: 13 }}>
          <div style={{ marginBottom: 6 }}>
            <strong>Organizer Base URL:</strong> <code style={{ color: '#0d9488' }}>{organizerStatus?.base_url}</code>
          </div>
          <div style={{ marginBottom: 6 }}>
            <strong>Auth Header:</strong> <code>{organizerStatus?.auth_header} ({organizerStatus?.auth_scheme})</code>
          </div>
          <div>
            <strong>Endpoints:</strong> Admissions (<code>{organizerStatus?.paths?.admissions}</code>), Beds (<code>{organizerStatus?.paths?.beds}</code>), Departments (<code>{organizerStatus?.paths?.departments}</code>)
          </div>
        </div>

        <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
          <button
            className="btn btn-outline btn-sm"
            onClick={handleTestOrganizer}
            disabled={testing}
          >
            {testing ? 'Pinging endpoint...' : '🔍 Test Connection'}
          </button>
          <button
            className="btn btn-primary btn-sm"
            onClick={handleSyncOrganizer}
            disabled={syncing}
          >
            {syncing ? 'Syncing...' : '🔄 Sync Feeds'}
          </button>
        </div>

        {testResult && (
          <div style={{
            padding: 12,
            borderRadius: 6,
            fontSize: 13,
            backgroundColor: testResult.success ? '#d1fae5' : '#fee2e2',
            color: testResult.success ? '#065f46' : '#991b1b',
            marginBottom: 12
          }}>
            <strong>Ping Result:</strong> {testResult.message}
          </div>
        )}

        {syncResult && (
          <div style={{
            padding: 12,
            borderRadius: 6,
            fontSize: 13,
            backgroundColor: syncResult.success ? '#d1fae5' : '#fee2e2',
            color: syncResult.success ? '#065f46' : '#991b1b'
          }}>
            <strong>Sync Result:</strong> {syncResult.message}
          </div>
        )}
      </div>

      {/* System Health Diagnostics */}
      {health && (
        <div className="dashboard-card">
          <div className="card-header">
            <h3>System Health & Engine Diagnostics</h3>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 14, fontSize: 13 }}>
            <div><strong>Status:</strong> <span style={{ color: '#059669', fontWeight: 700 }}>{health.status.toUpperCase()}</span></div>
            <div><strong>Database Engine:</strong> {health.database?.type.toUpperCase()}</div>
            <div><strong>ML Pipeline Ready:</strong> {health.ml_pipeline?.model_ready ? 'Yes' : 'No'}</div>
            <div><strong>Recommendation Engine:</strong> {health.ai_recommendations?.fallback}</div>
          </div>
        </div>
      )}
    </div>
  );
}
