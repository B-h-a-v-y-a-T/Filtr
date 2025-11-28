"""
Reddit News Scraper Service
Scrapes news posts from multiple news-focused subreddits based on keywords.
"""

import requests
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

NEWS_SUBREDDITS = [
    "news",
    "worldnews",
    "politics",
    "business",
    "technology",
    "science",
    "economics",
    "environment",
    "IndiaNews",
    "IndiaSpeaks",
    "IndianCountryNews",
]


def scrape_news(keyword: str, limit: int = 5) -> List[Dict[str, str]]:
    """
    Scrape news posts from Reddit based on keyword search.
    
    Args:
        keyword: Search term to find relevant posts
        limit: Maximum number of posts to retrieve per subreddit
        
    Returns:
        List of dictionaries containing post details:
        - url: Full Reddit post URL
        - title: Post title
        - subreddit: Source subreddit name
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    results = []

    logger.info(f"Searching Reddit NEWS sources for: {keyword}")

    for sub in NEWS_SUBREDDITS:
        url = f"https://www.reddit.com/r/{sub}/search.json?q={keyword}&restrict_sr=1&limit={limit}"

        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code != 200:
                logger.warning(f"Failed to fetch from r/{sub}: Status {r.status_code}")
                continue

            data = r.json().get("data", {}).get("children", [])

            for post in data:
                p = post["data"]
                title = p.get("title", "")
                permalink = p.get("permalink", "")
                full_url = "https://www.reddit.com" + permalink
                score = p.get("score", 0)
                num_comments = p.get("num_comments", 0)
                created_utc = p.get("created_utc", 0)

                results.append({
                    "url": full_url,
                    "title": title,
                    "subreddit": sub,
                    "score": score,
                    "num_comments": num_comments,
                    "created_utc": created_utc
                })

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout while fetching from r/{sub}")
        except Exception as e:
            logger.error(f"Error scraping r/{sub}: {str(e)}")
            pass

    if not results:
        logger.warning(f"No news posts found for keyword: {keyword}")
        return []

    # Sort by score (engagement) descending
    results.sort(key=lambda x: x.get("score", 0), reverse=True)

    logger.info(f"Found {len(results)} posts for keyword: {keyword}")
    return results[:limit]


def format_scrape_results(results: List[Dict[str, str]]) -> str:
    """
    Format scrape results into a human-readable string.
    
    Args:
        results: List of post dictionaries from scrape_news()
        
    Returns:
        Formatted string with post details
    """
    if not results:
        return "⚠ No news posts found."

    output = "=========== TOP NEWS POSTS ===========\n\n"
    
    for idx, post in enumerate(results, 1):
        output += f"{idx}. {post['url']}\n"
        output += f"   {post['title'][:150]}\n"
        output += f"   Source: r/{post['subreddit']} | "
        output += f"Score: {post['score']} | Comments: {post['num_comments']}\n\n"

    return output


if __name__ == "__main__":
    """CLI interface for testing the scraper"""
    print("=== Reddit News Scraper ===")
    keyword = input("Keyword to search (e.g., war, ai, economy): ").strip()
    max_posts = input("How many posts? (default 5): ").strip()

    limit = int(max_posts) if max_posts.isdigit() else 5

    results = scrape_news(keyword, limit)
    print(format_scrape_results(results))
