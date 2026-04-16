"""
ai_generator_v2.py
Generates X (Twitter) posts using:
  - OpenRouter (any model via OPENROUTER_API_KEY in .env)
  - Google Gemini native (via GEMINI_API_KEY in .env)
"""

import google.generativeai as genai
from folder_reader import read_project_folder
from openrouter_models import generate_with_openrouter

# ── Tone definitions ──────────────────────────────────────────────────────────
TONE_INSTRUCTIONS = {
    "funny": (
        "Write a witty, humorous tweet about the app. Use light humour, relatable pain points, "
        "or a funny observation. Keep it natural and shareable."
    ),
    "informative": (
        "Write a clear, useful tweet that teaches the reader something about the app or problem it solves. "
        "Could be a tip, a stat, a 'did you know', or a feature highlight."
    ),
    "business": (
        "Write a professional, value-focused tweet. Highlight ROI, time saved, or productivity benefits. "
        "Tone: confident, credible, not salesy."
    ),
    "hype": (
        "Write an energetic, exciting tweet that builds anticipation or celebrates the app. "
        "Use momentum language. Short punchy sentences. Think startup launch energy."
    ),
    "behind-the-scenes": (
        "Write a transparent, authentic tweet that gives a glimpse behind the scenes — "
        "why you built this, a challenge you faced, a lesson learned, or a milestone."
    ),
    "question": (
        "Write an engaging question tweet that invites replies. "
        "Relevant to your app's niche. Goal: start a conversation."
    ),
}

TONES_LIST = list(TONE_INSTRUCTIONS.keys())

SYSTEM_PROMPT = """You are a social media expert specialising in mobile app marketing on X (Twitter).
Your job is to write authentic, engaging tweets that grow an indie developer's audience.

Rules:
- Max 280 characters per tweet
- No hashtag spam (max 2 relevant hashtags, or none if it feels forced)
- No emojis unless they genuinely add value
- Sound like a real human developer, not a corporate brand
- Never use phrases like "Exciting news!" or "We're thrilled to announce"
- Each tweet must be unique and standalone
- Return ONLY the tweet text, nothing else — no numbering, no quotes, no explanation
"""


def _make_prompt(app_name: str, project_context: str, tone: str) -> str:
    instruction = TONE_INSTRUCTIONS.get(tone, TONE_INSTRUCTIONS["informative"])
    return f"""Here is the context about the app called "{app_name}":

{project_context}

---

Tone: {tone.upper()}
Instructions: {instruction}

Write ONE tweet about {app_name} using the above context and tone.
Remember: max 280 chars, sound human, return only the tweet text."""


def _clean_tweet(text: str) -> str:
    if not text:
        return ""
    text = str(text).strip().strip('"').strip("'")
    if len(text) > 280:
        text = text[:277] + "..."
    return text


# ── OpenRouter backend ────────────────────────────────────────────────────────
def generate_posts_openrouter(
    openrouter_api_key: str,
    model_id: str,
    app_name: str,
    project_folder: str,
    count: int = 6,
    progress_callback=None,
) -> list[dict]:
    """Generate tweets via OpenRouter. Returns list of {'tone', 'content'}."""
    project_context = read_project_folder(project_folder)
    posts = []

    import time
    for i in range(count):
        tone = TONES_LIST[i % len(TONES_LIST)]
        prompt = _make_prompt(app_name, project_context, tone)

        if progress_callback:
            progress_callback(i, count, tone)

        try:
            text = generate_with_openrouter(
                api_key=openrouter_api_key,
                model_id=model_id,
                system_prompt=SYSTEM_PROMPT,
                user_prompt=prompt,
            )
            posts.append({"tone": tone, "content": _clean_tweet(text)})
        except Exception as e:
            posts.append({"tone": tone, "content": f"[ERROR: {e}]"})
            
        # Add a delay to prevent 429 Too Many Requests on free-tier models
        if i < count - 1:
            time.sleep(2)

    if progress_callback:
        progress_callback(count, count, "done")

    return posts


# ── Google Gemini native backend ──────────────────────────────────────────────
def generate_posts_gemini(
    gemini_api_key: str,
    model_id: str,
    app_name: str,
    project_folder: str,
    count: int = 6,
    progress_callback=None,
) -> list[dict]:
    """Generate tweets via Google Gemini native API. Returns list of {'tone', 'content'}."""
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel(
        model_name=model_id,
        system_instruction=SYSTEM_PROMPT,
    )

    project_context = read_project_folder(project_folder)
    posts = []

    import time
    for i in range(count):
        tone = TONES_LIST[i % len(TONES_LIST)]
        prompt = _make_prompt(app_name, project_context, tone)

        if progress_callback:
            progress_callback(i, count, tone)

        try:
            response = model.generate_content(prompt)
            text = response.text
            posts.append({"tone": tone, "content": _clean_tweet(text)})
        except Exception as e:
            posts.append({"tone": tone, "content": f"[ERROR: {e}]"})
            
        # Add a delay for Gemini free tier rate limits (15 RPM)
        if i < count - 1:
            time.sleep(3)

    if progress_callback:
        progress_callback(count, count, "done")

    return posts


# ── Unified entry point ───────────────────────────────────────────────────────
def generate_posts(
    provider: str,       # "OpenRouter" or "Google Gemini"
    model_id: str,
    app_name: str,
    project_folder: str,
    api_key: str,        # OPENROUTER_API_KEY or GEMINI_API_KEY from .env
    count: int = 6,
    progress_callback=None,
) -> list[dict]:
    """Unified generate function. Dispatches to correct backend."""
    if provider == "Google Gemini":
        return generate_posts_gemini(
            gemini_api_key=api_key,
            model_id=model_id,
            app_name=app_name,
            project_folder=project_folder,
            count=count,
            progress_callback=progress_callback,
        )
    else:  # OpenRouter (default)
        return generate_posts_openrouter(
            openrouter_api_key=api_key,
            model_id=model_id,
            app_name=app_name,
            project_folder=project_folder,
            count=count,
            progress_callback=progress_callback,
        )
