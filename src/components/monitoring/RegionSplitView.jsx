import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import ChartView from '../global/ChartView';

const RegionSplitView = () => {
    const data = [
        { name: 'North America', value: 400 },
        { name: 'Europe', value: 300 },
        { name: 'Asia', value: 300 },
        { name: 'Others', value: 200 },
    ];

    const COLORS = ['#a855f7', '#06b6d4', '#3b82f6', '#64748b'];

    return (
        <ChartView title="Regional Breakdown">
            <PieChart>
                <Pie
                    data={data}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    fill="#8884d8"
                    paddingAngle={5}
                    dataKey="value"
                >
                    {data.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                </Pie>
                <Tooltip
                    contentStyle={{ backgroundColor: '#1e293b', borderColor: 'rgba(255,255,255,0.1)', color: '#f8fafc' }}
                />
                <Legend />
            </PieChart>
        </ChartView>
    );
};

export default RegionSplitView;
