import React from 'react';
import { Bell, User } from 'lucide-react';
import './HeaderBar.css';

const HeaderBar = ({ title }) => {
    return (
        <header className="header-bar">
            <h1 className="page-title">{title}</h1>

            <div className="header-actions">
                <button className="icon-btn notification-btn">
                    <Bell size={20} />
                    <span className="notification-badge"></span>
                </button>
                <div className="user-profile">
                    <div className="user-avatar">
                        <User size={16} className="user-icon" />
                    </div>
                </div>
            </div>
        </header>
    );
};

export default HeaderBar;
