"""
modules/stats_tracker.py
Fetches stats from GitHub, Codeforces, LeetCode — all free public APIs.
"""
import requests
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import database as db

TIMEOUT = 15  # seconds


# ═══════════════════════════════════════════════════════════
#  GITHUB
# ═══════════════════════════════════════════════════════════

def fetch_github(username: str) -> dict:
    if not username:
        return {}
    try:
        headers = {"Accept": "application/vnd.github+json"}

        # User profile
        r = requests.get(
            f"https://api.github.com/users/{username}",
            headers=headers, timeout=TIMEOUT
        )
        r.raise_for_status()
        user = r.json()

        # Repos
        repos_r = requests.get(
            f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated",
            headers=headers, timeout=TIMEOUT
        )
        repos_r.raise_for_status()
        repos = repos_r.json()

        # Save top repos to DB
        for repo in repos:
            if not repo.get("fork"):  # skip forks
                db.upsert_project(
                    name=repo["name"],
                    description=repo.get("description") or "",
                    language=repo.get("language") or "N/A",
                    stars=repo.get("stargazers_count", 0),
                    url=repo.get("html_url", "")
                )

        data = {
            "username": username,
            "public_repos": user.get("public_repos", 0),
            "followers": user.get("followers", 0),
            "total_stars": sum(r.get("stargazers_count", 0) for r in repos),
            "top_languages": _top_languages(repos),
            "profile_url": f"https://github.com/{username}",
        }

        db.save_snapshot("github", data)
        print(f"[GitHub] ✓ {data['public_repos']} repos, {data['total_stars']} stars")
        return data

    except requests.RequestException as e:
        print(f"[GitHub] Error: {e}")
        return db.get_latest_snapshot("github")


def _top_languages(repos: list) -> list:
    count = {}
    for r in repos:
        lang = r.get("language")
        if lang:
            count[lang] = count.get(lang, 0) + 1
    return sorted(count, key=count.get, reverse=True)[:5]


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

        # Also fetch submission count
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
        }

        db.save_snapshot("codeforces", data)
        print(f"[Codeforces] ✓ Rating {data['rating']} | {data['solved_count']} solved")
        return data

    except Exception as e:
        print(f"[Codeforces] Error: {e}")
        return db.get_latest_snapshot("codeforces")


# ═══════════════════════════════════════════════════════════
#  LEETCODE  (public GraphQL — no login needed)
# ═══════════════════════════════════════════════════════════

LC_URL = "https://leetcode.com/graphql"

LC_QUERY = """
query userPublicProfile($username: String!) {
  matchedUser(username: $username) {
    username
    profile { ranking }
    submitStats {
      acSubmissionNum {
        difficulty
        count
      }
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

        stats = {s["difficulty"]: s["count"]
                 for s in user["submitStats"]["acSubmissionNum"]}

        data = {
            "username": username,
            "ranking": user["profile"].get("ranking", 0),
            "solved_total": stats.get("All", 0),
            "solved_easy": stats.get("Easy", 0),
            "solved_medium": stats.get("Medium", 0),
            "solved_hard": stats.get("Hard", 0),
            "profile_url": f"https://leetcode.com/{username}",
        }

        db.save_snapshot("leetcode", data)
        print(f"[LeetCode] ✓ {data['solved_total']} solved (E:{data['solved_easy']} M:{data['solved_medium']} H:{data['solved_hard']})")
        return data

    except Exception as e:
        print(f"[LeetCode] Error: {e}")
        return db.get_latest_snapshot("leetcode")


# ═══════════════════════════════════════════════════════════
#  MAIN — fetch all
# ═══════════════════════════════════════════════════════════

def update_all_stats(config: dict) -> dict:
    profile = config.get("profile", {})
    print("\n[Stats] Starting update...")

    gh  = fetch_github(profile.get("github_username", ""))
    cf  = fetch_codeforces(profile.get("codeforces_handle", ""))
    lc  = fetch_leetcode(profile.get("leetcode_username", ""))

    print("[Stats] Update complete.\n")
    return {"github": gh, "codeforces": cf, "leetcode": lc}
