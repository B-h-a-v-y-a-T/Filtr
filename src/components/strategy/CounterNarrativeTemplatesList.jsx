import React from 'react';
import './CounterNarrativeTemplatesList.css';

const CounterNarrativeTemplatesList = ({ onSelect }) => {
    const templates = [
        { title: 'Fact Correction', desc: 'Direct rebuttal with evidence.' },
        { title: 'Empathetic Response', desc: 'Address concerns while correcting.' },
        { title: 'Official Statement', desc: 'Formal denial and clarification.' },
    ];

    return (
        <div className="templates-list glass-panel">
            <h3 className="templates-title">Strategy Templates</h3>
            <div className="templates-grid">
                {templates.map((t, i) => (
                    <div key={i} className="template-card" onClick={() => onSelect(t)}>
                        <h4>{t.title}</h4>
                        <p>{t.desc}</p>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default CounterNarrativeTemplatesList;
