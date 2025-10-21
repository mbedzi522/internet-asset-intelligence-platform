import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import SearchBar from '../components/SearchBar';
import ResultsList from '../components/ResultsList';
import DeviceDetail from '../components/DeviceDetail';
import './Search.css';

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

const Search: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState<Device[]>([]);
  const [selectedDevice, setSelectedDevice] = useState<Device | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [authToken] = useState<string | null>(localStorage.getItem('authToken'));

  useEffect(() => {
    const q = searchParams.get('q');
    if (q) {
      setSearchQuery(q);
      handleSearch(q);
    }
  }, [searchParams]);

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    setLoading(true);
    setError(null);
    setSelectedDevice(null);

    try {
      const response = await fetch('http://localhost:8001/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken || 'dummy_user_token'}`,
        },
        body: JSON.stringify({
          query: query,
          page: 1,
          size: 20,
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
      const response = await fetch(`http://localhost:8001/device/${deviceId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${authToken || 'dummy_user_token'}`,
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
    <div className="search-page">
      <div className="search-section">
        <SearchBar onSearch={handleSearch} />
        {results.length > 0 && !selectedDevice && (
          <div className="results-meta">
            <span className="results-count">{results.length} results found</span>
            <span className="search-query">for "{searchQuery}"</span>
          </div>
        )}
      </div>

      {error && <div className="error-message">⚠️ {error}</div>}
      {loading && (
        <div className="loading-message">
          <div className="loading-spinner"></div>
          <span>Searching assets...</span>
        </div>
      )}

      <div className="results-container">
        {selectedDevice ? (
          <DeviceDetail device={selectedDevice} onBack={() => setSelectedDevice(null)} />
        ) : (
          <>
            {results.length > 0 && (
              <ResultsList results={results} onSelectDevice={handleSelectDevice} />
            )}
            {results.length === 0 && !loading && searchQuery && (
              <div className="no-results">
                <div className="no-results-icon">🔍</div>
                <h3>No results found</h3>
                <p>Try adjusting your search query or filters</p>
              </div>
            )}
            {results.length === 0 && !loading && !searchQuery && (
              <div className="welcome-message">
                <h2>Search for Internet-Connected Assets</h2>
                <p>Enter an IP address, CIDR range, service name, or vulnerability to begin</p>
                <div className="example-searches">
                  <span className="example-label">Examples:</span>
                  <code onClick={() => handleSearch('192.168.1.1')}>192.168.1.1</code>
                  <code onClick={() => handleSearch('apache')}>apache</code>
                  <code onClick={() => handleSearch('port:80')}>port:80</code>
                  <code onClick={() => handleSearch('country:US')}>country:US</code>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default Search;
