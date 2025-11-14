import React, { useState, useEffect } from 'react';
import { Search, Grid, Network, Settings, Plus } from 'lucide-react';
import './App.css';

interface Capture {
  id: string;
  url: string;
  title: string;
  screenshot: string;
  created_at: string;
}

function App() {
  const [captures, setCaptures] = useState<Capture[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [view, setView] = useState<'grid' | 'map'>('grid');

  useEffect(() => {
    fetchCaptures();
    // Poll for new captures every 2 seconds
    const interval = setInterval(fetchCaptures, 2000);
    return () => clearInterval(interval);
  }, []);

  const fetchCaptures = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/captures');
      const data = await response.json();
      setCaptures(data);
    } catch (error) {
      console.error('Failed to fetch captures:', error);
    }
  };

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    if (query.trim() === '') {
      fetchCaptures();
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/search?q=${encodeURIComponent(query)}`);
      const data = await response.json();
      setCaptures(data);
    } catch (error) {
      console.error('Search failed:', error);
    }
  };

  return (
    <div className="app">
      {/* Custom Title Bar */}
      <div className="titlebar">
        <div className="titlebar-title">Synapse</div>
        <div className="titlebar-controls">
          {/* Windows controls would go here */}
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Sidebar */}
        <div className="sidebar">
          <div className="sidebar-logo">
            <div className="logo-icon">S</div>
            <span className="logo-text">Synapse</span>
          </div>

          <nav className="sidebar-nav">
            <button className="nav-item active">
              <Grid size={20} />
              <span>All Captures</span>
            </button>
            <button className="nav-item">
              <Network size={20} />
              <span>Mind Map</span>
            </button>
          </nav>

          <div className="sidebar-footer">
            <button className="nav-item">
              <Settings size={20} />
              <span>Settings</span>
            </button>
          </div>
        </div>

        {/* Content Area */}
        <div className="content">
          {/* Search Bar */}
          <div className="search-section">
            <div className="search-bar">
              <Search size={20} className="search-icon" />
              <input
                type="text"
                placeholder="Search your second brain..."
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                className="search-input"
              />
            </div>
          </div>

          {/* Captures Grid */}
          <div className="captures-grid">
            {captures.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">
                  <Plus size={48} />
                </div>
                <h2>No captures yet</h2>
                <p>Press Ctrl+Shift+S in your browser to capture a page</p>
              </div>
            ) : (
              captures.map((capture) => (
                <div key={capture.id} className="capture-card">
                  <div className="capture-screenshot">
                    <img src={capture.screenshot} alt={capture.title} />
                  </div>
                  <div className="capture-info">
                    <h3 className="capture-title">{capture.title}</h3>
                    <a href={capture.url} className="capture-url" target="_blank" rel="noopener noreferrer">
                      {new URL(capture.url).hostname}
                    </a>
                    <p className="capture-date">
                      {new Date(capture.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
