import React from 'react';
import TableView from '../global/TableView';
import BadgeVerdict from '../global/BadgeVerdict';

const HistoryTable = () => {
    const columns = [
        { key: 'id', label: 'ID', width: '10%' },
        { key: 'content', label: 'Content Snippet', width: '40%' },
        { key: 'source', label: 'Source', width: '15%' },
        { key: 'verdict', label: 'Verdict', width: '15%', render: (val) => <BadgeVerdict verdict={val} /> },
        { key: 'timestamp', label: 'Time', width: '20%' },
    ];

    const data = [
        { id: '#1023', content: 'Election results delayed due to...', source: 'Twitter', verdict: 'False', timestamp: '2 mins ago' },
        { id: '#1022', content: 'New policy announced for...', source: 'News API', verdict: 'True', timestamp: '15 mins ago' },
        { id: '#1021', content: 'Viral video claims...', source: 'Facebook', verdict: 'Manipulated', timestamp: '1 hour ago' },
        { id: '#1020', content: 'Statement from official...', source: 'Official', verdict: 'Needs Context', timestamp: '2 hours ago' },
        { id: '#1019', content: 'Breaking news regarding...', source: 'Telegram', verdict: 'False', timestamp: '3 hours ago' },
    ];

    return (
        <div className="history-table-section">
            <h3 className="text-lg font-semibold mb-4 text-white">Recent Verifications</h3>
            <TableView columns={columns} data={data} />
        </div>
    );
};

export default HistoryTable;
