import React from 'react';
import { ResponsiveContainer } from 'recharts';
import './ChartView.css';

const ChartView = ({ title, children, height = 300 }) => {
    return (
        <div className="chart-view glass-panel">
            <h3 className="chart-title">{title}</h3>
            <div className="chart-container" style={{ height }}>
                <ResponsiveContainer width="100%" height="100%">
                    {children}
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default ChartView;
