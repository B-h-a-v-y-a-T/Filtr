import React from 'react';
import BadgeVerdict from '../global/BadgeVerdict';
import { ShieldCheck, Clock } from 'lucide-react';
import './VerdictResultCard.css';

const VerdictResultCard = ({ result }) => {
    if (!result) return null;

    return (
        <div className="verdict-card glass-panel">
            <div className="verdict-header">
                <div className="verdict-icon-wrapper">
                    <ShieldCheck size={32} className="text-primary" />
                </div>
                <div className="verdict-info">
                    <h3>Analysis Verdict</h3>
                    <BadgeVerdict verdict={result.verdict} />
                </div>
                <div className="confidence-score">
                    <span className="score-label">Confidence</span>
                    <span className="score-value">{result.confidence}%</span>
                </div>
            </div>
            <div className="verdict-meta">
                <Clock size={14} />
                <span>Analyzed on {result.timestamp}</span>
            </div>
        </div>
    );
};

export default VerdictResultCard;
