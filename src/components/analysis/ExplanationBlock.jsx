import React from 'react';
import { AlertCircle, CheckCircle2, Info, AlertTriangle, FileText, Search, Shield, Clock, Scale } from 'lucide-react';
import './ExplanationBlock.css';

const ExplanationBlock = ({ explanation }) => {
    // Handle both string and array formats
    let rawSteps = [];
    if (Array.isArray(explanation)) {
        rawSteps = explanation;
    } else if (typeof explanation === 'string') {
        // Split by arrows if it's a concatenated string
        rawSteps = explanation
            .split('→')
            .map(s => s.trim())
            .filter(s => s.length > 0);
    } else {
        rawSteps = [String(explanation)];
    }
    
    // Filter out technical noise
    const steps = rawSteps.filter(step => 
        !step.includes('capped') && 
        !step.includes('capping') &&
        !step.includes('ceiling') &&
        !step.includes('boost') &&
        !step.includes('%') &&
        !step.includes('provider') &&
        !step.includes('Provider') &&
        !step.includes('GNEWS') &&
        !step.includes('NEWSAPI') &&
        !step.includes('Using') &&
        !step.includes('using') &&
        step.trim() !== '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
    ).map(step => 
        // Clean up remaining arrows and symbols
        step.replace(/^→\s*/, '')
            .replace(/✓\s*/g, '')
            .replace(/\s*→\s*/g, '. ')
            .trim()
    );

    // Categorize steps into sections
    const categorizeStep = (step) => {
        const lower = step.toLowerCase();
        
        if (lower.includes('classified as')) return 'classification';
        if (lower.includes('wikipedia') || lower.includes('fact-check') || 
            lower.includes('cross-referencing') || lower.includes('consulting')) return 'strategy';
        if (lower.includes('found') && lower.includes('article')) return 'evidence';
        if (lower.includes('found') && lower.includes('news')) return 'evidence';
        if (lower.includes('no news') || lower.includes('no existing')) return 'evidence';
        if (lower.includes('credible') || lower.includes('established') || 
            lower.includes('national') || lower.includes('independent') ||
            lower.includes('assessed')) return 'credibility';
        if (lower.includes('24 hours') || lower.includes('48 hours') || 
            lower.includes('breaking') || lower.includes('recent') ||
            lower.includes('week') || lower.includes('month')) return 'time';
        if (lower.includes('verdict') || lower.includes('corroboration') ||
            lower.includes('evidence suggests') || lower.includes('insufficient evidence')) return 'verdict';
        
        return 'other';
    };

    const sections = {
        classification: { title: 'Claim Type', icon: FileText, steps: [] },
        strategy: { title: 'Verification Strategy', icon: Search, steps: [] },
        evidence: { title: 'Evidence Found', icon: Shield, steps: [] },
        credibility: { title: 'Source Quality', icon: CheckCircle2, steps: [] },
        time: { title: 'Time Sensitivity', icon: Clock, steps: [] },
        verdict: { title: 'Final Reasoning', icon: Scale, steps: [] }
    };

    // Categorize each step
    steps.forEach(step => {
        const category = categorizeStep(step);
        if (category !== 'other' && sections[category]) {
            sections[category].steps.push(step);
        }
    });

    // Only render sections that have content
    const activeSections = Object.entries(sections).filter(([, section]) => section.steps.length > 0);

    return (
        <div className="explanation-block glass-panel">
            <div className="explanation-header">
                <AlertCircle size={20} className="text-warning" />
                <h3>How We Verified This</h3>
            </div>
            
            <div className="explanation-sections">
                {activeSections.map(([key, section]) => {
                    const IconComponent = section.icon;
                    return (
                        <div key={key} className="explanation-section">
                            <div className="section-header">
                                <IconComponent size={18} className="section-icon" />
                                <h4>{section.title}</h4>
                            </div>
                            <ul className="section-steps">
                                {section.steps.map((step, index) => (
                                    <li key={index}>{step}</li>
                                ))}
                            </ul>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default ExplanationBlock;
