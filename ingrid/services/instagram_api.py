"""
Instagram Graph API integration — Tier 3 (future).

When connected, this will:
- Auto-pull analytics (reach, engagement, follower growth)
- Track competitor accounts
- Suggest optimal posting times from real data
- Generate data-driven weekly reports

Setup requires:
1. Meta Developer account
2. Instagram Business/Creator account connected to a Facebook Page
3. Instagram Graph API access token
4. Set INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_BUSINESS_ID in .env
"""

import logging
from ingrid import config

log = logging.getLogger(__name__)


def is_connected() -> bool:
    """Check if Instagram API is configured."""
    return bool(config.INSTAGRAM_ACCESS_TOKEN and config.INSTAGRAM_BUSINESS_ID)


def get_account_insights(period: str = "day", days: int = 30) -> dict | None:
    """Fetch account-level insights. Returns None if not connected."""
    if not is_connected():
        return None

    # TODO: Implement when API is connected
    # GET /{ig-user-id}/insights?metric=reach,impressions,follower_count
    #   &period={period}&since={since}&until={until}
    log.info("Instagram API: get_account_insights — not yet implemented")
    return None


def get_media_insights(media_id: str) -> dict | None:
    """Fetch insights for a specific post/reel."""
    if not is_connected():
        return None

    # TODO: Implement
    # GET /{media-id}/insights?metric=engagement,impressions,reach,saved,shares
    log.info("Instagram API: get_media_insights — not yet implemented")
    return None


def get_recent_media(count: int = 10) -> list | None:
    """Fetch recent posts with metrics."""
    if not is_connected():
        return None

    # TODO: Implement
    # GET /{ig-user-id}/media?fields=id,caption,media_type,timestamp,like_count,
    #   comments_count,insights.metric(reach,impressions,engagement,saved,shares)
    log.info("Instagram API: get_recent_media — not yet implemented")
    return None


def get_audience_demographics() -> dict | None:
    """Fetch audience demographics (age, gender, location)."""
    if not is_connected():
        return None

    # TODO: Implement
    # GET /{ig-user-id}/insights?metric=audience_city,audience_country,
    #   audience_gender_age&period=lifetime
    log.info("Instagram API: get_audience_demographics — not yet implemented")
    return None
