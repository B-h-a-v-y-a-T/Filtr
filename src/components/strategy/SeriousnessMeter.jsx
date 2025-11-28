import React from 'react';
import './SeriousnessMeter.css';

const SeriousnessMeter = ({ level = 0, classification = 'Medium', justification = '' }) => {
    const getColor = (score) => {
        if (score === 0) return 'hsl(0, 0%, 50%)'; // Gray for no score
        if (score <= 25) return 'hsl(120, 100%, 50%)'; // Green
        if (score <= 50) return 'hsl(60, 100%, 50%)'; // Yellow
        if (score <= 75) return 'hsl(30, 100%, 50%)'; // Orange
        return 'hsl(0, 100%, 50%)'; // Red
    };

    const color = getColor(level);
    const hasData = level > 0;

    return (
        <div className="seriousness-meter glass-panel">
            <h3 className="meter-title">Threat Severity Assessment</h3>
            <div className="meter-container">
                <div className="meter-bar">
                    <div
                        className="meter-fill"
                        style={{ 
                            width: `${level}%`, 
                            background: color,
                            minWidth: level === 0 ? '0%' : '2%'
                        }}
                    ></div>
                </div>
                <div className="meter-labels">
                    <span>Low</span>
                    <span>Medium</span>
                    <span>High</span>
                    <span>Critical</span>
                </div>
            </div>
            <div className="meter-value">
                Score: <span style={{ color }}>{level}/100</span>
            </div>
            {hasData ? (
                <div className="meter-classification" style={{
                    marginTop: '10px',
                    padding: '10px',
                    background: 'rgba(74, 144, 226, 0.1)',
                    borderRadius: '6px',
                    fontSize: '0.9em'
                }}>
                    <strong>Classification:</strong> {classification}
                    {justification && (
                        <div style={{ marginTop: '8px', fontSize: '0.85em', color: '#666' }}>
                            {justification}
                        </div>
                    )}
                </div>
            ) : (
                <div className="meter-classification" style={{
                    marginTop: '10px',
                    padding: '10px',
                    background: 'rgba(255, 255, 255, 0.05)',
                    borderRadius: '6px',
                    fontSize: '0.9em',
                    color: '#888',
                    textAlign: 'center'
                }}>
                    Generate strategy to see threat assessment
                </div>
            )}
        </div>
    );
};

export default SeriousnessMeter;
