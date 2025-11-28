import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, Send, Loader } from 'lucide-react';
import { strategyChatbotAPI, rewriteMessageAPI } from '../../services/api';
import './ChatBotStrategyAssistant.css';

const ChatBotStrategyAssistant = ({ strategyResult, misinformation }) => {
    const [messages, setMessages] = useState([
        {
            role: 'bot',
            content: 'How can I help refine your response strategy today?'
        }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage = input.trim();
        setInput('');
        
        // Add user message
        const newMessages = [...messages, { role: 'user', content: userMessage }];
        setMessages(newMessages);
        setIsLoading(true);

        try {
            // Build context from strategy result
            const context = {};
            if (strategyResult) {
                if (strategyResult.public_message) {
                    context.current_message = strategyResult.public_message.message;
                }
                if (strategyResult.threat_assessment) {
                    context.threat_score = strategyResult.threat_assessment.threat_score;
                }
            }
            if (misinformation) {
                context.misinformation = misinformation;
            }

            // Check if user wants to rewrite message
            const rewriteKeywords = ['rewrite', 'tone', 'format', 'twitter', 'linkedin', 'press release'];
            const wantsRewrite = rewriteKeywords.some(keyword => userMessage.toLowerCase().includes(keyword));

            if (wantsRewrite && strategyResult?.public_message?.message) {
                // Extract tone and format from user message
                let tone = 'professional';
                let formatInstructions = '';

                if (userMessage.toLowerCase().includes('empathetic') || userMessage.toLowerCase().includes('empathy')) {
                    tone = 'empathetic';
                } else if (userMessage.toLowerCase().includes('urgent')) {
                    tone = 'urgent';
                } else if (userMessage.toLowerCase().includes('calm')) {
                    tone = 'calm';
                }

                if (userMessage.toLowerCase().includes('twitter') || userMessage.toLowerCase().includes('x ')) {
                    formatInstructions = 'Format for Twitter/X (280 characters max, engaging, concise)';
                } else if (userMessage.toLowerCase().includes('linkedin')) {
                    formatInstructions = 'Format for LinkedIn (professional, detailed, suitable for business audience)';
                } else if (userMessage.toLowerCase().includes('press release') || userMessage.toLowerCase().includes('pr ')) {
                    formatInstructions = 'Format as a formal press release with headline and structured body';
                }

                // Rewrite the message
                const rewriteResult = await rewriteMessageAPI(
                    strategyResult.public_message.message,
                    tone,
                    formatInstructions
                );

                if (rewriteResult.status === 'success') {
                    setMessages([
                        ...newMessages,
                        {
                            role: 'bot',
                            content: `Here's the rewritten message:\n\n**${rewriteResult.rewritten_message}**\n\n*Format: ${rewriteResult.format || 'general'}*\n*Tone: ${rewriteResult.tone || 'professional'}*`
                        }
                    ]);
                } else {
                    throw new Error(rewriteResult.message || 'Failed to rewrite message');
                }
            } else {
                // Regular chatbot query
                const response = await strategyChatbotAPI(userMessage, context);

                if (response.status === 'success') {
                    let botResponse = response.response;

                    // Add suggestions if available
                    if (response.suggestions && response.suggestions.length > 0) {
                        botResponse += '\n\n**Suggestions:**\n';
                        response.suggestions.forEach((suggestion, idx) => {
                            botResponse += `\n${idx + 1}. ${suggestion}`;
                        });
                    }

                    // Add action hint if available
                    if (response.action && response.action !== 'none') {
                        botResponse += `\n\n💡 *Tip: I can help you with ${response.action} tasks. Try asking me to rewrite your message or compare drafts.*`;
                    }

                    setMessages([
                        ...newMessages,
                        { role: 'bot', content: botResponse }
                    ]);
                } else {
                    throw new Error(response.message || response.response || 'Failed to get response');
                }
            }
        } catch (error) {
            console.error('Chatbot error:', error);
            setMessages([
                ...newMessages,
                {
                    role: 'bot',
                    content: `I apologize, but I encountered an error: ${error.message}. Please try again or rephrase your question.`
                }
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="strategy-chatbot glass-panel">
            <div className="chatbot-header">
                <MessageSquare size={20} />
                <h3>Strategy Assistant</h3>
            </div>
            
            <div className="chatbot-messages">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`message ${msg.role}`}>
                        <div className="message-content">
                            {msg.content.split('\n').map((line, lineIdx) => (
                                <React.Fragment key={lineIdx}>
                                    {line}
                                    {lineIdx < msg.content.split('\n').length - 1 && <br />}
                                </React.Fragment>
                            ))}
                        </div>
                    </div>
                ))}
                
                {isLoading && (
                    <div className="message bot">
                        <div className="message-content" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                            <Loader size={16} className="spinning" />
                            <span>Thinking...</span>
                        </div>
                    </div>
                )}
                
                <div ref={messagesEndRef} />
            </div>
            
            <div className="chatbot-input">
                <input
                    type="text"
                    placeholder={strategyResult ? "Ask for suggestions, rewrites, or improvements..." : "Ask me about misinformation strategy..."}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    disabled={isLoading}
                />
                <button
                    onClick={handleSend}
                    disabled={!input.trim() || isLoading}
                    className="chatbot-send-btn"
                >
                    <Send size={18} />
                </button>
            </div>

            {!strategyResult && (
                <div className="chatbot-hint" style={{
                    padding: '10px',
                    fontSize: '0.85em',
                    color: '#888',
                    textAlign: 'center',
                    borderTop: '1px solid rgba(255,255,255,0.1)',
                    marginTop: '10px'
                }}>
                    💡 Generate a strategy first to get contextual assistance
                </div>
            )}
        </div>
    );
};

export default ChatBotStrategyAssistant;
