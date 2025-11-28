import React from 'react';
import { Link2 } from 'lucide-react';
import './VeracityChain.css';

const VeracityChain = ({ chain }) => {
    return (
        <div className="veracity-chain glass-panel">
            <h3 className="chain-title">Veracity Chain</h3>
            <div className="chain-steps">
                {chain.map((step, index) => (
                    <div key={index} className="chain-step">
                        <div className="step-dot"></div>
                        <div className="step-content">
                            <span className="step-source">{step.source}</span>
                            <p className="step-desc">{step.description}</p>
                        </div>
                        {index < chain.length - 1 && <div className="step-connector"></div>}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default VeracityChain;
