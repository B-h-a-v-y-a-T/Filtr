import React, { useState } from 'react';
import { AlertOctagon } from 'lucide-react';
import './FakeNewsInputBox.css';

const FakeNewsInputBox = ({ onGenerate, isLoading = false }) => {
    const [input, setInput] = useState('');

    return (
        <div className="strategy-input-box glass-panel">
            <div className="strategy-header">
                <AlertOctagon className="text-danger" size={24} />
                <h3>Reported Misinformation</h3>
            </div>
            <textarea
                className="strategy-textarea"
                placeholder="Paste the misinformation narrative here to generate a counter-strategy..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                rows={6}
                disabled={isLoading}
            />
            <button
                className="generate-btn"
                onClick={() => input && onGenerate(input)}
                disabled={!input || isLoading}
            >
                {isLoading ? 'Generating Strategy...' : 'Generate Strategy'}
            </button>
        </div>
    );
};

export default FakeNewsInputBox;
