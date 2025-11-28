import React from 'react';
import './DailyEditReportWidget.css';

const DailyEditReportWidget = () => {
    return (
        <div className="daily-report-widget glass-panel">
            <h3 className="widget-title">Daily Edit Report</h3>
            <div className="report-content">
                <div className="report-item">
                    <span className="report-label">Total Edits</span>
                    <span className="report-value">1,240</span>
                </div>
                <div className="report-item">
                    <span className="report-label">Flagged</span>
                    <span className="report-value text-danger">45</span>
                </div>
                <div className="report-item">
                    <span className="report-label">Auto-Fixed</span>
                    <span className="report-value text-success">890</span>
                </div>
            </div>
        </div>
    );
};

export default DailyEditReportWidget;
