from typing import Any, Dict, Optional, List

import logging
import os
import requests
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from twilio.rest import Client as TwilioClient

from ..services.llm_agent import run_agent_workflow
from ..services.fact_checker import check_fact
from ..services.analysis_engine import verify_claim, clear_cache as clear_analysis_cache
from ..services.db import get_db, create_user, get_user_by_email, verify_login
from ..services.daily_summary import save_daily_summary, get_summaries
from ..services.reddit_scraper import scrape_news, format_scrape_results
from ..services.strategy_agent import (
    generate_strategy_output,
    chatbot_query,
    rewrite_message
)

load_dotenv()
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "")

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_VERIFY_SERVICE_SID = os.getenv("TWILIO_VERIFY_SERVICE_SID", "")

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class LoginRequest(BaseModel):
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")


class SignupRequest(BaseModel):
    name: str = Field(..., description="User's full name")
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")


class StrategyGenerateRequest(BaseModel):
    misinformation: str = Field(..., description="The misinformation text to analyze")


class StrategyChatbotRequest(BaseModel):
    user_message: str = Field(..., description="User's message to the chatbot")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Strategy context")


class RewriteMessageRequest(BaseModel):
    original_message: str = Field(..., description="The message to rewrite")
    target_tone: str = Field(..., description="Target tone (formal, empathetic, urgent, etc.)")
    additional_instructions: str = Field(default="", description="Additional formatting instructions")


class DailySummaryRequest(BaseModel):
    title: str = Field(..., description="Summary title")
    summary: str = Field(..., description="Summary content")
    source: str = Field(default="", description="Source of the summary")


class SendOTPRequest(BaseModel):
    phone: str = Field(..., description="Phone number with country code (e.g., +919136147222)")


class VerifyOTPRequest(BaseModel):
    phone: str = Field(..., description="Phone number with country code")
    code: str = Field(..., description="6-digit OTP code")


# ============================================================================
# AUTH ENDPOINTS
# ============================================================================

