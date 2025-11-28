import React from 'react';
import { Copy, RefreshCw } from 'lucide-react';
import './CounterNarrativeGenerator.css';

const CounterNarrativeGenerator = ({ narrative, headline, tone, strategyResult }) => {
    if (!narrative) return null;

    const handleCopy = () => {
        const fullText = headline ? `${headline}\n\n${narrative}` : narrative;
        navigator.clipboard.writeText(fullText).then(() => {
            alert('Message copied to clipboard!');
        }).catch(() => {
            alert('Failed to copy. Please select and copy manually.');
        });
    };

    return (
        <div className="counter-narrative glass-panel">
            <div className="narrative-header">
                <h3>Public Message for Company to Post</h3>
                <div className="narrative-actions">
                    <button className="icon-btn" title="Copy to Clipboard" onClick={handleCopy}>
                        <Copy size={18} />
                    </button>
                </div>
            </div>
            {headline && (
                <div className="narrative-headline" style={{
                    fontSize: '1.2em',
                    fontWeight: 'bold',
                    marginBottom: '15px',
                    color: '#4a90e2'
                }}>
                    {headline}
                </div>
            )}
            {tone && (
                <div className="narrative-tone" style={{
                    fontSize: '0.85em',
                    color: '#888',
                    marginBottom: '10px',
                    fontStyle: 'italic'
                }}>
                    Tone: {tone}
                </div>
            )}
            <div className="narrative-content">
                <p style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>{narrative}</p>
            </div>
        </div>
    );
};

export default CounterNarrativeGenerator;
