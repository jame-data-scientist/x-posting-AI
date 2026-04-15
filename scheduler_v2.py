"""
scheduler_v2.py
Fixed-time EST scheduler:
  - Generate 6 tweets at 12:00 AM EST every day
  - Post at: 2:00 AM, 7:00 AM, 11:00 AM, 12:00 PM, 4:00 PM, 9:00 PM (EST)
Supports OpenRouter and Google Gemini as AI backends.
"""

import threading
import time
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from post_queue import (
    get_due_posts, mark_posted, mark_failed, init_db,
    add_posts, get_pending_posts
)
from x_poster import post_tweet
from ai_generator_v2 import generate_posts

# ── Constants ─────────────────────────────────────────────────────────────────
EST = ZoneInfo("America/New_York")

# Fixed posting times (EST 24h)
POST_TIMES_EST = [
    (2, 0),   # 2:00 AM
    (7, 0),   # 7:00 AM
    (12, 0),  # 12:00 PM
    (16, 0),  # 4:00 PM
    (21, 0),  # 9:00 PM
    (23, 0),  # 11:00 PM
]

GENERATE_HOUR_EST = 0
GENERATE_MINUTE_EST = 0

logger = logging.getLogger("scheduler_v2")


def now_est() -> datetime:
    return datetime.now(tz=EST)


def get_scheduled_times_for_today_est() -> list[str]:
    """Return ISO strings for today's 6 post times. Past times → tomorrow."""
    now = now_est()
    times = []
    for h, m in POST_TIMES_EST:
        dt = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if dt <= now:
            dt += timedelta(days=1)
        times.append(dt.isoformat())
    return times


def get_scheduled_times_for_tomorrow_est() -> list[str]:
    """Return ISO strings for tomorrow's 6 post times."""
    tomorrow = now_est() + timedelta(days=1)
    times = []
    for h, m in POST_TIMES_EST:
        dt = tomorrow.replace(hour=h, minute=m, second=0, microsecond=0)
        times.append(dt.isoformat())
    return times


# ── Autonomous Engine ─────────────────────────────────────────────────────────
class AutonomousScheduler:
    """
    Runs in a background thread:
    1. Every 30s: check for due posts and fire them.
    2. At 12:00 AM EST: auto-generate 6 new tweets for the day.
    """

    def __init__(self):
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._running = False
        self._status_log: list[str] = []
        self._last_generation_date: str | None = None

        # Set before start()
        self.provider: str = "OpenRouter"          # "OpenRouter" or "Google Gemini"
        self.api_key: str = ""                      # key for chosen provider
        self.model_id: str = "openai/gpt-4o-mini"
        self.app_name: str = "Height Leveling"
        self.project_folder: str = "./project"

    # ── Helpers ───────────────────────────────────────────────────────────────

    @property
    def is_running(self) -> bool:
        return self._running

    def log(self, msg: str):
        ts = now_est().strftime("%Y-%m-%d %H:%M:%S EST")
        entry = f"[{ts}] {msg}"
        self._status_log.append(entry)
        logger.info(msg)
        if len(self._status_log) > 200:
            self._status_log = self._status_log[-200:]

    def get_logs(self, n: int = 50) -> list[str]:
        return self._status_log[-n:]

    # ── Start / Stop ──────────────────────────────────────────────────────────

    def start(self):
        if self._running:
            return
        init_db()
        self._stop_event.clear()
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self.log("✅ Autonomous scheduler started")
        self.log(f"   Provider : {self.provider}")
        self.log(f"   Model    : {self.model_id}")
        self.log(f"   App      : {self.app_name}")
        self.log(f"   Generate : 12:00 AM EST daily")
        self.log(f"   Post at  : 2AM · 7AM · 11AM · 12PM · 4PM · 9PM EST")

    def stop(self):
        self._stop_event.set()
        self._running = False
        self.log("🛑 Scheduler stopped")

    # ── Main loop ─────────────────────────────────────────────────────────────

    def _run_loop(self):
        while not self._stop_event.is_set():
            try:
                self._tick()
            except Exception as e:
                self.log(f"⚠️ Tick error: {e}")
            time.sleep(30)

    def _tick(self):
        now = now_est()
        today_str = now.strftime("%Y-%m-%d")

        # Auto-generate at 12:00 AM (within first 5 min window)
        if (
            now.hour == GENERATE_HOUR_EST
            and now.minute < 5
            and self._last_generation_date != today_str
        ):
            self.log(f"🤖 12:00 AM trigger — generating 6 tweets for {today_str}...")
            self._auto_generate()
            self._last_generation_date = today_str

        # Fire due posts
        due = get_due_posts()
        if due:
            self.log(f"📤 {len(due)} post(s) due — firing now")
            for post in due:
                self._fire_post(post)

    def _auto_generate(self):
        """Generate 6 tweets and schedule for today's fixed times."""
        try:
            posts = generate_posts(
                provider=self.provider,
                model_id=self.model_id,
                app_name=self.app_name,
                project_folder=self.project_folder,
                api_key=self.api_key,
                count=6,
            )
            if posts:
                times = get_scheduled_times_for_today_est()
                add_posts(posts, times)
                self.log(f"✅ Generated & scheduled {len(posts)} tweets")
                for i, (p, t) in enumerate(zip(posts, times), 1):
                    self.log(f"   [{i}] {p['tone']:20} → {t[:16]} | {p['content'][:50]}...")
        except Exception as e:
            self.log(f"❌ Auto-generation failed: {e}")

    def _fire_post(self, post: dict):
        try:
            tweet_id = post_tweet(post["content"])
            mark_posted(post["id"], tweet_id)
            self.log(f"✅ Posted [{post['tone']}] tweet_id={tweet_id}: {post['content'][:60]}...")
        except Exception as e:
            mark_failed(post["id"], str(e))
            self.log(f"❌ Failed to post ID {post['id']}: {e}")

    # ── Manual ────────────────────────────────────────────────────────────────

    def manual_generate_now(self):
        self.log("🔄 Manual generation triggered...")
        self._auto_generate()
        self._last_generation_date = now_est().strftime("%Y-%m-%d")

    def next_post_time(self) -> str | None:
        pending = get_pending_posts()
        if not pending:
            return None
        return sorted(pending, key=lambda x: x.get("scheduled_at") or "")[0].get("scheduled_at")


# Singleton
_scheduler = AutonomousScheduler()


def get_scheduler() -> AutonomousScheduler:
    return _scheduler
