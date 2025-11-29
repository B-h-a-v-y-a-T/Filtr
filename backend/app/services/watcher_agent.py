"""
Watcher Agent - Continuous Monitoring System for Breaking News and Misinformation
Polls news sources every 30 minutes, analyzes content, and detects emerging trends.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter
import hashlib
import feedparser
import httpx

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from ..models import WatcherEvent, WatcherLog
from .analysis_engine import verify_claim
from .gnews_service import search_gnews
from .newsapi_service import search_newsapi

logger = logging.getLogger(__name__)


class KeywordManager:
    """Manages keyword categories and rotation logic."""
    
    KEYWORD_GROUPS = {
        "health": [
            "COVID", "vaccine", "outbreak", "WHO", "pandemic", "virus",
            "disease", "vaccination", "health crisis", "epidemic"
        ],
        "politics": [
            "election", "riot", "protest", "vote fraud", "parliament",
            "government", "minister", "political crisis", "corruption"
        ],
        "disasters": [
            "earthquake", "cyclone", "flood", "tsunami", "wildfire",
            "natural disaster", "emergency", "evacuation"
        ],
        "technology": [
            "AI", "hacking", "data leak", "cyber attack", "privacy breach",
            "malware", "ransomware", "tech scandal"
        ],
        "finance": [
            "stock crash", "bank collapse", "scam", "fraud", "crypto crash",
            "financial crisis", "market crash", "economic collapse"
        ]
    }
    
    def __init__(self):
        # Randomize starting category for more variety each restart
        import random
        self.categories = list(self.KEYWORD_GROUPS.keys())
        self.current_index = random.randint(0, len(self.categories) - 1)
        self.groups = self.categories  # Use same list
    
    def get_next_group(self) -> Tuple[str, List[str]]:
        """Get next keyword group in rotation."""
        group_name = self.groups[self.current_index]
        keywords = self.KEYWORD_GROUPS[group_name]
        self.current_index = (self.current_index + 1) % len(self.groups)
        return group_name, keywords
    
    def get_all_groups(self) -> Dict[str, List[str]]:
        """Get all keyword groups."""
        return self.KEYWORD_GROUPS.copy()


class RateLimiter:
    """Manages API rate limits with daily reset."""
    
    def __init__(self, daily_limit: int = 100, safety_buffer: int = 10):
        self.daily_limit = daily_limit
        self.safety_buffer = safety_buffer
        self.max_calls = daily_limit - safety_buffer
        self.calls_today = 0
        self.last_reset = datetime.now().date()
    
    def check_and_increment(self) -> bool:
        """Check if API call is allowed and increment counter."""
        self._check_reset()
        
        if self.calls_today >= self.max_calls:
            logger.warning(f"Rate limit reached: {self.calls_today}/{self.max_calls}")
            return False
        
        self.calls_today += 1
        return True
    
    def _check_reset(self):
        """Reset counter at midnight."""
        today = datetime.now().date()
        if today > self.last_reset:
            logger.info(f"Rate limit reset. Previous count: {self.calls_today}")
            self.calls_today = 0
            self.last_reset = today
    
    def get_remaining(self) -> int:
        """Get remaining API calls for today."""
        self._check_reset()
        return max(0, self.max_calls - self.calls_today)


class RSSFeedFetcher:
    """Fallback RSS feed parser for when APIs are exhausted."""
    
    RSS_FEEDS = {
        "BBC": "http://feeds.bbci.co.uk/news/rss.xml",
        "Reuters": "https://www.reutersagency.com/feed/",
        "The Hindu": "https://www.thehindu.com/news/national/feeder/default.rss",
        "ANI": "https://www.aninews.in/feed/"
    }
    
    @staticmethod
    async def fetch_feeds(keyword_group: str, keywords: List[str]) -> List[Dict[str, Any]]:
        """Fetch articles from RSS feeds."""
        articles = []
        
        for source_name, feed_url in RSSFeedFetcher.RSS_FEEDS.items():
            try:
                logger.info(f"Fetching RSS from {source_name}: {feed_url}")
                
                # Use feedparser to parse RSS
                feed = await asyncio.to_thread(feedparser.parse, feed_url)
                
                if feed.bozo:
                    logger.warning(f"RSS parsing warning for {source_name}: {feed.bozo_exception}")
                
                for entry in feed.entries[:10]:  # Limit to 10 per source
                    # Check if any keyword matches
                    title = entry.get('title', '').lower()
                    summary = entry.get('summary', '').lower()
                    
                    if any(kw.lower() in title or kw.lower() in summary for kw in keywords):
                        articles.append({
                            "title": entry.get('title', ''),
                            "url": entry.get('link', ''),
                            "source": source_name,
                            "published_date": entry.get('published', ''),
                            "description": entry.get('summary', '')[:500]
                        })
                
                logger.info(f"Found {len([a for a in articles if a['source'] == source_name])} articles from {source_name}")
                
            except Exception as e:
                logger.error(f"Error fetching RSS from {source_name}: {e}")
                continue
        
        return articles


class TrendDetector:
    """Detects misinformation trends and clusters."""
    
    @staticmethod
    def normalize_headline(headline: str) -> str:
        """Normalize headline for comparison."""
        return ' '.join(headline.lower().split())
    
    @staticmethod
    def get_headline_hash(headline: str) -> str:
        """Generate hash for headline similarity detection."""
        normalized = TrendDetector.normalize_headline(headline)
        return hashlib.md5(normalized.encode()).hexdigest()[:16]
    
    @staticmethod
    async def detect_trends(db: Session, lookback_hours: int = 24) -> List[Dict[str, Any]]:
        """Detect trending misinformation patterns."""
        cutoff_time = datetime.utcnow() - timedelta(hours=lookback_hours)
        
        # Get recent high-risk events
        recent_events = db.query(WatcherEvent).filter(
            and_(
                WatcherEvent.first_seen >= cutoff_time,
                WatcherEvent.credibility_flag.in_(["high_risk", "medium_risk"])
            )
        ).all()
        
        if not recent_events:
            return []
        
        # Group by similar headlines
        headline_groups = defaultdict(list)
        for event in recent_events:
            hash_key = TrendDetector.get_headline_hash(event.headline)
            headline_groups[hash_key].append(event)
        
        # Detect trends
        trends = []
        
        for hash_key, events in headline_groups.items():
            if len(events) >= 3:  # Same narrative appears 3+ times
                trends.append({
                    "type": "repeated_narrative",
                    "headline": events[0].headline,
                    "occurrences": len(events),
                    "sources": list(set([e.source for e in events])),
                    "risk_level": "high",
                    "first_seen": min([e.first_seen for e in events]),
                    "last_seen": max([e.last_seen for e in events])
                })
        
        # Keyword clustering
        keyword_counts = defaultdict(int)
        for event in recent_events:
            words = TrendDetector.normalize_headline(event.headline).split()
            for word in words:
                if len(word) > 4:  # Only meaningful words
                    keyword_counts[word] += 1
        
        # Find keyword spikes
        for keyword, count in keyword_counts.items():
            if count >= 5:  # Keyword appears in 5+ articles
                related_events = [e for e in recent_events if keyword in TrendDetector.normalize_headline(e.headline)]
                trends.append({
                    "type": "keyword_cluster",
                    "keyword": keyword,
                    "occurrences": count,
                    "risk_level": "medium",
                    "related_headlines": [e.headline for e in related_events[:5]]
                })
        
        # Time-based spikes (1 hour window)
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_spike_events = [e for e in recent_events if e.first_seen >= one_hour_ago]
        
        if len(recent_spike_events) >= 5:
            category_counts = Counter([e.category for e in recent_spike_events])
            for category, count in category_counts.items():
                if count >= 3:
                    trends.append({
                        "type": "spike_alert",
                        "category": category,
                        "occurrences": count,
                        "risk_level": "high",
                        "timeframe": "1_hour",
                        "message": f"Spike detected: {count} {category}-related claims in past hour"
                    })
        
        return trends


class WatcherAgent:
    """Main Watcher Agent coordinating all monitoring activities."""
    
    def __init__(self, db: Session):
        self.db = db
        self.keyword_manager = KeywordManager()
        self.rate_limiter = RateLimiter(daily_limit=100, safety_buffer=10)
    
    async def run_monitoring_cycle(self, force_fresh: bool = False) -> Dict[str, Any]:
        """Execute one complete monitoring cycle.
        
        Args:
            force_fresh: If True, ensures we get NEW articles by analyzing more and skipping fewer.
        """
        start_time = time.time()
        cycle_timestamp = datetime.utcnow()
        
        logger.info(f"=== Starting Watcher Agent Cycle at {cycle_timestamp} (force_fresh={force_fresh}) ===")
        logger.info(f"Remaining API calls: {self.rate_limiter.get_remaining()}")
        
        # Get next keyword group
        keyword_group, keywords = self.keyword_manager.get_next_group()
        logger.info(f"Monitoring keyword group: {keyword_group}")
        logger.info(f"Keywords: {', '.join(keywords[:3])}...")
        
        articles = []
        api_source = "none"
        status = "success"
        error_message = None
        
        try:
            # Try GNews API first
            if self.rate_limiter.check_and_increment():
                logger.info("Using GNews API")
                api_source = "gnews"
                articles = await self._fetch_from_gnews(keywords)
            
            # Fallback to NewsAPI if GNews fails or returns few results
            if len(articles) < 5 and self.rate_limiter.check_and_increment():
                logger.info("Using NewsAPI as fallback")
                api_source = "newsapi"
                newsapi_articles = await self._fetch_from_newsapi(keywords)
                articles.extend(newsapi_articles)
            
            # Fallback to RSS if API exhausted
            if len(articles) < 5:
                logger.info("Using RSS feeds as fallback")
                api_source = "rss"
                rss_articles = await RSSFeedFetcher.fetch_feeds(keyword_group, keywords)
                articles.extend(rss_articles)
        
        except Exception as e:
            logger.error(f"Error fetching articles: {e}")
            status = "error"
            error_message = str(e)
        
        # Analyze articles - process more when force_fresh to ensure we get new ones
        articles_to_analyze = articles[:15] if force_fresh else articles[:10]
        analyzed_count = 0
        new_articles_stored = 0
        
        for article in articles_to_analyze:
            try:
                # Check if it's a duplicate before analyzing
                headline = article.get("title", "")
                if headline and len(headline) >= 10:
                    existing = self.db.query(WatcherEvent).filter(
                        WatcherEvent.headline == headline
                    ).first()
                    
                    if existing:
                        logger.info(f"⊗ Skipping duplicate: {headline[:50]}...")
                        continue
                    
                    # NEW article - analyze and store it
                    await self._analyze_and_store_article(article, keyword_group)
                    analyzed_count += 1
                    new_articles_stored += 1
                    
                    # If force_fresh and we have 2 NEW articles, we're done
                    if force_fresh and new_articles_stored >= 2:
                        logger.info(f"✓ Got {new_articles_stored} fresh articles for manual refresh")
                        break
                        
            except Exception as e:
                logger.error(f"Error analyzing article: {e}")
                continue
        
        # Log cycle
        execution_time = time.time() - start_time
        self._log_cycle(
            cycle_timestamp=cycle_timestamp,
            api_source=api_source,
            keyword_group=keyword_group,
            articles_fetched=len(articles),
            articles_analyzed=analyzed_count,
            api_calls_used=1 if api_source in ["gnews", "newsapi"] else 0,
            status=status,
            error_message=error_message,
            execution_time_seconds=execution_time
        )
        
        logger.info(f"=== Cycle Complete: {analyzed_count}/{len(articles)} articles analyzed in {execution_time:.2f}s ===")
        
        return {
            "cycle_timestamp": cycle_timestamp,
            "keyword_group": keyword_group,
            "articles_fetched": len(articles),
            "articles_analyzed": analyzed_count,
            "api_calls_remaining": self.rate_limiter.get_remaining(),
            "execution_time": execution_time
        }
    
    async def _fetch_from_gnews(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Fetch articles from GNews API."""
        try:
            # Use first 3 keywords combined
            query = " OR ".join(keywords[:3])
            results = search_gnews(query, max_results=20)
            
            articles = []
            for item in results.get("articles", []):
                # Source is already flattened to a string by gnews_service
                source = item.get("source", "Unknown")
                if isinstance(source, dict):
                    source = source.get("name", "Unknown")
                articles.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "source": source,
                    "published_date": item.get("published_at", ""),
                    "description": item.get("description", "")
                })
            
            return articles
        except Exception as e:
            logger.error(f"GNews fetch error: {e}")
            return []
    
    async def _fetch_from_newsapi(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Fetch articles from NewsAPI."""
        try:
            query = " OR ".join(keywords[:3])
            results = search_newsapi(query, max_results=20)
            
            articles = []
            for item in results.get("articles", []):
                # Source is already flattened to a string by newsapi_service
                source = item.get("source", "Unknown")
                if isinstance(source, dict):
                    source = source.get("name", "Unknown")
                articles.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "source": source,
                    "published_date": item.get("published_at", ""),
                    "description": item.get("description", "")
                })
            
            return articles
        except Exception as e:
            logger.error(f"NewsAPI fetch error: {e}")
            return []
    
    async def _analyze_and_store_article(self, article: Dict[str, Any], keyword_group: str):
        """
        Analyze article headline and store in database as NEW article.
        This should only be called after checking for duplicates.
        """
        headline = article.get("title", "")
        if not headline or len(headline) < 10:
            return
        
        # Analyze NEW headline using existing analysis engine
        try:
            analysis_result = await verify_claim(headline)
            
            verdict = analysis_result.get("verdict", "Unknown")
            confidence = analysis_result.get("confidence", 0)
            
            # Determine credibility flag
            credibility_flag = "low_risk"
            if "false" in verdict.lower() or "misleading" in verdict.lower():
                if confidence >= 70:
                    credibility_flag = "high_risk"
                elif confidence >= 50:
                    credibility_flag = "medium_risk"
            
            # Store new event
            watcher_event = WatcherEvent(
                keyword_group=keyword_group,
                headline=headline,
                source=article.get("source", "Unknown"),
                url=article.get("url", ""),
                verdict=verdict,
                confidence=confidence,
                category=keyword_group,
                credibility_flag=credibility_flag,
                first_seen=datetime.utcnow(),
                times_seen=1,
                last_seen=datetime.utcnow(),
                analysis_data=json.dumps(analysis_result)
            )
            
            self.db.add(watcher_event)
            self.db.commit()
            
            logger.info(f"✓ NEW stored [{credibility_flag}]: {headline[:50]}... (confidence: {confidence}%)")
        
        except Exception as e:
            logger.error(f"Error analyzing headline '{headline[:50]}...': {e}")
            self.db.rollback()
    
    def _log_cycle(self, **kwargs):
        """Log monitoring cycle to database."""
        try:
            log_entry = WatcherLog(**kwargs)
            self.db.add(log_entry)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error logging cycle: {e}")
            self.db.rollback()
    
    def _get_verification_badge(self, verdict: str, confidence: float) -> Dict[str, str]:
        """
        Compute verification badge based on verdict and confidence.
        Returns badge emoji and color.
        """
        verdict_lower = verdict.lower()
        
        # Green badge: Verified True or Likely True
        if "verified true" in verdict_lower or "likely true" in verdict_lower or "true" in verdict_lower:
            return {"badge": "✅", "color": "green"}
        
        # Red badge: Likely False BUT ONLY if confidence < 30
        if "false" in verdict_lower or "misleading" in verdict_lower:
            if confidence < 30:
                return {"badge": "❌", "color": "red"}
            # If confidence >= 30, treat as unverified (grey)
            return {"badge": "➖", "color": "grey"}
        
        # Grey badge: Unverified / Needs More Evidence (DEFAULT)
        return {"badge": "➖", "color": "grey"}
    
    def _get_trending_news(self) -> List[Dict[str, Any]]:
        """
        Get current news - ALWAYS RETURN LATEST 2 UNIQUE ARTICLES.
        Returns most recent articles from database.
        
        Orders by:
        1. Most recent first (first_seen DESC)
        2. Highest confidence
        """
        # Get the 2 most recent unique articles
        latest_events = self.db.query(WatcherEvent).order_by(
            desc(WatcherEvent.first_seen),
            desc(WatcherEvent.confidence)
        ).limit(2).all()
        
        current_news = []
        for event in latest_events:
            badge_info = self._get_verification_badge(event.verdict, event.confidence)
            
            current_news.append({
                "headline": event.headline,
                "source": event.source,
                "confidence": int(event.confidence) if event.confidence else 50,
                "verdict": event.verdict,
                "badge": badge_info["badge"],
                "badge_color": badge_info["color"],
                "published_at": event.first_seen.isoformat(),
                "url": event.url,
                "times_seen": event.times_seen,
                "category": event.category
            })
        
        return current_news
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for watcher dashboard API."""
        try:
            # Get trends
            trends = await TrendDetector.detect_trends(self.db, lookback_hours=24)
            
            # Get latest alerts (high risk items from last 24 hours) - KEEP EXISTING LOGIC
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            latest_alerts = self.db.query(WatcherEvent).filter(
                and_(
                    WatcherEvent.first_seen >= cutoff_time,
                    WatcherEvent.credibility_flag == "high_risk"
                )
            ).order_by(desc(WatcherEvent.first_seen)).limit(20).all()
            
            # Get most risky claims - KEEP EXISTING LOGIC
            risky_claims = self.db.query(WatcherEvent).filter(
                WatcherEvent.credibility_flag.in_(["high_risk", "medium_risk"])
            ).order_by(
                desc(WatcherEvent.times_seen),
                desc(WatcherEvent.confidence)
            ).limit(10).all()
            
            # Calculate risk level - KEEP EXISTING LOGIC
            high_risk_count = len([a for a in latest_alerts])
            if high_risk_count >= 10:
                risk_level = "high"
            elif high_risk_count >= 5:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            # Get latest log
            latest_log = self.db.query(WatcherLog).order_by(
                desc(WatcherLog.cycle_timestamp)
            ).first()
            
            # NEW: Get trending news (replaces recent_news)
            trending_news = self._get_trending_news()
            
            return {
                # NEW TRENDING FEED
                "trending_news": trending_news,
                
                # KEEP EXISTING DATA
                "trends": [
                    {
                        "type": t.get("type"),
                        "description": t.get("message", t.get("headline", "")),
                        "risk_level": t.get("risk_level"),
                        "occurrences": t.get("occurrences", 0),
                        "sources": t.get("sources", []),
                        "keyword": t.get("keyword", ""),
                        "category": t.get("category", "")
                    }
                    for t in trends
                ],
                "latest_alerts": [
                    {
                        "headline": alert.headline,
                        "source": alert.source,
                        "verdict": alert.verdict,
                        "confidence": alert.confidence,
                        "category": alert.category,
                        "timestamp": alert.first_seen.isoformat(),
                        "url": alert.url,
                        "times_seen": alert.times_seen
                    }
                    for alert in latest_alerts
                ],
                "risky_claims": [
                    {
                        "headline": claim.headline,
                        "source": claim.source,
                        "verdict": claim.verdict,
                        "confidence": claim.confidence,
                        "category": claim.category,
                        "times_seen": claim.times_seen,
                        "credibility_flag": claim.credibility_flag
                    }
                    for claim in risky_claims
                ],
                "risk_level": risk_level,
                "last_updated": datetime.utcnow().isoformat(),
                "api_calls_remaining": self.rate_limiter.get_remaining(),
                "monitoring_status": {
                    "api_calls_remaining": self.rate_limiter.get_remaining(),
                    "last_cycle": latest_log.cycle_timestamp.isoformat() if latest_log else None,
                    "last_status": latest_log.status if latest_log else None
                }
            }
        
        except Exception as e:
            logger.error(f"Error generating dashboard data: {e}")
            return {
                "trends": [],
                "latest_alerts": [],
                "risky_claims": [],
                "risk_level": "unknown",
                "last_updated": datetime.utcnow().isoformat(),
                "error": str(e)
            }
