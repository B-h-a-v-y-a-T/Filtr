import React, { useState } from 'react';
import { Search, Globe, ExternalLink, Clock, MessageCircle, Newspaper } from 'lucide-react';
import { scrapeRedditAPI, searchNewsAPI } from '../../services/api';
import './DualSourceSearch.css';

const DualSourceSearch = () => {
    const [keyword, setKeyword] = useState('');
    const [loading, setLoading] = useState({ reddit: false, news: false });
    const [redditResults, setRedditResults] = useState([]);
    const [newsResults, setNewsResults] = useState([]);
    const [hasSearched, setHasSearched] = useState(false);

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!keyword.trim()) return;

        setHasSearched(true);
        setLoading({ reddit: true, news: true });
        setRedditResults([]);
        setNewsResults([]);

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

        const newsPromise = searchNewsAPI(keyword.trim(), 8)
            .then(response => {
                if (response.status === 'success' && response.data) {
                    setNewsResults(response.data.map((item, index) => ({
                        id: index,
                        title: item.title,
                        source: item.source,
                        date: item.publishedAt ? new Date(item.publishedAt).toLocaleDateString() : new Date().toLocaleDateString(),
                        snippet: item.description || '',
                        url: item.url,
                        image: item.image
                    })));
                }
            })
            .catch(err => console.error("News fetch failed:", err))
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

    return (
        <div className="dual-source-search">
            <div className="search-header">
                <h2><Globe size={24} /> Multi-Source News Search</h2>
                <p>Search across social media and news outlets simultaneously</p>
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
                <button type="submit" className="search-btn" disabled={loading.reddit || loading.news || !keyword.trim()}>
                    {(loading.reddit || loading.news) ? 'Searching...' : 'Search All Sources'}
                </button>
            </form>

            <div className="dual-columns">
                {/* Social Media Column (Reddit) */}
                <div className="source-column reddit-column">
                    <div className="column-header">
                        <MessageCircle size={20} />
                        <h3>Social Media (Reddit)</h3>
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

                {/* News Outlets Column */}
                <div className="source-column news-column">
                    <div className="column-header">
                        <Newspaper size={20} />
                        <h3>News Outlets</h3>
                    </div>
                    
                    <div className="results-container">
                        {loading.news && (
                            <div className="loading-state">
                                <div className="spinner"></div>
                                <p>Scanning news sources...</p>
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
