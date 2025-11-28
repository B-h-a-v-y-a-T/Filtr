import asyncio
import logging
from backend.app.services.gnews_service import search_gnews

# Configure logging to see all output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def test_gnews_search():
    # Test multiple queries
    queries = [
        "Rahul Gandhi meets Congress leaders Priyank Kharge Karnataka",
        "Rahul Gandhi Karnataka",
        "Priyank Kharge Congress",
        "Karnataka Congress meeting",
        "Rahul Gandhi Congress meeting Delhi"
    ]
    
    print("=" * 80)
    print("TESTING GNEWS SEARCH")
    print("=" * 80)
    
    for claim in queries:
        print(f"\n\nQuery: '{claim}'")
        print("-" * 80)
        result = await asyncio.to_thread(search_gnews, claim, max_results=5)
        
        print(f"Has articles: {result.get('has_articles')}")
        print(f"Articles count: {len(result.get('articles', []))}")
        
        if result.get('articles'):
            print("Articles found:")
            for i, article in enumerate(result.get('articles', [])[:3], 1):
                print(f"  {i}. {article.get('title')[:60]}... - {article.get('source')}")

if __name__ == "__main__":
    asyncio.run(test_gnews_search())