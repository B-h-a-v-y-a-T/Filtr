import React from 'react';
import { Key, Server } from 'lucide-react';
import './APIConfigSection.css';

const APIConfigSection = () => {
    return (
        <div className="settings-section glass-panel">
            <h3 className="section-title">API Configuration</h3>
            <div className="settings-form">
                <div className="form-group">
                    <label>Backend API URL</label>
                    <div className="input-with-icon">
                        <Server size={16} />
                        <input type="text" defaultValue="https://api.filtr.ai/v1" />
                    </div>
                </div>
                <div className="form-group">
                    <label>API Key</label>
                    <div className="input-with-icon">
                        <Key size={16} />
                        <input type="password" defaultValue="sk_live_xxxxxxxxxxxx" />
                    </div>
                </div>
                <button className="save-btn">Save Changes</button>
            </div>
        </div>
    );
};

export default APIConfigSection;
