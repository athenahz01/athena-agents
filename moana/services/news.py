"""
News service — curated headlines for Moana's brief.
Categories: U.S. News, World News, AI & Tech, Startups & Business.
Uses keyword search for niche categories to get relevant results.
"""

import logging
import re
import requests
import feedparser
from moana import config

log = logging.getLogger(__name__)

_RSS_FEEDS = {
    "us_news": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
    "world_news": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en",
    "ai_tech": "https://news.google.com/rss/search?q=artificial+intelligence+OR+AI+startup+OR+machine+learning&hl=en-US&gl=US&ceid=US:en",
    "startups": "https://news.google.com/rss/search?q=startup+funding+OR+venture+capital+OR+series+A&hl=en-US&gl=US&ceid=US:en",
}

# Keyword searches for niche categories (more relevant than category-based)
_SEARCH_QUERIES = {
    "ai_tech": "artificial intelligence OR AI startup OR LLM OR machine learning",
    "startups": "startup funding OR venture capital OR YC OR series A",
}


def _fetch_gnews_category(category: str, country: str = None, max_results: int = 4) -> list:
    """Fetch headlines from GNews top-headlines (category-based)."""
    url = "https://gnews.io/api/v4/top-headlines"
    params = {
        "category": category,
        "lang": "en",
        "max": max_results,
        "apikey": config.GNEWS_API_KEY,
    }
    if country:
        params["country"] = country

    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    articles = resp.json().get("articles", [])

    return [
        {"title": a["title"], "url": a["url"], "source": a["source"]["name"]}
        for a in articles[:max_results]
    ]


def _fetch_gnews_search(query: str, max_results: int = 4) -> list:
    """Fetch headlines from GNews search (keyword-based, much more relevant)."""
    url = "https://gnews.io/api/v4/search"
    params = {
        "q": query,
        "lang": "en",
        "max": max_results,
        "sortby": "publishedAt",
        "apikey": config.GNEWS_API_KEY,
    }

    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    articles = resp.json().get("articles", [])

    return [
        {"title": a["title"], "url": a["url"], "source": a["source"]["name"]}
        for a in articles[:max_results]
    ]


def _fetch_rss(feed_url: str, max_results: int = 4) -> list:
    """Fallback: Google News RSS."""
    feed = feedparser.parse(feed_url)
    results = []
    for entry in feed.entries[:max_results]:
        source = entry.get("source", {})
        if isinstance(source, dict):
            source_name = source.get("title", "Unknown")
        else:
            source_name = str(source) if source else "Unknown"
        results.append({
            "title": getattr(entry, "title", "Untitled"),
            "url": getattr(entry, "link", ""),
            "source": source_name,
        })
    return results


def _clean_title(title: str) -> str:
    """Remove trailing ' - Source Name' from titles since we show source separately."""
    # Match patterns like " - CNN", " | Reuters", " — The New York Times"
    cleaned = re.sub(r"\s*[\-–—|]\s*[A-Z][\w\s.'']+$", "", title)
    # Only use cleaned if it didn't strip too much (at least 20 chars left)
    if len(cleaned) >= 20:
        return cleaned
    return title


def get_all_news() -> dict:
    """Fetch all 4 news categories. Falls back to RSS if GNews fails."""
    results = {}

    for key, cat_config in config.NEWS_CATEGORIES.items():
        try:
            # Use keyword search for niche categories (AI, startups)
            if key in _SEARCH_QUERIES:
                articles = _fetch_gnews_search(_SEARCH_QUERIES[key], max_results=4)
            else:
                articles = _fetch_gnews_category(
                    cat_config["gnews_category"],
                    cat_config.get("gnews_country"),
                    max_results=4,
                )

            if articles:
                # Clean titles that embed the source name
                for a in articles:
                    a["title"] = _clean_title(a["title"])
                results[key] = articles
                continue
        except Exception as e:
            log.warning(f"GNews failed for {key}: {e}")

        # Fallback to RSS
        if key in _RSS_FEEDS:
            try:
                articles = _fetch_rss(_RSS_FEEDS[key])
                for a in articles:
                    a["title"] = _clean_title(a["title"])
                results[key] = articles
            except Exception as e:
                log.error(f"RSS also failed for {key}: {e}")
                results[key] = []
        else:
            results[key] = []

    return results