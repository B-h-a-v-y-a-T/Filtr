import React from 'react';
import './BadgeVerdict.css';

const BadgeVerdict = ({ verdict }) => {
    const getVerdictConfig = (v) => {
        const lowerVerdict = v?.toLowerCase() || '';
        
        // Handle backend verdict types
        if (lowerVerdict.includes('verified true') || lowerVerdict === 'true') {
            return { color: 'success', label: v || 'True' };
        }
        if (lowerVerdict.includes('likely true')) {
            return { color: 'success', label: v || 'Likely True' };
        }
        if (lowerVerdict.includes('likely false') || lowerVerdict === 'false') {
            return { color: 'danger', label: v || 'False' };
        }
        if (lowerVerdict.includes('unverified') || lowerVerdict.includes('needs more evidence')) {
            return { color: 'warning', label: v || 'Unverified' };
        }
        if (lowerVerdict === 'manipulated') {
            return { color: 'warning', label: 'Manipulated' };
        }
        if (lowerVerdict === 'needs context') {
            return { color: 'info', label: 'Needs Context' };
        }
        
        return { color: 'default', label: v || 'Unknown' };
    };

    const config = getVerdictConfig(verdict);

    return (
        <span className={`badge-verdict badge-${config.color}`}>
            {config.label}
        </span>
    );
};

export default BadgeVerdict;
