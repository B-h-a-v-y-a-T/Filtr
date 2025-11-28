"""
NewsAPI integration as fallback when GNews quota is exceeded.
Provides same interface as GNews for seamless fallback.
"""
import os
import re
import requests
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load from multiple locations
load_dotenv()  # Root .env
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))  # backend/.env

NEWSAPI_URL = "https://newsapi.org/v2/everything"

# Common words to filter out from search queries (same as GNews)
STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "been", "be", "have", "has", "had",
    "do", "does", "did", "will", "would", "could", "should", "may", "might", "must",
    "shall", "can", "need", "dare", "ought", "used", "to", "of", "in", "for", "on",
    "with", "at", "by", "from", "as", "into", "through", "during", "before", "after",
    "above", "below", "between", "under", "again", "further", "then", "once", "here",
    "there", "when", "where", "why", "how", "all", "each", "few", "more", "most",
    "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than",
    "too", "very", "just", "also", "now", "reportedly", "allegedly", "said", "says",
    "according", "sources", "report", "reports", "claims", "claimed", "that", "this",
    "these", "those", "which", "who", "whom", "whose", "what", "and", "or", "but",
    "if", "because", "while", "although", "though", "unless", "until", "whether",
    "held", "meetings", "meeting", "met", "discussed", "discussions", "covered",
    "launched", "newly", "broader", "political", "situation", "sought", "brief",
    "originally", "scheduled", "unveil", "questioned", "involvement", "linked",
    "activities", "two", "about", "over", "their", "his", "her", "its", "our", "your"
}


def extract_search_query(claim: str, max_words: int = 5) -> str:
    """
    Extract key entities from a claim for NewsAPI search.
    Focuses on proper nouns, organizations, and key terms.
    
    Args:
        claim: The full claim text
        max_words: Maximum words in the search query
        
    Returns:
        Optimized search query string
    """
    # Clean the claim
    claim = claim.strip()
    
    # Extract words that look like proper nouns (capitalized words)
    words = claim.split()
    
    # Find proper nouns (capitalized words not at sentence start)
    proper_nouns = []
    key_terms = []
    
    for i, word in enumerate(words):
        # Clean the word
        clean_word = re.sub(r'[^\w\s]', '', word).strip()
        if not clean_word:
            continue
            
        lower_word = clean_word.lower()
        
        # Skip stop words
        if lower_word in STOP_WORDS:
            continue
        
        # Check if it's a proper noun (capitalized and not first word, or ALL CAPS)
        if word[0].isupper() and len(clean_word) > 1:
            # Could be a proper noun
            if clean_word.isupper() and len(clean_word) > 2:
                # ALL CAPS - likely an acronym or organization
                proper_nouns.append(clean_word)
            elif i > 0 or len(proper_nouns) == 0:
                # Capitalized word (not just sentence start)
                proper_nouns.append(clean_word)
        elif len(clean_word) > 4 and lower_word not in STOP_WORDS:
            # Potentially important keyword
            key_terms.append(clean_word)
    
    # Prioritize proper nouns, then key terms
    search_terms = []
    
    # Add proper nouns first (up to max_words - 1)
    for term in proper_nouns:
        if len(search_terms) < max_words - 1:
            if term not in search_terms:
                search_terms.append(term)
    
    # Fill remaining slots with key terms
    for term in key_terms:
        if len(search_terms) < max_words:
            if term not in search_terms and term.lower() not in [t.lower() for t in search_terms]:
                search_terms.append(term)
    
    # If we still don't have enough, add from original words
    if len(search_terms) < 2:
        for word in words:
            clean_word = re.sub(r'[^\w\s]', '', word).strip()
            if clean_word and clean_word.lower() not in STOP_WORDS and len(clean_word) > 3:
                if clean_word not in search_terms:
                    search_terms.append(clean_word)
                if len(search_terms) >= max_words:
                    break
    
    query = " ".join(search_terms[:max_words])
    logger.info(f"[NewsAPI] Extracted search query: '{query}' from claim: '{claim[:50]}...'")
    return query


def _get_newsapi_key() -> str:
    """Get NewsAPI key, reloading env if needed."""
    key = os.getenv("NEWSAPI_KEY", "")
    if not key:
        # Try reloading
        load_dotenv(override=True)
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"), override=True)
        key = os.getenv("NEWSAPI_KEY", "")
    return key


