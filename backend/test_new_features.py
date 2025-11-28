"""
Test script for new features:
- Caching with claim normalization
- Confidence breakdown
- Sandbox mode
- Wikipedia knowledge base verification

Run this AFTER starting the FastAPI server:
    cd backend
    uvicorn app.main:app --reload
    
Then in another terminal:
    python test_new_features.py
"""
import asyncio
import json
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.services.analysis_engine import verify_claim, normalize_claim, get_cached_result, _verification_cache, verify_with_wikipedia


def clear_cache():
    """Clear the verification cache for fresh tests."""
    _verification_cache.clear()
    print("Cache cleared.")


async def test_claim_normalization():
    """Test that claim normalization works correctly."""
    print("\n" + "=" * 80)
    print("TEST 1: CLAIM NORMALIZATION")
    print("=" * 80)
    
    test_cases = [
        ("  COVID-19 was created in a lab  ", "covid-19 was created in a lab"),
        ("COVID-19 was created in a lab.", "covid-19 was created in a lab"),
        ("   COVID-19    was created   in   a   lab!!!  ", "covid-19 was created in a lab"),
        ("COVID-19 WAS CREATED IN A LAB", "covid-19 was created in a lab"),
    ]
    
    for original, expected in test_cases:
        normalized = normalize_claim(original)
        status = "✓ PASS" if normalized == expected else "✗ FAIL"
        print(f"{status} | Original: '{original}'")
        print(f"       | Normalized: '{normalized}'")
        print(f"       | Expected: '{expected}'")
        print()


async def test_wikipedia_verification():
    """Test Wikipedia knowledge base verification."""
    print("\n" + "=" * 80)
    print("TEST 2: WIKIPEDIA VERIFICATION")
    print("=" * 80)
    
    # Test direct Wikipedia verification
    test_claims = [
        "The Earth is round",
        "Water boils at 100 degrees Celsius",
        "The speed of light is approximately 300,000 km per second",
    ]
    
    for claim in test_claims:
        print(f"\nTesting Wikipedia for: '{claim}'")
        result = await verify_with_wikipedia(claim)
        
        print(f"  Verified: {result.get('verified')}")
        print(f"  Verdict: {result.get('verdict')}")
        print(f"  Confidence: {result.get('confidence')}%")
        print(f"  Article: {result.get('article_title')}")
        print(f"  Explanation: {result.get('explanation')[:100]}...")


async def test_scientific_facts():
    """Test that well-established scientific facts are verified correctly."""
    print("\n" + "=" * 80)
    print("TEST 3: SCIENTIFIC FACTS VERIFICATION (FULL PIPELINE)")
    print("=" * 80)
    
    clear_cache()
    
    scientific_facts = [
        ("The Earth is round and orbits the Sun", "Likely True"),
        ("Water boils at 100 degrees Celsius at sea level", "Likely True"),
        ("Humans need oxygen to breathe", "Likely True"),
        ("The Earth is flat", "Likely False"),
        ("5G towers cause COVID-19", "Likely False"),
    ]
    
    for claim, expected_category in scientific_facts:
        print(f"\nTesting: '{claim}'")
        print(f"Expected: {expected_category}")
        
        result = await verify_claim(claim)
        
        actual_verdict = result.get("verdict", "Unknown")
        actual_confidence = result.get("confidence", 0)
        verification_source = result.get("verification_source", "unknown")
        breakdown = result.get("confidence_breakdown", {})
        
        # Check if verdict is in the right category
        true_verdicts = ["Verified True", "Likely True"]
        false_verdicts = ["Likely False"]
        
        is_correct = False
        if expected_category == "Likely True":
            is_correct = actual_verdict in true_verdicts
        elif expected_category == "Likely False":
            is_correct = actual_verdict in false_verdicts
        
        status = "✓ PASS" if is_correct else "✗ FAIL"
        
        print(f"Actual: {actual_verdict} ({actual_confidence}%) {status}")
        print(f"Verification Source: {verification_source}")
        print(f"Breakdown: {json.dumps(breakdown, indent=2)}")


