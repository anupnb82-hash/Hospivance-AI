import React from 'react';
import LiveStatusBadge from './LiveStatusBadge';

const TITLES = {
  dashboard: { title: 'Executive Command Center', subtitle: 'Real-time hospital bottleneck prediction and patient throughput monitoring' },
  predictions: { title: 'Patient Admission Forecasting', subtitle: 'Multi-horizon AI predictions for 24-hour, 3-day, and 7-day admission surges' },
  beds: { title: 'Bed Availability & Capacity Monitoring', subtitle: 'Inpatient census, turnover tracking, and discharge acceleration targets' },
  departments: { title: 'Department Overcrowding Analysis', subtitle: '30-day time series, net patient flow velocities, and ambulance diversion tracking' },
  alerts: { title: 'Overcrowding Operational Alerts', subtitle: 'Live capacity alerts, severity categorization, and clinical team acknowledgment' },
  recommendations: { title: 'AI Resource Allocation Recommendations', subtitle: 'Strategic clinical decision support powered by Gemini AI and heuristic rules' },
  analytics: { title: 'Historical Patient Admission Analytics & ML Scorecard', subtitle: '90-day seasonal admissions, day-of-week patterns, and chronological holdout evaluation' },
  settings: { title: 'Settings, Reports & Hackathon Hook', subtitle: 'Export HL7 FHIR encounters, download JSON reports, and configure external APIs' },
};

export default function Navbar({ currentTab, onRefresh }) {
  const meta = TITLES[currentTab] || { title: 'Hospital Operations', subtitle: '' };

  return (
    <header className="topbar">
      <div className="topbar-title">
        <h2>{meta.title}</h2>
        <p>{meta.subtitle}</p>
      </div>

      <div className="topbar-actions">
        <LiveStatusBadge />
        <button
          className="btn btn-outline btn-sm"
          onClick={onRefresh}
          title="Refresh current dashboard view"
        >
          🔄 Refresh
        </button>
      </div>
    </header>
  );
}
