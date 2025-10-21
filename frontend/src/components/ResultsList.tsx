
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
      <h2>Search Results ({results.length})</h2>
      <div className="results-table-container">
        <table className="results-table">
          <thead>
            <tr>
              <th>IP Address</th>
              <th>Port</th>
              <th>Protocol</th>
              <th>Risk Score</th>
              <th>Timestamp</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {results.map((device) => (
              <tr key={device.id}>
                <td className="ip-cell">{device.ip}</td>
                <td>{device.port}</td>
                <td>{device.protocol}</td>
                <td>
                  <div
                    className="risk-score"
                    style={{
                      backgroundColor: getRiskColor(device.risk_score),
                      color: 'white',
                      padding: '4px 8px',
                      borderRadius: '4px',
                      textAlign: 'center',
                    }}
                  >
                    {device.risk_score}
                  </div>
                </td>
                <td className="timestamp">{new Date(device.timestamp).toLocaleString()}</td>
                <td>
                  <button
                    className="detail-button"
                    onClick={() => onSelectDevice(device.id)}
                  >
                    View Details
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ResultsList;

