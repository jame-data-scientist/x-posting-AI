"""
openrouter_models.py
Live model fetching from OpenRouter API with free-model detection.
Also contains Google Gemini native model registry.
"""

import requests
from typing import Optional

OPENROUTER_API_URL  = "https://openrouter.ai/api/v1/models"

# ─── Google Gemini native models ─────────────────────────────────────────────
GOOGLE_PROVIDERS = {
    "Gemini 2.5": [
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
    ],
    "Gemma 4": [
        "gemma-4-31b-it",
        "gemma-4-26b-a4b-it",
    ],
    "Gemma 3": [
        "gemma-3-27b-it",
        "gemma-3-12b-it",
        "gemma-3-4b-it",
        "gemma-3-1b-it",
    ],
    "Gemini 2.0": [
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
    ],
    "Gemini 1.5": [
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
    ],

    "Gemini 1.0": [
        "gemini-1.0-pro",
    ],
}

GOOGLE_GEMINI_MODELS = [m for fam in GOOGLE_PROVIDERS.values() for m in fam]


# ─── Provider name mapping ────────────────────────────────────────────────────
PROVIDER_NAME_MAP = {
    "openai":                "OpenAI",
    "anthropic":             "Anthropic",
    "google":                "Google",
    "meta-llama":            "Meta (Llama)",
    "mistralai":             "Mistral AI",
    "deepseek":              "DeepSeek",
    "x-ai":                  "xAI (Grok)",
    "qwen":                  "Qwen (Alibaba)",
    "cohere":                "Cohere",
    "perplexity":            "Perplexity",
    "amazon":                "Amazon",
    "microsoft":             "Microsoft / Phi",
    "nvidia":                "NVIDIA",
    "01-ai":                 "01.AI (Yi)",
    "inflection":            "Inflection",
    "cognitivecomputations": "CognitiveComputations",
    "nousresearch":          "Nous Research",
    "liquid":                "Liquid AI",
    "sao10k":                "Sao10k",
    "pygmalionai":           "PygmalionAI",
    "undi95":                "Undi95",
    "sophosympatheia":       "SophoSympatheia",
    "thedrummer":            "TheDrummer",
    "eva-unit-01":           "Eva Unit 01",
    "koboldai":              "KoboldAI",
    "allenai":               "AllenAI",
    "huggingfaceh4":         "HuggingFace H4",
    "openchat":              "OpenChat",
    "teknium":               "Teknium",
    "gryphe":                "Gryphe",
    "recursal":              "Recursal",
    "jondurbin":             "Jon Durbin",
    "mancer":                "Mancer",
    "phind":                 "Phind",
    "rwkv":                  "RWKV",
    "ai21":                  "AI21 Labs",
    "databricks":            "Databricks",
    "togethercomputer":      "Together Computer",
    "neversleep":            "Neversleep",
    "aetherwiing":           "Aetherwiing",
    "alpindale":             "Alpindale",
    "migtissera":            "MigTissera",
    "sorcererlm":            "SorcererLM",
}

def _provider_display(model_id: str) -> str:
    """Return a clean provider name from model ID like 'openai/gpt-4o'."""
    prefix = model_id.split("/")[0].lower()
    return PROVIDER_NAME_MAP.get(prefix, prefix.replace("-", " ").title())


# ─── Free model detection ─────────────────────────────────────────────────────
def _is_free(model: dict) -> bool:
    """Detect if a model is free (zero pricing or :free suffix)."""
    if model.get("id", "").endswith(":free"):
        return True
    pricing = model.get("pricing", {})
    try:
        prompt_cost     = float(pricing.get("prompt", "1") or "1")
        completion_cost = float(pricing.get("completion", "1") or "1")
        return prompt_cost == 0 and completion_cost == 0
    except (ValueError, TypeError):
        return False


def _ctx_label(ctx: int) -> str:
    if ctx >= 1_000_000: return f"{ctx // 1_000_000}M ctx"
    if ctx >= 1_000:     return f"{ctx // 1_000}k ctx"
    return str(ctx)


def model_display_label(model: dict) -> str:
    """
    Build the dropdown label for an OpenRouter model.
    e.g.  "🆓 GPT-4o Mini  [128k]"  or  "GPT-4o  [128k]"
    """
    free_badge = "🆓 " if _is_free(model) else "   "
    name = model.get("name") or model["id"].split("/")[-1].replace("-", " ").title()
    ctx  = model.get("context_length", 0)
    ctx_str = f"  [{_ctx_label(ctx)}]" if ctx else ""
    return f"{free_badge}{name}{ctx_str}"


# ─── Live fetch ───────────────────────────────────────────────────────────────
def fetch_all_models(api_key: str) -> list[dict]:
    """
    Fetch ALL models from OpenRouter API.
    Returns list of model dicts. Each has: id, name, context_length, pricing, is_free.
    Falls back to empty list on error.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer":  "https://heightleveling.app",
        "X-Title":       "Height Leveling Twitter Bot",
    }
    try:
        r = requests.get(OPENROUTER_API_URL, headers=headers, timeout=12)
        r.raise_for_status()
        models = r.json().get("data", [])
        # Enrich with computed fields
        for m in models:
            m["is_free"]         = _is_free(m)
            m["provider_name"]   = _provider_display(m["id"])
            m["display_label"]   = model_display_label(m)
        # Sort: free first within each group, then alphabetical by id
        models.sort(key=lambda m: (m["provider_name"], not m["is_free"], m["id"]))
        return models
    except Exception as e:
        return []


def group_by_provider(models: list[dict]) -> dict[str, list[dict]]:
    """Group flat model list into {provider_name: [model, ...]}."""
    groups: dict[str, list[dict]] = {}
    for m in models:
        p = m.get("provider_name", "Other")
        groups.setdefault(p, []).append(m)
    return dict(sorted(groups.items()))


# ─── OpenRouter generate call ─────────────────────────────────────────────────
def generate_with_openrouter(
    api_key: str,
    model_id: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.8,
    max_tokens: int = 400,
) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type":  "application/json",
        "HTTP-Referer":  "https://heightleveling.app",
        "X-Title":       "Height Leveling Twitter Bot",
    }
    payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens":  max_tokens,
    }
    # Implement retry loop for 429 Too Many Requests
    import time
    max_retries = 3
    for attempt in range(max_retries):
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers, json=payload, timeout=60,
        )
        if r.status_code == 429 and attempt < max_retries - 1:
            time.sleep(3 + attempt * 2) # Exponential-ish backoff: 3s, 5s...
            continue
        break
        
    r.raise_for_status()
    
    data = r.json()
    choices = data.get("choices", [])
    if not choices:
        return ""
        
    msg = choices[0].get("message", {})
    content = msg.get("content")
    
    if content is None:
        return ""
        
    return content.strip()