def search_newsapi(query: str, max_results: int = 10, language: str = "en") -> Dict[str, Any]:
    """
    Search for news articles using NewsAPI as fallback when GNews fails.
    Returns same structure as GNews for seamless integration.
    
    Args:
        query: Search query/keywords (can be a full claim)
        max_results: Maximum number of articles to return (default: 10)
        language: Language code (default: en)
        
    Returns:
        Dictionary with articles and metadata (same format as GNews)
    """
    api_key = _get_newsapi_key()
    
    if not api_key:
        logger.warning("[NewsAPI] NEWSAPI_KEY not configured")
        return {
            "has_articles": False,
            "articles": [],
            "summary": "NewsAPI key not configured"
        }
    
    # If query is long, extract key terms
    original_query = query
    if len(query.split()) > 6:
        query = extract_search_query(query, max_words=5)
    
    try:
        params = {
            "q": query,
            "apiKey": api_key,
            "language": language,
            "pageSize": max_results,
            "sortBy": "publishedAt"  # Most recent first
        }
        
        logger.info(f"[NewsAPI] Searching for: {query}")
        response = requests.get(NEWSAPI_URL, params=params, timeout=10)
        
        # Check for rate limit or auth errors
        if response.status_code == 429:
            logger.error("[NewsAPI] Rate limit exceeded (429)")
            return {
                "has_articles": False,
                "articles": [],
                "summary": "NewsAPI rate limit exceeded",
                "error_code": 429
            }
        elif response.status_code == 401:
            logger.error("[NewsAPI] Authentication failed (401)")
            return {
                "has_articles": False,
                "articles": [],
                "summary": "NewsAPI authentication failed",
                "error_code": 401
            }
        
        response.raise_for_status()
        data = response.json()
        
        # Check for API-level errors
        if data.get("status") != "ok":
            error_msg = data.get("message", "Unknown error")
            logger.error(f"[NewsAPI] API error: {error_msg}")
            return {
                "has_articles": False,
                "articles": [],
                "summary": f"NewsAPI error: {error_msg}"
            }
        
        result = _process_newsapi_response(data, original_query)
        
        # If no results with extracted query, try a simpler query
        if not result["has_articles"] and len(query.split()) > 2:
            simpler_query = " ".join(query.split()[:3])
            logger.info(f"[NewsAPI] Retrying with simpler query: {simpler_query}")
            params["q"] = simpler_query
            response = requests.get(NEWSAPI_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "ok":
                result = _process_newsapi_response(data, original_query)
        
        return result
        
    except requests.exceptions.Timeout:
        logger.error("[NewsAPI] Request timeout")
        return {
            "has_articles": False,
            "articles": [],
            "summary": "NewsAPI request timeout"
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"[NewsAPI] Request error: {e}")
        return {
            "has_articles": False,
            "articles": [],
            "summary": f"NewsAPI connection error: {str(e)}"
        }
    except Exception as e:
        logger.exception(f"[NewsAPI] Unexpected error: {e}")
        return {
            "has_articles": False,
            "articles": [],
            "summary": f"NewsAPI failed: {str(e)}"
        }


def _process_newsapi_response(data: Dict[str, Any], original_query: str) -> Dict[str, Any]:
    """
    Process NewsAPI response into same format as GNews for compatibility.
    
    NewsAPI format:
    {
        "status": "ok",
        "totalResults": 123,
        "articles": [
            {
                "source": {"id": "...", "name": "CNN"},
                "author": "...",
                "title": "...",
                "description": "...",
                "url": "...",
                "urlToImage": "...",
                "publishedAt": "2024-01-01T12:00:00Z",
                "content": "..."
            }
        ]
    }
    
    GNews format (target):
    {
        "has_articles": true,
        "articles": [
            {
                "title": "...",
                "description": "...",
                "url": "...",
                "source": "CNN",
                "published_at": "2024-01-01T12:00:00Z",
                "image": "..."
            }
        ],
        "summary": "...",
        "total_found": 123
    }
    """
    articles_data = data.get("articles", [])
    
    if not articles_data:
        return {
            "has_articles": False,
            "articles": [],
            "summary": "No news articles found for this query (NewsAPI)."
        }
    
    processed_articles: List[Dict[str, Any]] = []
    
    for article in articles_data:
        # Convert NewsAPI format to GNews format
        processed_articles.append({
            "title": article.get("title", ""),
            "description": article.get("description", ""),
            "url": article.get("url", ""),
            "source": article.get("source", {}).get("name", "Unknown"),
            "published_at": article.get("publishedAt", ""),
            "image": article.get("urlToImage", "")
        })
    
    summary = f"Found {len(processed_articles)} news article(s) via NewsAPI (fallback)."
    
    return {
        "has_articles": len(processed_articles) > 0,
        "articles": processed_articles,
        "summary": summary,
        "total_found": data.get("totalResults", len(processed_articles))
    }
