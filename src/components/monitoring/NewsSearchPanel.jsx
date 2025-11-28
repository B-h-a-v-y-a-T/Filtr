import React, { useState } from 'react';
import { Search, Globe, ExternalLink, Clock } from 'lucide-react';
import { scrapeRedditAPI } from '../../services/api';
import './NewsSearchPanel.css';

const CONTINENTS = [
    'All Regions',
    'Africa',
    'Asia',
    'Europe',
    'North America',
    'South America',
    'Australia/Oceania',
    'Antarctica'
];

const NewsSearchPanel = () => {
    const [keyword, setKeyword] = useState('');
    const [region, setRegion] = useState('All Regions');
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState([]);
    const [hasSearched, setHasSearched] = useState(false);

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!keyword.trim()) return;

        setLoading(true);
        setHasSearched(true);
        setResults([]);

        try {
            // Use our Reddit scraper API
            const response = await scrapeRedditAPI(keyword.trim(), 10);

            if (response.status === 'success' && response.data) {
                const formatted = response.data.map((item, index) => ({
                    id: index,
                    title: item.title,
                    source: `r/${item.subreddit}`,
                    date: item.created_utc ? new Date(item.created_utc * 1000).toLocaleDateString() : new Date().toLocaleDateString(),
                    snippet: `Score: ${item.score} | Comments: ${item.num_comments}`,
                    url: item.url
                }));
                setResults(formatted);
            } else {
                setResults([]);
                console.error("Search error:", response.message);
            }
        } catch (err) {
            console.error("Fetch failed:", err);
            setResults([]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="news-search-panel">
            <div className="panel-header">
                <h3><Globe size={20} /> Global News Search</h3>
            </div>

            <form onSubmit={handleSearch} className="search-controls">
                <div className="input-group">
                    <Search size={18} className="search-icon" />
                    <input
                        type="text"
                        placeholder="Enter keyword..."
                        value={keyword}
                        onChange={(e) => setKeyword(e.target.value)}
                        className="search-input"
                    />
                </div>

                <select
                    value={region}
                    onChange={(e) => setRegion(e.target.value)}
                    className="region-select"
                >
                    {CONTINENTS.map((c) => (
                        <option key={c} value={c}>{c}</option>
                    ))}
                </select>

                <button type="submit" className="search-btn" disabled={loading || !keyword.trim()}>
                    {loading ? 'Searching...' : 'Search'}
                </button>
            </form>

            <div className="results-container">
                {loading && (
                    <div className="loading-state">
                        <div className="spinner"></div>
                        <p>Scanning global sources...</p>
                    </div>
                )}

                {!loading && hasSearched && results.length === 0 && (
                    <div className="empty-state">
                        No results found for "{keyword}" in {region}.
                    </div>
                )}

                {!loading && results.length > 0 && (
                    <div className="results-list">
                        {results.map((item) => (
                            <div key={item.id} className="result-card">
                                <div className="result-header">
                                    <span className="source-tag">{item.source}</span>
                                    <span className="date-tag">
                                        <Clock size={12} /> {item.date}
                                    </span>
                                </div>
                                <h4>{item.title}</h4>
                                <p>{item.snippet}</p>
                                <a
                                    href={item.url}
                                    className="read-more"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >
                                    Read Analysis <ExternalLink size={14} />
                                </a>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default NewsSearchPanel;
