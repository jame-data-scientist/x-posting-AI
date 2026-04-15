"""
x_poster.py
Posts tweets via X API v2 using tweepy.
"""

import sys
import tweepy

# Ensure stdout can handle Unicode on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
from config import X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET


def get_client() -> tweepy.Client:
    """Return an authenticated tweepy v2 Client."""
    return tweepy.Client(
        consumer_key=X_API_KEY,
        consumer_secret=X_API_SECRET,
        access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_TOKEN_SECRET,
    )


def post_tweet(content: str) -> str:
    """
    Post a tweet.

    Returns:
        tweet_id (str) on success

    Raises:
        Exception on failure
    """
    client = get_client()
    response = client.create_tweet(text=content)
    tweet_id = str(response.data["id"])
    print(f"[x_poster] [OK] Posted tweet {tweet_id}: {content[:60]}...")
    return tweet_id


def test_connection():
    """Verify credentials are valid by fetching own user info."""
    try:
        client = get_client()
        me = client.get_me()
        print(f"[x_poster] [OK] Connected as @{me.data.username} (id: {me.data.id})")
        return True
    except Exception as e:
        print(f"[x_poster] [FAIL] Connection failed: {e}")
        return False
