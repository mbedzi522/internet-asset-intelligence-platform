
import React from 'react';
import './DeviceDetail.css';

interface Device {
  id: string;
  timestamp: string;
  ip: string;
  port: number;
  protocol: string;
  probes: Record<string, any>;
  enrichment: Record<string, any>;
  risk_score: number;
  risk_breakdown: Record<string, number>;
}

interface DeviceDetailProps {
  device: Device;
  onBack: () => void;
}

const DeviceDetail: React.FC<DeviceDetailProps> = ({ device, onBack }) => {
  return (
    <div className="device-detail">
      <button className="back-button" onClick={onBack}>
        ← Back to Results
      </button>

      <div className="detail-header">
        <h2>{device.ip}:{device.port}</h2>
        <div className="risk-badge" style={{ backgroundColor: getRiskColor(device.risk_score) }}>
          Risk Score: {device.risk_score}
        </div>
      </div>

      <div className="detail-grid">
        <section className="detail-section">
          <h3>Basic Information</h3>
          <div className="info-row">
            <span className="label">IP Address:</span>
            <span className="value">{device.ip}</span>
          </div>
          <div className="info-row">
            <span className="label">Port:</span>
            <span className="value">{device.port}</span>
          </div>
          <div className="info-row">
            <span className="label">Protocol:</span>
            <span className="value">{device.protocol}</span>
          </div>
          <div className="info-row">
            <span className="label">Timestamp:</span>
            <span className="value">{new Date(device.timestamp).toLocaleString()}</span>
          </div>
        </section>

        <section className="detail-section">
          <h3>Risk Breakdown</h3>
          {Object.entries(device.risk_breakdown).map(([component, score]) => (
            <div key={component} className="risk-component">
              <span className="component-name">{component}:</span>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${Math.min(score, 100)}%` }}
                ></div>
              </div>
              <span className="component-score">{score}</span>
            </div>
          ))}
        </section>

        <section className="detail-section">
          <h3>Probe Results</h3>
          <div className="probes-container">
            {Object.entries(device.probes).map(([probeName, probeData]) => (
              <div key={probeName} className="probe-result">
                <h4>{probeName}</h4>
                <pre>{JSON.stringify(probeData, null, 2)}</pre>
              </div>
            ))}
          </div>
        </section>

        {device.enrichment && Object.keys(device.enrichment).length > 0 && (
          <section className="detail-section">
            <h3>Enrichment Data</h3>
            <div className="enrichment-container">
              {device.enrichment.geoip && (
                <div className="enrichment-item">
                  <h4>GeoIP Information</h4>
                  <p><strong>Country:</strong> {device.enrichment.geoip.country_name}</p>
                  <p><strong>City:</strong> {device.enrichment.geoip.city_name}</p>
                </div>
              )}

              {device.enrichment.tls_cert && (
                <div className="enrichment-item">
                  <h4>TLS Certificate</h4>
                  <p><strong>Subject CN:</strong> {device.enrichment.tls_cert.subject_cn}</p>
                  <p><strong>Issuer CN:</strong> {device.enrichment.tls_cert.issuer_cn}</p>
                  <p><strong>Valid From:</strong> {device.enrichment.tls_cert.valid_from}</p>
                  <p><strong>Valid To:</strong> {device.enrichment.tls_cert.valid_to}</p>
                  <p><strong>Self-Signed:</strong> {device.enrichment.tls_cert.self_signed ? 'Yes' : 'No'}</p>
                </div>
              )}

              {device.enrichment.cve_matches && device.enrichment.cve_matches.length > 0 && (
                <div className="enrichment-item">
                  <h4>CVE Matches</h4>
                  <ul>
                    {device.enrichment.cve_matches.map((cve: any, idx: number) => (
                      <li key={idx}>
                        <strong>{cve.cve_id}</strong> ({cve.severity}) - {cve.description}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </section>
        )}
      </div>
    </div>
  );
};

const getRiskColor = (score: number): string => {
  if (score >= 80) return '#dc3545';
  if (score >= 60) return '#fd7e14';
  if (score >= 40) return '#ffc107';
  return '#28a745';
};

export default DeviceDetail;

