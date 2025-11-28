"""
Filtr Analysis Engine - Production-style claim verification pipeline.

Pipeline:
1. Google Fact Check API (primary)
2. Wikipedia Knowledge Base (for scientific/educational facts)
3. GNews fallback with credibility scoring
4. Stance detection (Hugging Face zero-shot)
5. Recency/freshness check
6. Confidence aggregation & verdict

New Features:
- In-memory caching with claim normalization
- Confidence breakdown for UI transparency
- Sandbox mode for stress testing
- Wikipedia validation for established facts

Returns clean JSON structure for frontend consumption.
"""
import os
import logging
import re
import json
import string
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
import asyncio
import httpx

from dotenv import load_dotenv

from .fact_checker import check_fact
from .gnews_service import search_gnews
from .newsapi_service import search_newsapi

logger = logging.getLogger(__name__)

load_dotenv()
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# ============================================================================
# CACHING (IN-MEMORY + DATABASE FALLBACK)
# ============================================================================

_verification_cache: Dict[str, Dict[str, Any]] = {}
_use_database_cache = os.getenv("USE_DATABASE_CACHE", "true").lower() == "true"

def normalize_claim(claim: str) -> str:
    """
    Normalize claim for cache lookup.
    - Convert to lowercase
    - Remove extra whitespace
    - Strip leading/trailing punctuation
    """
    # Lowercase
    normalized = claim.lower()
    
    # Remove extra whitespace
    normalized = " ".join(normalized.split())
    
    # Strip leading/trailing punctuation
    normalized = normalized.strip(string.punctuation + string.whitespace)
    
    return normalized


def get_cached_result(claim: str) -> Optional[Dict[str, Any]]:
    """Check cache for existing verification result (in-memory first, then database)."""
    normalized = normalize_claim(claim)
    
    # Check in-memory cache first
    result = _verification_cache.get(normalized)
    if result:
        logger.info(f"Cache HIT (memory) for claim: {normalized[:50]}...")
        return result
    
    # Try database cache if enabled
    if _use_database_cache:
        try:
            from .db import get_db
            from ..models import ClaimHistory
            from datetime import timedelta
            
            db = get_db()
            # Look for recent claim (within last 12 hours)
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=12)
            recent_claim = db.query(ClaimHistory).filter(
                ClaimHistory.claim_text == normalized,
                ClaimHistory.created_at >= cutoff_time
            ).order_by(ClaimHistory.created_at.desc()).first()
            
            if recent_claim:
                # Parse the full analysis from sources_json
                sources_data = json.loads(recent_claim.sources_json) if recent_claim.sources_json else {}
                
                # Reconstruct complete result with all analysis details
                result = {
                    "claim": claim,
                    "verdict": recent_claim.verdict,
                    "confidence": int(recent_claim.confidence),
                    "sources": sources_data.get("sources", []),
                    "explanation": sources_data.get("explanation", []),
                    "confidence_breakdown": sources_data.get("confidence_breakdown", {}),
                    "claim_type": sources_data.get("claim_type", "unknown"),
                    "verification_path": sources_data.get("verification_path", []),
                    "publisher": sources_data.get("publisher", []),
                    "published_dates": sources_data.get("published_dates", []),
                    "verification_source": sources_data.get("verification_source", "cache"),
                    "last_checked": recent_claim.created_at.isoformat(),
                    "cached": True,
                    "cache_source": "database"
                }
                # Store in memory cache for faster subsequent access
                _verification_cache[normalized] = result
                logger.info(f"Cache HIT (database) for claim: {normalized[:50]}...")
                db.close()
                return result
            db.close()
        except Exception as e:
            logger.warning(f"Database cache lookup failed: {e}")
    
    logger.info(f"Cache MISS for claim: {normalized[:50]}...")
    return None


def cache_result(claim: str, result: Dict[str, Any]) -> None:
    """Store verification result in cache (memory + database)."""
    normalized = normalize_claim(claim)
    
    # Store in memory
    _verification_cache[normalized] = result
    logger.info(f"Cached result (memory) for claim: {normalized[:50]}... (cache size: {len(_verification_cache)})")
    
    # Store in database if enabled
    if _use_database_cache:
        try:
            from .db import get_db
            from ..models import ClaimHistory
            
            db = get_db()
            # Check if claim already exists in last 12 hours
            from datetime import timedelta
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=12)
            existing = db.query(ClaimHistory).filter(
                ClaimHistory.claim_text == normalized,
                ClaimHistory.created_at >= cutoff_time
            ).first()
            
            if not existing:
                # Store complete analysis details in sources_json
                complete_data = {
                    "sources": result.get("sources", []),
                    "explanation": result.get("explanation", []),
                    "confidence_breakdown": result.get("confidence_breakdown", {}),
                    "claim_type": result.get("claim_type", "unknown"),
                    "verification_path": result.get("verification_path", []),
                    "publisher": result.get("publisher", []),
                    "published_dates": result.get("published_dates", []),
                    "verification_source": result.get("verification_source", "analysis_engine")
                }
                
                # Create new cache entry (user_id = None for system cache)
                cache_entry = ClaimHistory(
                    user_id=None,  # System cache entries (no user)
                    claim_text=normalized,
                    verdict=result.get("verdict", "Uncertain"),
                    confidence=float(result.get("confidence", 0)),
                    sources_json=json.dumps(complete_data)
                )
                db.add(cache_entry)
                db.commit()
                logger.info(f"Cached result (database) for claim: {normalized[:50]}...")
            db.close()
        except Exception as e:
            logger.warning(f"Database cache storage failed: {e}")


def clear_cache() -> Dict[str, Any]:
    """
    Clear all cached results (both in-memory and database).
    
    Returns:
        Dict with cache clearing statistics
    """
    global _verification_cache
    
    memory_count = len(_verification_cache)
    database_count = 0
    
    # Clear in-memory cache
    _verification_cache.clear()
    logger.info(f"Cleared {memory_count} entries from memory cache")
    
    # Clear database cache if enabled
    if _use_database_cache:
        try:
            from .db import get_db
            from ..models import ClaimHistory
            
            db = get_db()
            # Delete all cache entries (user_id = None)
            database_count = db.query(ClaimHistory).filter(
                ClaimHistory.user_id == None
            ).delete()
            db.commit()
            db.close()
            logger.info(f"Cleared {database_count} entries from database cache")
        except Exception as e:
            logger.error(f"Database cache clearing failed: {e}")
    
    return {
        "success": True,
        "memory_cleared": memory_count,
        "database_cleared": database_count,
        "total_cleared": memory_count + database_count,
        "message": f"Successfully cleared {memory_count + database_count} cached results"
    }


# ============================================================================
# SANDBOX MODE - STRESS TESTING
# ============================================================================

SANDBOX_MODE = os.getenv("SANDBOX_MODE", "false").lower() == "true"

SANDBOX_TEST_CLAIMS = [
    # False medical claims
    {
        "claim": "Drinking bleach cures COVID-19",
        "expected_verdict": "Likely False",
        "category": "False Medical Claim"
    },
    {
        "claim": "5G towers cause coronavirus infections",
        "expected_verdict": "Likely False",
        "category": "False Medical Claim"
    },
    # Political rumors
    {
        "claim": "The 2020 US election was stolen through massive fraud",
        "expected_verdict": "Likely False",
        "category": "Political Rumor"
    },
    # Real news (should score high)
    {
        "claim": "NASA successfully launched the James Webb Space Telescope in 2021",
        "expected_verdict": "Verified True",
        "category": "Real News"
    },
    {
        "claim": "The COVID-19 pandemic began in late 2019",
        "expected_verdict": "Verified True",
        "category": "Real News"
    },
    # Ambiguous/viral messages
    {
        "claim": "Bill Gates wants to microchip everyone through vaccines",
        "expected_verdict": "Likely False",
        "category": "Conspiracy Theory"
    },
    {
        "claim": "Sharks are immune to cancer",
        "expected_verdict": "Likely False",
        "category": "Viral Misinformation"
    },
]