async def test_caching():
    """Test that caching works and returns cached results on second call."""
    print("\n" + "=" * 80)
    print("TEST 4: CACHING")
    print("=" * 80)
    
    clear_cache()
    
    test_claim = "The speed of light is approximately 300,000 km per second"
    
    print(f"Testing claim: '{test_claim}'")
    print("\n--- First call (should be cache MISS) ---")
    result1 = await verify_claim(test_claim)
    is_cached_1 = result1.get("cached", False)
    print(f"Cached: {is_cached_1}")
    print(f"Verdict: {result1['verdict']}")
    print(f"Confidence: {result1['confidence']}%")
    print(f"Verification Source: {result1.get('verification_source', 'unknown')}")
    
    print("\n--- Second call (should be cache HIT) ---")
    result2 = await verify_claim(test_claim)
    is_cached_2 = result2.get("cached", False)
    print(f"Cached: {is_cached_2}")
    print(f"Verdict: {result2['verdict']}")
    print(f"Confidence: {result2['confidence']}%")
    
    # Verify caching works
    if not is_cached_1 and is_cached_2:
        print("\n✓ PASS - Caching works correctly!")
    else:
        print(f"\n✗ FAIL - Caching issue: first={is_cached_1}, second={is_cached_2}")


async def test_confidence_breakdown():
    """Test that confidence breakdown is returned in API response."""
    print("\n" + "=" * 80)
    print("TEST 5: CONFIDENCE BREAKDOWN")
    print("=" * 80)
    
    clear_cache()
    
    test_claim = "The Moon landing in 1969 was real"
    
    print(f"Testing claim: '{test_claim}'")
    result = await verify_claim(test_claim)
    
    # Check if confidence_breakdown exists
    if "confidence_breakdown" not in result:
        print("✗ FAIL - confidence_breakdown not found in result")
        return
    
    breakdown = result["confidence_breakdown"]
    
    # Validate structure (now includes wikipedia instead of ai_verification)
    required_fields = ["authority", "wikipedia", "news_consensus", "stance_alignment", "recency_adjustment", "final_score"]
    missing_fields = [f for f in required_fields if f not in breakdown]
    
    if missing_fields:
        print(f"✗ FAIL - Missing fields: {missing_fields}")
        return
    
    print("\n✓ PASS - Confidence breakdown structure correct")
    print("\nBreakdown:")
    print(f"  Authority Score:        {breakdown['authority']:+d}")
    print(f"  Wikipedia Score:        {breakdown['wikipedia']:+d}")
    print(f"  News Consensus Score:   {breakdown['news_consensus']:+d}")
    print(f"  Stance Alignment Score: {breakdown['stance_alignment']:+d}")
    print(f"  Recency Adjustment:     {breakdown['recency_adjustment']:+d}")
    print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  Final Score:            {breakdown['final_score']}%")
    print(f"\nVerdict: {result['verdict']}")
    print(f"Verification Source: {result.get('verification_source', 'unknown')}")


async def test_verification_source():
    """Test that verification_source field is present in responses."""
    print("\n" + "=" * 80)
    print("TEST 6: VERIFICATION SOURCE FIELD")
    print("=" * 80)
    
    clear_cache()
    
    test_claim = "The Earth revolves around the Sun"
    
    print(f"Testing claim: '{test_claim}'")
    result = await verify_claim(test_claim)
    
    if "verification_source" not in result:
        print("✗ FAIL - verification_source not found in result")
        return
    
    verification_source = result["verification_source"]
    print(f"✓ PASS - verification_source present: {verification_source}")
    
    # Check valid values
    valid_sources = ["google_fact_check", "wikipedia", "gnews", "analysis_engine", "none"]
    if verification_source in valid_sources:
        print(f"✓ PASS - verification_source is valid: {verification_source}")
    else:
        print(f"✗ FAIL - unexpected verification_source: {verification_source}")


async def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("TESTING ENHANCED ANALYSIS ENGINE WITH WIKIPEDIA")
    print("=" * 80)
    print("Features:")
    print("  C) Caching + Claim Normalization")
    print("  D) Confidence Breakdown (with Wikipedia)")
    print("  E) Sandbox Mode (check server logs)")
    print("  NEW: Wikipedia Knowledge Base for Scientific/Educational Facts")
    print("=" * 80)
    
    try:
        await test_claim_normalization()
        await test_wikipedia_verification()
        await test_scientific_facts()
        await test_caching()
        await test_confidence_breakdown()
        await test_verification_source()
        
        print("\n" + "=" * 80)
        print("ALL TESTS COMPLETED")
        print("=" * 80)
        print("\nTo test SANDBOX MODE:")
        print("  1. Set SANDBOX_MODE=true in backend/.env")
        print("  2. Restart the FastAPI server")
        print("  3. Check server logs for stress test results")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
