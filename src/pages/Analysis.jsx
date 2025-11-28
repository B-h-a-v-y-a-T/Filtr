import React, { useState } from 'react';
import InputBoxAnalysis from '../components/analysis/InputBoxAnalysis';
import AnalysisProgressTracker from '../components/analysis/AnalysisProgressTracker';
import VerdictResultCard from '../components/analysis/VerdictResultCard';
import VeracityChain from '../components/analysis/VeracityChain';
import ExplanationBlock from '../components/analysis/ExplanationBlock';
import ReferenceSourcesList from '../components/analysis/ReferenceSourcesList';
import AnalysisUnderstandingGraph from '../components/analysis/AnalysisUnderstandingGraph';
import RecommendedActionStrip from '../components/analysis/RecommendedActionStrip';
import { analyzeClaimAPI, clearCacheAPI } from '../services/api';
import './Analysis.css';

const DEBUG = import.meta.env.MODE === 'development'; // Enable debug panel in development only

const Analysis = () => {
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [result, setResult] = useState(null);
    const [stage, setStage] = useState(0);
    const [error, setError] = useState(null);
    const [rawResponse, setRawResponse] = useState(null); // Debug: store raw API response
    const [clearingCache, setClearingCache] = useState(false);
    const [cacheMessage, setCacheMessage] = useState(null);

    const handleClearCache = async () => {
        setClearingCache(true);
        setCacheMessage(null);
        
        try {
            const response = await clearCacheAPI();
            setCacheMessage({
                type: 'success',
                text: response.message || `Cleared ${response.total_cleared || 0} cached results`
            });
            setTimeout(() => setCacheMessage(null), 5000);
        } catch (err) {
            console.error('Clear cache error:', err);
            setCacheMessage({
                type: 'error',
                text: 'Failed to clear cache. Please try again.'
            });
            setTimeout(() => setCacheMessage(null), 5000);
        } finally {
            setClearingCache(false);
        }
    };

    const handleAnalyze = async (text) => {
        setIsAnalyzing(true);
        setStage(1);
        setResult(null);
        setError(null);
        setRawResponse(null);

        try {
            // Stage 1: Analyzing claim
            setTimeout(() => setStage(2), 500);
            
            // Stage 2: Fetching sources
            setTimeout(() => setStage(3), 1500);
            
            // Call the real backend API
            const response = await analyzeClaimAPI(text);
            
            // Store raw response for debugging
            if (DEBUG) {
                setRawResponse(response);
                console.log('📊 Backend Response:', response);
                console.log('📊 Response Keys:', Object.keys(response));
                console.log('📊 Response Verdict:', response.verdict, response.final_verdict);
                console.log('📊 Response Confidence:', response.confidence);
            }
            
            // Stage 3: Verifying information
            setStage(4);
            
            // Check if API returned error
            if (response.status === 'error') {
                throw new Error(response.message || 'Analysis failed');
            }

            // Transform backend response to match UI expectations
            // Backend returns: verdict, final_verdict, confidence, explanation, sources, etc.
            const transformedResult = {
                verdict: response.final_verdict || response.verdict || 'Unverified / Needs More Evidence',
                confidence: response.confidence ?? 50,
                timestamp: 'Just now',
                claim: response.claim || text,
                claim_type: response.claim_type || 'unknown',
                explanation: Array.isArray(response.explanation) 
                    ? response.explanation.join('\n\n') 
                    : (response.explanation || 'No explanation available.'),
                chain: buildVeracityChain(response),
                sources: formatSources(response.sources || [], response.publisher || []),
                verification_path: response.verification_path || [],
                confidence_breakdown: response.confidence_breakdown || {}
            };

            if (DEBUG) {
                console.log('✅ Transformed Result:', transformedResult);
                console.log('✅ Verdict:', transformedResult.verdict);
                console.log('✅ Confidence:', transformedResult.confidence);
            }

            setResult(transformedResult);
            setIsAnalyzing(false);
        } catch (err) {
            console.error('Analysis error:', err);
            setError(err.message || 'Failed to analyze claim. Please try again.');
            setIsAnalyzing(false);
            setStage(0);
        }
    };

    // Build veracity chain from backend response
    const buildVeracityChain = (response) => {
        const chain = [];
        
        // Add verification path steps
        if (response.verification_path) {
            response.verification_path.forEach(step => {
                let description = '';
                if (step === 'google_fact_check') {
                    description = 'Checked Google Fact Check API for existing fact-checks';
                } else if (step === 'wikipedia') {
                    description = 'Verified claim against Wikipedia knowledge base';
                } else if (step === 'gnews') {
                    description = 'Searched news articles and credible sources';
                }
                
                if (description) {
                    chain.push({
                        source: step.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                        description: description
                    });
                }
            });
        }
        
        // Add final verification step
        chain.push({
            source: 'Final Verdict',
            description: `Confidence: ${response.confidence}% - ${response.verdict}`
        });
        
        return chain;
    };

    // Format sources from backend response
    // Backend returns sources as array of URL strings, and publisher as separate array
    const formatSources = (sources, publishers = []) => {
        if (!sources || sources.length === 0) return [];
        
        return sources.map((source, index) => {
            // Handle if source is a string (URL) or object
            if (typeof source === 'string') {
                return {
                    name: publishers[index] || extractDomain(source),
                    url: source,
                    published_at: ''
                };
            }
            // Handle if source is already an object
            return {
                name: source.publisher || source.name || 'Unknown Source',
                url: source.url || '#',
                published_at: source.published_at || ''
            };
        });
    };
    
    // Helper to extract domain name from URL
    const extractDomain = (url) => {
        try {
            const domain = new URL(url).hostname.replace('www.', '');
            return domain.charAt(0).toUpperCase() + domain.slice(1);
        } catch {
            return 'Unknown Source';
        }
    };

    return (
        <div className="analysis-page">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <div style={{ flex: 1 }}>
                    <InputBoxAnalysis onAnalyze={handleAnalyze} />
                </div>
                <button
                    onClick={handleClearCache}
                    disabled={clearingCache}
                    style={{
                        marginLeft: '15px',
                        padding: '12px 24px',
                        background: clearingCache ? '#666' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: clearingCache ? 'not-allowed' : 'pointer',
                        fontSize: '14px',
                        fontWeight: '600',
                        transition: 'all 0.3s ease',
                        boxShadow: clearingCache ? 'none' : '0 4px 15px rgba(102, 126, 234, 0.4)',
                        whiteSpace: 'nowrap'
                    }}
                    onMouseOver={(e) => {
                        if (!clearingCache) {
                            e.target.style.transform = 'translateY(-2px)';
                            e.target.style.boxShadow = '0 6px 20px rgba(102, 126, 234, 0.6)';
                        }
                    }}
                    onMouseOut={(e) => {
                        if (!clearingCache) {
                            e.target.style.transform = 'translateY(0)';
                            e.target.style.boxShadow = '0 4px 15px rgba(102, 126, 234, 0.4)';
                        }
                    }}
                >
                    {clearingCache ? '🔄 Clearing...' : '🗑️ Clear Cache'}
                </button>
            </div>

            {cacheMessage && (
                <div style={{
                    background: cacheMessage.type === 'success' ? '#10b981' : '#ef4444',
                    color: 'white',
                    padding: '12px 20px',
                    borderRadius: '8px',
                    marginBottom: '20px',
                    textAlign: 'center',
                    animation: 'fadeIn 0.3s ease'
                }}>
                    {cacheMessage.type === 'success' ? '✅' : '⚠️'} {cacheMessage.text}
                </div>
            )}

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

            {(isAnalyzing || result) && (
                <div className="analysis-results fade-in">
                    <AnalysisProgressTracker currentStage={stage} />

                    {result && (
                        <div className="results-grid">
                            <div className="results-main">
                                <VerdictResultCard result={result} />
                                <ExplanationBlock explanation={result.explanation} />
                                <RecommendedActionStrip 
                                    severity={result.confidence < 40 ? 'high' : result.confidence < 70 ? 'medium' : 'low'} 
                                />
                            </div>

                            <div className="results-sidebar">
                                <AnalysisUnderstandingGraph 
                                    confidence={result.confidence} 
                                    confidenceBreakdown={result.confidence_breakdown}
                                />
                                <VeracityChain chain={result.chain} />
                                <ReferenceSourcesList sources={result.sources} />
                            </div>
                        </div>
                    )}
                </div>
            )}

            <div style={{ textAlign: 'center', padding: '20px', fontSize: '12px', opacity: 0.6 }}>
                Made by OptiMl
            </div>

            {/* Debug Panel - Only shown in development mode */}
            {DEBUG && rawResponse && (
                <div style={{
                    background: '#1a1a2e',
                    border: '1px solid #4a4a6a',
                    borderRadius: '8px',
                    padding: '15px',
                    margin: '20px 0',
                    fontSize: '12px',
                    fontFamily: 'monospace',
                    maxHeight: '300px',
                    overflow: 'auto'
                }}>
                    <h4 style={{ color: '#00ff88', marginBottom: '10px' }}>🔍 Debug: Raw API Response</h4>
                    <div style={{ color: '#ffffff' }}>
                        <p><strong>Verdict:</strong> {rawResponse.verdict || rawResponse.final_verdict || 'N/A'}</p>
                        <p><strong>Confidence:</strong> {rawResponse.confidence}%</p>
                        <p><strong>Claim Type:</strong> {rawResponse.claim_type || 'N/A'}</p>
                        <p><strong>Status:</strong> {rawResponse.status || 'N/A'}</p>
                    </div>
                    <details style={{ marginTop: '10px' }}>
                        <summary style={{ cursor: 'pointer', color: '#888' }}>Full Response JSON</summary>
                        <pre style={{ color: '#aaa', whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
                            {JSON.stringify(rawResponse, null, 2)}
                        </pre>
                    </details>
                </div>
            )}
        </div>
    );
};

export default Analysis;
