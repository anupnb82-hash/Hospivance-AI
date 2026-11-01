/**
 * Hospivance AI - REST API Client.
 * Connects frontend dashboard with FastAPI backend endpoints.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

async function request(path, options = {}) {
  const url = `${BASE_URL}${path}`;
  const headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    ...options.headers,
  };

  const response = await fetch(url, { ...options, headers });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API Error ${response.status}: ${errorText || response.statusText}`);
  }
  return response.json();
}

export const api = {
  // Health
  getHealth: () => request('/health'),

  // Dashboard Overview
  getDashboard: () => request('/api/dashboard'),

  // Bed Availability Monitoring
  getBeds: () => request('/api/beds'),

  // Department Series
  getDepartments: (deptId = null, days = 30) => {
    const params = new URLSearchParams();
    if (deptId) params.append('department_id', deptId);
    if (days) params.append('days', days);
    const qs = params.toString();
    return request(`/api/departments${qs ? `?${qs}` : ''}`);
  },

  // Predictions (24h, 3d, 7d)
  getPredictions: (horizonDays = 1, department = null) => {
    return request('/api/predict', {
      method: 'POST',
      body: JSON.stringify({
        horizon_days: parseInt(horizonDays, 10),
        department: department || null,
      }),
    });
  },

  // Alerts
  getAlerts: (riskLevel = null, acknowledged = null) => {
    const params = new URLSearchParams();
    if (riskLevel && riskLevel !== 'ALL') params.append('risk_level', riskLevel);
    if (acknowledged !== null) params.append('acknowledged', acknowledged);
    const qs = params.toString();
    return request(`/api/alerts${qs ? `?${qs}` : ''}`);
  },

  ackAlert: (alertId) => {
    return request(`/api/alerts/${alertId}/ack`, { method: 'POST' });
  },

  simulateAlert: (payload) => {
    return request('/api/alerts/simulate', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  // Analytics & ML Retrain
  getAnalytics: () => request('/api/analytics'),
  retrainModel: () => request('/api/analytics/retrain', { method: 'POST' }),

  // AI Resource Recommendations
  getRecommendations: (horizonDays = 1, department = null) => {
    return request('/api/recommendations', {
      method: 'POST',
      body: JSON.stringify({
        horizon_days: parseInt(horizonDays, 10),
        department: department || null,
      }),
    });
  },

  // Reports Export
  getExportReportUrl: () => `${BASE_URL}/api/reports/export`,

  // Hackathon Organizer Integration Hook
  getOrganizerStatus: () => request('/api/organizer/status'),
  testOrganizer: () => request('/api/organizer/test', { method: 'POST' }),
  syncOrganizer: () => request('/api/organizer/sync', { method: 'POST' }),

  // WebSocket Live URL
  getWsUrl: () => {
    const wsBase = import.meta.env.VITE_WS_BASE_URL;
    if (wsBase) return wsBase;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname || '127.0.0.1';
    return `${protocol}//${host}:8000/ws/live`;
  },
};
