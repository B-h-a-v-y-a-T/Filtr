import os
import requests
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

API_KEY = os.getenv("GOOGLE_FACT_CHECK_API_KEY", "")
API_URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"


def check_fact(query: str, language_code: str = "en") -> Dict[str, Any]:
    """Check facts using Google Fact Check API.
    
    Args:
        query: The claim to fact-check
        language_code: Language code (default: en)
        
    Returns:
        Structured fact-check results with claims and ratings
    """
    if not API_KEY:
        logger.warning("GOOGLE_FACT_CHECK_API_KEY not configured")
        return {
            "has_claims": False,
            "claims": [],
            "summary": "Google Fact Check API key not configured"
        }
    
    try:
        params = {
            "query": query,
            "languageCode": language_code,
            "key": API_KEY
        }
        
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return _process_fact_check_response(data, query)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Fact check API error: {e}")
        return {
            "has_claims": False,
            "claims": [],
            "summary": f"Could not verify claim via Fact Check API: {str(e)}"
        }
    except Exception as e:
        logger.exception(f"Unexpected fact check error: {e}")
        return {
            "has_claims": False,
            "claims": [],
            "summary": f"Fact check failed: {str(e)}"
        }


def _process_fact_check_response(data: Dict[str, Any], original_query: str) -> Dict[str, Any]:
    """Process Google Fact Check API response into a structured format."""
    claims = data.get("claims", [])
    
    if not claims:
        return {
            "has_claims": False,
            "claims": [],
            "summary": "No fact-check claims found for this query."
        }
    
    processed_claims: List[Dict[str, Any]] = []
    
    for claim_data in claims[:5]:  # Limit to top 5 claims
        claim_review = claim_data.get("claimReview", [])
        
        if claim_review:
            review = claim_review[0]  # Take first review
            
            processed_claims.append({
                "text": claim_data.get("text", ""),
                "claimant": claim_data.get("claimant", "Unknown"),
                "claim_date": claim_data.get("claimDate", ""),
                "publisher": review.get("publisher", {}).get("name", "Unknown"),
                "url": review.get("url", ""),
                "title": review.get("title", ""),
                "rating": review.get("textualRating", "Unrated"),
                "language": review.get("languageCode", "en")
            })
    
    # Generate summary
    if processed_claims:
        rating_counts = {}
        for claim in processed_claims:
            rating = claim["rating"]
            rating_counts[rating] = rating_counts.get(rating, 0) + 1
        
        summary = f"Found {len(processed_claims)} fact-check(s). "
        summary += ", ".join([f"{count} {rating}" for rating, count in rating_counts.items()])
    else:
        summary = "Claims found but no reviews available."
    
    return {
        "has_claims": len(processed_claims) > 0,
        "claims": processed_claims,
        "summary": summary,
        "total_found": len(claims)
    }
