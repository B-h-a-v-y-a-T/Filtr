import React from 'react';
import './MetricCard.css';

const MetricCard = ({ title, value, trend, trendValue, icon: Icon, color = 'primary' }) => {
    return (
        <div className={`metric-card metric-card-${color}`}>
            <div className="metric-header">
                <span className="metric-title">{title}</span>
                {Icon && <Icon size={20} className="metric-icon" />}
            </div>
            <div className="metric-value">{value}</div>
            {trend && (
                <div className={`metric-trend ${trend === 'up' ? 'trend-up' : 'trend-down'}`}>
                    <span>{trend === 'up' ? '↑' : '↓'} {trendValue}</span>
                    <span className="trend-label">vs last week</span>
                </div>
            )}
        </div>
    );
};

export default MetricCard;
