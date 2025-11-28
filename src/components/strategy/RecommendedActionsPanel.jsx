import React from 'react';
import { CheckSquare } from 'lucide-react';
import './RecommendedActionsPanel.css';

const RecommendedActionsPanel = ({ actions = [] }) => {
    const getPriorityColor = (priority) => {
        switch (priority?.toLowerCase()) {
            case 'critical': return '#ff4444';
            case 'high': return '#ff8800';
            case 'medium': return '#ffaa00';
            case 'low': return '#4a90e2';
            default: return '#666';
        }
    };

    if (!actions || actions.length === 0) {
        return (
            <div className="actions-panel glass-panel">
                <h3 className="panel-title">Recommended Response Plan</h3>
                <div style={{ padding: '15px', color: '#888', textAlign: 'center' }}>
                    Generate a strategy to see recommended actions
                </div>
            </div>
        );
    }

    return (
        <div className="actions-panel glass-panel">
            <h3 className="panel-title">Company Action Plan</h3>
            <div className="actions-list-check">
                {actions.map((actionItem, idx) => (
                    <div key={idx} className="action-check-item" style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '10px',
                        marginBottom: '10px',
                        padding: '8px',
                        background: 'rgba(74, 144, 226, 0.05)',
                        borderRadius: '6px'
                    }}>
                        <CheckSquare size={18} className="text-primary" style={{ flexShrink: 0, marginTop: '2px' }} />
                        <div style={{ flex: 1 }}>
                            <span>{actionItem.action || actionItem}</span>
                            {actionItem.priority && (
                                <span style={{
                                    marginLeft: '8px',
                                    fontSize: '0.75em',
                                    padding: '2px 6px',
                                    borderRadius: '4px',
                                    background: getPriorityColor(actionItem.priority),
                                    color: 'white',
                                    fontWeight: 'bold'
                                }}>
                                    {actionItem.priority.toUpperCase()}
                                </span>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default RecommendedActionsPanel;
