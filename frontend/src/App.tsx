
import React, { useState, useEffect } from 'react';
import './App.css';
import SearchBar from './components/SearchBar';
import ResultsList from './components/ResultsList';
import DeviceDetail from './components/DeviceDetail';

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

const App: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState<Device[]>([]);
  const [selectedDevice, setSelectedDevice] = useState<Device | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [authToken] = useState<string | null>(localStorage.getItem('authToken'));
  // Placeholder for authentication
  useEffect(() => {
    if (!authToken) {
      // Redirect to login or show login modal
      console.log('No auth token found. User should log in.');
    }
  }, [authToken]);

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    setLoading(true);
    setError(null);
    setSelectedDevice(null);

    try {
      const response = await fetch('http://localhost:8000/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken || 'dummy_user_token'}`, // Placeholder token
        },
        body: JSON.stringify({
          query: query,
          page: 1,
          size: 10,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data: Device[] = await response.json();
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectDevice = async (deviceId: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://localhost:8000/device/${deviceId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${authToken || 'dummy_user_token'}`, // Placeholder token
        },
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data: Device = await response.json();
      setSelectedDevice(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Internet Asset Intelligence Platform</h1>
        <p>Search and analyze internet-facing assets</p>
      </header>

      <main className="app-main">
        <SearchBar onSearch={handleSearch} />

        {error && <div className="error-message">{error}</div>}
        {loading && <div className="loading-message">Loading...</div>}

        <div className="results-container">
          {selectedDevice ? (
            <DeviceDetail device={selectedDevice} onBack={() => setSelectedDevice(null)} />
          ) : (
            <>
              {results.length > 0 && (
                <ResultsList results={results} onSelectDevice={handleSelectDevice} />
              )}
              {results.length === 0 && !loading && searchQuery && (
                <div className="no-results">No results found for "{searchQuery}"</div>
              )}
            </>
          )}
        </div>
      </main>

      <footer className="app-footer">
        <p>&copy; 2025 Internet Asset Intelligence Platform. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default App;

