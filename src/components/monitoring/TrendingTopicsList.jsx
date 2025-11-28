import React from 'react';
import { TrendingUp, ArrowUpRight } from 'lucide-react';
import './TrendingTopicsList.css';

const TrendingTopicsList = () => {
    const topics = [
        { rank: 1, topic: 'Election Fraud Claims', volume: '2.4M', trend: '+12%' },
        { rank: 2, topic: 'New Health Policy', volume: '1.1M', trend: '+8%' },
        { rank: 3, topic: 'Celebrity Scandal', volume: '890K', trend: '+5%' },
        { rank: 4, topic: 'Tech IPO', volume: '650K', trend: '+2%' },
        { rank: 5, topic: 'Climate Summit', volume: '420K', trend: '-1%' },
    ];

    return (
        <div className="trending-topics glass-panel">
            <div className="trending-header">
                <TrendingUp size={20} className="text-primary" />
                <h3>Trending Narratives</h3>
            </div>
            <div className="topics-list">
                {topics.map((item) => (
                    <div key={item.rank} className="topic-item">
                        <span className="topic-rank">#{item.rank}</span>
                        <div className="topic-info">
                            <span className="topic-name">{item.topic}</span>
                            <span className="topic-volume">{item.volume} mentions</span>
                        </div>
                        <div className={`topic-trend ${item.trend.startsWith('+') ? 'text-success' : 'text-muted'}`}>
                            {item.trend}
                        </div>
                        <button className="topic-action">
                            <ArrowUpRight size={16} />
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default TrendingTopicsList;
