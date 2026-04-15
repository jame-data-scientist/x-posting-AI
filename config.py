"""
config.py
Loads environment variables from .env.
Does NOT call validate() at import time — Streamlit sets keys via UI.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# X API credentials
X_API_KEY             = os.getenv("X_API_KEY", "")
X_API_SECRET          = os.getenv("X_API_SECRET", "")
X_ACCESS_TOKEN        = os.getenv("X_ACCESS_TOKEN", "")
X_ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET", "")
X_BEARER_TOKEN        = os.getenv("X_BEARER_TOKEN", "")

# OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# Gemini (legacy — kept for backward compat)
GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL    = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# App settings
PROJECT_FOLDER  = os.getenv("PROJECT_FOLDER", "./project")
APP_NAME        = os.getenv("APP_NAME", "Height Leveling")
POSTS_PER_DAY   = int(os.getenv("POSTS_PER_DAY", 6))
POST_START_HOUR = int(os.getenv("POST_START_HOUR", 2))
POST_END_HOUR   = int(os.getenv("POST_END_HOUR", 22))

# SQLite DB path
DB_PATH = "posts.db"

# Available post tones
POST_TONES = ["funny", "informative", "business", "hype", "behind-the-scenes", "question"]


def validate():
    """Call this explicitly when you need to verify all credentials are present."""
    missing = []
    required = {
        "X_API_KEY": X_API_KEY,
        "X_API_SECRET": X_API_SECRET,
        "X_ACCESS_TOKEN": X_ACCESS_TOKEN,
        "X_ACCESS_TOKEN_SECRET": X_ACCESS_TOKEN_SECRET,
    }
    for var, val in required.items():
        if not val:
            missing.append(var)
    if missing:
        raise EnvironmentError(
            f"Missing required env vars: {', '.join(missing)}\n"
            "Check your .env file."
        )
