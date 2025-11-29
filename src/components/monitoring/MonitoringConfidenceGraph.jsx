import React, { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import ChartView from '../global/ChartView';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1';

const MonitoringConfidenceGraph = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [avgConfidence, setAvgConfidence] = useState(0);

    const fetchConfidenceData = async () => {
        try {
            // Fetch verified articles to build confidence timeline
            const response = await fetch(`${API_BASE_URL}/watcher-verified`);
            if (!response.ok) throw new Error('Failed to fetch data');
            
            const result = await response.json();
            
            if (result.verified_articles && result.verified_articles.length > 0) {
                // Group articles by hour and calculate average confidence
                const hourlyData = {};
                let totalConfidence = 0;
                let count = 0;
                
                result.verified_articles.forEach(article => {
                    const date = new Date(article.verified_at);
                    const hour = date.getHours();
                    const timeKey = `${hour.toString().padStart(2, '0')}:00`;
                    
                    if (!hourlyData[timeKey]) {
                        hourlyData[timeKey] = { total: 0, count: 0 };
                    }
                    hourlyData[timeKey].total += article.confidence || 50;
                    hourlyData[timeKey].count += 1;
                    totalConfidence += article.confidence || 50;
                    count += 1;
                });
                
                // Convert to array format for chart
                const chartData = Object.entries(hourlyData)
                    .map(([time, { total, count }]) => ({
                        time,
                        confidence: Math.round(total / count)
                    }))
                    .sort((a, b) => a.time.localeCompare(b.time));
                
                // If we have data, use it; otherwise show current confidence
                if (chartData.length > 0) {
                    setData(chartData);
                    setAvgConfidence(Math.round(totalConfidence / count));
                } else {
                    // Fallback: show current time with latest confidence
                    const now = new Date();
                    setData([{
                        time: `${now.getHours().toString().padStart(2, '0')}:00`,
                        confidence: result.verified_articles[0]?.confidence || 75
                    }]);
                }
            } else {
                // No data yet - show placeholder
                const now = new Date();
                setData([
                    { time: `${(now.getHours() - 2).toString().padStart(2, '0')}:00`, confidence: 70 },
                    { time: `${(now.getHours() - 1).toString().padStart(2, '0')}:00`, confidence: 75 },
                    { time: `${now.getHours().toString().padStart(2, '0')}:00`, confidence: 72 }
                ]);
                setAvgConfidence(72);
            }
        } catch (err) {
            console.error('Error fetching confidence data:', err);
            // Fallback data on error
            setData([
                { time: '08:00', confidence: 75 },
                { time: '12:00', confidence: 68 },
                { time: '16:00', confidence: 72 },
                { time: '20:00', confidence: 78 }
            ]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchConfidenceData();
        // Refresh every 5 minutes
        const interval = setInterval(fetchConfidenceData, 300000);
        return () => clearInterval(interval);
    }, []);

    return (
        <ChartView title={`Real-time Confidence Index ${avgConfidence > 0 ? `(Avg: ${avgConfidence}%)` : ''}`}>
            {loading ? (
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '200px', color: '#94a3b8' }}>
                    Loading confidence data...
                </div>
            ) : (
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
                        formatter={(value) => [`${value}%`, 'Confidence']}
                    />
                    <Area
                        type="monotone"
                        dataKey="confidence"
                        stroke="#06b6d4"
                        fillOpacity={1}
                        fill="url(#colorConfidence)"
                    />
                </AreaChart>
            )}
        </ChartView>
    );
};

export default MonitoringConfidenceGraph;
