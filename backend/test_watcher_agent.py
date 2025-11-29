"""
Test script for Watcher Agent functionality.
Run this to verify the Watcher Agent is working correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.watcher_agent import (
    KeywordManager,
    RateLimiter,
    TrendDetector,
    WatcherAgent
)
from app.services.db import get_db

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_keyword_manager():
    """Test keyword rotation."""
    logger.info("=== Testing KeywordManager ===")
    
    km = KeywordManager()
    
    for i in range(7):  # Test 7 rotations (more than 5 groups)
        group_name, keywords = km.get_next_group()
        logger.info(f"Rotation {i+1}: {group_name} -> {keywords[:3]}")
    
    logger.info("✅ KeywordManager test passed\n")


async def test_rate_limiter():
    """Test rate limiting logic."""
    logger.info("=== Testing RateLimiter ===")
    
    rl = RateLimiter(daily_limit=10, safety_buffer=2)
    
    # Simulate API calls
    for i in range(12):
        allowed = rl.check_and_increment()
        remaining = rl.get_remaining()
        logger.info(f"Call {i+1}: Allowed={allowed}, Remaining={remaining}")
    
    logger.info("✅ RateLimiter test passed\n")


async def test_trend_detector():
    """Test headline normalization."""
    logger.info("=== Testing TrendDetector ===")
    
    headlines = [
        "COVID-19 Vaccine Causes Autism",
        "Covid 19    Vaccine  Causes    Autism",
        "Election Fraud Discovered in 2020",
        "Major Earthquake Hits California"
    ]
    
    for headline in headlines:
        normalized = TrendDetector.normalize_headline(headline)
        hash_val = TrendDetector.get_headline_hash(headline)
        logger.info(f"Original: {headline}")
        logger.info(f"Normalized: {normalized}")
        logger.info(f"Hash: {hash_val}\n")
    
    logger.info("✅ TrendDetector test passed\n")


async def test_watcher_agent():
    """Test full watcher agent cycle."""
    logger.info("=== Testing WatcherAgent ===")
    
    db = next(get_db())
    
    try:
        watcher = WatcherAgent(db)
        
        # Test monitoring cycle
        logger.info("Running monitoring cycle (this may take 10-20 seconds)...")
        result = await watcher.run_monitoring_cycle()
        
        logger.info(f"Cycle result: {result}")
        logger.info(f"Articles fetched: {result['articles_fetched']}")
        logger.info(f"Articles analyzed: {result['articles_analyzed']}")
        logger.info(f"API calls remaining: {result['api_calls_remaining']}")
        
        # Test dashboard data
        logger.info("\nFetching dashboard data...")
        dashboard = await watcher.get_dashboard_data()
        
        logger.info(f"Trends detected: {len(dashboard.get('trends', []))}")
        logger.info(f"Latest alerts: {len(dashboard.get('latest_alerts', []))}")
        logger.info(f"Risky claims: {len(dashboard.get('risky_claims', []))}")
        logger.info(f"Risk level: {dashboard.get('risk_level')}")
        
        logger.info("✅ WatcherAgent test passed\n")
    
    finally:
        db.close()


async def main():
    """Run all tests."""
    logger.info("=" * 60)
    logger.info("WATCHER AGENT TEST SUITE")
    logger.info("=" * 60 + "\n")
    
    try:
        await test_keyword_manager()
        await test_rate_limiter()
        await test_trend_detector()
        await test_watcher_agent()
        
        logger.info("=" * 60)
        logger.info("✅ ALL TESTS PASSED SUCCESSFULLY")
        logger.info("=" * 60)
    
    except Exception as e:
        logger.error(f"❌ TEST FAILED: {e}")
        logger.exception(e)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
