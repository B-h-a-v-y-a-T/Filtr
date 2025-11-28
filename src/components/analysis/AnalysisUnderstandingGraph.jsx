import React from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';
import ChartView from '../global/ChartView';

const AnalysisUnderstandingGraph = ({ confidence = 50, confidenceBreakdown = {} }) => {
    // Calculate meaningful metrics based on confidence and breakdown
    // If breakdown values are available and non-zero, use them; otherwise derive from confidence
    const hasBreakdownData = confidenceBreakdown && 
        (confidenceBreakdown.authority > 0 || 
         confidenceBreakdown.wikipedia > 0 || 
         confidenceBreakdown.news_consensus > 0 ||
         confidenceBreakdown.stance_alignment > 0);
    
    // Base confidence for calculations
    const baseConf = confidence || 50;
    
    const data = hasBreakdownData ? [
        { subject: 'Factual', A: Math.max(confidenceBreakdown.authority || 0, baseConf * 0.7), fullMark: 100 },
        { subject: 'Emot', A: confidenceBreakdown.stance_alignment || baseConf * 0.5, fullMark: 100 },
        { subject: 'Bias', A: Math.max(0, 100 - (confidenceBreakdown.stance_alignment || baseConf * 0.5)), fullMark: 100 },
        { subject: 'Source', A: confidenceBreakdown.news_consensus || baseConf * 0.6, fullMark: 100 },
        { subject: 'Context', A: confidenceBreakdown.wikipedia || baseConf * 0.55, fullMark: 100 },
        { subject: 'Viral', A: Math.abs(confidenceBreakdown.recency_adjustment) || baseConf * 0.4, fullMark: 100 },
    ] : [
        // Derive meaningful chart values from the overall confidence score
        { subject: 'Factual', A: Math.min(100, baseConf * 1.1), fullMark: 100 },
        { subject: 'Emot', A: Math.min(100, baseConf * 0.7), fullMark: 100 },
        { subject: 'Bias', A: Math.max(0, 100 - baseConf * 0.6), fullMark: 100 },
        { subject: 'Source', A: Math.min(100, baseConf * 0.85), fullMark: 100 },
        { subject: 'Context', A: Math.min(100, baseConf * 0.75), fullMark: 100 },
        { subject: 'Viral', A: Math.min(100, baseConf * 0.5), fullMark: 100 },
    ];

    return (
        <ChartView title="Content Analysis Metrics" height={300}>
            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
                <PolarGrid stroke="rgba(255,255,255,0.1)" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                <Radar
                    name="Analysis"
                    dataKey="A"
                    stroke="#a855f7"
                    fill="#a855f7"
                    fillOpacity={0.6}
                />
            </RadarChart>
        </ChartView>
    );
};

export default AnalysisUnderstandingGraph;
