import React, { useState, useEffect } from 'react';
import { Globe, Rss, RefreshCw, ExternalLink, AlertCircle } from 'lucide-react';
import { scrapeRedditAPI } from '../../services/api';
import './FeedWebScrapePanel.css';

const FeedWebScrapePanel = () => {
    const [feeds, setFeeds] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [lastUpdated, setLastUpdated] = useState(null);

    const fetchFeeds = async () => {
        setLoading(true);
        setError(null);
        try {
            // Fetch latest Reddit posts about news/misinformation
            const response = await scrapeRedditAPI('', 8);
            
            if (response.status === 'success' && response.data) {
                const formattedFeeds = response.data.map((item, index) => ({
                    id: index,
                    source: `r/${item.subreddit}`,
                    title: item.title,
                    time: formatTimeAgo(item.created_utc),
                    type: item.subreddit.includes('news') ? 'news' : 'scrape',
                    url: item.url,
                    score: item.score,
                    comments: item.num_comments
                }));
                setFeeds(formattedFeeds);
                setLastUpdated(new Date());
            }
        } catch (err) {
            console.error('Error fetching feeds:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const formatTimeAgo = (timestamp) => {
        if (!timestamp) return 'Recently';
        const seconds = Math.floor(Date.now() / 1000 - timestamp);
        if (seconds < 60) return 'Just now';
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
        return `${Math.floor(seconds / 86400)}d ago`;
    };

    useEffect(() => {
        fetchFeeds();
        // Auto-refresh every 3 minutes
        const interval = setInterval(fetchFeeds, 180000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="feed-panel glass-panel">
            <div className="feed-header">
                <h3>Live Ingestion Feed</h3>
                <div className="feed-header-right">
                    <button 
                        className="refresh-btn" 
                        onClick={fetchFeeds}
                        disabled={loading}
                        title="Refresh Feed"
                    >
                        <RefreshCw size={14} className={loading ? 'spinning' : ''} />
                    </button>
                    <div className="live-indicator">
                        <span className="pulse-dot"></span>
                        Live
                    </div>
                </div>
            </div>
            
            {error && (
                <div className="feed-error">
                    <AlertCircle size={14} /> {error}
                </div>
            )}
            
            <div className="feed-list">
                {loading && feeds.length === 0 ? (
                    <div className="feed-loading">Loading feeds...</div>
                ) : feeds.length === 0 ? (
                    <div className="feed-empty">No feeds available</div>
                ) : (
                    feeds.map((item) => (
                        <div key={item.id} className="feed-item">
                            <div className="feed-icon">
                                {item.type === 'scrape' ? <Globe size={16} /> : <Rss size={16} />}
                            </div>
                            <div className="feed-content">
                                <span className="feed-source">{item.source}</span>
                                <p className="feed-title">{item.title}</p>
                                {item.score !== undefined && (
                                    <span className="feed-meta">
                                        ↑{item.score} · {item.comments} comments
                                    </span>
                                )}
                            </div>
                            <div className="feed-actions">
                                <span className="feed-time">{item.time}</span>
                                {item.url && (
                                    <a 
                                        href={item.url} 
                                        target="_blank" 
                                        rel="noopener noreferrer"
                                        className="feed-link"
                                        title="Open Link"
                                    >
                                        <ExternalLink size={12} />
                                    </a>
                                )}
                            </div>
                        </div>
                    ))
                )}
            </div>
            
            {lastUpdated && (
                <div className="feed-footer">
                    Last updated: {lastUpdated.toLocaleTimeString()}
                </div>
            )}
        </div>
    );
};

export default FeedWebScrapePanel;
