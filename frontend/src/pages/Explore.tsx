import React, { useState } from 'react';
import './Explore.css';

interface StatCard {
  title: string;
  value: string;
  trend: string;
  icon: string;
}

const Explore: React.FC = () => {
  const [stats] = useState<StatCard[]>([
    { title: 'Total Devices', value: '0', trend: '+0', icon: '🌐' },
    { title: 'Countries', value: '0', trend: '+0', icon: '🗺️' },
    { title: 'Open Ports', value: '0', trend: '+0', icon: '🔓' },
    { title: 'Vulnerabilities', value: '0', trend: '+0', icon: '⚠️' },
  ]);

  const [topServices] = useState([
    { name: 'HTTP', count: 'Loading...', port: 80 },
    { name: 'HTTPS', count: 'Loading...', port: 443 },
    { name: 'SSH', count: 'Loading...', port: 22 },
    { name: 'FTP', count: 'Loading...', port: 21 },
    { name: 'Telnet', count: 'Loading...', port: 23 },
  ]);

  const [topCountries] = useState([
    { name: 'United States', count: 'Loading...', code: 'US' },
    { name: 'China', count: 'Loading...', code: 'CN' },
    { name: 'Germany', count: 'Loading...', code: 'DE' },
    { name: 'United Kingdom', count: 'Loading...', code: 'UK' },
    { name: 'France', count: 'Loading...', code: 'FR' },
  ]);

  const [recentScans] = useState([
    { ip: '192.168.1.1', timestamp: new Date().toISOString(), ports: 3 },
    { ip: '10.0.0.1', timestamp: new Date().toISOString(), ports: 5 },
    { ip: '172.16.0.1', timestamp: new Date().toISOString(), ports: 2 },
  ]);

  return (
    <div className="explore-page">
      <div className="explore-header">
        <h1>Explore Network Intelligence</h1>
        <p>Real-time statistics and insights from internet-connected devices</p>
      </div>

      <div className="stats-grid">
        {stats.map((stat, index) => (
          <div key={index} className="stat-card">
            <div className="stat-icon">{stat.icon}</div>
            <div className="stat-content">
              <div className="stat-value">{stat.value}</div>
              <div className="stat-title">{stat.title}</div>
              <div className="stat-trend">{stat.trend} this week</div>
            </div>
          </div>
        ))}
      </div>

      <div className="explore-grid">
        <div className="explore-section">
          <h2>Top Services</h2>
          <div className="service-list">
            {topServices.map((service, index) => (
              <div key={index} className="service-item">
                <div className="service-info">
                  <span className="service-name">{service.name}</span>
                  <span className="service-port">:{service.port}</span>
                </div>
                <div className="service-count">{service.count}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="explore-section">
          <h2>Top Countries</h2>
          <div className="country-list">
            {topCountries.map((country, index) => (
              <div key={index} className="country-item">
                <div className="country-info">
                  <span className="country-flag">{country.code}</span>
                  <span className="country-name">{country.name}</span>
                </div>
                <div className="country-count">{country.count}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="explore-section full-width">
          <h2>Recent Scans</h2>
          <div className="recent-scans">
            {recentScans.map((scan, index) => (
              <div key={index} className="scan-item">
                <div className="scan-ip">{scan.ip}</div>
                <div className="scan-info">
                  <span className="scan-ports">{scan.ports} ports</span>
                  <span className="scan-time">
                    {new Date(scan.timestamp).toLocaleString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="popular-searches">
        <h2>Popular Search Queries</h2>
        <div className="search-tags">
          <span className="search-tag">apache</span>
          <span className="search-tag">port:80</span>
          <span className="search-tag">country:US</span>
          <span className="search-tag">nginx</span>
          <span className="search-tag">ssl</span>
          <span className="search-tag">mongodb</span>
          <span className="search-tag">mysql</span>
          <span className="search-tag">redis</span>
        </div>
      </div>
    </div>
  );
};

export default Explore;
