import React, { useState, useEffect } from 'react';
import './WatcherAgentWidget.css';

const WatcherAgentWidget = () => {
    const [watcherData, setWatcherData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [lastUpdate, setLastUpdate] = useState(null);
    const [isRefreshing, setIsRefreshing] = useState(false);

    const fetchWatcherData = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await fetch('http://localhost:8000/api/v1/watcher-dashboard');
            if (!response.ok) throw new Error('Watcher service unavailable');
            
            const data = await response.json();
            
            // DEBUGGING: Log API response once on load
            console.log('[Watcher Agent] API Response:', data);
            
            setWatcherData(data);
            setLastUpdate(new Date());
        } catch (err) {
            console.error('[Watcher Agent] Fetch error:', err);
            setError(err.message);
            setWatcherData(null);
        } finally {
            setLoading(false);
        }
    };

    const triggerFreshCycle = async () => {
        try {
            setIsRefreshing(true);
            setError(null);
            
            console.log('[Watcher Agent] 🔄 Triggering NEW monitoring cycle...');
            
            // Step 1: Trigger new monitoring cycle to fetch fresh articles from internet
            const triggerResponse = await fetch('http://localhost:8000/api/v1/watcher-trigger', {
                method: 'POST'
            });
            
            if (!triggerResponse.ok) {
                throw new Error('Failed to trigger monitoring cycle');
            }
            
            const triggerResult = await triggerResponse.json();
            console.log('[Watcher Agent] ✓ Monitoring cycle completed:', triggerResult);
            
            // Step 2: Wait 2 seconds for analysis to complete
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Step 3: Fetch updated dashboard data
            await fetchWatcherData();
            
        } catch (err) {
            console.error('[Watcher Agent] Refresh error:', err);
            setError('Failed to fetch fresh news: ' + err.message);
        } finally {
            setIsRefreshing(false);
        }
    };

    useEffect(() => {
        fetchWatcherData();
        // Auto-refresh every 10 minutes by triggering NEW monitoring cycle
        const interval = setInterval(triggerFreshCycle, 10 * 60 * 1000);
        return () => clearInterval(interval);
    }, []);

    const getBadgeClass = (badgeText) => {
        // Parse badge from backend format: "✅ green", "➖ grey", "❌ red"
        if (!badgeText) return 'verification-badge badge-grey';
        
        const lowerBadge = String(badgeText).toLowerCase();
        if (lowerBadge.includes('green')) return 'verification-badge badge-green';
        if (lowerBadge.includes('red')) return 'verification-badge badge-red';
        return 'verification-badge badge-grey';
    };

    if (loading && !watcherData) {
        return (
            <div className="watcher-widget">
                <div className="watcher-header">
                    <h3>🔍 Watcher Agent</h3>
                    <span className="watcher-badge monitoring">Monitoring</span>
                </div>
                <div className="watcher-loading">
                    <div className="spinner"></div>
                    <p>Loading monitoring data...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="watcher-widget">
                <div className="watcher-header">
                    <h3>🔍 Watcher Agent</h3>
                    <span className="watcher-badge error">Error</span>
                </div>
                <div className="watcher-error">
                    <p>⚠️ {error}</p>
                    <button onClick={fetchWatcherData} className="retry-btn">Retry</button>
                </div>
            </div>
        );
    }

    // No data check
    if (!watcherData) {
        return (
            <div className="watcher-widget">
                <div className="watcher-header">
                    <h3>🔍 Watcher Agent</h3>
                </div>
                <div className="watcher-empty">
                    <p>No watcher data available.</p>
                    <button onClick={fetchWatcherData} className="retry-btn">Refresh</button>
                </div>
            </div>
        );
    }

    return (
        <div className="watcher-widget">
            <div className="watcher-header">
                <div>
                    <h3>🔍 Watcher Agent</h3>
                    <p className="watcher-subtitle">Real-time misinformation monitoring</p>
                </div>
                <div className="watcher-header-right">
                    <button onClick={fetchWatcherData} className="refresh-btn" title="Refresh">
                        🔄
                    </button>
                </div>
            </div>

            {/* Monitoring Status */}
            <div className="watcher-status-bar">
                <div className="status-item">
                    <span className="status-label">Status:</span>
                    <span className="status-value monitoring">● Active</span>
                </div>
                <div className="status-item">
                    <span className="status-label">API Calls Left:</span>
                    <span className="status-value">
                        {watcherData?.api_calls_remaining || 0}/100
                    </span>
                </div>
                <div className="status-item">
                    <span className="status-label">Last Updated:</span>
                    <span className="status-value">
                        {watcherData?.last_updated 
                            ? new Date(watcherData.last_updated).toLocaleTimeString()
                            : 'N/A'}
                    </span>
                </div>
            </div>

            {/* Live Trending News Monitor - ONLY FROM API */}
            {watcherData?.trending_news && watcherData.trending_news.length > 0 ? (
                <div className="watcher-section">
                    <h4>📡 Live Trending News Monitor</h4>
                    <div className="trending-news-list">
                        {watcherData.trending_news.map((news, idx) => (
                            <div key={idx} className="trending-news-item">
                                <div className="trending-header">
                                    <span className="trending-source">{news.source}</span>
                                    <span className={getBadgeClass(news.badge_color)}>
                                        {news.badge} {news.verdict}
                                    </span>
                                </div>
                                <a 
                                    href={news.url} 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    className="trending-headline-link"
                                >
                                    <p className="trending-headline">{news.headline}</p>
                                </a>
                                <div className="trending-meta">
                                    <span className="confidence-indicator">
                                        {news.confidence}% confidence
                                    </span>
                                    {news.times_seen > 1 && (
                                        <span className="trending-repeat">🔁 Seen {news.times_seen}x</span>
                                    )}
                                    {news.category && (
                                        <span className="trending-category">📁 {news.category}</span>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            ) : (
                <div className="watcher-section">
                    <div className="watcher-empty-state">
                        <p>🔍 Watcher agent running — no trends detected yet.</p>
                    </div>
                </div>
            )}

            {/* Footer */}
            <div className="watcher-footer">
                <span className="update-time">
                    Last updated: {lastUpdate ? lastUpdate.toLocaleTimeString() : 'N/A'}
                </span>
                <button 
                    onClick={triggerFreshCycle} 
                    className="manual-refresh"
                    disabled={isRefreshing}
                >
                    {isRefreshing ? '⏳ Fetching Fresh News...' : '🔄 Fetch New Articles'}
                </button>
            </div>
        </div>
    );
};

export default WatcherAgentWidget;
