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
    "Write a single witty tweet. "
    "30% of the time, make it a standalone funny observation about work, productivity, or builder life — no mention of {app_name}. "
    "70% of the time, make it about {app_name}: pick exactly ONE of these angles: relatable pain point, unexpected analogy, self-aware product joke, or absurdist observation about the problem space. "
    "Humour must feel earned — no forced puns or emoji-as-punchline. "
    "No exclamation marks. Dry > loud."
),
"informative": (
    "Write a single educational tweet. "
    "30% of the time, share a standalone insight about work, productivity, or the problem space {app_name} operates in — no mention of {app_name}. "
    "70% of the time, make it about {app_name}: lead with the insight, not the product — the hook is the surprising fact, stat, or tip. "
    "Frame: choose one — a counterintuitive stat, a concrete before/after, or a step-by-step tip in ≤3 lines. "
    "No vague claims like 'saves time' — use specifics or skip it."
),
"business": (
    "Write a single professional tweet aimed at decision-makers (founders, managers, ops leads). "
    "30% of the time, share a standalone hard-won business lesson or contrarian take — no mention of {app_name}. "
    "70% of the time, make it about {app_name}: lead with outcome — time saved, cost cut, risk reduced, or revenue unlocked. "
    "No jargon: cut 'synergy', 'streamline', 'game-changer', 'robust', 'seamlessly'. "
    "Confident declarative sentences only — no hedging like 'might' or 'could help'. "
    "One clear value claim. Don't stack three benefits — pick the strongest one."
),
"hype": (
    "Write a single high-energy tweet. "
    "30% of the time, make it an energetic take on a builder milestone, a lesson, or a moment in the {app_name} niche — no direct mention of {app_name}. "
    "70% of the time, make it about {app_name}: open with momentum — an action, a milestone number, or a bold claim. "
    "Use short sentences — each one lands before the next begins. "
    "One exclamation mark max. Zero 'game-changer', 'next level', or 'revolutionary'. "
    "End with a pull: what should the reader do or feel next?"
),
"behind-the-scenes": (
    "Write a single behind-the-scenes tweet from the perspective of a founder or builder. "
    "30% of the time, share a raw, personal reflection on building in general — no mention of {app_name}. "
    "70% of the time, make it specific to {app_name}: pick one angle — a hard decision made, a surprising user insight, a shipped-vs-scrapped moment, or a candid milestone reflection. "
    "Voice: first person, honest, no PR polish — reads like a real person, not a company. "
    "The vulnerability or specificity IS the hook — don't bury it. "
    "Avoid: 'Excited to share', 'We're thrilled', 'On this journey'."
),
"question": (
    "Write a single question tweet. "
    "30% of the time, ask a broad, thought-provoking question about work, building, or the niche {app_name} operates in — no mention of {app_name}. "
    "70% of the time, make it directly relevant to {app_name}'s niche. "
    "The question must be specific enough to feel answerable but open enough to invite diverse responses. "
    "Avoid yes/no questions and leading questions like 'Don't you think…?'. "
    "The best replies will be opinions or experiences — not facts."
),
}

TONES_LIST = list(TONE_INSTRUCTIONS.keys())

SYSTEM_PROMPT = """You are a social media expert specialising in mobile app marketing on X (Twitter).
Your job is to write authentic, engaging tweets that grow an indie developer's audience.

Rules:
- Max 250 characters per tweet #IMPORTANT
- No hashtag spam (max 2 relevant hashtags, or none if it feels forced)
- No emojis unless they genuinely add value
- Sound like a real human developer, not a corporate brand
- Never use phrases like "Exciting news!" or "We're thrilled to announce"
- Each tweet must be unique and standalone
- Return ONLY the tweet text, nothing else — no numbering, no quotes, no explanation
"""


def _make_prompt(app_name: str, project_context: str, tone: str) -> str:
    instruction = TONE_INSTRUCTIONS.get(tone, TONE_INSTRUCTIONS["informative"]).format(app_name=app_name)
    return f"""Here is the context about the app called "{app_name}":

{project_context}

---

Tone: {tone.upper()}
Instructions: {instruction}

Write ONE tweet about {app_name} using the above context and tone.
Remember: max 250 chars, sound human, return only the tweet text."""


def _clean_tweet(text: str) -> str:
    if not text:
        return ""
    text = str(text).strip().strip('"').strip("'")
    if len(text) > 250:
        text = text[:247] + "..."
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
