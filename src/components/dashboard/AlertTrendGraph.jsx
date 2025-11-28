import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import ChartView from '../global/ChartView';

const AlertTrendGraph = () => {
    const data = [
        { time: '00:00', alerts: 4 },
        { time: '04:00', alerts: 7 },
        { time: '08:00', alerts: 15 },
        { time: '12:00', alerts: 23 },
        { time: '16:00', alerts: 18 },
        { time: '20:00', alerts: 10 },
        { time: '23:59', alerts: 6 },
    ];

    return (
        <ChartView title="Misinformation Alerts (24h)">
            <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="time" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip
                    contentStyle={{ backgroundColor: '#1e293b', borderColor: 'rgba(255,255,255,0.1)', color: '#f8fafc' }}
                    itemStyle={{ color: '#a855f7' }}
                />
                <Line
                    type="monotone"
                    dataKey="alerts"
                    stroke="#a855f7"
                    strokeWidth={3}
                    dot={{ fill: '#a855f7', strokeWidth: 2 }}
                    activeDot={{ r: 8 }}
                />
            </LineChart>
        </ChartView>
    );
};

export default AlertTrendGraph;
