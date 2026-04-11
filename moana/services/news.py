"""
News service — fetches headlines + descriptions, then uses Claude
to write a conversational brief (like Morning Brew / TechCrunch Daily).
Falls back to raw headlines if Claude is unavailable.
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

_SEARCH_QUERIES = {
    "ai_tech": "artificial intelligence OR AI startup OR LLM OR machine learning",
    "startups": "startup funding OR venture capital OR YC OR series A",
}


def _fetch_gnews_category(category: str, country: str = None, max_results: int = 5) -> list:
    """Fetch from GNews top-headlines with descriptions."""
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
        {
            "title": a.get("title", ""),
            "description": a.get("description", ""),
            "content": a.get("content", ""),
            "url": a.get("url", ""),
            "source": a.get("source", {}).get("name", "Unknown"),
        }
        for a in articles[:max_results]
    ]


def _fetch_gnews_search(query: str, max_results: int = 5) -> list:
    """Fetch from GNews search with descriptions."""
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
        {
            "title": a.get("title", ""),
            "description": a.get("description", ""),
            "content": a.get("content", ""),
            "url": a.get("url", ""),
            "source": a.get("source", {}).get("name", "Unknown"),
        }
        for a in articles[:max_results]
    ]


def _fetch_rss(feed_url: str, max_results: int = 5) -> list:
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
            "description": getattr(entry, "summary", ""),
            "content": "",
            "url": getattr(entry, "link", ""),
            "source": source_name,
        })
    return results


def _clean_title(title: str) -> str:
    """Remove trailing ' - Source Name' from titles."""
    cleaned = re.sub(r"\s*[\-–—|]\s*[A-Z][\w\s.'']+$", "", title)
    if len(cleaned) >= 20:
        return cleaned
    return title


def get_all_news_raw() -> dict:
    """Fetch raw article data from all 4 categories."""
    results = {}

    for key, cat_config in config.NEWS_CATEGORIES.items():
        try:
            if key in _SEARCH_QUERIES:
                articles = _fetch_gnews_search(_SEARCH_QUERIES[key], max_results=5)
            else:
                articles = _fetch_gnews_category(
                    cat_config["gnews_category"],
                    cat_config.get("gnews_country"),
                    max_results=5,
                )

            if articles:
                for a in articles:
                    a["title"] = _clean_title(a["title"])
                results[key] = articles
                continue
        except Exception as e:
            log.warning(f"GNews failed for {key}: {e}")

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


def summarize_news(raw_news: dict) -> dict:
    """Use Claude to turn raw articles into a conversational brief.
    Returns dict with same keys but values are summarized text strings.
    Falls back to raw headlines if Claude is unavailable.
    """
    if not config.ANTHROPIC_API_KEY:
        log.info("No Anthropic API key — using raw headlines")
        return _fallback_format(raw_news)

    try:
        from core.claude_client import oneshot

        # Build the prompt with all articles
        articles_text = ""
        for key, articles in raw_news.items():
            label = config.NEWS_CATEGORIES.get(key, {}).get("label", key)
            articles_text += f"\n--- {label} ---\n"
            for a in articles:
                desc = a.get("description", "") or a.get("content", "")
                articles_text += f"- {a['title']} ({a['source']})\n"
                if desc:
                    articles_text += f"  {desc[:200]}\n"

        prompt = f"""Here are today's news articles grouped by category. Write a conversational daily brief — like Morning Brew or TechCrunch Daily podcast style.

Rules:
- Write 2-4 sentences per category summarizing the KEY stories, not every single one
- Be conversational and concise — imagine you're texting a friend the highlights
- Don't list every article — pick the most important 2-3 per category and weave them together
- Skip fluff articles (product reviews, listicles, gaming updates) — focus on actual news
- No bullet points — write in flowing paragraphs
- Keep each category section to ~50-80 words max
- Don't include URLs or source attributions in the text

Format your response EXACTLY like this (keep the category headers):

🇺🇸 U.S. News
[your summary paragraph]

🌍 World News
[your summary paragraph]

🤖 AI & Tech
[your summary paragraph]

🚀 Startups & Business
[your summary paragraph]

Here are the articles:
{articles_text}"""

        summary = oneshot(
            api_key=config.ANTHROPIC_API_KEY,
            model=config.CLAUDE_MODEL,
            prompt=prompt,
            system_prompt=(
                "You are a news briefing writer. Write like Morning Brew — "
                "smart, concise, slightly witty, no fluff. "
                "Your reader is a 23-year-old Cornell engineering grad student "
                "who cares about tech, startups, and global affairs."
            ),
            max_tokens=1024,
        )

        return {"summary": summary, "raw": raw_news}

    except Exception as e:
        log.warning(f"Claude news summary failed, using raw: {e}")
        return _fallback_format(raw_news)


def _fallback_format(raw_news: dict) -> dict:
    """If Claude is unavailable, return raw articles for the old-style display."""
    return {"summary": None, "raw": raw_news}


def get_all_news() -> dict:
    """Main entry point — fetch + summarize."""
    raw = get_all_news_raw()
    return summarize_news(raw)