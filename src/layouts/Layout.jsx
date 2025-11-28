import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import SidebarNav from '../components/global/SidebarNav';
import HeaderBar from '../components/global/HeaderBar';
import './Layout.css';

const Layout = () => {
    const location = useLocation();

    const getPageTitle = () => {
        switch (location.pathname) {
            case '/': return 'Dashboard';
            case '/monitoring': return 'Monitoring Console';
            case '/analysis': return 'Content Analysis';
            case '/strategy': return 'Strategy & Response';
            case '/settings': return 'System Settings';
            default: return 'Filtr';
        }
    };

    return (
        <div className="app-layout">
            <SidebarNav />
            <div className="main-content-wrapper">
                <HeaderBar title={getPageTitle()} />
                <main className="page-content">
                    <Outlet />
                </main>
            </div>
        </div>
    );
};

export default Layout;
