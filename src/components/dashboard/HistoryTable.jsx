import React, { useState, useEffect } from 'react';
import TableView from '../global/TableView';
import BadgeVerdict from '../global/BadgeVerdict';

const HistoryTable = () => {
    const [verifiedArticles, setVerifiedArticles] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchVerifiedArticles();
    }, []);

    const fetchVerifiedArticles = async () => {
        try {
            setLoading(true);
            const response = await fetch('http://localhost:8000/api/v1/watcher-verified');
            if (response.ok) {
                const data = await response.json();
                setVerifiedArticles(data.verified_articles || []);
            }
        } catch (err) {
            console.error('[HistoryTable] Error fetching verified articles:', err);
        } finally {
            setLoading(false);
        }
    };

    const columns = [
        { key: 'id', label: 'ID', width: '8%' },
        { key: 'content', label: 'Headline', width: '42%' },
        { key: 'source', label: 'Source', width: '15%' },
        { key: 'verdict', label: 'Verdict', width: '15%', render: (val) => <BadgeVerdict verdict={val} /> },
        { key: 'timestamp', label: 'Verified', width: '20%' },
    ];

    // Transform API data to table format
    const tableData = verifiedArticles.map((article, idx) => ({
        id: `#${String(article.id || idx + 1).padStart(4, '0')}`,
        content: article.headline,
        source: article.source,
        verdict: article.verdict || 'Unknown',
        timestamp: article.verified_at 
            ? new Date(article.verified_at).toLocaleString('en-US', { 
                month: 'short', 
                day: 'numeric', 
                hour: '2-digit', 
                minute: '2-digit' 
            })
            : 'N/A'
    }));

    return (
        <div className="history-table-section">
            <h3 className="text-lg font-semibold mb-4 text-white">Previously Verified Articles</h3>
            {loading ? (
                <div style={{ padding: '20px', textAlign: 'center', color: 'rgba(255,255,255,0.6)' }}>
                    Loading verified articles...
                </div>
            ) : tableData.length > 0 ? (
                <TableView columns={columns} data={tableData} />
            ) : (
                <div style={{ padding: '20px', textAlign: 'center', color: 'rgba(255,255,255,0.6)' }}>
                    No verified articles yet
                </div>
            )}
        </div>
    );
};

export default HistoryTable;
