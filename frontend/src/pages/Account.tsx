import React, { useState } from 'react';
import './Account.css';

const Account: React.FC = () => {
  const [user] = useState({
    username: 'demo_user',
    email: 'demo@assetscan.io',
    apiKey: 'sk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxx',
    plan: 'Free',
    queriesUsed: 47,
    queriesLimit: 100,
    exportsUsed: 3,
    exportsLimit: 10,
    joined: '2025-01-15',
  });

  const [savedSearches] = useState([
    { id: 1, name: 'Apache Servers', query: 'apache port:80', count: 234 },
    { id: 2, name: 'MongoDB Instances', query: 'product:mongodb', count: 89 },
    { id: 3, name: 'Log4j Vulnerable', query: 'vuln:CVE-2021-44228', count: 12 },
  ]);

  const [alerts] = useState([
    { id: 1, name: 'New Apache Vulnerabilities', active: true },
    { id: 2, name: 'Port 80 Changes in US', active: false },
  ]);

  const [recentActivity] = useState([
    { action: 'Search', query: 'nginx port:443', time: '2 hours ago' },
    { action: 'Export', query: 'country:US apache', time: '1 day ago' },
    { action: 'Search', query: 'mongodb', time: '2 days ago' },
  ]);

  const copyApiKey = () => {
    navigator.clipboard.writeText(user.apiKey);
    alert('API Key copied to clipboard!');
  };

  return (
    <div className="account-page">
      <div className="account-header">
        <h1>Account Dashboard</h1>
        <p>Manage your account, API access, and usage statistics</p>
      </div>

      <div className="account-grid">
        <div className="account-section profile-section">
          <h2>Profile Information</h2>
          <div className="profile-info">
            <div className="profile-item">
              <span className="profile-label">Username</span>
              <span className="profile-value">{user.username}</span>
            </div>
            <div className="profile-item">
              <span className="profile-label">Email</span>
              <span className="profile-value">{user.email}</span>
            </div>
            <div className="profile-item">
              <span className="profile-label">Plan</span>
              <span className="profile-badge">{user.plan}</span>
            </div>
            <div className="profile-item">
              <span className="profile-label">Member Since</span>
              <span className="profile-value">{new Date(user.joined).toLocaleDateString()}</span>
            </div>
          </div>
          <button className="btn-edit">Edit Profile</button>
        </div>

        <div className="account-section api-section">
          <h2>API Access</h2>
          <div className="api-key-container">
            <label>API Key</label>
            <div className="api-key-display">
              <code>{user.apiKey}</code>
              <button className="btn-copy" onClick={copyApiKey}>
                Copy
              </button>
            </div>
          </div>
          <div className="api-docs">
            <p>Use this API key to programmatically search and export data.</p>
            <a href="#" className="api-docs-link">View API Documentation →</a>
          </div>
        </div>

        <div className="account-section usage-section">
          <h2>Usage Statistics</h2>
          <div className="usage-metrics">
            <div className="usage-metric">
              <div className="metric-header">
                <span className="metric-label">Search Queries</span>
                <span className="metric-value">{user.queriesUsed} / {user.queriesLimit}</span>
              </div>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${(user.queriesUsed / user.queriesLimit) * 100}%` }}
                ></div>
              </div>
            </div>
            <div className="usage-metric">
              <div className="metric-header">
                <span className="metric-label">Data Exports</span>
                <span className="metric-value">{user.exportsUsed} / {user.exportsLimit}</span>
              </div>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${(user.exportsUsed / user.exportsLimit) * 100}%` }}
                ></div>
              </div>
            </div>
          </div>
          <button className="btn-upgrade">Upgrade Plan</button>
        </div>

        <div className="account-section saved-searches-section">
          <h2>Saved Searches</h2>
          <div className="saved-list">
            {savedSearches.map((search) => (
              <div key={search.id} className="saved-item">
                <div className="saved-info">
                  <span className="saved-name">{search.name}</span>
                  <code className="saved-query">{search.query}</code>
                </div>
                <span className="saved-count">{search.count} results</span>
              </div>
            ))}
          </div>
          <button className="btn-new">+ New Saved Search</button>
        </div>

        <div className="account-section alerts-section">
          <h2>Alerts</h2>
          <div className="alerts-list">
            {alerts.map((alert) => (
              <div key={alert.id} className="alert-item">
                <div className="alert-info">
                  <span className="alert-name">{alert.name}</span>
                  <span className={`alert-status ${alert.active ? 'active' : 'inactive'}`}>
                    {alert.active ? 'Active' : 'Paused'}
                  </span>
                </div>
                <button className="btn-toggle">
                  {alert.active ? 'Pause' : 'Activate'}
                </button>
              </div>
            ))}
          </div>
          <button className="btn-new">+ New Alert</button>
        </div>

        <div className="account-section activity-section">
          <h2>Recent Activity</h2>
          <div className="activity-list">
            {recentActivity.map((activity, index) => (
              <div key={index} className="activity-item">
                <div className="activity-icon">
                  {activity.action === 'Search' ? '🔍' : '📥'}
                </div>
                <div className="activity-info">
                  <span className="activity-action">{activity.action}</span>
                  <code className="activity-query">{activity.query}</code>
                </div>
                <span className="activity-time">{activity.time}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Account;
