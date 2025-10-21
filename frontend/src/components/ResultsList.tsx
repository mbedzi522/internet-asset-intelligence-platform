
import React from 'react';
import './ResultsList.css';

interface Device {
  id: string;
  timestamp: string;
  ip: string;
  port: number;
  protocol: string;
  risk_score: number;
}

interface ResultsListProps {
  results: Device[];
  onSelectDevice: (deviceId: string) => void;
}

const getRiskColor = (score: number): string => {
  if (score >= 80) return '#dc3545'; // Red for critical
  if (score >= 60) return '#fd7e14'; // Orange for high
  if (score >= 40) return '#ffc107'; // Yellow for medium
  return '#28a745'; // Green for low
};

const ResultsList: React.FC<ResultsListProps> = ({ results, onSelectDevice }) => {
  return (
    <div className="results-list">
      <div className="results-grid">
        {results.map((device) => (
          <div
            key={device.id}
            className="result-card"
            onClick={() => onSelectDevice(device.id)}
          >
            <div className="card-header">
              <div className="ip-address">{device.ip}</div>
              <div
                className="risk-badge"
                style={{ backgroundColor: getRiskColor(device.risk_score) }}
              >
                Risk: {device.risk_score}
              </div>
            </div>

            <div className="card-body">
              <div className="info-row">
                <span className="label">Port:</span>
                <span className="value">{device.port}</span>
              </div>
              <div className="info-row">
                <span className="label">Protocol:</span>
                <span className="value protocol">{device.protocol}</span>
              </div>
              <div className="info-row">
                <span className="label">Last Seen:</span>
                <span className="value timestamp">
                  {new Date(device.timestamp).toLocaleString()}
                </span>
              </div>
            </div>

            <div className="card-footer">
              <button className="details-link">
                View Details →
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ResultsList;

