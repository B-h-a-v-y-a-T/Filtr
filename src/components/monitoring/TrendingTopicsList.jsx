import React, { useState, useEffect } from 'react';
import { TrendingUp, ArrowUpRight, RefreshCw, ExternalLink, AlertCircle, CheckCircle } from 'lucide-react';
import './TrendingTopicsList.css';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1';

const TrendingTopicsList = () => {
    const [topics, setTopics] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchTrendingTopics = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_BASE_URL}/watcher-dashboard`);
            if (!response.ok) throw new Error('Failed to fetch trending topics');
            
            const data = await response.json();
            
            if (data.status === 'success' && data.trending_news) {
                // Transform watcher data to trending topics format
                const trendingTopics = data.trending_news.map((item, index) => ({
                    rank: index + 1,
                    topic: item.headline || item.title || 'Unknown Topic',
                    source: item.source || 'Unknown',
                    confidence: item.confidence || 0,
                    verdict: item.verdict || 'Analyzing...',
                    url: item.url || '#',
                    timesSeen: item.times_seen || 1
                }));
                setTopics(trendingTopics);
            } else {
                setTopics([]);
            }
        } catch (err) {
            console.error('Error fetching trending topics:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchTrendingTopics();
        // Auto-refresh every 2 minutes
        const interval = setInterval(fetchTrendingTopics, 120000);
        return () => clearInterval(interval);
    }, []);

    const getVerdictClass = (verdict) => {
        if (!verdict) return 'analyzing';
        const v = verdict.toLowerCase();
        if (v.includes('true') || v.includes('verified')) return 'verified';
        if (v.includes('false') || v.includes('misleading')) return 'false';
        return 'unverified';
    };

    const getVerdictIcon = (verdict) => {
        const v = (verdict || '').toLowerCase();
        if (v.includes('true') || v.includes('verified')) return <CheckCircle size={14} />;
        if (v.includes('false') || v.includes('misleading')) return <AlertCircle size={14} />;
        return null;
    };

    return (
        <div className="trending-topics glass-panel">
            <div className="trending-header">
                <TrendingUp size={20} className="text-primary" />
                <h3>Trending Narratives</h3>
                <button 
                    className="refresh-btn" 
                    onClick={fetchTrendingTopics}
                    disabled={loading}
                    title="Refresh"
                >
                    <RefreshCw size={16} className={loading ? 'spinning' : ''} />
                </button>
            </div>
            
            {error && (
                <div className="error-message">
                    <AlertCircle size={16} /> {error}
                </div>
            )}
            
            <div className="topics-list">
                {loading && topics.length === 0 ? (
                    <div className="loading-state">Loading trending topics...</div>
                ) : topics.length === 0 ? (
                    <div className="empty-state">No trending topics detected yet</div>
                ) : (
                    topics.map((item) => (
                        <div key={item.rank} className="topic-item">
                            <span className="topic-rank">#{item.rank}</span>
                            <div className="topic-info">
                                <span className="topic-name">{item.topic}</span>
                                <span className="topic-source">{item.source}</span>
                            </div>
                            <div className={`topic-verdict ${getVerdictClass(item.verdict)}`}>
                                {getVerdictIcon(item.verdict)}
                                <span>{item.confidence}%</span>
                            </div>
                            <a 
                                href={item.url} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="topic-action"
                                title="View Source"
                            >
                                <ExternalLink size={16} />
                            </a>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default TrendingTopicsList;
