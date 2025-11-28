// API Service for Filtr Backend

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1';
const DEBUG = import.meta.env.MODE === 'development'; // Only log in development

/**
 * Analyze a claim using the backend analysis engine
 * @param {string} claim - The claim text to analyze
 * @returns {Promise<Object>} Analysis result
 */
export const analyzeClaimAPI = async (claim) => {
    try {
        if (DEBUG) {
            console.log('🔵 API Call - URL:', `${API_BASE_URL}/analyze`);
            console.log('🔵 API Call - Claim:', claim);
        }
        
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ claim }),
        });

        if (DEBUG) console.log('🔵 API Response Status:', response.status);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        if (DEBUG) console.log('🔵 API Response Data:', data);
        return data;
    } catch (error) {
        console.error('❌ API Error:', error);
        throw error;
    }
};

/**
 * Fact check a query using Google Fact Check API
 * @param {string} query - The query to fact check
 * @returns {Promise<Object>} Fact check result
 */
export const factCheckAPI = async (query) => {
    try {
        const response = await fetch(`${API_BASE_URL}/fact-check`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
};

/**
 * Run agent workflow for complex analysis
 * @param {string} type - Type of analysis (url|text|image|video)
 * @param {Object} payload - Payload to analyze
 * @returns {Promise<Object>} Analysis result
 */
export const queryAPI = async (type, payload) => {
    try {
        const response = await fetch(`${API_BASE_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ type, payload }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
};

/**
 * Check backend health
 * @returns {Promise<Object>} Health status
 */
export const healthCheckAPI = async () => {
    try {
        const response = await fetch('http://127.0.0.1:8000/health');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Health Check Error:', error);
        throw error;
    }
};

/**
 * Clear the verification cache
 * @returns {Promise<Object>} Cache clearing result
 */
export const clearCacheAPI = async () => {
    try {
        if (DEBUG) {
            console.log('🔵 API Call - Clear Cache:', `${API_BASE_URL}/clear-cache`);
        }
        
        const response = await fetch(`${API_BASE_URL}/clear-cache`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (DEBUG) console.log('🔵 Clear Cache Response Status:', response.status);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        if (DEBUG) console.log('🔵 Clear Cache Response Data:', data);
        return data;
    } catch (error) {
        console.error('❌ Clear Cache Error:', error);
        throw error;
    }
};

/**
 * Generate strategy for misinformation
 * @param {string} misinformation - The misinformation text to analyze
 * @returns {Promise<Object>} Strategy generation result
 */
export const generateStrategyAPI = async (misinformation) => {
    try {
        if (DEBUG) {
            console.log('🔵 API Call - Generate Strategy:', `${API_BASE_URL}/strategy/generate`);
        }
        
        const response = await fetch(`${API_BASE_URL}/strategy/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ misinformation }),
        });

        if (DEBUG) console.log('🔵 Strategy Response Status:', response.status);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        if (DEBUG) console.log('🔵 Strategy Response Data:', data);
        return data;
    } catch (error) {
        console.error('❌ Strategy API Error:', error);
        throw error;
    }
};

/**
 * Query strategy chatbot
 * @param {string} userMessage - The user's question
 * @param {string} context - The current strategy context
 * @returns {Promise<Object>} Chatbot response
 */
export const strategyChatbotAPI = async (userMessage, context) => {
    try {
        if (DEBUG) {
            console.log('🔵 API Call - Strategy Chatbot:', `${API_BASE_URL}/strategy/chatbot`);
        }
        
        const response = await fetch(`${API_BASE_URL}/strategy/chatbot`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_message: userMessage, context }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('❌ Chatbot API Error:', error);
        throw error;
    }
};

/**
 * Rewrite message with different tone
 * @param {string} message - The original message
 * @param {string} tone - The desired tone (formal|casual|urgent|empathetic)
 * @param {string} additionalInstructions - Additional formatting instructions (e.g., "twitter format", "press release")
 * @returns {Promise<Object>} Rewritten message
 */
export const rewriteMessageAPI = async (message, tone, additionalInstructions = '') => {
    try {
        const response = await fetch(`${API_BASE_URL}/strategy/rewrite`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                original_message: message, 
                target_tone: tone,
                additional_instructions: additionalInstructions
            }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('❌ Rewrite API Error:', error);
        throw error;
    }
};

/**
 * Scrape Reddit news
 * @param {string} keyword - Search keyword (optional)
 * @param {number} limit - Number of posts per subreddit (default 5)
 * @returns {Promise<Object>} Reddit scraping results
 */
export const scrapeRedditAPI = async (keyword = '', limit = 5) => {
    try {
        const params = new URLSearchParams();
        if (keyword) params.append('keyword', keyword);
        params.append('limit', limit);
        
        const response = await fetch(`${API_BASE_URL}/scrape-reddit?${params.toString()}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('❌ Reddit Scraper API Error:', error);
        throw error;
    }
};

/**
 * Search news articles using GNews API
 * @param {string} keyword - Search keyword
 * @param {number} limit - Number of articles (default 10)
 * @returns {Promise<Object>} News search results
 */
export const searchNewsAPI = async (keyword, limit = 10) => {
    try {
        const params = new URLSearchParams();
        params.append('keyword', keyword);
        params.append('limit', limit);
        
        const response = await fetch(`${API_BASE_URL}/search-news?${params.toString()}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('❌ News Search API Error:', error);
        throw error;
    }
};

/**
 * Save daily summary
 * @param {string} title - The summary title
 * @param {string} summary - The summary text
 * @param {string} source - The source of the summary
 * @returns {Promise<Object>} Save result
 */
export const saveDailySummaryAPI = async (title, summary, source) => {
    try {
        const response = await fetch(`${API_BASE_URL}/daily-summary`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title, summary, source }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('❌ Save Daily Summary Error:', error);
        throw error;
    }
};

/**
 * Get daily summaries
 * @param {number} limit - Number of summaries to retrieve
 * @returns {Promise<Object>} List of summaries
 */
export const getDailySummariesAPI = async (limit = 10) => {
    try {
        const response = await fetch(`${API_BASE_URL}/daily-summary?limit=${limit}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('❌ Get Daily Summaries Error:', error);
        throw error;
    }
};

/**
 * Send OTP to phone number for 2FA
 * @param {string} phone - Phone number with country code (e.g., +919136147222)
 * @returns {Promise<Object>} OTP send result
 */
export const sendOtpAPI = async (phone) => {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/send-otp`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ phone }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('❌ Send OTP Error:', error);
        throw error;
    }
};

/**
 * Verify OTP code for 2FA
 * @param {string} phone - Phone number with country code
 * @param {string} code - 6-digit OTP code
 * @returns {Promise<Object>} Verification result
 */
export const verifyOtpAPI = async (phone, code) => {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/verify-otp`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ phone, code }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('❌ Verify OTP Error:', error);
        throw error;
    }
};
