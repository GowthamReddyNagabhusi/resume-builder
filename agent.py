"""
agent.py — Career Automation Agent (Main Entry Point)
Run with:  python agent.py

On Windows startup, create a shortcut to this in:
  shell:startup  →  pythonw agent.py
"""

import sys
import time
import threading
import logging
from pathlib import Path
from datetime import datetime

import yaml

# ── Bootstrap ──────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

logging.basicConfig(
    format="%(asctime)s [AGENT] %(levelname)s %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(BASE_DIR / "data" / "agent.log", encoding="utf-8"),
    ]
)
log = logging.getLogger("agent")


# ── Load config ────────────────────────────────────────────
def load_config():
    path = BASE_DIR / "config.yaml"
    if not path.exists():
        log.error("config.yaml not found!")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ── Scheduled tasks ────────────────────────────────────────
def task_update_stats(config):
    log.info("Scheduled: updating stats...")
    try:
        from modules.stats_tracker import update_all_stats
        update_all_stats(config)
        log.info("Stats update complete.")
    except Exception as e:
        log.error(f"Stats update failed: {e}")


def task_generate_resume(config):
    log.info("Scheduled: generating resume...")
    try:
        from modules.resume_engine import generate_resume, REPORTLAB_OK
        if REPORTLAB_OK:
            generate_resume(config)
            log.info("Resume generated.")
        else:
            log.warning("ReportLab not installed — skipping resume generation.")
    except Exception as e:
        log.error(f"Resume generation failed: {e}")


def send_telegram_message(config, text):
    """Send a plain message to Telegram (used by scheduler)."""
    try:
        import requests
        token   = config["telegram"]["bot_token"]
        chat_id = config["telegram"]["chat_id"]
        if not token or token == "PASTE_YOUR_BOT_TOKEN_HERE":
            return
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            timeout=10
        )
    except Exception as e:
        log.error(f"Telegram send failed: {e}")


def task_nightly_report(config):
    log.info("Scheduled: sending nightly report...")
    try:
        import database as db
        gh = db.get_latest_snapshot("github")
        cf = db.get_latest_snapshot("codeforces")
        lc = db.get_latest_snapshot("leetcode")

        lines = [f"🌙 *Career Agent — Daily Report* ({datetime.now().strftime('%d %b %Y')})\n"]

        if gh:
            lines.append(f"🐙 GitHub: {gh.get('public_repos',0)} repos · {gh.get('total_stars',0)} ★")
        if cf:
            lines.append(f"⚡ CF: {cf.get('rating',0)} ({cf.get('rank','')}) · {cf.get('solved_count',0)} solved")
        if lc:
            lines.append(f"💻 LC: {lc.get('solved_total',0)} problems solved")

        lines.append("\n_Resume auto-updated. Have a great evening!_ 🚀")
        send_telegram_message(config, "\n".join(lines))
    except Exception as e:
        log.error(f"Nightly report failed: {e}")


# ── Simple scheduler (no APScheduler needed) ───────────────

class SimpleScheduler:
    """
    Lightweight interval scheduler. No extra dependencies.
    Each job runs in its own thread so they don't block each other.
    """
    def __init__(self):
        self._jobs = []  # (interval_seconds, last_run, func, args)
        self._daily = []  # (HH:MM, last_date, func, args)

    def every(self, hours: float, func, *args):
        self._jobs.append({
            "interval": hours * 3600,
            "last_run": 0,
            "func": func,
            "args": args
        })

    def daily_at(self, time_str: str, func, *args):
        """time_str like '20:00'"""
        self._daily.append({
            "time": time_str,
            "last_date": None,
            "func": func,
            "args": args
        })

    def _run_in_thread(self, func, args):
        t = threading.Thread(target=func, args=args, daemon=True)
        t.start()

    def tick(self):
        now = time.time()
        today = datetime.now().strftime("%Y-%m-%d")
        now_hhmm = datetime.now().strftime("%H:%M")

        for job in self._jobs:
            if now - job["last_run"] >= job["interval"]:
                job["last_run"] = now
                self._run_in_thread(job["func"], job["args"])

        for job in self._daily:
            if job["time"] == now_hhmm and job["last_date"] != today:
                job["last_date"] = today
                self._run_in_thread(job["func"], job["args"])

    def run_forever(self, tick_every=30):
        log.info("Scheduler running (tick every %ds)...", tick_every)
        while True:
            self.tick()
            time.sleep(tick_every)


# ── Main ───────────────────────────────────────────────────

def main():
    # Create data dir if needed
    (BASE_DIR / "data").mkdir(exist_ok=True)
    (BASE_DIR / "resume").mkdir(exist_ok=True)

    # Init DB
    import database as db
    db.init_db()

    config = load_config()
    log.info("=" * 50)
    log.info("Career Agent starting up...")
    log.info(f"Profile: {config['profile'].get('name','?')}")
    
    gemini_key = config.get("gemini", {}).get("api_key", "")
    groq_key = config.get("groq", {}).get("api_key", "")
    if (not gemini_key or gemini_key.startswith("PASTE")) and (not groq_key or groq_key.startswith("PASTE")):
        log.warning("No AI API keys configured! Resume bullets will use basic fallbacks.")
        log.info("Get a FREE Groq key at: https://console.groq.com/keys")
    elif groq_key and not groq_key.startswith("PASTE"):
        log.info("Using Groq API for AI generation (Faster & more reliable).")
    elif gemini_key and not gemini_key.startswith("PASTE"):
        log.info("Using Gemini API for AI generation.")
        
    log.info("=" * 50)

    sched = config.get("schedule", {})

    # ── 1. Run initial stat fetch immediately ──────────────
    log.info("Running initial stats fetch...")
    threading.Thread(
        target=task_update_stats, args=(config,), daemon=True
    ).start()

    # ── 2. Schedule periodic tasks ─────────────────────────
    scheduler = SimpleScheduler()

    stats_interval = sched.get("stats_interval_hours", 6)
    scheduler.every(stats_interval, task_update_stats, config)
    log.info(f"Stats fetch scheduled every {stats_interval}h")

    if sched.get("resume_generate_daily", True):
        scheduler.daily_at("08:00", task_generate_resume, config)
        log.info("Resume generation scheduled daily at 08:00")

    report_time = sched.get("daily_report_time", "20:00")
    scheduler.daily_at(report_time, task_nightly_report, config)
    log.info(f"Nightly report scheduled at {report_time}")

    # ── 3. Start Telegram bot in background thread ─────────
    def start_bot():
        try:
            from bot.telegram_bot import run_bot
            run_bot(config)
        except Exception as e:
            log.error(f"Telegram bot crashed: {e}")

    bot_thread = threading.Thread(target=start_bot, daemon=True, name="TelegramBot")
    bot_thread.start()
    log.info("Telegram bot thread started.")

    # ── 4. Send startup notification ───────────────────────
    time.sleep(3)  # give bot a moment to connect
    send_telegram_message(
        config,
        f"🤖 *Career Agent Online*\n"
        f"Started at {datetime.now().strftime('%d %b %Y %H:%M')}\n"
        f"Type /help to see commands."
    )

    # ── 5. Run scheduler (blocks forever) ──────────────────
    try:
        scheduler.run_forever(tick_every=30)
    except KeyboardInterrupt:
        log.info("Agent stopped by user.")


if __name__ == "__main__":
    main()
