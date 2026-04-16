"""
streamlit_app.py  —  Height Leveling · X Auto Poster
API keys loaded from .env ONLY.
Provider → Model two-level selector.
All 300+ OpenRouter models loaded live with FREE badges.
"""

import streamlit as st
import os
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path=env_path, override=True)
# ─── Page config MUST be first ───────────────────────────────────────────────
st.set_page_config(
    page_title="Height Leveling · X Auto Poster",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html,body,[class*="css"]{font-family:'Inter',sans-serif;color:#E8EBF0;}

.stApp{background:linear-gradient(135deg,#0D1117 0%,#131920 50%,#0D1117 100%);min-height:100vh;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#161D26,#111820);border-right:1px solid #1E2D3D;}

.glass-card{background:rgba(22,29,38,.85);border:1px solid #1E2D3D;border-radius:16px;padding:24px;margin-bottom:16px;}
.glass-card:hover{border-color:#3B82F680;}

.metric-card{background:rgba(22,29,38,.9);border:1px solid #1E2D3D;border-radius:12px;padding:18px;text-align:center;transition:all .3s ease;}
.metric-card:hover{border-color:#3B82F6;transform:translateY(-2px);box-shadow:0 8px 32px rgba(59,130,246,.15);}
.metric-number{font-size:36px;font-weight:800;background:linear-gradient(135deg,#3B82F6,#8B5CF6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1.2;}
.metric-label{font-size:12px;color:#64748B;font-weight:500;margin-top:4px;text-transform:uppercase;letter-spacing:.5px;}

.timeline-item{display:flex;align-items:center;gap:12px;padding:10px 14px;border-radius:10px;margin-bottom:8px;background:rgba(255,255,255,.02);border:1px solid #1E2D3D;font-size:14px;transition:all .2s ease;}
.timeline-item:hover{background:rgba(59,130,246,.06);border-color:#3B82F640;}
.timeline-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0;}
.dot-done{background:#22C55E;box-shadow:0 0 8px #22C55E60;}
.dot-next{background:#3B82F6;box-shadow:0 0 8px #3B82F660;animation:pulse 2s infinite;}
.dot-future{background:#1E2D3D;}
@keyframes pulse{0%,100%{transform:scale(1);opacity:1;}50%{transform:scale(1.3);opacity:.7;}}

.log-console{background:#0A0E14;border:1px solid #1E2D3D;border-radius:12px;padding:16px;font-family:'JetBrains Mono',monospace;font-size:12px;max-height:320px;overflow-y:auto;line-height:1.7;}
.log-ok{color:#22C55E;}.log-err{color:#EF4444;}.log-wrn{color:#F59E0B;}.log-inf{color:#3B82F6;}.log-def{color:#64748B;}

.tweet-card{background:rgba(22,29,38,.95);border:1px solid #1E2D3D;border-radius:14px;padding:18px 20px;margin-bottom:12px;position:relative;overflow:hidden;transition:all .25s ease;}
.tweet-card::before{content:'';position:absolute;left:0;top:0;bottom:0;width:3px;border-radius:3px 0 0 3px;}
.tweet-card.posted::before{background:#22C55E;}.tweet-card.pending::before{background:#3B82F6;}.tweet-card.failed::before{background:#EF4444;}
.tweet-card:hover{border-color:#3B82F6;transform:translateX(3px);}
.tweet-content{font-size:15px;line-height:1.6;color:#CBD5E1;margin-bottom:10px;}
.tweet-meta{display:flex;gap:12px;flex-wrap:wrap;font-size:12px;color:#475569;align-items:center;}
.tone-chip{background:#1E2D3D;color:#94A3B8;padding:3px 10px;border-radius:6px;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.5px;}

.badge{display:inline-block;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.5px;}
.badge-live{background:#0D2A1A;color:#22C55E;border:1px solid #22C55E40;}
.badge-idle{background:#1A1A2A;color:#94A3B8;border:1px solid #94A3B840;}
.badge-posted{background:#0D2A1A;color:#22C55E;border:1px solid #22C55E40;}
.badge-pending{background:#1A2A0D;color:#84CC16;border:1px solid #84CC1640;}
.badge-failed{background:#2A0D0D;color:#EF4444;border:1px solid #EF444440;}

.hero-title{font-size:44px;font-weight:800;text-align:center;background:linear-gradient(135deg,#3B82F6 0%,#8B5CF6 50%,#EC4899 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1.1;margin-bottom:6px;}
.hero-sub{font-size:16px;color:#64748B;text-align:center;}

.model-pill-or{background:linear-gradient(135deg,#1E3A5F,#0D2040);border:1px solid #3B82F640;border-radius:8px;padding:8px 12px;font-size:12px;color:#60A5FA;font-family:'JetBrains Mono',monospace;margin-top:4px;word-break:break-all;}
.model-pill-goog{background:linear-gradient(135deg,#1A2E1A,#0D1F0D);border:1px solid #22C55E40;border-radius:8px;padding:8px 12px;font-size:12px;color:#4ADE80;font-family:'JetBrains Mono',monospace;margin-top:4px;}
.free-tag{background:#0D2A1A;color:#22C55E;border:1px solid #22C55E40;border-radius:4px;padding:1px 6px;font-size:10px;font-weight:700;letter-spacing:.5px;margin-left:6px;}

div[data-testid="stSelectbox"]>div>div{background:#162030!important;border:1px solid #1E2D3D!important;border-radius:10px!important;color:#CBD5E1!important;}
div[data-testid="stTextInput"] input{background:#162030!important;border:1px solid #1E2D3D!important;border-radius:10px!important;color:#CBD5E1!important;}
label,.stTextInput>label,.stSelectbox>label{color:#94A3B8!important;font-size:13px!important;}
.stButton>button{border-radius:10px!important;font-weight:600!important;transition:all .2s ease!important;}
.stButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 4px 20px rgba(59,130,246,.25)!important;}
hr{border-color:#1E2D3D!important;margin:16px 0!important;}
::-webkit-scrollbar{width:5px;}::-webkit-scrollbar-track{background:#0D1117;}::-webkit-scrollbar-thumb{background:#1E2D3D;border-radius:3px;}
</style>
""", unsafe_allow_html=True)

# ─── Imports ──────────────────────────────────────────────────────────────────
from post_queue import init_db, get_all_posts, get_pending_posts, delete_post, add_posts
from scheduler_v2 import (
    get_scheduler, get_scheduled_times_for_today_est,
    get_scheduled_times_for_tomorrow_est, POST_TIMES_EST, EST
)
from openrouter_models import (
    fetch_all_models, group_by_provider,
    GOOGLE_PROVIDERS, GOOGLE_GEMINI_MODELS
)
from x_poster import test_connection
from ai_generator_v2 import generate_posts

# ─── Keys from .env ONLY ──────────────────────────────────────────────────────
def get_or_key():
    # Check Streamlit secrets first (for Cloud), then local .env or os environ
    try:
        val = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY", ""))
    except Exception:
        val = os.getenv("OPENROUTER_API_KEY", "")
    return str(val).strip().strip(' "\'') if val else ""

def get_gemini_key():
    try:
        val = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
    except Exception:
        val = os.getenv("GEMINI_API_KEY", "")
    return str(val).strip().strip(' "\'') if val else ""

APP_NAME = os.getenv("APP_NAME", "Height Leveling")
PROJ_DIR = os.getenv("PROJECT_FOLDER", "./project")

# ─── Session state ────────────────────────────────────────────────────────────
def _init():
    defs = {
        "provider":        "Google Gemini" if (get_gemini_key() and not get_or_key()) else "OpenRouter",
        "or_models":       [],      # all OpenRouter models (live fetched)
        "or_fetched":      False,
        "or_prov_filter":  "All",
        "or_model_id":     "openrouter/elephant-alpha",
        "google_family":   "Gemini 2.0",
        "google_model":    "gemini-2.0-flash",
        "app_name":        APP_NAME,
        "proj_dir":        PROJ_DIR,
        "preview_tweets":  [],
    }
    for k, v in defs.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()
init_db()

# ─── Auto-fetch OpenRouter models on first load ───────────────────────────────
if get_or_key() and not st.session_state.or_fetched:
    with st.spinner("⏳ Loading OpenRouter models..."):
        models = fetch_all_models(get_or_key())
        st.session_state.or_models  = models
        st.session_state.or_fetched = True

# ─── Helpers ──────────────────────────────────────────────────────────────────
def _api_key():
    return get_gemini_key() if st.session_state.provider == "Google Gemini" else get_or_key()

def _active_model():
    return (st.session_state.google_model
            if st.session_state.provider == "Google Gemini"
            else st.session_state.or_model_id)

def _log_class(l):
    if "✅" in l or "ok" in l.lower():                    return "log-ok"
    if "❌" in l or "fail" in l.lower() or "error" in l.lower(): return "log-err"
    if "⚠️" in l or "warn" in l.lower():                  return "log-wrn"
    if any(e in l for e in ("🤖","🔄","ℹ","📤","▶")):     return "log-inf"
    return "log-def"

def _render_logs(lines):
    html = "".join(f'<div class="{_log_class(l)}">{l}</div>' for l in reversed(lines))
    return f'<div class="log-console">{html}</div>'

def _badge(status):
    m = {"posted":"badge-posted","pending":"badge-pending","failed":"badge-failed"}
    return f'<span class="badge {m.get(status,"badge-idle")}">{status}</span>'

def _time_status(h, m):
    now = datetime.now(tz=EST)
    t = now.replace(hour=h, minute=m, second=0, microsecond=0)
    if now > t: return "done"
    upcoming = [(hh,mm) for hh,mm in POST_TIMES_EST
                if now < now.replace(hour=hh,minute=mm,second=0,microsecond=0)]
    if upcoming and upcoming[0] == (h, m): return "next"
    return "future"

def _fmt_time(h, m):
    if h == 0:  return f"12:{m:02d} AM"
    if h < 12:  return f"{h}:{m:02d} AM"
    if h == 12: return f"12:{m:02d} PM"
    if h == 23: return f"11:{m:02d} PM"
    return f"{h-12}:{m:02d} PM"

def _free_label(is_free: bool) -> str:
    return ' <span class="free-tag">FREE</span>' if is_free else ""

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:14px 0 18px">
        <div style="font-size:36px">🚀</div>
        <div style="font-size:18px;font-weight:800;background:linear-gradient(135deg,#3B82F6,#8B5CF6);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
            Height Leveling</div>
        <div style="font-size:11px;color:#475569;margin-top:2px;">X Autonomous Poster</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # ── 1. Provider ───────────────────────────────────────────────────────────
    st.markdown("**🌐 Provider**")
    # Always show both — warn per-provider if key missing
    provider_options = ["OpenRouter", "Google Gemini"]

    if st.session_state.provider not in provider_options:
        st.session_state.provider = provider_options[0]

    st.session_state.provider = st.selectbox(
        "Provider", provider_options,
        index=provider_options.index(st.session_state.provider),
        label_visibility="collapsed",
    )

    # Key status
    key_ok = bool(_api_key())
    if key_ok:
        prov_key_name = "OPENROUTER_API_KEY" if st.session_state.provider == "OpenRouter" else "GEMINI_API_KEY"
        st.markdown(f"""
        <div style="background:#0D2A1A;border:1px solid #22C55E40;border-radius:8px;
             padding:6px 12px;font-size:12px;color:#22C55E;margin-top:4px;">
            ✅ {prov_key_name} loaded from .env
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background:#2A0D0D;border:1px solid #EF444440;border-radius:8px;
             padding:6px 12px;font-size:12px;color:#EF4444;margin-top:4px;">
            ❌ Add {'OPENROUTER_API_KEY' if st.session_state.provider=='OpenRouter' else 'GEMINI_API_KEY'} to .env
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 2. Model selector ─────────────────────────────────────────────────────
    if st.session_state.provider == "OpenRouter":
        st.markdown("**🤖 Model — OpenRouter**")

        if not get_or_key():
            st.caption("Add OPENROUTER_API_KEY to .env to load models")
        else:
            models = st.session_state.or_models  # list of enriched dicts
            if not models:
                if st.button("🔄 Retry loading models", use_container_width=True):
                    with st.spinner("Loading..."):
                        models = fetch_all_models(get_or_key())
                        st.session_state.or_models  = models
                        st.session_state.or_fetched = True
                    st.rerun()
            else:
                # Provider filter
                grouped   = group_by_provider(models)
                prov_keys = ["All Providers"] + sorted(grouped.keys())

                if st.session_state.or_prov_filter not in prov_keys:
                    st.session_state.or_prov_filter = "All Providers"

                st.session_state.or_prov_filter = st.selectbox(
                    "Filter by provider",
                    prov_keys,
                    index=prov_keys.index(st.session_state.or_prov_filter),
                )

                # Build filtered model list
                if st.session_state.or_prov_filter == "All Providers":
                    filtered_models = models
                else:
                    filtered_models = grouped.get(st.session_state.or_prov_filter, [])

                # Stats
                free_count = sum(1 for m in filtered_models if m.get("is_free"))
                st.markdown(f"""
                <div style="font-size:12px;color:#64748B;margin-bottom:6px;">
                    {len(filtered_models)} models
                    {'· <span style="color:#22C55E">🆓 ' + str(free_count) + ' free</span>' if free_count else ''}
                </div>""", unsafe_allow_html=True)

                # Model dropdown — labels show 🆓 for free
                model_ids    = [m["id"] for m in filtered_models]
                model_labels = [m["display_label"] for m in filtered_models]

                if st.session_state.or_model_id not in model_ids:
                    st.session_state.or_model_id = model_ids[0] if model_ids else ""

                sel_idx = st.selectbox(
                    "Model",
                    range(len(model_labels)),
                    index=model_ids.index(st.session_state.or_model_id)
                          if st.session_state.or_model_id in model_ids else 0,
                    format_func=lambda i: model_labels[i],
                    label_visibility="collapsed",
                )
                st.session_state.or_model_id = model_ids[sel_idx]

                # Show selected model ID + free tag
                sel_model = filtered_models[sel_idx]
                free_html = '<span class="free-tag" style="vertical-align:middle">FREE</span> ' if sel_model.get("is_free") else ""
                ctx_str   = f" · {sel_model.get('context_length',0)//1000}k ctx" if sel_model.get("context_length") else ""
                st.markdown(f"""
                <div class="model-pill-or">{free_html}{st.session_state.or_model_id}{ctx_str}</div>
                """, unsafe_allow_html=True)

                # Refresh button
                if st.button("🔄 Refresh model list", use_container_width=True):
                    with st.spinner("Refreshing..."):
                        new_models = fetch_all_models(get_or_key())
                        st.session_state.or_models = new_models
                    st.success(f"Loaded {len(new_models)} models")
                    st.rerun()

    else:  # Google Gemini
        st.markdown("**🤖 Model — Google Gemini**")
        g_families = list(GOOGLE_PROVIDERS.keys())
        if st.session_state.google_family not in g_families:
            st.session_state.google_family = g_families[0]

        st.session_state.google_family = st.selectbox(
            "Model family", g_families,
            index=g_families.index(st.session_state.google_family),
        )
        g_models = GOOGLE_PROVIDERS[st.session_state.google_family]
        if st.session_state.google_model not in g_models:
            st.session_state.google_model = g_models[0]

        st.session_state.google_model = st.selectbox(
            "Model", g_models,
            index=g_models.index(st.session_state.google_model),
            label_visibility="collapsed",
        )
        st.markdown(f'<div class="model-pill-goog">{st.session_state.google_model}</div>',
                    unsafe_allow_html=True)

    st.markdown("---")

    # ── App settings ──────────────────────────────────────────────────────────
    st.markdown("**⚙️ App Settings**")
    st.session_state.app_name = st.text_input("App Name", value=st.session_state.app_name)
    st.session_state.proj_dir = st.text_input(
        "Project Folder", value=st.session_state.proj_dir,
        help="Folder containing .md/.txt files about your app",
    )
    st.markdown("---")
    if st.button("🐦 Test X/Twitter Connection", use_container_width=True):
        with st.spinner("Testing..."):
            ok = test_connection()
        st.success("Connected ✅") if ok else st.error("Failed — check .env X credentials")

    st.markdown("---")
    st.markdown("""
    <div style="font-size:11px;color:#334155;text-align:center;padding-bottom:10px;">
        All keys from .env only<br>
        Generate: 12:00 AM EST · Post: 2AM 7AM 12PM 4PM 9PM 11PM
    </div>""", unsafe_allow_html=True)


# ─── MAIN ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:24px 0 18px">
    <div class="hero-title">X Auto Poster</div>
    <div class="hero-sub">Autonomous tweet bot — all keys from .env · 300+ models via OpenRouter</div>
</div>""", unsafe_allow_html=True)

# ─── Metrics ─────────────────────────────────────────────────────────────────
all_posts   = get_all_posts(200)
pending_ps  = get_pending_posts()
posted_ps   = [p for p in all_posts if p["status"]=="posted"]
failed_ps   = [p for p in all_posts if p["status"]=="failed"]
sched       = get_scheduler()
is_live     = sched.is_running
now_est_dt  = datetime.now(tz=EST)

c1,c2,c3,c4,c5,c6 = st.columns(6)
def _mc(col, val, lbl):
    col.markdown(f'<div class="metric-card"><div class="metric-number">{val}</div><div class="metric-label">{lbl}</div></div>', unsafe_allow_html=True)

live_badge = '<span class="badge badge-live">● LIVE</span>' if is_live else '<span class="badge badge-idle">● IDLE</span>'
c1.markdown(f'<div class="metric-card"><div class="metric-number">{live_badge}</div><div class="metric-label">Status</div></div>', unsafe_allow_html=True)
_mc(c2, len(pending_ps), "Queued")
_mc(c3, len(posted_ps),  "Posted")
_mc(c4, len(failed_ps),  "Failed")
_mc(c5, len(all_posts),  "Total")
c6.markdown(f'<div class="metric-card"><div class="metric-number" style="font-size:20px">{now_est_dt.strftime("%I:%M %p")}</div><div class="metric-label">EST Now</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Tabs ─────────────────────────────────────────────────────────────────────
t1,t2,t3,t4,t5 = st.tabs([
    "🎛️  Control", "📅  Schedule", "📋  Queue", "📊  History", "✏️  Preview"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — CONTROL
# ══════════════════════════════════════════════════════════════════════════════
with t1:
    left, right = st.columns([1.2,1], gap="large")

    with left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🤖 Autonomous Engine")

        active_key   = _api_key()
        active_model = _active_model()

        if is_live:
            st.markdown(f"""
            <div style="background:#0D2A1A;border:1px solid #22C55E40;border-radius:12px;
                 padding:16px;margin-bottom:16px;text-align:center;">
                <div style="font-size:26px;margin-bottom:4px">✅</div>
                <div style="font-size:16px;font-weight:700;color:#22C55E">Bot is RUNNING</div>
                <div style="font-size:12px;color:#64748B;margin-top:6px">
                    {sched.provider} · <code style="color:#94A3B8;background:#1E2D3D;padding:2px 6px;border-radius:4px">{sched.model_id}</code><br>
                    Generates at 12:00 AM EST · Posts on fixed schedule
                </div>
            </div>""", unsafe_allow_html=True)
            if st.button("🛑 Stop Bot", use_container_width=True, type="primary"):
                sched.stop(); st.success("Bot stopped"); st.rerun()
        else:
            st.markdown(f"""
            <div style="background:#1A1A2A;border:1px solid #3B82F640;border-radius:12px;
                 padding:16px;margin-bottom:16px;text-align:center;">
                <div style="font-size:26px;margin-bottom:4px">⏸️</div>
                <div style="font-size:16px;font-weight:700;color:#94A3B8">Bot is IDLE</div>
                <div style="font-size:12px;color:#64748B;margin-top:6px">Select provider + model in sidebar → Start</div>
            </div>""", unsafe_allow_html=True)

            can_start = bool(active_key and active_model)
            if st.button("▶️ Start Autonomous Bot", use_container_width=True,
                         type="primary", disabled=not can_start):
                sched.provider       = st.session_state.provider
                sched.api_key        = active_key
                sched.model_id       = active_model
                sched.app_name       = st.session_state.app_name
                sched.project_folder = st.session_state.proj_dir
                sched.start()
                st.success("✅ Bot started! Generates at midnight, posts on schedule.")
                st.rerun()
            if not active_key:
                st.caption("⚠️ Add the API key to .env to enable starting")

        st.markdown("</div>", unsafe_allow_html=True)

        # Manual controls
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🔧 Manual Controls")
        ca, cb = st.columns(2)

        with ca:
            if st.button("⚡ Generate Now", use_container_width=True,
                         help="Generate 6 tweets immediately"):
                if not active_key:
                    st.error("No API key in .env")
                else:
                    with st.spinner(f"Generating via {st.session_state.provider}..."):
                        try:
                            posts = generate_posts(
                                provider=st.session_state.provider,
                                model_id=active_model,
                                app_name=st.session_state.app_name,
                                project_folder=st.session_state.proj_dir,
                                api_key=active_key, count=6,
                            )
                            times = get_scheduled_times_for_today_est()
                            add_posts(posts, times)
                            sched.log(f"⚡ Manual: {len(posts)} tweets scheduled")
                            st.success(f"✅ {len(posts)} tweets scheduled!")
                        except Exception as e:
                            st.error(f"Failed: {e}")
                    st.rerun()

        with cb:
            if st.button("🗑️ Clear Queue", use_container_width=True):
                pend = get_pending_posts()
                for p in pend: delete_post(p["id"])
                st.success(f"Cleared {len(pend)} posts"); st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="glass-card" style="height:100%">', unsafe_allow_html=True)
        st.markdown("### 📟 Live Log")
        logs = sched.get_logs(40)
        if logs:
            st.markdown(_render_logs(logs), unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="log-console" style="color:#334155;text-align:center;padding-top:48px">
                No logs yet — start the bot to see activity
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — SCHEDULE
# ══════════════════════════════════════════════════════════════════════════════
with t2:
    st.markdown("### 📅 Daily Schedule (EST)")
    st.markdown("""
    <div style="color:#64748B;font-size:14px;margin-bottom:20px">
        Tweets auto-generate at <strong style="color:#3B82F6">12:00 AM EST</strong> every night
        and are posted at the 6 fixed times below.
    </div>""", unsafe_allow_html=True)

    post_labels = [
        (2,  0, "Early morning engagement"),
        (7,  0, "Morning commute audience"),
        (12, 0, "Lunch break peak"),
        (16, 0, "Afternoon peak"),
        (21, 0, "Evening wind-down"),
        (23, 0, "Late night audience"),
    ]

    ls, rs = st.columns([1,1], gap="large")
    with ls:
        st.markdown("#### 🤖 Generation")
        gs = _time_status(0,0)
        st.markdown(f"""
        <div class="timeline-item">
            <div class="timeline-dot dot-{gs}"></div>
            <div style="flex:1"><div style="font-weight:600;color:#CBD5E1">12:00 AM</div>
            <div style="font-size:12px;color:#475569">Generate 6 tweets via AI</div></div>
            <div style="font-size:11px;color:#3B82F6">DAILY</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📤 Posting Times")
        for h,m,desc in post_labels:
            s = _time_status(h,m)
            label = _fmt_time(h,m) + (" ← NEXT" if s=="next" else "")
            st.markdown(f"""
            <div class="timeline-item">
                <div class="timeline-dot dot-{s}"></div>
                <div style="flex:1"><div style="font-weight:600;color:#CBD5E1">{label}</div>
                <div style="font-size:12px;color:#475569">{desc}</div></div>
            </div>""", unsafe_allow_html=True)

    with rs:
        st.markdown("#### ⏰ Next Post Countdown")
        now_dt = datetime.now(tz=EST)
        upcoming = []
        for h,m,desc in post_labels:
            t = now_dt.replace(hour=h,minute=m,second=0,microsecond=0)
            if t <= now_dt: t += timedelta(days=1)
            upcoming.append((t,desc))
        upcoming.sort(key=lambda x: x[0])
        nxt, nxt_desc = upcoming[0]
        delta = nxt - now_dt
        hh = int(delta.total_seconds()//3600)
        mm = int((delta.total_seconds()%3600)//60)

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0D2040,#1A0D40);
             border:1px solid #3B82F640;border-radius:14px;padding:28px;text-align:center">
            <div style="font-size:12px;color:#64748B;font-weight:600;text-transform:uppercase;letter-spacing:1px">Next Post In</div>
            <div style="font-size:52px;font-weight:800;color:#3B82F6;margin:12px 0;font-family:'JetBrains Mono',monospace">{hh:02d}:{mm:02d}</div>
            <div style="font-size:16px;font-weight:600;color:#CBD5E1">{nxt.strftime('%I:%M %p EST')}</div>
            <div style="font-size:13px;color:#64748B;margin-top:6px">{nxt_desc}</div>
        </div>
        <div style="margin-top:16px;background:rgba(22,29,38,.8);border:1px solid #1E2D3D;
             border-radius:12px;padding:16px;font-size:13px;color:#94A3B8;line-height:1.9">
            <strong style="color:#CBD5E1">How it works</strong><br>
            1️⃣ Start bot → runs silently in background<br>
            2️⃣ At 12:00 AM EST → AI generates 6 tweets<br>
            3️⃣ Each tweet gets a fixed post time<br>
            4️⃣ Scheduler checks queue every 30 seconds<br>
            5️⃣ Posts fire automatically at their time<br>
            6️⃣ Cycle repeats every single night 🔁
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — QUEUE
# ══════════════════════════════════════════════════════════════════════════════
with t3:
    st.markdown("### 📋 Pending Queue")
    pending = get_pending_posts()

    if not pending:
        st.markdown("""
        <div style="text-align:center;padding:60px 0;color:#334155">
            <div style="font-size:48px;margin-bottom:12px">📭</div>
            <div style="font-size:18px;font-weight:600">Queue is empty</div>
            <div style="font-size:13px;margin-top:8px">Use <b>Generate Now</b> or wait for midnight</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"**{len(pending)} tweet(s) scheduled**")
        for p in pending:
            raw = p.get("scheduled_at","")
            try:
                dt = datetime.fromisoformat(raw)
                if not dt.tzinfo:
                    from datetime import timezone
                    dt = dt.replace(tzinfo=timezone.utc)
                disp = dt.astimezone(EST).strftime("%b %d · %I:%M %p EST")
            except Exception:
                disp = raw[:16] if raw else "Unscheduled"

            cw, cd = st.columns([12,1])
            with cw:
                st.markdown(f"""
                <div class="tweet-card pending">
                    <div class="tweet-content">{p['content']}</div>
                    <div class="tweet-meta">
                        <span class="tone-chip">{p['tone']}</span>
                        <span>📅 {disp}</span>
                        <span style="color:#475569">{len(p['content'])}/280</span>
                    </div>
                </div>""", unsafe_allow_html=True)
            with cd:
                if st.button("🗑️", key=f"dq_{p['id']}"): delete_post(p["id"]); st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — HISTORY
# ══════════════════════════════════════════════════════════════════════════════
with t4:
    st.markdown("### 📊 Post History")
    history = get_all_posts(100)
    h_p = [p for p in history if p["status"]=="posted"]
    h_f = [p for p in history if p["status"]=="failed"]
    h_q = [p for p in history if p["status"]=="pending"]

    hc1,hc2,hc3 = st.columns(3)
    hc1.metric("✅ Posted", len(h_p))
    hc2.metric("❌ Failed", len(h_f))
    hc3.metric("⏳ Pending", len(h_q))

    st.markdown("<br>", unsafe_allow_html=True)
    filt = st.selectbox("Filter", ["All","posted","pending","failed"])
    rows = history if filt=="All" else [p for p in history if p["status"]==filt]

    for p in rows:
        status = p["status"]
        tk = p.get("posted_at") or p.get("scheduled_at") or p.get("created_at") or ""
        td = tk[:16] if tk else "—"
        tid = p.get("tweet_id","")
        link = f"https://x.com/i/web/status/{tid}" if tid else ""
        st.markdown(f"""
        <div class="tweet-card {status}">
            <div class="tweet-content">{p['content']}</div>
            <div class="tweet-meta">
                {_badge(status)}
                <span class="tone-chip">{p['tone']}</span>
                <span>🕐 {td}</span>
                {"<a href='"+link+"' target='_blank' style='color:#3B82F6'>🐦 View</a>" if link else ""}
            </div>
            {"<div style='font-size:12px;color:#EF4444;margin-top:8px'>Error: "+str(p.get('error',''))+"</div>" if status=="failed" else ""}
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — PREVIEW
# ══════════════════════════════════════════════════════════════════════════════
with t5:
    st.markdown("### ✏️ Preview & Generate")
    st.markdown('<div style="color:#64748B;font-size:14px;margin-bottom:20px">Generate a preview — nothing posts automatically until you schedule it.</div>', unsafe_allow_html=True)

    pc, po = st.columns([2,1], gap="large")
    with po:
        st.markdown("#### Options")
        n_tweets = st.slider("Number of tweets", 1, 12, 6)
        schedule_after = st.checkbox("Schedule after preview", value=True)
        if schedule_after:
            when = st.radio("Schedule for", ["Today (next slots)","Tomorrow"])

    with pc:
        active_key_now   = _api_key()
        active_model_now = _active_model()

        # Show which provider/model is active
        is_free_now = False
        if st.session_state.provider == "OpenRouter" and st.session_state.or_models:
            model_match = next((m for m in st.session_state.or_models if m["id"]==active_model_now), None)
            if model_match: is_free_now = model_match.get("is_free", False)

        free_html = '<span class="free-tag">FREE</span> ' if is_free_now else ""
        st.markdown(f"""
        <div style="background:rgba(22,29,38,.8);border:1px solid #1E2D3D;border-radius:12px;
             padding:14px 18px;margin-bottom:16px;font-size:13px;color:#94A3B8">
            Provider: <strong style="color:#CBD5E1">{st.session_state.provider}</strong> &nbsp;·&nbsp;
            Model: {free_html}<strong style="color:#CBD5E1">{active_model_now}</strong>
        </div>""", unsafe_allow_html=True)

        if st.button("🔮 Generate Preview", type="primary", use_container_width=True):
            if not active_key_now:
                st.error("No API key in .env")
            else:
                prog = st.progress(0)
                stat = st.empty()
                def cb(i, total, tone):
                    prog.progress(i/total if total else 0)
                    if tone != "done": stat.markdown(f"Generating {i+1}/{total} · **{tone}**")
                    else: stat.markdown("✅ Done!")
                try:
                    tweets = generate_posts(
                        provider=st.session_state.provider,
                        model_id=active_model_now,
                        app_name=st.session_state.app_name,
                        project_folder=st.session_state.proj_dir,
                        api_key=active_key_now, count=n_tweets,
                        progress_callback=cb,
                    )
                    st.session_state.preview_tweets = tweets
                    prog.progress(1.0)
                except Exception as e:
                    st.error(f"Failed: {e}")

    if st.session_state.preview_tweets:
        st.markdown(f"---\n#### Preview — {len(st.session_state.preview_tweets)} tweets")
        for tw in st.session_state.preview_tweets:
            cc = len(tw["content"])
            col = "#22C55E" if cc<=240 else "#F59E0B" if cc<=270 else "#EF4444"
            st.markdown(f"""
            <div class="tweet-card pending">
                <div class="tweet-content">{tw['content']}</div>
                <div class="tweet-meta">
                    <span class="tone-chip">{tw['tone']}</span>
                    <span style="color:{col};font-weight:600">{cc}/280</span>
                </div>
            </div>""", unsafe_allow_html=True)

        if schedule_after:
            if st.button("📅 Schedule These Tweets", type="primary", use_container_width=True):
                times = (get_scheduled_times_for_today_est()
                         if when.startswith("Today")
                         else get_scheduled_times_for_tomorrow_est())
                times = times[:len(st.session_state.preview_tweets)]
                add_posts(st.session_state.preview_tweets, times)
                sched.log(f"📅 Manually scheduled {len(st.session_state.preview_tweets)} tweets")
                st.success(f"✅ Scheduled {len(st.session_state.preview_tweets)} tweets!")
                st.session_state.preview_tweets = []
                st.rerun()


# ─── Auto-refresh when bot running ───────────────────────────────────────────
if is_live:
    time.sleep(2)
    st.rerun()
