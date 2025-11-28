"""
Test the upgraded NEWS confidence scoring system.
Tests multi-source confirmation, brand trust, recency, and anti-inflation rules.
"""
import asyncio
import sys
from backend.app.services.analysis_engine import analyze_claim

# Ensure UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')


async def test_news_confidence():
    """Test various news claim scenarios."""
    
    test_cases = [
        {
            "name": "Recent Political News (Multiple Sources)",
            "claim": "RAHUL GANDHI MEETS CONGRESS LEADERS\nRahul Gandhi reportedly held meetings with Karnataka leaders Priyank Kharge and Sharath Bacchegowda in Delhi."
        },
        {
            "name": "Breaking Tech News",
            "claim": "OpenAI releases GPT-5 with new features"
        },
        {
            "name": "Sports News",
            "claim": "India defeats Australia in cricket world cup final"
        },
        {
            "name": "International News",
            "claim": "UN Security Council holds emergency meeting on climate change"
        }
    ]
    
    print("="*100)
    print("NEWS CONFIDENCE SCORING TEST SUITE")
    print("="*100)
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*100}")
        print(f"TEST {i}/{len(test_cases)}: {test['name']}")
        print(f"{'='*100}")
        print(f"CLAIM: {test['claim'][:150]}{'...' if len(test['claim']) > 150 else ''}")
        print("-"*100)
        
        try:
            result = await analyze_claim(test['claim'])
            
            print(f"\n✓ VERDICT: {result['verdict']}")
            print(f"✓ CONFIDENCE: {result['confidence']}%")
            print(f"✓ CLAIM TYPE: {result['claim_type']}")
            print(f"✓ VERIFICATION PATH: {' → '.join(result['verification_path'])}")
            print(f"✓ SOURCES FOUND: {len(result['sources'])}")
            
            # Show sources
            if result['sources']:
                print(f"\n📰 SOURCES:")
                for j, source in enumerate(result['sources'][:5], 1):
                    pub_time = source.get('published_at', 'Unknown')
                    if pub_time and 'T' in pub_time:
                        pub_time = pub_time.split('T')[0]
                    print(f"   {j}. {source['publisher']} ({pub_time})")
            
            # Show key scoring factors
            print(f"\n📊 SCORING FACTORS:")
            key_lines = [line for line in result['explanation'] 
                        if any(keyword in line.lower() for keyword in 
                               ['reputable', 'premium', 'hours', 'credible', 'consistent', 'hedging', 'publisher'])]
            for line in key_lines:
                print(f"   {line}")
            
            # Store result
            results.append({
                "test": test['name'],
                "verdict": result['verdict'],
                "confidence": result['confidence'],
                "sources": len(result['sources'])
            })
            
        except Exception as e:
            print(f"\n✗ ERROR: {e}")
            results.append({
                "test": test['name'],
                "verdict": "ERROR",
                "confidence": 0,
                "sources": 0
            })
    
    # Summary
    print(f"\n{'='*100}")
    print("SUMMARY")
    print("="*100)
    print(f"{'Test Name':<50} {'Verdict':<25} {'Confidence':<12} {'Sources'}")
    print("-"*100)
    for r in results:
        print(f"{r['test']:<50} {r['verdict']:<25} {r['confidence']:<12}% {r['sources']}")
    print("="*100)
    
    # Validate confidence ranges
    print("\n✓ VALIDATION:")
    for r in results:
        if r['verdict'] == "Verified True" or r['verdict'] == "Likely True":
            if r['confidence'] >= 75 and r['confidence'] <= 85:
                print(f"   ✓ {r['test']}: Confidence {r['confidence']}% is within NEWS range (75-85%)")
            elif r['confidence'] >= 65:
                print(f"   ✓ {r['test']}: Confidence {r['confidence']}% is acceptable for fewer sources")
            else:
                print(f"   ⚠ {r['test']}: Confidence {r['confidence']}% may be too low")


if __name__ == "__main__":
    asyncio.run(test_news_confidence())
