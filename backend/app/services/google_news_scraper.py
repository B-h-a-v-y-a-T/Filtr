"""
Google News RSS Scraper Service
Scrapes news from Google News RSS feed with continent-based filtering.
"""

import requests
from lxml import etree
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Mapping of news sources by continent
CONTINENT_SOURCES = {
    "asia": [
        "Al Jazeera", "The Hindu", "Hindustan Times", "Times of India",
        "Nikkei Asia", "Japan Times", "South China Morning Post",
        "The Straits Times", "Korea Herald", "Dawn", "The Jakarta Post",
        "NDTV", "India Today", "Economic Times", "Business Standard",
        "Mint", "ANI", "PTI", "Asian News International"
    ],
    "europe": [
        "BBC", "DW", "Euronews", "The Guardian", "The Telegraph",
        "Le Monde", "Der Spiegel", "Reuters UK", "Sky News",
        "The Independent", "Financial Times", "The Times"
    ],
    "north america": [
        "CNN", "Fox News", "New York Times", "Washington Post",
        "CBC", "CTV", "ABC News", "NBC News", "NPR", "USA Today",
        "Los Angeles Times", "Chicago Tribune", "Wall Street Journal",
        "Associated Press", "AP News", "Reuters"
    ],
    "south america": [
        "Buenos Aires Herald", "Brazilian Report", "Folha de S.Paulo",
        "El País", "La Nación"
    ],
    "africa": [
        "Africanews", "Daily Nation", "The Star Kenya", "Mail & Guardian",
        "News24", "IOL"
    ],
    "australia": [
        "ABC News (AU)", "The Australian", "Sydney Morning Herald", "SBS",
        "Nine News", "7NEWS"
    ]
}


def detect_continent(source_name: str) -> Optional[str]:
    """
    Detect which continent a news source belongs to.
    
    Args:
        source_name: Name of the news source
        
    Returns:
        Continent name or None if not found
    """
    if source_name is None:
        return None

    source_lower = source_name.lower()

    for continent, sources in CONTINENT_SOURCES.items():
        for s in sources:
            if s.lower() in source_lower:
                return continent

    return None


def scrape_google_news(keyword: str, continent: Optional[str] = None, limit: int = 10) -> List[Dict[str, str]]:
    """
    Scrape news from Google News RSS feed.
    
    Args:
        keyword: Search term for news articles
        continent: Optional continent filter (asia, europe, north america, south america, africa, australia)
        limit: Maximum number of articles to return
        
    Returns:
        List of dictionaries containing article details
    """
    logger.info(f"Searching Google News for: {keyword}" + (f" (continent: {continent})" if continent else ""))

    url = f"https://news.google.com/rss/search?q={keyword.replace(' ', '+')}&hl=en-US&gl=US&ceid=US:en"

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch Google News RSS: {e}")
        return []

    try:
        # Parse XML with lxml
        root = etree.fromstring(response.content)
    except etree.XMLSyntaxError as e:
        logger.error(f"Failed to parse RSS XML: {e}")
        return []

    # RSS items are under /channel/item
    items = root.xpath("//item")

    results = []

    for item in items:
        title = item.xpath("./title/text()")
        link = item.xpath("./link/text()")
        source = item.xpath("./source/text()")
        pub_date = item.xpath("./pubDate/text()")

        title = title[0] if title else ""
        link = link[0] if link else ""
        source = source[0] if source else "Unknown"
        pub_date = pub_date[0] if pub_date else ""

        # Detect continent for this source
        detected_continent = detect_continent(source)

        # Apply continent filter if specified
        if continent:
            if detected_continent != continent.lower():
                continue

        results.append({
            "title": title,
            "link": link,
            "source": source,
            "publishedAt": pub_date,
            "continent": detected_continent or "unknown"
        })

        if len(results) >= limit:
            break

    logger.info(f"Found {len(results)} articles for keyword: {keyword}")
    return results


def get_continent_stats(articles: List[Dict[str, str]]) -> Dict[str, int]:
    """
    Get statistics of articles by continent.
    
    Args:
        articles: List of article dictionaries
        
    Returns:
        Dictionary with continent counts
    """
    stats = {
        "asia": 0,
        "europe": 0,
        "north america": 0,
        "south america": 0,
        "africa": 0,
        "australia": 0,
        "unknown": 0
    }
    
    for article in articles:
        continent = article.get("continent", "unknown")
        if continent in stats:
            stats[continent] += 1
        else:
            stats["unknown"] += 1
    
    return stats


if __name__ == "__main__":
    """CLI interface for testing the scraper"""
    print("=== Google News RSS Scraper ===")
    keyword = input("Enter keyword: ").strip()
    continent = input("Enter continent (Asia, Europe, North America, South America, Africa, Australia) or leave blank: ").strip().lower()

    continent = continent if continent else None

    articles = scrape_google_news(keyword, continent, limit=10)

    print(f"\nTop {len(articles)} results for '{keyword}'" + (f" in {continent}" if continent else "") + "\n")
    
    if not articles:
        print("No articles found for this filter.")
    else:
        for i, a in enumerate(articles, 1):
            print(f"{i}. {a['title']}")
            print(f"   Source: {a['source']} ({a['continent']})")
            print(f"   Link: {a['link']}\n")
