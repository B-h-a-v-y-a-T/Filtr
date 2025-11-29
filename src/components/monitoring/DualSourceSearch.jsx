import React, { useState } from 'react';
import { Search, Globe, ExternalLink, Clock, MessageCircle, Newspaper, BarChart3, MapPin } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { scrapeRedditAPI, scrapeGoogleNewsAPI } from '../../services/api';
import './DualSourceSearch.css';

const CONTINENT_COLORS = {
    'asia': '#f59e0b',
    'europe': '#3b82f6',
    'north america': '#22c55e',
    'south america': '#a855f7',
    'africa': '#ef4444',
    'australia': '#06b6d4',
    'unknown': '#64748b'
};

const DualSourceSearch = () => {
    const [keyword, setKeyword] = useState('');
    const [continent, setContinent] = useState('');
    const [loading, setLoading] = useState({ reddit: false, news: false });
    const [redditResults, setRedditResults] = useState([]);
    const [newsResults, setNewsResults] = useState([]);
    const [continentStats, setContinentStats] = useState(null);
    const [hasSearched, setHasSearched] = useState(false);

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!keyword.trim()) return;

        setHasSearched(true);
        setLoading({ reddit: true, news: true });
        setRedditResults([]);
        setNewsResults([]);
        setContinentStats(null);

        // Search both sources in parallel
        const redditPromise = scrapeRedditAPI(keyword.trim(), 8)
            .then(response => {
                if (response.status === 'success' && response.data) {
                    setRedditResults(response.data.map((item, index) => ({
                        id: index,
                        title: item.title,
                        source: `r/${item.subreddit}`,
                        date: item.created_utc ? new Date(item.created_utc * 1000).toLocaleDateString() : new Date().toLocaleDateString(),
                        snippet: `Score: ${item.score} | Comments: ${item.num_comments}`,
                        url: item.url
                    })));
                }
            })
            .catch(err => console.error("Reddit fetch failed:", err))
            .finally(() => setLoading(prev => ({ ...prev, reddit: false })));

        // Use Google News RSS scraper instead of GNews API
        const newsPromise = scrapeGoogleNewsAPI(keyword.trim(), continent, 10)
            .then(response => {
                if (response.status === 'success' && response.data) {
                    setNewsResults(response.data.map((item, index) => ({
                        id: index,
                        title: item.title,
                        source: item.source,
                        date: item.publishedAt || new Date().toLocaleDateString(),
                        url: item.link,
                        continent: item.continent
                    })));
                    // Set continent statistics for the chart
                    if (response.continent_stats) {
                        setContinentStats(response.continent_stats);
                    }
                }
            })
            .catch(err => console.error("Google News fetch failed:", err))
            .finally(() => setLoading(prev => ({ ...prev, news: false })));

        await Promise.all([redditPromise, newsPromise]);
    };

    const ResultCard = ({ item, type }) => (
        <div className="result-card">
            <div className="result-header">
                <span className={`source-tag ${type}`}>{item.source}</span>
                <span className="date-tag">
                    <Clock size={12} /> {item.date}
                </span>
            </div>
            <h4>{item.title}</h4>
            {item.snippet && <p className="snippet">{item.snippet}</p>}
            {item.continent && (
                <span className="continent-badge" style={{ backgroundColor: CONTINENT_COLORS[item.continent] || CONTINENT_COLORS.unknown }}>
                    <MapPin size={10} /> {item.continent}
                </span>
            )}
            <a
                href={item.url}
                className="read-more"
                target="_blank"
                rel="noopener noreferrer"
            >
                Read More <ExternalLink size={14} />
            </a>
        </div>
    );

    // Prepare chart data from continent stats
    const chartData = continentStats ? Object.entries(continentStats)
        .filter(([_, count]) => count > 0)
        .map(([continent, count]) => ({
            name: continent.charAt(0).toUpperCase() + continent.slice(1),
            count: count,
            fill: CONTINENT_COLORS[continent] || CONTINENT_COLORS.unknown
        }))
        .sort((a, b) => b.count - a.count) : [];

    return (
        <div className="dual-source-search">
            <div className="search-header">
                <h2><Globe size={24} /> Multi-Source News Search</h2>
                <p>Search across Reddit and Google News RSS simultaneously</p>
            </div>

            <form onSubmit={handleSearch} className="search-form">
                <div className="search-input-wrapper">
                    <Search size={20} className="search-icon" />
                    <input
                        type="text"
                        placeholder="Enter keyword to search news..."
                        value={keyword}
                        onChange={(e) => setKeyword(e.target.value)}
                        className="search-input"
                    />
                </div>
                <select 
                    value={continent} 
                    onChange={(e) => setContinent(e.target.value)}
                    className="continent-select"
                >
                    <option value="">All Continents</option>
                    <option value="asia">Asia</option>
                    <option value="europe">Europe</option>
                    <option value="north america">North America</option>
                    <option value="south america">South America</option>
                    <option value="africa">Africa</option>
                    <option value="australia">Australia</option>
                </select>
                <button type="submit" className="search-btn" disabled={loading.reddit || loading.news || !keyword.trim()}>
                    {(loading.reddit || loading.news) ? 'Searching...' : 'Search All Sources'}
                </button>
            </form>

            {/* Comparison Chart - Shows after search */}
            {hasSearched && chartData.length > 0 && (
                <div className="comparison-chart glass-panel">
                    <div className="chart-header">
                        <BarChart3 size={20} />
                        <h3>News Coverage by Continent</h3>
                    </div>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height={200}>
                            <BarChart data={chartData} layout="vertical">
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                                <XAxis type="number" stroke="#94a3b8" fontSize={12} />
                                <YAxis dataKey="name" type="category" stroke="#94a3b8" fontSize={12} width={100} />
                                <Tooltip 
                                    contentStyle={{ backgroundColor: '#1e293b', borderColor: 'rgba(255,255,255,0.1)', color: '#f8fafc' }}
                                    formatter={(value) => [`${value} articles`, 'Count']}
                                />
                                <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                                    {chartData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.fill} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="chart-summary">
                        <span>Reddit: {redditResults.length} posts</span>
                        <span>News: {newsResults.length} articles</span>
                    </div>
                </div>
            )}

            <div className="dual-columns">
                {/* Social Media Column (Reddit) */}
                <div className="source-column reddit-column">
                    <div className="column-header">
                        <MessageCircle size={20} />
                        <h3>Social Media (Reddit)</h3>
                        {redditResults.length > 0 && <span className="result-count">{redditResults.length}</span>}
                    </div>
                    
                    <div className="results-container">
                        {loading.reddit && (
                            <div className="loading-state">
                                <div className="spinner"></div>
                                <p>Scanning Reddit...</p>
                            </div>
                        )}

                        {!loading.reddit && hasSearched && redditResults.length === 0 && (
                            <div className="empty-state">No Reddit posts found for "{keyword}"</div>
                        )}

                        {!loading.reddit && redditResults.length > 0 && (
                            <div className="results-list">
                                {redditResults.map((item) => (
                                    <ResultCard key={item.id} item={item} type="reddit" />
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* News Outlets Column (Google News RSS) */}
                <div className="source-column news-column">
                    <div className="column-header">
                        <Newspaper size={20} />
                        <h3>News Outlets (Google News)</h3>
                        {newsResults.length > 0 && <span className="result-count">{newsResults.length}</span>}
                    </div>
                    
                    <div className="results-container">
                        {loading.news && (
                            <div className="loading-state">
                                <div className="spinner"></div>
                                <p>Scanning Google News RSS...</p>
                            </div>
                        )}

                        {!loading.news && hasSearched && newsResults.length === 0 && (
                            <div className="empty-state">No news articles found for "{keyword}"</div>
                        )}

                        {!loading.news && newsResults.length > 0 && (
                            <div className="results-list">
                                {newsResults.map((item) => (
                                    <ResultCard key={item.id} item={item} type="news" />
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DualSourceSearch;