async def run_sandbox_tests():
    """
    Run stress tests on the verification engine.
    Internal use only - not exposed to frontend.
    """
    if not SANDBOX_MODE:
        logger.info("Sandbox mode disabled. Set SANDBOX_MODE=true to enable stress testing.")
        return
    
    logger.info("=" * 80)
    logger.info("SANDBOX MODE: Running stress tests on verification engine")
    logger.info("=" * 80)
    
    results = []
    
    for test in SANDBOX_TEST_CLAIMS:
        claim = test["claim"]
        expected = test["expected_verdict"]
        category = test["category"]
        
        logger.info(f"\n--- Testing: {category} ---")
        logger.info(f"Claim: {claim}")
        logger.info(f"Expected: {expected}")
        
        try:
            result = await analyze_claim(claim)
            
            actual_verdict = result.get("verdict", "Unknown")
            actual_confidence = result.get("confidence", 0)
            
            # Check if verdict matches expected category
            match = "✓ PASS" if _verdict_category_match(actual_verdict, expected) else "✗ FAIL"
            
            logger.info(f"Actual: {actual_verdict} ({actual_confidence}%) {match}")
            logger.info(f"Explanation:\n  " + "\n  ".join(result.get("explanation", [])))
            logger.info(f"Sources: {len(result.get('sources', []))} found")
            
            results.append({
                "claim": claim,
                "category": category,
                "expected": expected,
                "actual_verdict": actual_verdict,
                "actual_confidence": actual_confidence,
                "match": match,
                "sources_count": len(result.get("sources", []))
            })
            
        except Exception as e:
            logger.error(f"✗ FAIL - Exception: {e}")
            results.append({
                "claim": claim,
                "category": category,
                "expected": expected,
                "actual_verdict": "ERROR",
                "actual_confidence": 0,
                "match": "✗ FAIL",
                "error": str(e)
            })
    
    logger.info("\n" + "=" * 80)
    logger.info("SANDBOX TEST SUMMARY")
    logger.info("=" * 80)
    
    passed = sum(1 for r in results if r["match"] == "✓ PASS")
    failed = len(results) - passed
    
    logger.info(f"Total Tests: {len(results)}")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Success Rate: {(passed/len(results)*100):.1f}%")
    
    return results


def _verdict_category_match(actual: str, expected: str) -> bool:
    """Check if actual verdict is in the same category as expected."""
    true_verdicts = ["Verified True", "Likely True"]
    false_verdicts = ["Likely False"]
    uncertain_verdicts = ["Unverified / Needs More Evidence"]
    
    if expected in true_verdicts:
        return actual in true_verdicts
    elif expected in false_verdicts:
        return actual in false_verdicts
    elif expected in uncertain_verdicts:
        return actual in uncertain_verdicts
    
    return actual == expected


# ============================================================================
# WIKIPEDIA KNOWLEDGE BASE VALIDATION
# ============================================================================

def extract_subject_keywords(claim: str) -> List[str]:
    """
    Extract key subject terms from a claim for Wikipedia lookup.
    Returns a list of potential Wikipedia article titles.
    """
    # Common patterns for scientific/educational claims
    claim_lower = claim.lower()
    
    # Remove common question words and claim starters
    stopwords = {
        "the", "a", "an", "is", "are", "was", "were", "has", "have", "had",
        "does", "do", "did", "will", "would", "could", "should", "can",
        "that", "this", "these", "those", "it", "its", "and", "or", "but",
        "in", "on", "at", "to", "for", "of", "with", "by", "from", "as",
        "about", "into", "through", "during", "before", "after", "above",
        "below", "between", "under", "over", "again", "further", "then",
        "once", "here", "there", "when", "where", "why", "how", "all",
        "each", "few", "more", "most", "other", "some", "such", "no",
        "not", "only", "own", "same", "so", "than", "too", "very",
        "just", "also", "now", "around", "approximately", "roughly"
    }
    
    # Extract potential subjects
    subjects = []
    
    # Try to extract main nouns/entities
    words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9\-]+\b', claim)
    
    # Identify capitalized words (proper nouns)
    capitalized = [w for w in claim.split() if w and w[0].isupper() and len(w) > 2]
    
    # Add capitalized terms first (likely to be subjects)
    for term in capitalized:
        clean_term = re.sub(r'[^\w\s\-]', '', term)
        if clean_term.lower() not in stopwords and len(clean_term) > 2:
            subjects.append(clean_term)
    
    # Common scientific/educational subjects
    scientific_terms = {
        "earth": "Earth",
        "sun": "Sun",
        "moon": "Moon",
        "moon landing": "Moon_landing",
        "apollo": "Apollo_program",
        "mars": "Mars",
        "jupiter": "Jupiter",
        "water": "Properties_of_water",
        "boiling": "Boiling_point",
        "boiling point": "Boiling_point",
        "boils": "Boiling_point",
        "oxygen": "Oxygen",
        "carbon": "Carbon",
        "gravity": "Gravity",
        "photosynthesis": "Photosynthesis",
        "dna": "DNA",
        "evolution": "Evolution",
        "atom": "Atom",
        "molecule": "Molecule",
        "cell": "Cell_(biology)",
        "bacteria": "Bacteria",
        "virus": "Virus",
        "vaccine": "Vaccine",
        "light": "Light",
        "speed of light": "Speed_of_light",
        "electromagnetic": "Electromagnetic_radiation",
        "newton": "Isaac_Newton",
        "einstein": "Albert_Einstein",
        "tesla": "Nikola_Tesla",
        "climate change": "Climate_change",
        "global warming": "Global_warming",
        "covid": "COVID-19",
        "covid-19": "COVID-19",
        "coronavirus": "Coronavirus",
        "5g": "5G",
        # Historical events
        "holocaust": "The_Holocaust",
        "world war": "World_War_II",
    }
    
    # Check for scientific terms
    for term, wiki_title in scientific_terms.items():
        if term in claim_lower:
            subjects.insert(0, wiki_title)  # Priority
    
    # Add significant words that aren't stopwords
    for word in words:
        if word.lower() not in stopwords and len(word) > 3 and word not in subjects:
            subjects.append(word)
    
    return subjects[:5]  # Return top 5 candidates


async def query_wikipedia(subject: str) -> Optional[Dict[str, Any]]:
    """
    Query Wikipedia REST API for article summary.
    
    Args:
        subject: Wikipedia article title or search term
        
    Returns:
        Dict with title, description, extract, or None if not found
    """
    # URL encode the subject
    encoded_subject = subject.replace(" ", "_")
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_subject}"
    
    # Wikipedia API requires a proper User-Agent header
    headers = {
        "User-Agent": "FiltrFactChecker/1.0 (https://github.com/filtr; contact@filtr.app) httpx/0.24",
        "Accept": "application/json",
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers, follow_redirects=True)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "title": data.get("title", ""),
                    "description": data.get("description", ""),
                    "extract": data.get("extract", ""),
                    "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                    "type": data.get("type", ""),
                }
            elif response.status_code == 404:
                logger.debug(f"Wikipedia article not found: {subject}")
                return None
            else:
                logger.warning(f"Wikipedia API returned {response.status_code} for {subject}")
                return None
                
    except Exception as e:
        logger.error(f"Wikipedia query failed for {subject}: {e}")
        return None


