"""
scheduler.py — Background Stats Refresh Daemon
Run with:  python scheduler.py

Periodically pulls GitHub / Codeforces / LeetCode stats
and saves them to the SQLite database.
The FastAPI backend reads the latest snapshot on request.
"""

import sys
import time
import threading
import logging
from pathlib import Path
from datetime import datetime

import yaml

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

logging.basicConfig(
    format="%(asctime)s [SCHEDULER] %(levelname)s %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(BASE_DIR / "data" / "scheduler.log", encoding="utf-8"),
    ]
)
log = logging.getLogger("scheduler")


def load_config():
    path = BASE_DIR / "config.yaml"
    if not path.exists():
        log.error("config.yaml not found!")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def task_update_stats(config):
    log.info("Scheduled: updating stats...")
    try:
        from backend.services.github_parser import update_all_stats
        update_all_stats(config)
        log.info("Stats update complete.")
    except Exception as e:
        log.error(f"Stats update failed: {e}")


class SimpleScheduler:
    def __init__(self):
        self._jobs = []

    def every(self, hours: float, func, *args):
        self._jobs.append({
            "interval": hours * 3600,
            "last_run": 0,
            "func": func,
            "args": args
        })

    def _run_in_thread(self, func, args):
        t = threading.Thread(target=func, args=args, daemon=True)
        t.start()

    def tick(self):
        now = time.time()
        for job in self._jobs:
            if now - job["last_run"] >= job["interval"]:
                job["last_run"] = now
                self._run_in_thread(job["func"], job["args"])

    def run_forever(self, tick_every=60):
        log.info("Scheduler running (tick every %ds)...", tick_every)
        while True:
            self.tick()
            time.sleep(tick_every)


def main():
    (BASE_DIR / "data").mkdir(exist_ok=True)

    import backend.database.models as db
    db.init_db()

    config = load_config()
    log.info("=" * 50)
    log.info("Antigravity Scheduler starting...")
    log.info(f"Profile: {config['profile'].get('name','?')}")
    log.info("=" * 50)

    sched_cfg = config.get("schedule", {})
    scheduler = SimpleScheduler()

    stats_interval = sched_cfg.get("stats_interval_hours", 6)
    scheduler.every(stats_interval, task_update_stats, config)
    log.info(f"Stats fetch scheduled every {stats_interval}h")

    # Run immediately on startup
    log.info("Running initial stats fetch...")
    threading.Thread(target=task_update_stats, args=(config,), daemon=True).start()

    try:
        scheduler.run_forever(tick_every=60)
    except KeyboardInterrupt:
        log.info("Scheduler stopped by user.")


if __name__ == "__main__":
    main()
