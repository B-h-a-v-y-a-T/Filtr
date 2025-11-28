import React from 'react';
import { AlertTriangle, Share2, Flag, Slash } from 'lucide-react';
import './RecommendedActionStrip.css';

const RecommendedActionStrip = ({ severity = 'high' }) => {
    return (
        <div className="action-strip glass-panel">
            <div className="action-header">
                <h3>Recommended Actions</h3>
                <span className={`severity-badge severity-${severity}`}>
                    Severity: {severity.toUpperCase()}
                </span>
            </div>
            <div className="actions-list">
                <button className="action-btn-primary">
                    <Flag size={16} />
                    <span>Report to Platform</span>
                </button>
                <button className="action-btn-secondary">
                    <Share2 size={16} />
                    <span>Share Correction</span>
                </button>
                <button className="action-btn-danger">
                    <Slash size={16} />
                    <span>Takedown Request</span>
                </button>
            </div>
        </div>
    );
};

export default RecommendedActionStrip;
