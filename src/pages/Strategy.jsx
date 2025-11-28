import React, { useState } from 'react';
import FakeNewsInputBox from '../components/strategy/FakeNewsInputBox';
import CounterNarrativeGenerator from '../components/strategy/CounterNarrativeGenerator';
import SeriousnessMeter from '../components/strategy/SeriousnessMeter';
import RecommendedActionsPanel from '../components/strategy/RecommendedActionsPanel';
import CounterNarrativeTemplatesList from '../components/strategy/CounterNarrativeTemplatesList';
import ExportStrategyFileButton from '../components/strategy/ExportStrategyFileButton';
import ChatBotStrategyAssistant from '../components/strategy/ChatBotStrategyAssistant';
import { generateStrategyAPI } from '../services/api';
import './Strategy.css';

const Strategy = () => {
    const [misinformation, setMisinformation] = useState('');
    const [isGenerating, setIsGenerating] = useState(false);
    const [strategyResult, setStrategyResult] = useState(null);
    const [error, setError] = useState(null);

    const handleGenerate = async (input) => {
        if (!input || !input.trim()) {
            setError('Please enter misinformation text to analyze');
            return;
        }

        setIsGenerating(true);
        setError(null);
        setStrategyResult(null);
        setMisinformation(input);

        try {
            const result = await generateStrategyAPI(input);
            
            if (result.status === 'error') {
                throw new Error(result.message || 'Strategy generation failed');
            }

            setStrategyResult(result);
        } catch (err) {
            console.error('Strategy generation error:', err);
            setError(err.message || 'Failed to generate strategy. Please try again.');
        } finally {
            setIsGenerating(false);
        }
    };

    const handleExport = () => {
        if (!strategyResult || !strategyResult.export_package) {
            return;
        }

        const exportData = strategyResult.export_package;
        const threatAssessment = strategyResult.threat_assessment || {};
        
        // Create export-ready document (Module B format)
        const exportContent = `
---------------------------------------------------------------
📄 EXPORT PACKAGE
---------------------------------------------------------------

Summary of the misinformation:
${exportData.summary || misinformation}

Threat Level: ${exportData.threat_level || threatAssessment.classification || 'Unknown'} (Score: ${exportData.threat_score || threatAssessment.threat_score || 0}/100)

Fact-Check Verdict: ${exportData.fact_check_verdict || 'Unverified'} (Confidence: ${exportData.fact_check_confidence || 0}%)


---------------------------------------------------------------
FINAL OFFICIAL MESSAGE TO PUBLISH (COPY-PASTE READY)
---------------------------------------------------------------

Public Post:

» ${exportData.public_post?.headline || 'Clarification Statement'}

${exportData.public_post?.message || 'No message generated.'}


---------------------------------------------------------------
COMPANY ACTION PLAN
---------------------------------------------------------------

${exportData.action_plan?.map((action, idx) => `• ${action.action} (Priority: ${action.priority})`).join('\n') || 'No actions recommended.'}


Generated: ${exportData.generated_at ? new Date(exportData.generated_at).toLocaleString() : new Date().toLocaleString()}

---------------------------------------------------------------
Content suitable for PDF export.
---------------------------------------------------------------
        `.trim();

        // Create downloadable file
        const blob = new Blob([exportContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `misinformation-strategy-${Date.now()}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    const threatScore = strategyResult?.threat_assessment?.threat_score || 0;
    const threatClassification = strategyResult?.threat_assessment?.classification || 'Medium';
    const publicMessage = strategyResult?.public_message;
    const recommendedActions = strategyResult?.recommended_actions || [];

    return (
        <div className="strategy-page">
            <div className="strategy-grid">
                <div className="strategy-main">
                    <FakeNewsInputBox 
                        onGenerate={handleGenerate} 
                        isLoading={isGenerating}
                    />
                    
                    {error && (
                        <div className="error-message" style={{
                            background: '#ff4444',
                            color: 'white',
                            padding: '15px',
                            borderRadius: '8px',
                            margin: '20px 0',
                            textAlign: 'center'
                        }}>
                            ⚠️ {error}
                        </div>
                    )}

                    {isGenerating && (
                        <div className="loading-message" style={{
                            background: '#4a90e2',
                            color: 'white',
                            padding: '15px',
                            borderRadius: '8px',
                            margin: '20px 0',
                            textAlign: 'center'
                        }}>
                            🔄 Generating strategy... Analyzing threat level and preparing response...
                        </div>
                    )}

                    {publicMessage && (
                        <CounterNarrativeGenerator 
                            narrative={publicMessage.message}
                            headline={publicMessage.headline}
                            tone={publicMessage.tone}
                            strategyResult={strategyResult}
                        />
                    )}

                    <CounterNarrativeTemplatesList 
                        onSelect={(t) => {
                            if (publicMessage) {
                                // Template selection can be used for regeneration
                                console.log('Template selected:', t);
                            }
                        }} 
                    />
                </div>

                <div className="strategy-sidebar">
                    <SeriousnessMeter 
                        level={threatScore}
                        classification={threatClassification}
                        justification={strategyResult?.threat_assessment?.justification}
                    />
                    
                    {strategyResult ? (
                        <RecommendedActionsPanel actions={recommendedActions} />
                    ) : (
                        <RecommendedActionsPanel actions={[]} />
                    )}
                    
                    <ChatBotStrategyAssistant 
                        strategyResult={strategyResult}
                        misinformation={misinformation}
                    />
                    
                    {strategyResult && (
                        <ExportStrategyFileButton 
                            onExport={handleExport}
                            strategyResult={strategyResult}
                        />
                    )}
                </div>
            </div>

            <div style={{ textAlign: 'center', padding: '20px', fontSize: '12px', opacity: 0.6 }}>
                Made by OptiMl
            </div>
        </div>
    );
};

export default Strategy;
