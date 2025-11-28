import React from 'react';
import { Download } from 'lucide-react';
import './ExportStrategyFileButton.css';

const ExportStrategyFileButton = ({ onExport, strategyResult }) => {
    if (!strategyResult) {
        return null;
    }

    return (
        <button className="export-btn" onClick={onExport}>
            <Download size={18} />
            <span>Export Strategy Package</span>
        </button>
    );
};

export default ExportStrategyFileButton;
