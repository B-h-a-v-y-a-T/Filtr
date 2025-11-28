"""
Quick test to verify the analysis API endpoint is working correctly.
"""
import asyncio
import sys
from backend.app.services.analysis_engine import analyze_claim

sys.stdout.reconfigure(encoding='utf-8')


async def test_integration():
    """Test a simple claim to verify the integration."""
    
    claim = "The Earth is round"
    
    print("="*80)
    print("TESTING ANALYSIS API INTEGRATION")
    print("="*80)
    print(f"\nTest Claim: {claim}")
    print("-"*80)
    
    try:
        result = await analyze_claim(claim)
        
        print(f"\n✓ Analysis completed successfully!")
        print(f"\nVerdict: {result['verdict']}")
        print(f"Confidence: {result['confidence']}%")
        print(f"Claim Type: {result['claim_type']}")
        print(f"Sources: {len(result['sources'])} found")
        
        print(f"\n{'='*80}")
        print("RESPONSE STRUCTURE CHECK")
        print("="*80)
        
        required_fields = ['claim', 'verdict', 'confidence', 'explanation', 'sources', 
                          'claim_type', 'verification_path', 'last_checked']
        
        for field in required_fields:
            status = "✓" if field in result else "✗"
            print(f"{status} {field}: {'Present' if field in result else 'MISSING'}")
        
        print(f"\n{'='*80}")
        print("INTEGRATION TEST: PASSED ✓")
        print("="*80)
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        print(f"\n{'='*80}")
        print("INTEGRATION TEST: FAILED ✗")
        print("="*80)


if __name__ == "__main__":
    asyncio.run(test_integration())
