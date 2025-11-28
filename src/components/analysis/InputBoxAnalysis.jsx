import React, { useState } from 'react';
import { Search, Link, FileText } from 'lucide-react';
import './InputBoxAnalysis.css';

const InputBoxAnalysis = ({ onAnalyze }) => {
    const [input, setInput] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (input.trim()) onAnalyze(input);
    };

    return (
        <div className="analysis-input-container glass-panel">
            <h3 className="input-title">Verify Content</h3>
            <form onSubmit={handleSubmit} className="input-form">
                <div className="input-wrapper">
                    <Search className="input-icon" size={20} />
                    <input
                        type="text"
                        placeholder="Paste URL or text snippet to analyze..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        className="analysis-input"
                    />
                </div>
                <div className="input-actions">
                    <button type="button" className="action-btn">
                        <Link size={16} />
                        <span>URL</span>
                    </button>
                    <button type="button" className="action-btn">
                        <FileText size={16} />
                        <span>Text</span>
                    </button>
                    <button type="submit" className="analyze-btn">
                        Analyze
                    </button>
                </div>
            </form>
        </div>
    );
};

export default InputBoxAnalysis;
