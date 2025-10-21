import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import './App.css';
import Search from './pages/Search';
import Explore from './pages/Explore';
import Filters from './pages/Filters';
import Account from './pages/Account';

const App: React.FC = () => {
  return (
    <Router>
      <div className="app">
        <Header />
        <main className="app-main">
          <Routes>
            <Route path="/" element={<Search />} />
            <Route path="/explore" element={<Explore />} />
            <Route path="/filters" element={<Filters />} />
            <Route path="/account" element={<Account />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
};

const Header: React.FC = () => {
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path ? 'active' : '';
  };

  return (
    <header className="app-header">
      <div className="header-content">
        <Link to="/" className="logo">
          <span className="logo-icon">🔍</span>
          <span className="logo-text">AssetScan</span>
        </Link>
        <nav className="header-nav">
          <Link to="/" className={`nav-link ${isActive('/')}`}>
            Search
          </Link>
          <Link to="/explore" className={`nav-link ${isActive('/explore')}`}>
            Explore
          </Link>
          <Link to="/filters" className={`nav-link ${isActive('/filters')}`}>
            Filters
          </Link>
          <Link to="/account" className={`nav-link ${isActive('/account')}`}>
            Account
          </Link>
        </nav>
      </div>
    </header>
  );
};

const Footer: React.FC = () => {
  return (
    <footer className="app-footer">
      <div className="footer-content">
        <p>AssetScan Intelligence Platform • Powered by OpenSearch</p>
        <div className="footer-links">
          <a href="#">API Docs</a>
          <a href="#">Terms</a>
          <a href="#">Privacy</a>
          <a href="#">Support</a>
        </div>
      </div>
    </footer>
  );
};

export default App;