@router.post("/auth/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Login a user with email and password."""
    try:
        user = verify_login(db, request.email, request.password)
        if not user:
            return {
                "success": False,
                "error": "Invalid email or password"
            }
        
        return {
            "success": True,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        }
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        return {
            "success": False,
            "error": "Login failed. Please try again."
        }


@router.post("/auth/signup")
async def signup(request: SignupRequest, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Register a new user."""
    try:
        # Check if user already exists
        existing = get_user_by_email(db, request.email)
        if existing:
            return {
                "success": False,
                "error": "User already exists with this email"
            }
        
        # Create new user
        user = create_user(db, request.name, request.email, request.password)
        
        return {
            "success": True,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        }
    except Exception as e:
        logger.error(f"Signup failed: {str(e)}")
        return {
            "success": False,
            "error": "Registration failed. Please try again."
        }


@router.post("/auth/send-otp")
async def send_otp(request: SendOTPRequest) -> Dict[str, Any]:
    """Send OTP to a phone number using Twilio Verify."""
    try:
        if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_VERIFY_SERVICE_SID]):
            logger.error("Twilio credentials not configured")
            return {
                "success": False,
                "error": "SMS service not configured"
            }
        
        client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        verification = client.verify.v2.services(
            TWILIO_VERIFY_SERVICE_SID
        ).verifications.create(
            to=request.phone,
            channel="sms"
        )
        
        logger.info(f"OTP sent to {request.phone}, status: {verification.status}")
        
        return {
            "success": True,
            "message": "OTP sent successfully",
            "status": verification.status
        }
    except Exception as e:
        logger.error(f"Failed to send OTP: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to send OTP: {str(e)}"
        }


@router.post("/auth/verify-otp")
async def verify_otp(request: VerifyOTPRequest) -> Dict[str, Any]:
    """Verify OTP code using Twilio Verify."""
    try:
        if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_VERIFY_SERVICE_SID]):
            logger.error("Twilio credentials not configured")
            return {
                "success": False,
                "verified": False,
                "error": "SMS service not configured"
            }
        
        client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        verification_check = client.verify.v2.services(
            TWILIO_VERIFY_SERVICE_SID
        ).verification_checks.create(
            to=request.phone,
            code=request.code
        )
        
        logger.info(f"OTP verification for {request.phone}, status: {verification_check.status}")
        
        if verification_check.status == "approved":
            return {
                "success": True,
                "verified": True,
                "message": "Phone number verified successfully"
            }
        else:
            return {
                "success": False,
                "verified": False,
                "error": "Invalid OTP code"
            }
    except Exception as e:
        logger.error(f"Failed to verify OTP: {str(e)}")
        return {
            "success": False,
            "verified": False,
            "error": f"Failed to verify OTP: {str(e)}"
        }


# ============================================================================
# CACHE MANAGEMENT ENDPOINT
# ============================================================================

@router.post("/clear-cache")
async def clear_cache() -> Dict[str, Any]:
    """Clear the verification cache to force fresh analysis for all claims."""
    try:
        result = clear_analysis_cache()
        return {
            "status": "success",
            **result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to clear cache: {str(e)}",
            "memory_cleared": 0,
            "database_cleared": 0,
            "total_cleared": 0
        }


class QueryPayload(BaseModel):
    type: str = Field(..., description="Type of analysis: url|text|image|video")
    payload: Dict[str, Any] = Field(..., description="Payload to analyze")


@router.post("/query")
async def query(payload: QueryPayload) -> Dict[str, Any]:
    """Run the verification workflow and always return a structured response."""
    try:
        result = await run_agent_workflow(payload.type, payload.payload)
        return {"status": "completed", **result}
    except Exception as exc:
        # Ensure frontend never receives a blank; provide useful error info
        return {
            "status": "error",
            "summary": f"Analysis failed: {exc}",
            "verdict": "Uncertain",
            "evidence": [],
            "sources": [],
        }


# Fact Check endpoint
class FactCheckRequest(BaseModel):
    query: str = Field(..., description="Query to fact check")


@router.post("/fact-check")
async def fact_check(request: FactCheckRequest) -> Dict[str, Any]:
    """Check a fact using Google Fact Checker API."""
    try:
        result = check_fact(request.query)
        return {"status": "completed", "result": result}
    except Exception as exc:
        return {
            "status": "error",
            "message": f"Fact check failed: {exc}"
        }


# ============================================================================
# NEW ANALYSIS ENGINE ENDPOINT
# ============================================================================

class AnalyzeClaimRequest(BaseModel):
    claim: str = Field(..., description="The claim text to verify")


@router.post("/analyze")
async def analyze(request: AnalyzeClaimRequest) -> Dict[str, Any]:
    """
    Production-style claim verification endpoint.
    
    Pipeline:
    1. Google Fact Check API (primary)
    2. GNews fallback with credibility scoring
    3. Stance detection (Hugging Face zero-shot)
    4. Recency/freshness check
    5. Confidence aggregation & verdict
    
    Returns:
        {
            "claim": string,
            "verdict": "Likely False" | "Unverified / Needs More Evidence" | "Likely True" | "Verified True",
            "confidence": int (0-100),
            "explanation": [list of reasoning steps],
            "sources": [list of URLs],
            "publisher": [list],
            "published_dates": [list of ISO timestamps],
            "last_checked": ISO timestamp
        }
    """
    try:
        result = await verify_claim(request.claim)
        return {"status": "completed", **result}
    except Exception as exc:
        return {
            "status": "error",
            "claim": request.claim,
            "verdict": "Unverified / Needs More Evidence",
            "confidence": 0,
            "explanation": [f"Analysis failed: {str(exc)}"],
            "sources": [],
            "publisher": [],
            "published_dates": [],
            "last_checked": None
        }


# ============================================================================
# DAILY SUMMARY ENDPOINTS
# ============================================================================

@router.post("/daily-summary")
async def create_daily_summary(
    request: DailySummaryRequest,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Save a daily summary of claims/news."""
    try:
        result = save_daily_summary(db, request.title, request.summary, request.source)
        return {
            "status": "success",
            "data": {
                "id": result.id,
                "title": result.title,
                "summary": result.summary,
                "source": result.source,
                "created_at": result.created_at.isoformat() if result.created_at else None
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to save daily summary: {str(e)}"
        }


@router.get("/daily-summary")
async def fetch_daily_summaries(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Retrieve all daily summaries."""
    try:
        summaries = get_summaries(db)
        return {
            "status": "success",
            "data": [
                {
                    "id": s.id,
                    "title": s.title,
                    "summary": s.summary,
                    "source": s.source,
                    "created_at": s.created_at.isoformat() if s.created_at else None
                }
                for s in summaries[:limit]
            ]
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to fetch summaries: {str(e)}"
        }


# ============================================================================
# REDDIT NEWS SCRAPER ENDPOINT
# ============================================================================

@router.get("/scrape-reddit")
async def scrape_reddit_news(
    keyword: str = Query(default="", description="Search term for relevant news posts"),
    limit: int = Query(default=5, ge=1, le=20, description="Maximum posts to retrieve")
) -> Dict[str, Any]:
    """
    Scrape news posts from Reddit based on keyword.
    
    Args:
        keyword: Search term to find relevant news posts
        limit: Maximum number of posts to retrieve (default: 5)
        
    Returns:
        Dict with status and scraped posts data
    """
    try:
        results = scrape_news(keyword.strip() if keyword else "", limit)
        
        return {
            "status": "success",
            "keyword": keyword,
            "count": len(results),
            "data": results
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to scrape Reddit: {str(e)}",
            "data": []
        }


# ============================================================================
# NEWS SEARCH ENDPOINT (GNews API)
# ============================================================================

@router.get("/search-news")
async def search_news(
    keyword: str = Query(..., description="Search term for news articles"),
    limit: int = Query(default=10, ge=1, le=20, description="Maximum articles to retrieve")
) -> Dict[str, Any]:
    """
    Search for news articles using GNews API.
    
    Args:
        keyword: Search term for news articles
        limit: Maximum number of articles (default: 10)
        
    Returns:
        Dict with status and news articles
    """
    try:
        if not GNEWS_API_KEY:
            return {
                "status": "error",
                "message": "News API not configured",
                "data": []
            }
        
        if not keyword or not keyword.strip():
            return {
                "status": "error",
                "message": "Keyword is required",
                "data": []
            }
        
        # Call GNews API
        url = "https://gnews.io/api/v4/search"
        params = {
            "q": keyword.strip(),
            "lang": "en",
            "max": min(limit, 10),  # GNews free tier limit
            "apikey": GNEWS_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            return {
                "status": "error",
                "message": f"News API error: {response.status_code}",
                "data": []
            }
        
        data = response.json()
        articles = data.get("articles", [])
        
        # Format the results
        formatted = [
            {
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "url": article.get("url", ""),
                "source": article.get("source", {}).get("name", "Unknown"),
                "publishedAt": article.get("publishedAt", ""),
                "image": article.get("image", "")
            }
            for article in articles
        ]
        
        return {
            "status": "success",
            "keyword": keyword,
            "count": len(formatted),
            "data": formatted
        }
        
    except requests.Timeout:
        return {
            "status": "error",
            "message": "News API request timed out",
            "data": []
        }
    except Exception as e:
        logger.error(f"News search failed: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to search news: {str(e)}",
            "data": []
        }


# ============================================================================
# STRATEGY AGENT ENDPOINTS
# ============================================================================

@router.post("/strategy/generate")
async def generate_strategy(
    request: StrategyGenerateRequest
) -> Dict[str, Any]:
    """
    Generate comprehensive strategy for handling misinformation.
    
    Args:
        request: JSON body with misinformation text
        
    Returns:
        Strategy output including threat assessment, public message, and actions
    """
    try:
        if not request.misinformation or not request.misinformation.strip():
            return {
                "status": "error",
                "message": "Misinformation text is required"
            }
        
        result = await generate_strategy_output(request.misinformation.strip())
        return {
            "status": "success",
            **result
        }
    except Exception as e:
        logger.error(f"Strategy generation failed: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to generate strategy: {str(e)}"
        }


@router.post("/strategy/chatbot")
async def strategy_chatbot(
    request: StrategyChatbotRequest
) -> Dict[str, Any]:
    """
    Interactive chatbot for refining strategy responses.
    
    Args:
        request: JSON body with user_message and optional context
        
    Returns:
        Chatbot response with refined suggestions
    """
    try:
        if not request.user_message or not request.user_message.strip():
            return {
                "status": "error",
                "message": "User message is required"
            }
        
        result = await chatbot_query(request.user_message.strip(), request.context or {})
        return {
            "status": "success",
            **result
        }
    except Exception as e:
        logger.error(f"Strategy chatbot failed: {str(e)}")
        return {
            "status": "error",
            "message": f"Chatbot query failed: {str(e)}"
        }


@router.post("/strategy/rewrite")
async def rewrite_strategy_message(
    request: RewriteMessageRequest
) -> Dict[str, Any]:
    """
    Rewrite a message with a different tone/style.
    
    Args:
        request: JSON body with original_message, target_tone, and optional instructions
        
    Returns:
        Rewritten message variations
    """
    try:
        if not request.original_message or not request.original_message.strip():
            return {
                "status": "error",
                "message": "Original message is required"
            }
        
        if not request.target_tone or not request.target_tone.strip():
            return {
                "status": "error",
                "message": "Target tone is required"
            }
        
        result = await rewrite_message(
            request.original_message.strip(),
            request.target_tone.strip(),
            request.additional_instructions.strip() if request.additional_instructions else ""
        )
        return {
            "status": "success",
            **result
        }
    except Exception as e:
        logger.error(f"Message rewrite failed: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to rewrite message: {str(e)}"
        }

