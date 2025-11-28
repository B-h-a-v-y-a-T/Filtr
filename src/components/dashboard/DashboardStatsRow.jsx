import React from 'react';
import MetricCard from '../global/MetricCard';
import { Globe, Activity, AlertTriangle, CheckCircle } from 'lucide-react';
import './DashboardStatsRow.css';

const DashboardStatsRow = () => {
    // Mock data
    const stats = [
        { title: 'Regions Covered', value: '12', trend: 'up', trendValue: '2', icon: Globe, color: 'primary' },
        { title: 'Avg Response Time', value: '1.2s', trend: 'down', trendValue: '0.3s', icon: Activity, color: 'info' },
        { title: 'Active Alerts', value: '5', trend: 'up', trendValue: '3', icon: AlertTriangle, color: 'warning' },
        { title: 'Verified Today', value: '142', trend: 'up', trendValue: '12%', icon: CheckCircle, color: 'success' },
    ];

    return (
        <div className="dashboard-stats-row">
            {stats.map((stat, index) => (
                <MetricCard key={index} {...stat} />
            ))}
        </div>
    );
};

export default DashboardStatsRow;
