import React from 'react';
import { Check, Loader2 } from 'lucide-react';
import './AnalysisProgressTracker.css';

const AnalysisProgressTracker = ({ currentStage }) => {
    const stages = [
        { id: 1, label: 'Extracting' },
        { id: 2, label: 'Classifying' },
        { id: 3, label: 'Fact-checking' },
        { id: 4, label: 'Finalizing' },
    ];

    return (
        <div className="progress-tracker glass-panel">
            {stages.map((stage, index) => {
                const isCompleted = stage.id < currentStage;
                const isCurrent = stage.id === currentStage;

                return (
                    <div key={stage.id} className={`progress-step ${isCompleted ? 'completed' : ''} ${isCurrent ? 'current' : ''}`}>
                        <div className="step-indicator">
                            {isCompleted ? <Check size={16} /> : isCurrent ? <Loader2 size={16} className="animate-spin" /> : stage.id}
                        </div>
                        <span className="step-label">{stage.label}</span>
                        {index < stages.length - 1 && <div className="step-line"></div>}
                    </div>
                );
            })}
        </div>
    );
};

export default AnalysisProgressTracker;
