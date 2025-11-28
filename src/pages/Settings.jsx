import React from 'react';
import APIConfigSection from '../components/settings/APIConfigSection';
import TwoFactorSetupPanel from '../components/settings/TwoFactorSetupPanel';
import DatabaseConfigCard from '../components/settings/DatabaseConfigCard';
import ThemeSwitcher from '../components/settings/ThemeSwitcher';
import NotificationToggle from '../components/settings/NotificationToggle';
import './Settings.css';

const Settings = () => {
    return (
        <div className="settings-page">
            <div className="settings-grid">
                <div className="settings-column">
                    <APIConfigSection />
                    <DatabaseConfigCard />
                </div>
                <div className="settings-column">
                    <TwoFactorSetupPanel />
                    <ThemeSwitcher />
                    <NotificationToggle />
                </div>
            </div>

            <div style={{ textAlign: 'center', padding: '20px', fontSize: '12px', opacity: 0.6 }}>
                Made by OptiMl
            </div>
        </div>
    );
};

export default Settings;
