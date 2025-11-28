import asyncio
from backend.app.services.analysis_engine import verify_claim

async def test_news_claim():
    claim = """
    RAHUL GANDHI MEETS CONGRESS LEADERS
    Rahul Gandhi reportedly held meetings with Karnataka leaders Priyank Kharge and Sharath Bacchegowda in Delhi.

    The discussions covered "vote chori," the newly launched KEO AI PC device, the SIR platform, and the broader political situation in Karnataka.

    Priyank Kharge and Sharath Bacchegowda had sought the meeting to brief the Leader of the Opposition on the AI-powered device he was originally scheduled to unveil at the Karnataka Tech Summit.

    Rahul Gandhi questioned the two on the alleged "vote chori" in Aland and the involvement of Chilume, the NGO linked to voter-revision activities.
    """
    result = await verify_claim(claim)
    print(result)

if __name__ == "__main__":
    asyncio.run(test_news_claim())