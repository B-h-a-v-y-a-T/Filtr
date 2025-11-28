"""
Test script for the updated verification logic.

Tests the following scenarios:
1. Scientific claim (should use Wikipedia)
2. News claim (should use GNews)
3. Misinformation claim (should use Google Fact Check)
4. Empty result handling
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.analysis_engine import verify_claim


async def test_verification_logic():
    """Run comprehensive tests on the verification engine."""
    
    print("=" * 80)
    print("VERIFICATION LOGIC TEST SUITE")
    print("=" * 80)
    
    test_cases = [
        {
            "name": "Scientific Claim - Water Boiling Point",
            "claim": "Water boils at 100 degrees Celsius at sea level",
            "expected_type": "scientific",
            "expected_verdict": "Verified True",
        },
        {
            "name": "News Claim - Political Event",
            "claim": "Karnataka CM discusses resolution with Congress leaders",
            "expected_type": "news",
            "expected_verdict": "Likely True or Unverified",
        },
        {
            "name": "Misinformation Claim - Vaccine Conspiracy",
            "claim": "Bill Gates wants to microchip everyone through vaccines",
            "expected_type": "misinformation",
            "expected_verdict": "Likely False",
        },
        {
            "name": "Scientific Claim - Earth Shape",
            "claim": "The Earth is round and orbits the Sun",
            "expected_type": "scientific",
            "expected_verdict": "Verified True",
        },
        {
            "name": "Fresh News with Entities",
            "claim": "'Will resolve issue': Kharge to discuss Karnataka CM row with Sonia, Rahul | India News",
            "expected_type": "news",
            "expected_verdict": "Likely True or Unverified",
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST {i}: {test['name']}")
        print(f"{'=' * 80}")
        print(f"Claim: {test['claim']}")
        print(f"Expected Type: {test['expected_type']}")
        print(f"Expected Verdict: {test['expected_verdict']}")
        print()
        
        try:
            result = await verify_claim(test['claim'])
            
            claim_type = result.get('claim_type', 'unknown')
            verdict = result.get('verdict', 'Unknown')
            confidence = result.get('confidence', 0)
            verification_path = result.get('verification_path', [])
            misinformation_checked = result.get('misinformation_checked', False)
            
            print(f"ACTUAL RESULT:")
            print(f"  Claim Type: {claim_type}")
            print(f"  Verification Path: {' → '.join(verification_path)}")
            print(f"  Misinformation Checked: {misinformation_checked}")
            print(f"  Verdict: {verdict}")
            print(f"  Confidence: {confidence}%")
            print()
            
            # Check if type matches
            type_match = claim_type == test['expected_type']
            print(f"  Type Match: {'✓ PASS' if type_match else '✗ FAIL'}")
            
            # Check if verdict is reasonable
            verdict_ok = True
            if "Verified True" in test['expected_verdict'] and confidence < 80:
                verdict_ok = False
            elif "Likely False" in test['expected_verdict'] and confidence > 40:
                verdict_ok = False
            
            print(f"  Verdict Reasonable: {'✓ PASS' if verdict_ok else '✗ FAIL'}")
            
            # Show explanation (first 5 lines)
            explanation = result.get('explanation', [])
            if explanation:
                print(f"\n  Explanation (first 5 lines):")
                for line in explanation[:5]:
                    print(f"    {line}")
            
            # Show sources
            sources = result.get('sources', [])
            if sources:
                print(f"\n  Sources ({len(sources)}):")
                for source in sources[:3]:
                    print(f"    - {source}")
            
            results.append({
                "test": test['name'],
                "type_match": type_match,
                "verdict_ok": verdict_ok,
                "pass": type_match and verdict_ok
            })
            
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            results.append({
                "test": test['name'],
                "type_match": False,
                "verdict_ok": False,
                "pass": False,
                "error": str(e)
            })
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for r in results if r['pass'])
    total = len(results)
    
    for result in results:
        status = "✓ PASS" if result['pass'] else "✗ FAIL"
        print(f"{status} - {result['test']}")
        if 'error' in result:
            print(f"    Error: {result['error']}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({(passed/total*100):.1f}%)")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_verification_logic())
