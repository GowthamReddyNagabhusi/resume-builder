"""
backend/services/github_parser.py
Fetch GitHub repos, Codeforces, and LeetCode stats.
All public APIs — no authentication required.
"""

import requests
from datetime import datetime
from database import models as db
from core.logger import get_logger

TIMEOUT = 15
log = get_logger(__name__)


# ═══════════════════════════════════════════════════════════
#  GITHUB
# ═══════════════════════════════════════════════════════════

def fetch_github(username: str, user_id: int = 1) -> dict:
    if not username:
        return {}
    try:
        headers = {"Accept": "application/vnd.github+json"}

        r = requests.get(
            f"https://api.github.com/users/{username}",
            headers=headers, timeout=TIMEOUT
        )
        r.raise_for_status()
        user = r.json()

        repos_r = requests.get(
            f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated",
            headers=headers, timeout=TIMEOUT
        )
        repos_r.raise_for_status()
        repos = repos_r.json()

        # Save non-fork repos to DB
        for repo in repos:
            if not repo.get("fork"):
                topics = ",".join(repo.get("topics", []))
                db.upsert_project(
                    name=repo["name"],
                    description=repo.get("description") or "",
                    language=repo.get("language") or "N/A",
                    stars=repo.get("stargazers_count", 0),
                    url=repo.get("html_url", ""),
                    topics=topics,
                    user_id=user_id
                )

        data = {
            "username": username,
            "name": user.get("name", username),
            "bio": user.get("bio", ""),
            "public_repos": user.get("public_repos", 0),
            "followers": user.get("followers", 0),
            "following": user.get("following", 0),
            "total_stars": sum(r.get("stargazers_count", 0) for r in repos if not r.get("fork")),
            "top_languages": _top_languages(repos),
            "profile_url": f"https://github.com/{username}",
            "avatar_url": user.get("avatar_url", ""),
            "fetched_at": datetime.now().isoformat(),
        }

        db.save_snapshot("github", data)
        log.info("GitHub OK: %s repos, %s stars", data["public_repos"], data["total_stars"])
        return data

    except requests.RequestException as e:
        log.error("GitHub error: %s", e)
        return db.get_latest_snapshot("github")


def _top_languages(repos: list) -> list:
    count = {}
    for r in repos:
        lang = r.get("language")
        if lang:
            count[lang] = count.get(lang, 0) + 1
    return sorted(count, key=count.get, reverse=True)[:6]


# ═══════════════════════════════════════════════════════════
#  CODEFORCES
# ═══════════════════════════════════════════════════════════

def fetch_codeforces(handle: str) -> dict:
    if not handle:
        return {}
    try:
        r = requests.get(
            f"https://codeforces.com/api/user.info?handles={handle}",
            timeout=TIMEOUT
        )
        r.raise_for_status()
        j = r.json()

        if j.get("status") != "OK":
            raise ValueError(j.get("comment", "CF API error"))

        u = j["result"][0]

        sub_r = requests.get(
            f"https://codeforces.com/api/user.status?handle={handle}&count=1000",
            timeout=TIMEOUT
        )
        solved = set()
        if sub_r.ok:
            for s in sub_r.json().get("result", []):
                if s.get("verdict") == "OK":
                    pid = str(s["problem"].get("contestId", "")) + str(s["problem"].get("index", ""))
                    solved.add(pid)

        data = {
            "handle": handle,
            "rating": u.get("rating", 0),
            "max_rating": u.get("maxRating", 0),
            "rank": u.get("rank", "unrated"),
            "max_rank": u.get("maxRank", "unrated"),
            "solved_count": len(solved),
            "profile_url": f"https://codeforces.com/profile/{handle}",
            "avatar_url": u.get("titlePhoto", ""),
            "fetched_at": datetime.now().isoformat(),
        }

        db.save_snapshot("codeforces", data)
        log.info("Codeforces OK: rating %s | solved %s", data["rating"], data["solved_count"])
        return data

    except Exception as e:
        log.error("Codeforces error: %s", e)
        return db.get_latest_snapshot("codeforces")


# ═══════════════════════════════════════════════════════════
#  LEETCODE  (public GraphQL)
# ═══════════════════════════════════════════════════════════

LC_URL = "https://leetcode.com/graphql"
LC_QUERY = """
query userPublicProfile($username: String!) {
  matchedUser(username: $username) {
    username
    profile { ranking }
    submitStats {
      acSubmissionNum { difficulty count }
    }
  }
}
"""


def fetch_leetcode(username: str) -> dict:
    if not username:
        return {}
    try:
        r = requests.post(
            LC_URL,
            json={"query": LC_QUERY, "variables": {"username": username}},
            headers={"Content-Type": "application/json", "Referer": "https://leetcode.com"},
            timeout=TIMEOUT
        )
        r.raise_for_status()
        j = r.json()
        user = j["data"]["matchedUser"]
        if not user:
            raise ValueError("User not found on LeetCode")

        stats = {s["difficulty"]: s["count"] for s in user["submitStats"]["acSubmissionNum"]}
        data = {
            "username": username,
            "ranking": user["profile"].get("ranking", 0),
            "solved_total": stats.get("All", 0),
            "solved_easy": stats.get("Easy", 0),
            "solved_medium": stats.get("Medium", 0),
            "solved_hard": stats.get("Hard", 0),
            "profile_url": f"https://leetcode.com/{username}",
            "fetched_at": datetime.now().isoformat(),
        }

        db.save_snapshot("leetcode", data)
        log.info("LeetCode OK: solved %s", data["solved_total"])
        return data

    except Exception as e:
        log.error("LeetCode error: %s", e)
        return db.get_latest_snapshot("leetcode")


# ═══════════════════════════════════════════════════════════
#  MASTER UPDATE
# ═══════════════════════════════════════════════════════════

def update_all_stats(config: dict) -> dict:
    profile = config.get("profile", {})
    log.info("Stats update starting")
    gh = fetch_github(profile.get("github_username", ""))
    cf = fetch_codeforces(profile.get("codeforces_handle", ""))
    lc = fetch_leetcode(profile.get("leetcode_username", ""))
    log.info("Stats update complete")
    return {"github": gh, "codeforces": cf, "leetcode": lc}
