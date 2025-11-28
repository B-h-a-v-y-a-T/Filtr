import asyncio
import logging
from backend.app.services.analysis_engine import verify_claim

# Configure logging to see all output
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def test_news_verification_debug():
    claim = """
    RAHUL GANDHI MEETS CONGRESS LEADERS
    Rahul Gandhi reportedly held meetings with Karnataka leaders Priyank Kharge and Sharath Bacchegowda in Delhi.

    The discussions covered "vote chori," the newly launched KEO AI PC device, the SIR platform, and the broader political situation in Karnataka.

    Priyank Kharge and Sharath Bacchegowda had sought the meeting to brief the Leader of the Opposition on the AI-powered device he was originally scheduled to unveil at the Karnataka Tech Summit.

    Rahul Gandhi questioned the two on the alleged "vote chori" in Aland and the involvement of Chilume, the NGO linked to voter-revision activities.
    """
    
    print("=" * 80)
    print("TESTING NEWS VERIFICATION WITH DEBUG")
    print("=" * 80)
    
    result = await verify_claim(claim)
    
    print("\nVERIFICATION RESULT:")
    print(f"Claim Type: {result.get('claim_type')}")
    print(f"Verification Path: {result.get('verification_path')}")
    print(f"Verdict: {result.get('verdict')}")
    print(f"Confidence: {result.get('confidence')}%")
    print(f"Sources: {len(result.get('sources', []))}")
    print(f"Publishers: {result.get('publisher')}")
    
    print("\nExplanation:")
    for line in result.get('explanation', []):
        print(f"  {line}")

if __name__ == "__main__":
    asyncio.run(test_news_verification_debug())