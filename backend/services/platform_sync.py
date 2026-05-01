"""User-specific coding platform and GitHub data synchronization."""

from __future__ import annotations

from database import models as db
from services.github_parser import fetch_codeforces, fetch_github, fetch_leetcode

SUPPORTED = {
    "leetcode": fetch_leetcode,
    "codeforces": fetch_codeforces,
}


def sync_user_platform_data(user_id: int) -> dict:
    bundle = db.get_profile_bundle(user_id)
    profile = bundle.get("profile") or {}
    coding_platforms = bundle.get("coding_platforms") or []

    results = {"github": None, "platforms": []}

    github_profile = profile.get("github_profile") or ""
    if github_profile:
        username = github_profile.rstrip("/").split("/")[-1]
        gh = fetch_github(username)
        if gh:
            db.upsert_github_data(
                user_id,
                {
                    "profile_link": gh.get("profile_url", github_profile),
                    "repositories": gh.get("public_repos", 0),
                    "stars": gh.get("total_stars", 0),
                    "languages": gh.get("top_languages", []),
                    "projects": db.get_projects(limit=10, only_resume=False),
                    "contributions": 0,
                },
            )
            results["github"] = gh

    updated = []
    for cp in coding_platforms:
        platform_name = (cp.get("platform_name") or "").strip().lower()
        username = (cp.get("username") or "").strip()
        if not username:
            continue
        fetcher = SUPPORTED.get(platform_name)
        if fetcher:
            data = fetcher(username)
            updated.append({"platform": platform_name, "username": username, "data": data})

    results["platforms"] = updated
    return results
