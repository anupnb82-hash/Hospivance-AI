import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import DashboardOverview from './pages/DashboardOverview';
import PredictionsPage from './pages/PredictionsPage';
import BedMonitoringPage from './pages/BedMonitoringPage';
import DepartmentOvercrowdingPage from './pages/DepartmentOvercrowdingPage';
import AlertsPage from './pages/AlertsPage';
import RecommendationsPage from './pages/RecommendationsPage';
import AnalyticsPage from './pages/AnalyticsPage';
import SettingsReportsPage from './pages/SettingsReportsPage';

export default function App() {
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [refreshKey, setRefreshKey] = useState(0);

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
  };

  const renderPage = () => {
    switch (currentTab) {
      case 'dashboard':
        return <DashboardOverview key={refreshKey} onNavigate={setCurrentTab} />;
      case 'predictions':
        return <PredictionsPage key={refreshKey} />;
      case 'beds':
        return <BedMonitoringPage key={refreshKey} />;
      case 'departments':
        return <DepartmentOvercrowdingPage key={refreshKey} />;
      case 'alerts':
        return <AlertsPage key={refreshKey} />;
      case 'recommendations':
        return <RecommendationsPage key={refreshKey} />;
      case 'analytics':
        return <AnalyticsPage key={refreshKey} />;
      case 'settings':
        return <SettingsReportsPage key={refreshKey} />;
      default:
        return <DashboardOverview key={refreshKey} onNavigate={setCurrentTab} />;
    }
  };

  return (
    <div className="app-layout">
      <Sidebar currentTab={currentTab} onSelectTab={setCurrentTab} />
      <div className="main-content">
        <Navbar currentTab={currentTab} onRefresh={handleRefresh} />
        <main className="page-container">
          {renderPage()}
        </main>
      </div>
    </div>
  );
}
