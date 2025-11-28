import React, { useState } from 'react';
import { Bell } from 'lucide-react';
import './NotificationToggle.css';

const NotificationToggle = () => {
    const [enabled, setEnabled] = useState(true);

    return (
        <div className="settings-section glass-panel">
            <h3 className="section-title">Notifications</h3>
            <div className="notification-item">
                <div className="notification-info">
                    <Bell size={20} className="text-primary" />
                    <div>
                        <h4>Enable Alerts</h4>
                        <p>Receive real-time updates on high-severity threats.</p>
                    </div>
                </div>
                <label className="switch">
                    <input type="checkbox" checked={enabled} onChange={() => setEnabled(!enabled)} />
                    <span className="slider round"></span>
                </label>
            </div>
        </div>
    );
};

export default NotificationToggle;
