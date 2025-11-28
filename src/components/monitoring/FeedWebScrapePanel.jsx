import React from 'react';
import { Globe, Rss } from 'lucide-react';
import './FeedWebScrapePanel.css';

const FeedWebScrapePanel = () => {
    const feeds = [
        { source: 'PIB Fact Check', title: 'Clarification on viral message...', time: '10m ago', type: 'official' },
        { source: 'News API', title: 'Breaking: Global summit outcomes...', time: '24m ago', type: 'news' },
        { source: 'Web Scraper', title: 'Suspicious blog post detected...', time: '1h ago', type: 'scrape' },
    ];

    return (
        <div className="feed-panel glass-panel">
            <div className="feed-header">
                <h3>Live Ingestion Feed</h3>
                <div className="live-indicator">
                    <span className="pulse-dot"></span>
                    Live
                </div>
            </div>
            <div className="feed-list">
                {feeds.map((item, idx) => (
                    <div key={idx} className="feed-item">
                        <div className="feed-icon">
                            {item.type === 'scrape' ? <Globe size={16} /> : <Rss size={16} />}
                        </div>
                        <div className="feed-content">
                            <span className="feed-source">{item.source}</span>
                            <p className="feed-title">{item.title}</p>
                        </div>
                        <span className="feed-time">{item.time}</span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default FeedWebScrapePanel;
