import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Filters.css';

const Filters: React.FC = () => {
  const navigate = useNavigate();
  const [filters, setFilters] = useState({
    ip: '',
    port: '',
    country: '',
    city: '',
    org: '',
    hostname: '',
    product: '',
    version: '',
    os: '',
    asn: '',
    netblock: '',
    ssl_version: '',
    has_screenshot: false,
    vuln: '',
  });

  const handleInputChange = (field: string, value: string | boolean) => {
    setFilters({ ...filters, [field]: value });
  };

  const buildQuery = () => {
    const parts: string[] = [];

    if (filters.ip) parts.push(`ip:${filters.ip}`);
    if (filters.port) parts.push(`port:${filters.port}`);
    if (filters.country) parts.push(`country:${filters.country}`);
    if (filters.city) parts.push(`city:${filters.city}`);
    if (filters.org) parts.push(`org:"${filters.org}"`);
    if (filters.hostname) parts.push(`hostname:${filters.hostname}`);
    if (filters.product) parts.push(`product:${filters.product}`);
    if (filters.version) parts.push(`version:${filters.version}`);
    if (filters.os) parts.push(`os:${filters.os}`);
    if (filters.asn) parts.push(`asn:${filters.asn}`);
    if (filters.netblock) parts.push(`net:${filters.netblock}`);
    if (filters.ssl_version) parts.push(`ssl.version:${filters.ssl_version}`);
    if (filters.has_screenshot) parts.push('has_screenshot:true');
    if (filters.vuln) parts.push(`vuln:${filters.vuln}`);

    return parts.join(' ');
  };

  const handleSearch = () => {
    const query = buildQuery();
    if (query) {
      navigate(`/?q=${encodeURIComponent(query)}`);
    }
  };

  const clearFilters = () => {
    setFilters({
      ip: '',
      port: '',
      country: '',
      city: '',
      org: '',
      hostname: '',
      product: '',
      version: '',
      os: '',
      asn: '',
      netblock: '',
      ssl_version: '',
      has_screenshot: false,
      vuln: '',
    });
  };

  return (
    <div className="filters-page">
      <div className="filters-header">
        <h1>Advanced Search Filters</h1>
        <p>Build complex queries to find exactly what you're looking for</p>
      </div>

      <div className="filters-container">
        <div className="filter-section">
          <h2>Network</h2>
          <div className="filter-grid">
            <div className="filter-item">
              <label>IP Address</label>
              <input
                type="text"
                placeholder="192.168.1.1"
                value={filters.ip}
                onChange={(e) => handleInputChange('ip', e.target.value)}
              />
            </div>
            <div className="filter-item">
              <label>Port</label>
              <input
                type="text"
                placeholder="80, 443, 22"
                value={filters.port}
                onChange={(e) => handleInputChange('port', e.target.value)}
              />
            </div>
            <div className="filter-item">
              <label>Hostname</label>
              <input
                type="text"
                placeholder="example.com"
                value={filters.hostname}
                onChange={(e) => handleInputChange('hostname', e.target.value)}
              />
            </div>
            <div className="filter-item">
              <label>Net Block (CIDR)</label>
              <input
                type="text"
                placeholder="192.168.0.0/24"
                value={filters.netblock}
                onChange={(e) => handleInputChange('netblock', e.target.value)}
              />
            </div>
          </div>
        </div>

        <div className="filter-section">
          <h2>Location</h2>
          <div className="filter-grid">
            <div className="filter-item">
              <label>Country Code</label>
              <input
                type="text"
                placeholder="US, CN, DE"
                value={filters.country}
                onChange={(e) => handleInputChange('country', e.target.value)}
              />
            </div>
            <div className="filter-item">
              <label>City</label>
              <input
                type="text"
                placeholder="New York"
                value={filters.city}
                onChange={(e) => handleInputChange('city', e.target.value)}
              />
            </div>
            <div className="filter-item">
              <label>Organization</label>
              <input
                type="text"
                placeholder="Google LLC"
                value={filters.org}
                onChange={(e) => handleInputChange('org', e.target.value)}
              />
            </div>
            <div className="filter-item">
              <label>ASN</label>
              <input
                type="text"
                placeholder="AS15169"
                value={filters.asn}
                onChange={(e) => handleInputChange('asn', e.target.value)}
              />
            </div>
          </div>
        </div>

        <div className="filter-section">
          <h2>Technology</h2>
          <div className="filter-grid">
            <div className="filter-item">
              <label>Product/Service</label>
              <input
                type="text"
                placeholder="apache, nginx, iis"
                value={filters.product}
                onChange={(e) => handleInputChange('product', e.target.value)}
              />
            </div>
            <div className="filter-item">
              <label>Version</label>
              <input
                type="text"
                placeholder="2.4.41"
                value={filters.version}
                onChange={(e) => handleInputChange('version', e.target.value)}
              />
            </div>
            <div className="filter-item">
              <label>Operating System</label>
              <input
                type="text"
                placeholder="linux, windows"
                value={filters.os}
                onChange={(e) => handleInputChange('os', e.target.value)}
              />
            </div>
            <div className="filter-item">
              <label>SSL Version</label>
              <input
                type="text"
                placeholder="TLSv1.2, TLSv1.3"
                value={filters.ssl_version}
                onChange={(e) => handleInputChange('ssl_version', e.target.value)}
              />
            </div>
          </div>
        </div>

        <div className="filter-section">
          <h2>Security</h2>
          <div className="filter-grid">
            <div className="filter-item">
              <label>Vulnerability (CVE)</label>
              <input
                type="text"
                placeholder="CVE-2021-44228"
                value={filters.vuln}
                onChange={(e) => handleInputChange('vuln', e.target.value)}
              />
            </div>
            <div className="filter-item">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={filters.has_screenshot}
                  onChange={(e) => handleInputChange('has_screenshot', e.target.checked)}
                />
                Has Screenshot
              </label>
            </div>
          </div>
        </div>

        <div className="query-preview">
          <h3>Generated Query</h3>
          <div className="query-display">
            <code>{buildQuery() || 'No filters selected'}</code>
          </div>
        </div>

        <div className="filter-actions">
          <button className="btn-clear" onClick={clearFilters}>
            Clear All
          </button>
          <button className="btn-search" onClick={handleSearch}>
            Search
          </button>
        </div>
      </div>

      <div className="filter-examples">
        <h2>Example Queries</h2>
        <div className="example-list">
          <div className="example-item" onClick={() => navigate('/?q=apache+port:80')}>
            <code>apache port:80</code>
            <span>Apache servers on port 80</span>
          </div>
          <div className="example-item" onClick={() => navigate('/?q=country:US+has_screenshot:true')}>
            <code>country:US has_screenshot:true</code>
            <span>Devices in US with screenshots</span>
          </div>
          <div className="example-item" onClick={() => navigate('/?q=product:mongodb+port:27017')}>
            <code>product:mongodb port:27017</code>
            <span>MongoDB databases</span>
          </div>
          <div className="example-item" onClick={() => navigate('/?q=vuln:CVE-2021-44228')}>
            <code>vuln:CVE-2021-44228</code>
            <span>Log4j vulnerability</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Filters;
