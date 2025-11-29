import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import ChartView from '../global/ChartView';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1';

const RegionSplitView = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);

    const COLORS = ['#a855f7', '#06b6d4', '#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#64748b'];

    const fetchSourceDistribution = async () => {
        try {
            // Fetch verified articles to analyze source distribution
            const response = await fetch(`${API_BASE_URL}/watcher-verified`);
            if (!response.ok) throw new Error('Failed to fetch data');
            
            const result = await response.json();
            
            if (result.verified_articles && result.verified_articles.length > 0) {
                // Count articles by source
                const sourceCounts = {};
                result.verified_articles.forEach(article => {
                    const source = article.source || 'Unknown';
                    sourceCounts[source] = (sourceCounts[source] || 0) + 1;
                });
                
                // Convert to array format for pie chart
                const chartData = Object.entries(sourceCounts)
                    .map(([name, value]) => ({ name, value }))
                    .sort((a, b) => b.value - a.value)
                    .slice(0, 6); // Top 6 sources
                
                // If more than 6 sources, group the rest as "Others"
                const topSources = Object.entries(sourceCounts)
                    .sort((a, b) => b[1] - a[1]);
                
                if (topSources.length > 6) {
                    const othersCount = topSources.slice(6).reduce((sum, [, count]) => sum + count, 0);
                    if (othersCount > 0) {
                        chartData.push({ name: 'Others', value: othersCount });
                    }
                }
                
                setData(chartData.length > 0 ? chartData : [{ name: 'No Data', value: 1 }]);
            } else {
                // No data - show placeholder
                setData([
                    { name: 'Awaiting Data', value: 1 }
                ]);
            }
        } catch (err) {
            console.error('Error fetching source distribution:', err);
            // Fallback data
            setData([
                { name: 'News Outlets', value: 40 },
                { name: 'Social Media', value: 30 },
                { name: 'Official Sources', value: 20 },
                { name: 'Others', value: 10 }
            ]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchSourceDistribution();
        // Refresh every 5 minutes
        const interval = setInterval(fetchSourceDistribution, 300000);
        return () => clearInterval(interval);
    }, []);

    return (
        <ChartView title="Source Distribution">
            {loading ? (
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '200px', color: '#94a3b8' }}>
                    Loading source data...
                </div>
            ) : (
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
                        label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                        labelLine={false}
                    >
                        {data.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                    </Pie>
                    <Tooltip
                        contentStyle={{ backgroundColor: '#1e293b', borderColor: 'rgba(255,255,255,0.1)', color: '#f8fafc' }}
                        formatter={(value, name) => [`${value} articles`, name]}
                    />
                    <Legend 
                        wrapperStyle={{ fontSize: '12px' }}
                        formatter={(value) => <span style={{ color: '#94a3b8' }}>{value}</span>}
                    />
                </PieChart>
            )}
        </ChartView>
    );
};

export default RegionSplitView;
