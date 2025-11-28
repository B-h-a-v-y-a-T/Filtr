import React from 'react';
import DashboardStatsRow from '../components/dashboard/DashboardStatsRow';
import DailyEditReportWidget from '../components/dashboard/DailyEditReportWidget';
import AlertTrendGraph from '../components/dashboard/AlertTrendGraph';
import HistoryTable from '../components/dashboard/HistoryTable';
import ChatBotButton from '../components/dashboard/ChatBotButton';
import PaginationLoadMore from '../components/global/PaginationLoadMore';
import './Dashboard.css';

const Dashboard = () => {
    return (
        <div className="dashboard-page">
            <DashboardStatsRow />

            <div className="dashboard-grid">
                <div className="dashboard-main-chart">
                    <AlertTrendGraph />
                </div>
                <div className="dashboard-side-widget">
                    <DailyEditReportWidget />
                </div>
            </div>

            <div className="dashboard-section">
                <HistoryTable />
                <PaginationLoadMore isLoading={false} onLoadMore={() => { }} />
            </div>

            <ChatBotButton />

            <div style={{ textAlign: 'center', padding: '20px', fontSize: '12px', opacity: 0.6 }}>
                Made by OptiMl
            </div>
        </div>
    );
};

export default Dashboard;
