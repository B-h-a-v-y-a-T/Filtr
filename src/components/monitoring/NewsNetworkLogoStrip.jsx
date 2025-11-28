import React from 'react';
import './NewsNetworkLogoStrip.css';

const NewsNetworkLogoStrip = () => {
    const networks = ['CNN', 'BBC', 'Fox', 'Reuters', 'AP', 'Al Jazeera', 'MSNBC'];

    return (
        <div className="logo-strip glass-panel">
            <span className="strip-label">Monitored Sources:</span>
            <div className="logos-container">
                {networks.map((net) => (
                    <div key={net} className="network-logo">
                        {net}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default NewsNetworkLogoStrip;
