import React from 'react';
import { Database, RefreshCw, HardDrive } from 'lucide-react';
import './DatabaseConfigCard.css';

const DatabaseConfigCard = () => {
    return (
        <div className="settings-section glass-panel">
            <h3 className="section-title">Database Management</h3>
            <div className="db-status">
                <div className="db-info">
                    <Database size={24} className="text-primary" />
                    <div>
                        <span className="db-name">Primary Cluster (US-East)</span>
                        <span className="db-state text-success">● Operational</span>
                    </div>
                </div>
                <div className="db-stats">
                    <div className="stat-item">
                        <HardDrive size={14} />
                        <span>45% Used</span>
                    </div>
                </div>
            </div>
            <div className="db-actions">
                <button className="action-btn">
                    <RefreshCw size={16} />
                    Refresh Connection
                </button>
                <button className="action-btn">
                    Backup Now
                </button>
            </div>
        </div>
    );
};

export default DatabaseConfigCard;
