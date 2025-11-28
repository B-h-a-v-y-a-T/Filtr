import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import ChartView from '../global/ChartView';

const MonitoringConfidenceGraph = () => {
    const data = [
        { time: '00:00', confidence: 85 },
        { time: '04:00', confidence: 82 },
        { time: '08:00', confidence: 75 },
        { time: '12:00', confidence: 60 },
        { time: '16:00', confidence: 65 },
        { time: '20:00', confidence: 78 },
        { time: '23:59', confidence: 88 },
    ];

    return (
        <ChartView title="Real-time Confidence Index">
            <AreaChart data={data}>
                <defs>
                    <linearGradient id="colorConfidence" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                    </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="time" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} domain={[0, 100]} />
                <Tooltip
                    contentStyle={{ backgroundColor: '#1e293b', borderColor: 'rgba(255,255,255,0.1)', color: '#f8fafc' }}
                    itemStyle={{ color: '#06b6d4' }}
                />
                <Area
                    type="monotone"
                    dataKey="confidence"
                    stroke="#06b6d4"
                    fillOpacity={1}
                    fill="url(#colorConfidence)"
                />
            </AreaChart>
        </ChartView>
    );
};

export default MonitoringConfidenceGraph;