def semantic_match_claim_to_wikipedia(claim: str, wiki_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check if Wikipedia content semantically confirms or refutes the claim.
    Uses keyword and phrase matching (no LLM).
    
    Returns:
        {
            "matches": bool,
            "confidence": 0-100,
            "match_type": "confirms" | "refutes" | "related" | "unrelated",
            "matched_content": str
        }
    """
    claim_lower = claim.lower()
    extract_lower = wiki_data.get("extract", "").lower()
    description_lower = wiki_data.get("description", "").lower()
    title_lower = wiki_data.get("title", "").lower()
    
    combined_wiki = f"{title_lower} {description_lower} {extract_lower}"
    
    # Define confirmation patterns for common claim types
    confirmation_patterns = [
        # Earth/planetary facts
        (r"earth.*(round|sphere|spherical|oblate)", r"(sphere|spherical|oblate|ball|round)", "earth_shape"),
        (r"earth.*(orbit|revolve|around).*sun", r"(orbit|revolution|around the sun|heliocentric)", "earth_orbit"),
        (r"sun.*(center|centre|middle).*solar", r"(center|centre|star.*solar)", "sun_center"),
        
        # Scientific facts
        (r"water.*boil.*(100|212|celsius|fahrenheit)", r"(100.*celsius|212.*fahrenheit|boiling point)", "water_boiling"),
        (r"speed.*light.*(\d+)", r"(299|300|speed of light|electromagnetic)", "speed_of_light"),
        (r"human.*(need|require).*oxygen", r"(oxygen|respiration|breathing)", "oxygen_need"),
        (r"plant.*(photosynthesis|convert.*light)", r"(photosynthesis|convert.*light)", "photosynthesis"),
        (r"gravity.*attract", r"(gravitational|attraction|newton)", "gravity"),
        
        # Historical facts
        (r"moon.*landing.*1969", r"(1969|apollo|lunar)", "moon_landing"),
        (r"world war.*(2|ii|two).*1945", r"(1945|world war|ended)", "ww2"),
        (r"covid.*19.*(2019|2020|pandemic)", r"(2019|2020|pandemic|coronavirus)", "covid"),
        
        # Debunked claims (for refutation)
        (r"earth.*(flat)", r"(sphere|oblate|spherical)", "earth_flat_debunk"),
        (r"vaccine.*(microchip|tracking)", r"(immunization|protection|immune)", "vaccine_microchip_debunk"),
        (r"5g.*(covid|coronavirus|virus)", r"(fifth.generation|mobile|wireless)", "5g_covid_debunk"),
    ]
    
    for claim_pattern, wiki_pattern, pattern_name in confirmation_patterns:
        claim_matches = re.search(claim_pattern, claim_lower)
        wiki_matches = re.search(wiki_pattern, combined_wiki)
        
        if claim_matches and wiki_matches:
            # Check if it's a debunk pattern
            if "debunk" in pattern_name:
                # The claim is false, Wikipedia confirms the truth
                return {
                    "matches": True,
                    "confidence": 90,
                    "match_type": "refutes",
                    "matched_content": wiki_data.get("extract", "")[:200],
                    "pattern": pattern_name
                }
            else:
                return {
                    "matches": True,
                    "confidence": 90,
                    "match_type": "confirms",
                    "matched_content": wiki_data.get("extract", "")[:200],
                    "pattern": pattern_name
                }
    
    # Generic keyword overlap check
    claim_words = set(re.findall(r'\b\w{4,}\b', claim_lower))
    wiki_words = set(re.findall(r'\b\w{4,}\b', combined_wiki))
    
    overlap = claim_words & wiki_words
    overlap_ratio = len(overlap) / max(len(claim_words), 1)
    
    if overlap_ratio > 0.5:
        return {
            "matches": True,
            "confidence": 70,
            "match_type": "related",
            "matched_content": wiki_data.get("extract", "")[:200],
            "overlap_words": list(overlap)[:10]
        }
    elif overlap_ratio > 0.25:
        return {
            "matches": True,
            "confidence": 55,
            "match_type": "related",
            "matched_content": wiki_data.get("extract", "")[:200],
            "overlap_words": list(overlap)[:10]
        }

    # Default: no meaningful match
    return {
        "matches": False,
        "confidence": 50,
        "match_type": "unrelated",
        "matched_content": ""
    }


def classify_claim_type(claim: str) -> str:
    """Classify claim into 'scientific', 'news', or 'unknown'.

    Uses keyword patterns and the existing scientific_terms mapping to decide.
    This is intentionally lightweight (no LLM).
    """
    c = claim.lower()

    # Strong indicators for scientific/educational claims
    scientific_indicators = [
        "physics", "chemistry", "biology", "geology", "geography",
        "astronomy", "photosynthesis", "dna", "atom", "molecule",
        "boil", "boiling", "celsius", "kelvin", "temperature",
        "speed of light", "gravity", "orbit", "revolv", "evolution",
        "vaccine", "infection", "oxygen", "cell",
        "moon", "sun", "earth", "planet", "april", "1969", "apollo"
    ]

    # Indicators for news/rumor/allegation
    news_indicators = [
        "election", "president", "senate", "congress", "arrest", "charged",
        "investigation", "resigns", "scandal", "claim says", "reported", "breaking",
        "alleges", "alleged", "leaked", "press", "cnn", "bbc", "politic",
        "tweet", "twitter", "facebook", "celebr", "company", "acquisition", "lawsuit"
    ]

    sci_score = sum(1 for k in scientific_indicators if k in c)
    news_score = sum(1 for k in news_indicators if k in c)

    # Also check for presence of known scientific terms (from mapping)
    try:
        # Inspect the scientific_terms dict defined earlier
        sci_terms = set(k for k in globals().get('scientific_terms', {}).keys())
        for term in sci_terms:
            if term in c:
                sci_score += 1
    except Exception:
        pass

    # Decision rules
    if sci_score >= 1 and sci_score >= news_score:
        return "scientific"
    if news_score >= 1 and news_score > sci_score:
        return "news"
    return "unknown"


def _is_fact_check_relevant(claim: str, fc_text: str, threshold: float = 0.3) -> bool:
    """Determine whether a Google Fact Check result is relevant to the input claim.

    Uses simple keyword overlap heuristics to avoid applying a fact-check for an
    unrelated or opposite claim (e.g., "Earth is round" vs "Earth is flat").
    """
    if not fc_text:
        return False
    c_words = set(re.findall(r"\b\w{4,}\b", claim.lower()))
    f_words = set(re.findall(r"\b\w{4,}\b", fc_text.lower()))
    if not c_words or not f_words:
        return False
    overlap = c_words & f_words
    overlap_ratio = len(overlap) / max(len(c_words), 1)
    return overlap_ratio >= threshold


async def verify_with_wikipedia(claim: str) -> Dict[str, Any]:
    """
    Verify a claim using Wikipedia as a knowledge base.
    
    Returns:
        {
            "verified": bool,
            "verdict": "Verified True" | "Likely False" | "Uncertain",
            "confidence": 0-100,
            "source": "Wikipedia",
            "article_title": str,
            "article_url": str,
            "explanation": str
        }
    """
    subjects = extract_subject_keywords(claim)
    
    if not subjects:
        return {
            "verified": False,
            "verdict": "Uncertain",
            "confidence": 50,
            "source": "Wikipedia",
            "article_title": "",
            "article_url": "",
            "explanation": "Could not extract subject for Wikipedia lookup"
        }
    
    best_match = None
    best_confidence = 0
    best_wiki_data = None
    
    for subject in subjects:
        wiki_data = await query_wikipedia(subject)
        
        if wiki_data and wiki_data.get("extract"):
            match_result = semantic_match_claim_to_wikipedia(claim, wiki_data)
            
            if match_result["matches"] and match_result["confidence"] > best_confidence:
                best_confidence = match_result["confidence"]
                best_match = match_result
                best_wiki_data = wiki_data
    
    if best_match and best_confidence >= 70:
        match_type = best_match.get("match_type", "related")
        
        if match_type == "confirms":
            return {
                "verified": True,
                "verdict": "Verified True",
                "confidence": min(95, best_confidence + 5),
                "source": "Wikipedia",
                "article_title": best_wiki_data.get("title", ""),
                "article_url": best_wiki_data.get("url", ""),
                "explanation": f"Wikipedia confirms: {best_match.get('matched_content', '')[:150]}..."
            }
        elif match_type == "refutes":
            return {
                "verified": True,
                "verdict": "Likely False",
                "confidence": min(95, best_confidence + 5),
                "source": "Wikipedia",
                "article_title": best_wiki_data.get("title", ""),
                "article_url": best_wiki_data.get("url", ""),
                "explanation": f"Wikipedia refutes: {best_match.get('matched_content', '')[:150]}..."
            }
        else:
            # Related but not definitively confirming/refuting
            return {
                "verified": False,
                "verdict": "Uncertain",
                "confidence": best_confidence,
                "source": "Wikipedia",
                "article_title": best_wiki_data.get("title", ""),
                "article_url": best_wiki_data.get("url", ""),
                "explanation": f"Wikipedia related content found but not definitive"
            }
    
    return {
        "verified": False,
        "verdict": "Uncertain",
        "confidence": 50,
        "source": "Wikipedia",
        "article_title": "",
        "article_url": "",
        "explanation": "No matching Wikipedia content found"
    }

# ============================================================================
# CREDIBLE SOURCE REGISTRY
# ============================================================================

CREDIBLE_SOURCES = {
    # Major News Agencies
    "reuters", "associated press", "ap news", "afp", "agence france-presse",
    # Major US News
    "bbc", "bbc news", "cnn", "nbc news", "abc news", "cbs news", "npr",
    "the new york times", "new york times", "washington post", "the washington post",
    "wall street journal", "the wall street journal", "usa today", "los angeles times",
    # International News
    "the guardian", "guardian", "the telegraph", "financial times", "the economist",
    "al jazeera", "dw", "deutsche welle", "france 24", "sky news",
    # Tech News
    "techcrunch", "wired", "ars technica", "the verge", "engadget",
    # Fact-Checkers
    "snopes", "politifact", "factcheck.org", "full fact", "lead stories",
    # Business News
    "bloomberg", "cnbc", "forbes", "business insider", "marketwatch",
}

LOW_CREDIBILITY_INDICATORS = {
    "daily mail", "the sun", "new york post", "infowars", "breitbart",
    "natural news", "worldnetdaily", "newsmax", "oann", "gateway pundit",
    "zero hedge", "epoch times", "sputnik", "rt.com", "russia today",
}

# ============================================================================
# RATING CONFIDENCE MAPPING
# ============================================================================

RATING_CONFIDENCE_MAP = {
    # True ratings
    "true": 85,
    "correct": 85,
    "accurate": 85,
    "verified": 90,
    "mostly true": 75,
    "mostly correct": 75,
    
    # False ratings
    "false": 15,
    "incorrect": 15,
    "pants on fire": 5,
    "fake": 10,
    "misleading": 25,
    "mostly false": 20,
    
    # Half/Mixed ratings
    "half true": 50,
    "mixture": 50,
    "mixed": 50,
    "partly true": 55,
    "partly false": 45,
    "unproven": 40,
    "outdated": 35,
    
    # Neutral/Unknown
    "unrated": 50,
    "unknown": 50,
}

# ============================================================================
# STANCE DETECTION (Hugging Face Zero-Shot)
# ============================================================================

_classifier = None
_classifier_loading = False
ENABLE_STANCE_DETECTION = os.getenv("ENABLE_STANCE_DETECTION", "false").lower() == "true"

def get_stance_classifier():
    """Lazy-load the zero-shot classifier to avoid slow startup."""
    global _classifier, _classifier_loading
    
    if not ENABLE_STANCE_DETECTION:
        return None
    
    if _classifier_loading:
        return None  # Prevent concurrent loads
        
    if _classifier is None:
        try:
            _classifier_loading = True
            logger.info("Loading stance classifier (this may take a moment)...")
            try:
                from transformers import pipeline
            except ImportError:
                logger.warning("transformers library not installed. Install with: pip install transformers torch")
                _classifier = "failed"
                _classifier_loading = False
                return None
            
            _classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=-1  # CPU; use 0 for GPU
            )
            logger.info("Stance classifier loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load stance classifier: {e}")
            _classifier = "failed"
        finally:
            _classifier_loading = False
    return _classifier if _classifier != "failed" else None


def classify_stance(claim: str, headline: str) -> Tuple[str, float]:
    """
    Classify whether headline SUPPORTS, REFUTES, or is UNRELATED to claim.
    
    Returns:
        Tuple of (stance, confidence) where stance is "SUPPORTS", "REFUTES", or "UNRELATED"
    """
    classifier = get_stance_classifier()
    
    if classifier is None:
        return ("UNRELATED", 0.5)
    
    try:
        hypothesis_template = f"This headline {{}} the claim: {claim}"
        candidate_labels = ["supports", "refutes", "is unrelated to"]
        
        result = classifier(
            headline,
            candidate_labels,
            hypothesis_template=hypothesis_template,
            multi_label=False
        )
        
        label = result["labels"][0]
        score = result["scores"][0]
        
        stance_map = {
            "supports": "SUPPORTS",
            "refutes": "REFUTES",
            "is unrelated to": "UNRELATED"
        }
        
        return (stance_map.get(label, "UNRELATED"), score)
        
    except Exception as e:
        logger.error(f"Stance classification error: {e}")
        return ("UNRELATED", 0.5)


# ============================================================================
# UNIFIED NEWS INTERFACE - GNews with NewsAPI Fallback
# ============================================================================

async def get_news_results(query: str, max_results: int = 10) -> Dict[str, Any]:
    """
    Unified news interface with automatic fallback.
    
    Flow:
    1. Try GNews (primary)
    2. If GNews fails (429, 401, 5xx, timeout, empty) → fallback to NewsAPI
    3. Return unified format in both cases
    
    Args:
        query: Search query/claim text
        max_results: Maximum articles to return
        
    Returns:
        Dict with unified format:
        {
            "has_articles": bool,
            "articles": [...],
            "summary": str,
            "total_found": int,
            "news_provider_used": "gnews" | "newsapi"
        }
    """
    logger.info(f"[UnifiedNews] Fetching news for query: {query[:100]}...")
    
    # Try GNews first (primary provider)
    try:
        gnews_result = await asyncio.to_thread(search_gnews, query[:200], max_results=max_results)
        
        # Check if GNews succeeded
        if gnews_result.get("has_articles") and len(gnews_result.get("articles", [])) > 0:
            gnews_result["news_provider_used"] = "gnews"
            logger.info(f"[UnifiedNews] ✓ GNews returned {len(gnews_result.get('articles', []))} articles")
            return gnews_result
        else:
            # GNews returned empty (might be quota/rate limit or no results)
            logger.warning(f"[UnifiedNews] GNews returned no articles: {gnews_result.get('summary', 'Unknown')}")
            # Fall through to NewsAPI
    
    except Exception as e:
        # GNews failed with exception (network error, timeout, etc.)
        logger.error(f"[UnifiedNews] GNews failed with exception: {e}")
        # Fall through to NewsAPI
    
    # Fallback to NewsAPI
    logger.info("[UnifiedNews] Falling back to NewsAPI...")
    try:
        newsapi_result = await asyncio.to_thread(search_newsapi, query[:200], max_results=max_results)
        
        # Check for NewsAPI errors
        if newsapi_result.get("error_code") in [429, 401]:
            logger.error(f"[UnifiedNews] NewsAPI also failed: {newsapi_result.get('summary')}")
            # Both providers failed
            return {
                "has_articles": False,
                "articles": [],
                "summary": "Both news providers temporarily unavailable",
                "total_found": 0,
                "news_provider_used": "none"
            }
        
        newsapi_result["news_provider_used"] = "newsapi"
        
        if newsapi_result.get("has_articles"):
            logger.info(f"[UnifiedNews] ✓ NewsAPI returned {len(newsapi_result.get('articles', []))} articles (fallback)")
        else:
            logger.warning(f"[UnifiedNews] NewsAPI returned no articles: {newsapi_result.get('summary')}")
        
        return newsapi_result
    
    except Exception as e:
        logger.error(f"[UnifiedNews] NewsAPI also failed with exception: {e}")
        # Both providers failed
        return {
            "has_articles": False,
            "articles": [],
            "summary": "Both news providers temporarily unavailable",
            "total_found": 0,
            "news_provider_used": "none"
        }


# ============================================================================
# PREMIUM NEWS BRANDS - For trust boost calculation
# ============================================================================

PREMIUM_NEWS_BRANDS = {
    # Tier 1: International news agencies & premium outlets (+10 points)
    "reuters", "associated press", "ap news", "afp", "agence france-presse",
    "bbc", "bbc news", "the guardian", "the new york times", "washington post",
    "wall street journal", "financial times", "the economist",
    
    # Tier 2: Major credible outlets (+5 points)
    "cnn", "nbc news", "abc news", "cbs news", "npr", "pbs",
    "usa today", "los angeles times", "the telegraph",
    "bloomberg", "cnbc", "al jazeera", "dw", "deutsche welle",
    
    # Indian premium outlets
    "the hindu", "indian express", "hindustan times", "ani", "pti"
}


def calculate_news_confidence(articles: List[Dict[str, Any]], claim: str) -> Dict[str, Any]:
    """
    Advanced NEWS confidence scoring with multi-source consensus rules.
    
    Journalism Consensus Rules:
    - 3+ independent sources reporting = 80-90% confidence (STRONG)
    - 2 independent sources = 75-80% confidence (MODERATE)  
    - 1 credible source = 65-70% confidence (WEAK)
    - Premium brand boost: +5% (major outlets), +10% (Reuters/BBC/ANI)
    - Recency boost: +5% if <24h old, +3% if <48h old
    - Agreement bonus: +5% if multiple sources use consistent language
    - Anti-inflation limiters:
      * -5% if sources are from same parent publisher
      * -10% if language contains uncertainty markers
      * Floor: 75% minimum for multi-source news
      * Ceiling: 90% maximum to prevent overconfidence
    
    Args:
        articles: List of news articles from GNews
        claim: The original claim text
        
    Returns:
        Dict with confidence, explanation, sources, publishers, dates
    """
    if not articles:
        return {
            "confidence": 50,
            "explanation": ["No news articles found"],
            "sources": [],
            "publishers": [],
            "published_dates": [],
            "news_consensus_score": 0
        }
    
    explanation = []
    sources = []
    publishers = []
    published_dates = []
    
    # Step 1: Count independent sources
    unique_publishers = set()
    premium_count = 0
    articles_by_publisher = {}
    recent_articles = []  # < 48 hours
    very_recent_articles = []  # < 24 hours
    
    now = datetime.now(timezone.utc)
    
    for article in articles[:15]:  # Limit to top 15
        publisher = article.get("source", "").lower().strip()
        url = article.get("url", "")
        pub_date_str = article.get("published_at", "")
        title = article.get("title", "")
        
        if not publisher or not url:
            continue
            
        # Track unique publishers
        unique_publishers.add(publisher)
        
        # Group by publisher to detect same-publisher duplication
        if publisher not in articles_by_publisher:
            articles_by_publisher[publisher] = []
        articles_by_publisher[publisher].append(article)
        
        # Check if premium brand
        is_premium = any(brand in publisher for brand in PREMIUM_NEWS_BRANDS)
        if is_premium:
            premium_count += 1
        
        # Track sources
        if url not in sources:
            sources.append(url)
        if publisher not in publishers:
            publishers.append(publisher)
        if pub_date_str:
            published_dates.append(pub_date_str)
            
            # Check recency
            try:
                if "T" in pub_date_str:
                    pub_date = datetime.fromisoformat(pub_date_str.replace("Z", "+00:00"))
                    age_hours = (now - pub_date).total_seconds() / 3600
                    
                    if age_hours <= 24:
                        very_recent_articles.append(article)
                    elif age_hours <= 48:
                        recent_articles.append(article)
            except Exception:
                pass
    
    source_count = len(unique_publishers)
    
    # Step 2: Base confidence from source count
    if source_count >= 3:
        base_confidence = 82  # Center of 80-85 range
        tier = "STRONG (3+ sources)"
        explanation.append(f"Multiple independent news outlets report this event.")
    elif source_count == 2:
        base_confidence = 77  # Center of 75-80 range
        tier = "MODERATE (2 sources)"
        explanation.append(f"Two independent sources cover this topic.")
    elif source_count == 1:
        base_confidence = 67  # Center of 65-70 range
        tier = "WEAK (1 source)"
        explanation.append(f"Only one source found for this claim.")
    else:
        return {
            "confidence": 50,
            "explanation": ["No sources found for verification."],
            "sources": sources,
            "publishers": publishers,
            "published_dates": published_dates,
            "news_consensus_score": 0
        }
    
    confidence = base_confidence
    
    # Step 3: Brand trust boost
    brand_boost = 0
    if premium_count > 0:
        # Check for Tier 1 premium (Reuters, BBC, ANI, etc.)
        tier1_brands = {"reuters", "bbc", "ani", "pti", "associated press", "ap news"}
        has_tier1 = any(any(t1 in pub for t1 in tier1_brands) for pub in publishers)
        
        if has_tier1:
            brand_boost = 10
            explanation.append("Includes nationally recognized news outlets.")
        else:
            brand_boost = 5
            explanation.append("Includes established news organizations.")
        
        confidence += brand_boost
    
    # Step 4: Recency boost
    recency_boost = 0
    if len(very_recent_articles) > 0:
        recency_boost = 5
        explanation.append("Breaking: Articles published within 24 hours.")
        confidence += 5
    elif len(recent_articles) > 0:
        recency_boost = 3
        explanation.append("Recent coverage (within 48 hours).")
        confidence += 3
    
    # Step 5: Agreement bonus (check if headlines are consistent)
    if source_count >= 2:
        # Simple heuristic: check if key claim words appear in multiple headlines
        claim_words = set(claim.lower().split())
        claim_words = {w for w in claim_words if len(w) > 4}  # Only significant words
        
        matching_count = 0
        for article in articles[:5]:
            title = article.get("title", "").lower()
            if any(word in title for word in claim_words):
                matching_count += 1
        
        if matching_count >= 2:
            agreement_bonus = 5
            confidence += 5
            explanation.append("Headlines align with key details of the claim.")
    
    # Step 6: Anti-inflation penalties
    # Penalty 1: Same publisher duplication
    same_publisher_penalty = 0
    max_articles_from_one = max(len(arts) for arts in articles_by_publisher.values())
    if max_articles_from_one >= 3 and source_count < 3:
        same_publisher_penalty = 5
        confidence -= 5
        explanation.append("Multiple articles from the same publisher (limited diversity).")
    
    # Penalty 2: Uncertainty language markers
    uncertainty_markers = [
        "allegedly", "reportedly", "claimed", "unconfirmed",
        "rumor", "speculation", "may have", "might have", "could be"
    ]
    
    uncertain_count = 0
    for article in articles[:5]:
        title = article.get("title", "").lower()
        desc = article.get("description", "").lower()
        combined = title + " " + desc
        
        if any(marker in combined for marker in uncertainty_markers):
            uncertain_count += 1
    
    if uncertain_count >= 2:
        uncertainty_penalty = 10
        confidence -= 10
        explanation.append("Coverage includes speculative or unconfirmed language.")
    
    # Step 7: Enforce floor and ceiling for multi-source news
    if source_count >= 2:
        if confidence < 75:
            confidence = 75
        elif confidence > 90:
            confidence = 90
    elif source_count == 1:
        # Single source: cap at 70%
        if confidence > 70:
            confidence = 70
    
    # Step 8: Final clamp
    confidence = max(0, min(100, confidence))
    
    news_consensus_score = confidence - base_confidence
    
    return {
        "confidence": confidence,
        "explanation": explanation,
        "sources": sources,
        "publishers": publishers,
        "published_dates": published_dates,
        "news_consensus_score": news_consensus_score
    }


# ============================================================================
# CONFIDENCE CEILINGS BY CLAIM TYPE
# ============================================================================

MAX_CONFIDENCE_SCIENTIFIC = 99  # Wikipedia verified facts
MAX_CONFIDENCE_MISINFORMATION = 95  # Google Fact Check verdicts
MAX_CONFIDENCE_NEWS = 90  # GNews multi-source consensus
MAX_CONFIDENCE_UNKNOWN = 75  # General/mixed claims


def apply_confidence_ceiling(confidence: int, claim_type: str, verification_source: str, explanation: List[str]) -> int:
    """
    Apply domain-specific confidence caps to prevent over-certainty.
    
    Rules:
    - SCIENTIFIC (Wikipedia): max 99%
    - MISINFORMATION (Google Fact Check): max 95%
    - NEWS (GNews/NewsAPI): max 90%
    - UNKNOWN: max 75%
    
    Args:
        confidence: Raw confidence score
        claim_type: "scientific", "news", or "unknown"
        verification_source: Primary source used
        explanation: List to append ceiling notes
        
    Returns:
        Capped confidence value
    """
    original_confidence = confidence
    
    # Determine appropriate ceiling
    if claim_type == "scientific" and verification_source == "wikipedia":
        ceiling = MAX_CONFIDENCE_SCIENTIFIC
    elif verification_source == "google_fact_check":
        ceiling = MAX_CONFIDENCE_MISINFORMATION
    elif claim_type == "news" or verification_source in ["gnews", "newsapi"]:
        ceiling = MAX_CONFIDENCE_NEWS
    else:  # unknown or general
        ceiling = MAX_CONFIDENCE_UNKNOWN
    
    # Apply ceiling (silently - don't show in UI)
    if confidence > ceiling:
        confidence = ceiling
    
    return confidence


# ============================================================================
# ANALYSIS ENGINE
# ============================================================================

async def analyze_claim(claim: str) -> Dict[str, Any]:
    """
    Main entry point for claim verification with domain-based routing.

    Flow is determined by `claim_type` (scientific | news | unknown).
    This implements domain-based routing rules and builds a `verification_path`.

    Args:
        claim: The text claim to verify

    Returns:
        Clean JSON structure with verdict, confidence, explanation, sources,
        confidence breakdown, `claim_type`, `verification_path`, and `final_verdict`.
    """
    start_time = datetime.now(timezone.utc)
    
    explanation: List[str] = []
    sources: List[str] = []
    publishers: List[str] = []
    published_dates: List[str] = []
    confidence = 50  # Start neutral
    verification_source = "analysis_engine"  # Default source
    news_provider = "none"  # Track which news provider was used (gnews/newsapi/none)
    
    # Track confidence components for breakdown
    authority_score = 0
    news_consensus_score = 0
    stance_alignment_score = 0
    recency_adjustment = 0
    wikipedia_score = 0
    
    # Track if we have strong external evidence
    has_fact_check = False
    has_wikipedia_verification = False
    verification_path: List[str] = []

    # Classify claim type for domain-based routing
    claim_type = classify_claim_type(claim)
    explanation.append(f"Claim classified as {claim_type.upper()}.")
    
    # Domain-based routing
    if claim_type == "scientific":
        # For scientific claims we query Wikipedia first, but Google fact-checks
        # can override Wikipedia if they contain explicit verdicts. To respect
        # both rules we run both lookups (Wikipedia first for speed/readability,
        # then consider Google if available).
        verification_path.append("wikipedia")
        explanation.append("Consulting Wikipedia for scientific verification.")
        wiki_result = await verify_with_wikipedia(claim)

        if wiki_result.get("verified"):
            has_wikipedia_verification = True
            verification_source = "wikipedia"
            wiki_verdict = wiki_result.get("verdict", "Uncertain")
            wiki_confidence = wiki_result.get("confidence", 50)
            wiki_title = wiki_result.get("article_title", "")
            wiki_url = wiki_result.get("article_url", "")
            wiki_explanation = wiki_result.get("explanation", "")

            explanation.append(f"Wikipedia article found: {wiki_title}.")
            explanation.append(f"{wiki_explanation}")
            if wiki_url:
                sources.append(wiki_url)
                publishers.append("Wikipedia")

        # Query Google concurrently (may override Wikipedia)
        verification_path.append("google_fact_check")
        explanation.append("Cross-referencing with professional fact-checkers.")
        fact_check_result = await asyncio.to_thread(check_fact, claim[:500])

        if fact_check_result.get("has_claims"):
            claims_data = fact_check_result.get("claims", [])
            # Find a relevant fact-check (avoid opposite/irrelevant matches)
            relevant_fc = None
            for c in claims_data:
                fc_text = c.get("text", "")
                if _is_fact_check_relevant(claim, fc_text):
                    relevant_fc = c
                    break

            if relevant_fc:
                # Trust Google if it returns an explicit, relevant verdict
                has_fact_check = True
                verification_source = "google_fact_check"
                explanation.append("Professional fact-checker reviewed this claim.")
                fc_claim = relevant_fc
                rating = fc_claim.get("rating", "").lower()
                publisher = fc_claim.get("publisher", "Unknown")
                url = fc_claim.get("url", "")
                claim_date = fc_claim.get("claim_date", "")
                if url and url not in sources:
                    sources.append(url)
                if publisher and publisher not in publishers:
                    publishers.append(publisher)
                if claim_date:
                    published_dates.append(claim_date)

                rating_confidence = _get_confidence_from_rating(rating) or 50
                authority_score = rating_confidence - 50
                confidence = rating_confidence
                explanation.append(f"{publisher} assessed this as: {fc_claim.get('rating', 'Unrated')}.")

                # If the Google fact-check is debunking an opposite claim (e.g. "Earth is flat" rated False)
                # then this actually supports the input claim. Detect simple debunk indicators and invert.
                fc_text = (fc_claim.get("text") or "").lower()
                debunk_indicators = ["flat", "hoax", "fake", "never happened", "did not", "didn't", "not real", "conspiracy", "myth"]
                if any(ind in fc_text for ind in debunk_indicators) and rating_confidence <= 40:
                    # Treat this as supporting evidence for the user's claim
                    support_conf = 90
                    confidence = support_conf
                    authority_score = support_conf - 50
                    explanation.append("Fact-checkers debunked the opposite claim, supporting this statement.")

                # Google wins over Wikipedia if both exist
                # Apply confidence ceiling
                confidence = apply_confidence_ceiling(confidence, claim_type, verification_source, explanation)
                confidence = max(0, min(100, confidence))
                final_verdict = _confidence_to_verdict(confidence)
                confidence_breakdown = {
                    "authority": authority_score,
                    "wikipedia": wikipedia_score,
                    "news_consensus": news_consensus_score,
                    "stance_alignment": stance_alignment_score,
                    "recency_adjustment": recency_adjustment,
                    "final_score": confidence
                }

                return {
                    "claim": claim,
                    "claim_type": claim_type,
                    "verification_path": verification_path,
                    "final_verdict": final_verdict,
                    "verdict": final_verdict,
                    "confidence": confidence,
                    "confidence_breakdown": confidence_breakdown,
                    "explanation": explanation,
                    "sources": sources[:10],
                    "publisher": publishers[:10],
                    "published_dates": published_dates[:10],
                    "verification_source": verification_source,
                    "last_checked": start_time.isoformat()
                }
            else:
                explanation.append("  → Google fact-checks found but none relevant to this claim; ignoring Google result")

        # If Google had no explicit claim, use Wikipedia result if present
        if has_wikipedia_verification and wiki_result.get("verified"):
            wiki_verdict = wiki_result.get("verdict", "Uncertain")
            wiki_confidence = wiki_result.get("confidence", 50)
            if wiki_verdict == "Verified True":
                # Enforce Wikipedia-confirm rule: confidence 85-99
                confidence = max(85, min(99, int(wiki_confidence)))
                wikipedia_score = confidence - 50
                final_verdict = "Verified True"
            elif wiki_verdict == "Likely False":
                # Wikipedia refutes -> Likely False (low confidence range)
                confidence = max(0, min(20, int(wiki_confidence)))
                wikipedia_score = - (50 - confidence)
                final_verdict = "Likely False"
            else:
                final_verdict = _confidence_to_verdict(confidence)

            # Apply confidence ceiling for scientific claims
            confidence = apply_confidence_ceiling(confidence, claim_type, verification_source, explanation)
            confidence_breakdown = {
                "authority": authority_score,
                "wikipedia": wikipedia_score,
                "news_consensus": news_consensus_score,
                "stance_alignment": stance_alignment_score,
                "recency_adjustment": recency_adjustment,
                "final_score": confidence
            }

            return {
                "claim": claim,
                "claim_type": claim_type,
                "verification_path": verification_path,
                "final_verdict": final_verdict,
                "verdict": final_verdict,
                "confidence": confidence,
                "confidence_breakdown": confidence_breakdown,
                "explanation": explanation,
                "sources": sources[:10],
                "publisher": publishers[:10],
                "published_dates": published_dates[:10],
                "verification_source": verification_source,
                "last_checked": start_time.isoformat()
            }

        # Nothing definitive from Google or Wikipedia -> fall through to news search
        verification_path.append("news_search")
        explanation.append("No existing fact-checks found. Searching news coverage.")
        news_result = await get_news_results(claim[:200], max_results=10)
        news_provider = news_result.get("news_provider_used", "none")
        # (News handling continues below)

    elif claim_type == "news":
        # For news/rumor: Google Fact Check first, Wikipedia only for background
        verification_path.append("google_fact_check")
        explanation.append("Prioritizing fact-checker databases for recent claims.")
        fact_check_result = await asyncio.to_thread(check_fact, claim[:500])
        if fact_check_result.get("has_claims"):
            claims_data = fact_check_result.get("claims", [])
            relevant_fc = None
            for c in claims_data:
                if _is_fact_check_relevant(claim, c.get("text", "")):
                    relevant_fc = c
                    break

            if relevant_fc:
                has_fact_check = True
                verification_source = "google_fact_check"
                explanation.append("Professional fact-checker reviewed this claim.")
                fc_claim = relevant_fc
                rating = fc_claim.get("rating", "").lower()
                publisher = fc_claim.get("publisher", "Unknown")
                url = fc_claim.get("url", "")
                if url and url not in sources:
                    sources.append(url)
                if publisher and publisher not in publishers:
                    publishers.append(publisher)
                rating_confidence = _get_confidence_from_rating(rating) or 50
                authority_score = rating_confidence - 50
                confidence = rating_confidence
                explanation.append(f"{publisher} assessed this as: {fc_claim.get('rating', 'Unrated')}.")

                fc_text = (fc_claim.get("text") or "").lower()
                debunk_indicators = ["flat", "hoax", "fake", "never happened", "did not", "didn't", "not real", "conspiracy", "myth"]
                if any(ind in fc_text for ind in debunk_indicators) and rating_confidence <= 40:
                    support_conf = 90
                    confidence = support_conf
                    authority_score = support_conf - 50
                    explanation.append("Fact-checkers debunked the opposite claim, supporting this statement.")

                # Apply confidence ceiling for news claims
                confidence = apply_confidence_ceiling(confidence, claim_type, verification_source, explanation)
                final_verdict = _confidence_to_verdict(confidence)

                confidence_breakdown = {
                    "authority": authority_score,
                    "wikipedia": wikipedia_score,
                    "news_consensus": news_consensus_score,
                    "stance_alignment": stance_alignment_score,
                    "recency_adjustment": recency_adjustment,
                    "final_score": confidence
                }

                return {
                    "claim": claim,
                    "claim_type": claim_type,
                    "verification_path": verification_path,
                    "final_verdict": final_verdict,
                    "verdict": final_verdict,
                    "confidence": confidence,
                    "confidence_breakdown": confidence_breakdown,
                    "explanation": explanation,
                    "sources": sources[:10],
                    "publisher": publishers[:10],
                    "published_dates": published_dates[:10],
                    "verification_source": verification_source,
                    "last_checked": start_time.isoformat()
                }
            else:
                explanation.append("Existing fact-checks do not directly address this claim.")
        
        # No Google verdict -> use unified news search with advanced NEWS confidence scoring
        verification_path.append("news_search")
        explanation.append("No existing fact-checks found. Analyzing news coverage.")
        news_result = await get_news_results(claim[:200], max_results=15)
        news_provider = news_result.get("news_provider_used", "none")
        
        if news_result.get("has_articles"):
            verification_source = news_provider
            articles = news_result.get("articles", [])
            if len(articles) > 0:
                explanation.append(f"Found {len(articles)} news articles covering this topic.")
            
            # Use advanced NEWS confidence scoring
            news_analysis = calculate_news_confidence(articles, claim)
            
            confidence = news_analysis["confidence"]
            explanation.extend(news_analysis["explanation"])
            sources.extend(news_analysis["sources"])
            publishers.extend(news_analysis["publishers"])
            published_dates.extend(news_analysis["published_dates"])
            news_consensus_score = news_analysis["news_consensus_score"]
            
            # For NEWS claims, the verdict is based on confidence from news consensus
            # Apply confidence ceiling
            confidence = apply_confidence_ceiling(confidence, claim_type, verification_source, explanation)
            final_verdict = _confidence_to_verdict(confidence)
            
            confidence_breakdown = {
                "authority": authority_score,
                "wikipedia": wikipedia_score,
                "news_consensus": news_consensus_score,
                "stance_alignment": 0,  # Not used for NEWS path
                "recency_adjustment": 0,  # Already included in calculate_news_confidence
                "final_score": confidence
            }
            
            return {
                "claim": claim,
                "claim_type": claim_type,
                "verification_path": verification_path,
                "final_verdict": final_verdict,
                "verdict": final_verdict,
                "confidence": confidence,
                "confidence_breakdown": confidence_breakdown,
                "explanation": explanation,
                "sources": sources[:10],
                "publisher": publishers[:10],
                "published_dates": published_dates[:10],
                "verification_source": verification_source,
                "news_provider_used": news_provider,
                "last_checked": start_time.isoformat()
            }
        else:
            explanation.append("No news coverage found for this claim.")
            # Fall through to final fallback handling at end of function

    else:
        # UNKNOWN / MIXED default path: Google -> GNews -> Wikipedia (if GNews neutral)
        verification_path.append("google_fact_check")
        explanation.append("Checking fact-checker databases.")
        fact_check_result = await asyncio.to_thread(check_fact, claim[:500])
        if fact_check_result.get("has_claims"):
            claims_data = fact_check_result.get("claims", [])
            relevant_fc = None
            for c in claims_data:
                if _is_fact_check_relevant(claim, c.get("text", "")):
                    relevant_fc = c
                    break

            if relevant_fc:
                has_fact_check = True
                verification_source = "google_fact_check"
                explanation.append("Professional fact-checker reviewed this claim.")
                fc_claim = relevant_fc
                rating = fc_claim.get("rating", "").lower()
                publisher = fc_claim.get("publisher", "Unknown")
                url = fc_claim.get("url", "")
                if url and url not in sources:
                    sources.append(url)
                if publisher and publisher not in publishers:
                    publishers.append(publisher)
                rating_confidence = _get_confidence_from_rating(rating) or 50
                authority_score = rating_confidence - 50
                confidence = rating_confidence
                explanation.append(f"{publisher} assessed this as: {fc_claim.get('rating', 'Unrated')}.")

                fc_text = (fc_claim.get("text") or "").lower()
                debunk_indicators = ["flat", "hoax", "fake", "never happened", "did not", "didn't", "not real", "conspiracy", "myth"]
                if any(ind in fc_text for ind in debunk_indicators) and rating_confidence <= 40:
                    support_conf = 90
                    confidence = support_conf
                    authority_score = support_conf - 50
                    explanation.append("Fact-checkers debunked the opposite claim, supporting this statement.")

                # Apply confidence ceiling for unknown claims
                confidence = apply_confidence_ceiling(confidence, claim_type, verification_source, explanation)
                final_verdict = _confidence_to_verdict(confidence)

                confidence_breakdown = {
                    "authority": authority_score,
                    "wikipedia": wikipedia_score,
                    "news_consensus": news_consensus_score,
                    "stance_alignment": stance_alignment_score,
                    "recency_adjustment": recency_adjustment,
                    "final_score": confidence
                }

                return {
                    "claim": claim,
                    "claim_type": claim_type,
                    "verification_path": verification_path,
                    "final_verdict": final_verdict,
                    "verdict": final_verdict,
                    "confidence": confidence,
                    "confidence_breakdown": confidence_breakdown,
                    "explanation": explanation,
                    "sources": sources[:10],
                    "publisher": publishers[:10],
                    "published_dates": published_dates[:10],
                    "verification_source": verification_source,
                    "last_checked": start_time.isoformat()
                }
            else:
                explanation.append("Existing fact-checks do not directly address this claim.")
        # No Google result -> use unified news search
        verification_path.append("news_search")
        explanation.append("No existing fact-checks found. Searching news sources.")
        news_result = await get_news_results(claim[:200], max_results=10)
        news_provider = news_result.get("news_provider_used", "none")
        
        if news_result.get("has_articles"):
            verification_source = news_provider
            articles = news_result.get("articles", [])
            if len(articles) > 0:
                explanation.append(f"Found {len(articles)} news articles covering this topic.")
            
            credible_count = 0
            low_cred_count = 0
            
            for article in articles:
                source_name = article.get("source", "").lower()
                url = article.get("url", "")
                pub_date = article.get("published_at", "")
                
                if url and url not in sources:
                    sources.append(url)
                if article.get("source") and article.get("source") not in publishers:
                    publishers.append(article.get("source"))
                if pub_date:
                    published_dates.append(pub_date)
                
                # Check credibility
                is_credible = any(cred in source_name for cred in CREDIBLE_SOURCES)
                is_low_cred = any(low in source_name for low in LOW_CREDIBILITY_INDICATORS)
                
                if is_credible:
                    credible_count += 1
                elif is_low_cred:
                    low_cred_count += 1
            
            # Apply credibility-based confidence adjustment
            if credible_count >= 3:
                news_consensus_score = 15
                confidence += 15
                explanation.append(f"Multiple credible news outlets independently confirm this event.")
            elif credible_count >= 1:
                news_consensus_score = 8
                confidence += 8
                explanation.append(f"Several credible sources report on this topic.")

            if low_cred_count >= 3 and credible_count == 0:
                news_consensus_score = -20
                confidence -= 20
                explanation.append("Coverage limited to less established sources.")
            elif low_cred_count > credible_count:
                news_consensus_score = -10
                confidence -= 10
                explanation.append("Majority of coverage from less established outlets.")
            
            # ================================================================
            # STEP 4: Stance Detection (internal only, not shown to user)
            # ================================================================
            if ENABLE_STANCE_DETECTION:
                support_count = 0
                refute_count = 0
                
                for article in articles[:5]:  # Top 5 only
                    headline = article.get("title", "")
                    if headline:
                        stance, stance_conf = await asyncio.to_thread(classify_stance, claim, headline)
                        
                        if stance == "SUPPORTS" and stance_conf > 0.6:
                            support_count += 1
                        elif stance == "REFUTES" and stance_conf > 0.6:
                            refute_count += 1
                
                if support_count > refute_count:
                    boost = min(support_count * 5, 15)
                    stance_alignment_score = boost
                    confidence += boost
                    if support_count >= 3:
                        explanation.append("Multiple sources confirm claim accuracy.")
                elif refute_count > support_count:
                    penalty = min(refute_count * 5, 15)
                    stance_alignment_score = -penalty
                    confidence -= penalty
                    if refute_count >= 3:
                        explanation.append("Multiple sources contradict this claim.")
        else:
            explanation.append("No news coverage found for this claim.")
    
    # ========================================================================
    # STEP 5: Recency / Freshness Check
    # ========================================================================
    newest_date = _get_newest_date(published_dates)
    
    if newest_date:
        days_old = (datetime.now(timezone.utc) - newest_date).days
        
        if days_old > 90:
            recency_adjustment = -10
            confidence -= 10
            explanation.append(f"Evidence is over 3 months old ({days_old} days).")
        elif days_old > 30:
            recency_adjustment = -5
            confidence -= 5
            explanation.append(f"Evidence is over 1 month old ({days_old} days).")
        elif days_old <= 1:
            explanation.append("Articles published within the last 24 hours.")
        elif days_old <= 7:
            explanation.append("Recent coverage (within the last week).")
    else:
        explanation.append("→ Could not determine evidence recency")
    
    # ========================================================================
    # STEP 6: Confidence Aggregation & Verdict
    # ========================================================================
    confidence = max(0, min(100, confidence))  # Clamp 0-100
    
    # Apply confidence ceiling based on claim type and verification source
    confidence = apply_confidence_ceiling(confidence, claim_type, verification_source, explanation)
    
    verdict = _confidence_to_verdict(confidence)
    
    # Final verdict justification (human-readable)
    if confidence >= 90:
        explanation.append("Verdict based on strong corroboration from multiple credible sources.")
    elif confidence >= 70:
        explanation.append("Verdict based on evidence from credible sources with some verification.")
    elif confidence >= 40:
        explanation.append("Insufficient evidence to confirm or refute. More investigation needed.")
    else:
        explanation.append("Evidence suggests this claim is questionable or contradicted.")
    
    # ========================================================================
    # STEP 7: Build Confidence Breakdown (UI Friendly)
    # ========================================================================
    confidence_breakdown = {
        "authority": authority_score,
        "wikipedia": wikipedia_score,
        "news_consensus": news_consensus_score,
        "stance_alignment": stance_alignment_score,
        "recency_adjustment": recency_adjustment,
        "final_score": confidence
    }
    
    # ========================================================================
    # STEP 8: Build Final Result
    # ========================================================================
    
    # Handle case where both news providers failed
    if verification_source in ["gnews", "newsapi"] and not sources and news_provider == "none":
        confidence = 47  # Slightly below neutral due to provider unavailability
        verdict = "Unverified / Needs More Evidence"
        explanation.append("Unable to access news sources at this time.")
    
    return {
        "claim": claim,
        "verdict": verdict,
        "final_verdict": verdict,  # Frontend compatibility - both fields
        "confidence": confidence,
        "confidence_breakdown": confidence_breakdown,
        "claim_type": claim_type,
        "verification_path": verification_path,
        "explanation": explanation,
        "sources": sources[:10],  # Limit to 10
        "publisher": publishers[:10],
        "published_dates": published_dates[:10],
        "verification_source": verification_source,
        "news_provider_used": news_provider,  # NEW: Track which provider was used
        "last_checked": start_time.isoformat()
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _get_confidence_from_rating(rating: str) -> Optional[int]:
    """Convert fact-check rating text to confidence score."""
    rating_lower = rating.lower().strip()
    
    # Check exact match
    if rating_lower in RATING_CONFIDENCE_MAP:
        return RATING_CONFIDENCE_MAP[rating_lower]
    
    # Check partial match
    for key, value in RATING_CONFIDENCE_MAP.items():
        if key in rating_lower or rating_lower in key:
            return value
    
    return None


def _get_newest_date(date_strings: List[str]) -> Optional[datetime]:
    """Parse date strings and return the most recent one."""
    dates = []
    
    for ds in date_strings:
        if not ds:
            continue
        
        try:
            # Try ISO format
            if "T" in ds:
                dt = datetime.fromisoformat(ds.replace("Z", "+00:00"))
            else:
                # Try common formats
                for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%m/%d/%Y"]:
                    try:
                        dt = datetime.strptime(ds, fmt).replace(tzinfo=timezone.utc)
                        break
                    except ValueError:
                        continue
                else:
                    continue
            
            dates.append(dt)
        except Exception:
            continue
    
    return max(dates) if dates else None


def _confidence_to_verdict(confidence: int) -> str:
    """Convert confidence score to verdict string with updated thresholds."""
    if confidence >= 90:
        return "Verified True"
    elif confidence >= 70:
        return "Likely True"
    elif confidence >= 40:
        return "Unverified / Needs More Evidence"
    else:
        return "Likely False"


# ============================================================================
# SIMPLE API WRAPPER
# ============================================================================

async def verify_claim(claim: str) -> Dict[str, Any]:
    """
    Simple wrapper for the analysis engine with caching support.
    Use this function from API endpoints.
    
    Args:
        claim: Text claim to verify
        
    Returns:
        JSON-serializable analysis result with confidence breakdown
    """
    if not claim or not claim.strip():
        return {
            "claim": "",
            "verdict": "Unverified / Needs More Evidence",
            "confidence": 0,
            "confidence_breakdown": {
                "authority": 0,
                "wikipedia": 0,
                "news_consensus": 0,
                "stance_alignment": 0,
                "recency_adjustment": 0,
                "final_score": 0
            },
            "explanation": ["No claim provided"],
            "sources": [],
            "publisher": [],
            "published_dates": [],
            "verification_source": "none",
            "last_checked": datetime.now(timezone.utc).isoformat()
        }
    
    # Check cache first
    cached = get_cached_result(claim)
    if cached:
        # Return cached result with updated last_checked timestamp
        cached_copy = cached.copy()
        cached_copy["last_checked"] = datetime.now(timezone.utc).isoformat()
        cached_copy["cached"] = True  # Indicator for debugging
        return cached_copy
    
    # Run full analysis
    result = await analyze_claim(claim.strip())
    
    # Cache the result
    cache_result(claim, result)
    
    return result
