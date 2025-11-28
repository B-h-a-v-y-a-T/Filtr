import React, { useState } from 'react';
import { Shield, Smartphone } from 'lucide-react';
import './TwoFactorSetupPanel.css';

const TwoFactorSetupPanel = () => {
    const [enabled, setEnabled] = useState(true);

    return (
        <div className="settings-section glass-panel">
            <h3 className="section-title">Security</h3>
            <div className="security-item">
                <div className="security-info">
                    <div className="security-icon">
                        <Shield size={20} />
                    </div>
                    <div>
                        <h4>Two-Factor Authentication</h4>
                        <p>Add an extra layer of security to your account.</p>
                    </div>
                </div>
                <label className="switch">
                    <input type="checkbox" checked={enabled} onChange={() => setEnabled(!enabled)} />
                    <span className="slider round"></span>
                </label>
            </div>

            {enabled && (
                <div className="setup-2fa">
                    <button className="setup-btn">
                        <Smartphone size={16} />
                        Configure Authenticator App
                    </button>
                </div>
            )}
        </div>
    );
};

export default TwoFactorSetupPanel;
