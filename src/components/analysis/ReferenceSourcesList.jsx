import React from 'react';
import { ExternalLink } from 'lucide-react';
import './ReferenceSourcesList.css';

const ReferenceSourcesList = ({ sources }) => {
    return (
        <div className="reference-list glass-panel">
            <h3 className="reference-title">Reference Sources</h3>
            <div className="sources-grid">
                {sources.map((source, index) => (
                    <a key={index} href={source.url} target="_blank" rel="noopener noreferrer" className="source-card">
                        <div className="source-icon">
                            <img src={`https://www.google.com/s2/favicons?domain=${source.url}`} alt="favicon" />
                        </div>
                        <div className="source-info">
                            <span className="source-name">{source.name}</span>
                            <span className="source-domain">{new URL(source.url).hostname}</span>
                        </div>
                        <ExternalLink size={14} className="source-link-icon" />
                    </a>
                ))}
            </div>
        </div>
    );
};

export default ReferenceSourcesList;
