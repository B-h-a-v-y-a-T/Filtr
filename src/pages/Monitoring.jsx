import React from 'react';
import MonitoringConfidenceGraph from '../components/monitoring/MonitoringConfidenceGraph';
import RegionSplitView from '../components/monitoring/RegionSplitView';
import TrendingTopicsList from '../components/monitoring/TrendingTopicsList';
import NewsNetworkLogoStrip from '../components/monitoring/NewsNetworkLogoStrip';
import FeedWebScrapePanel from '../components/monitoring/FeedWebScrapePanel';
import DualSourceSearch from '../components/monitoring/DualSourceSearch';
import PaginationLoadMore from '../components/global/PaginationLoadMore';
import './Monitoring.css';

const Monitoring = () => {
    return (
        <div className="monitoring-page">
            <NewsNetworkLogoStrip />

            {/* Dual Source Search - Social Media + News */}
            <DualSourceSearch />

            <div className="monitoring-grid">
                <div className="grid-col-left">
                    <MonitoringConfidenceGraph />
                    <RegionSplitView />
                </div>

                <div className="grid-col-right">
                    <TrendingTopicsList />
                </div>
            </div>

            <div className="feed-section">
                <FeedWebScrapePanel />
                <PaginationLoadMore isLoading={false} onLoadMore={() => { }} />
            </div>

            <div style={{ textAlign: 'center', padding: '20px', fontSize: '12px', opacity: 0.6 }}>
                Made by OptiMl
            </div>
        </div>
    );
};

export default Monitoring;
