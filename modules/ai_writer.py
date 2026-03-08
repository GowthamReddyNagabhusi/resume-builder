"""
modules/ai_writer.py

Uses Google Gemini Flash (FREE — 1500 requests/day, no credit card) to write
professional resume content with action words.

Get free key: aistudio.google.com → Get API Key
"""

import sys
import json
import time
import hashlib
import requests
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
import database as db

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_CALL_DELAY = 6  # 10 RPM to be safe for Gemini
GROQ_CALL_DELAY = 2    # 30 RPM for Llama3 8B on Free Tier

def _call_groq(api_key: str, prompt: str, max_tokens=800) -> str:
    if not api_key or api_key == "PASTE_GROq_KEY_HERE":
        return None
    
    time.sleep(GROQ_CALL_DELAY)
    try:
        r = requests.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.7
            },
            timeout=30
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print("[AI] Groq rate limit (429) hit. Will fallback or retry later.")
        else:
            print(f"[AI] Groq error: {e}")
    except Exception as e:
        print(f"[AI] Groq error: {e}")
    return None

def _call_gemini(api_key: str, prompt: str, max_tokens=800) -> str:
    if not api_key or api_key == "PASTE_GEMINI_KEY_HERE":
        return None
    
    time.sleep(GEMINI_CALL_DELAY)
    
    for attempt in range(2):  # Max 2 retries
        try:
            r = requests.post(
                f"{GEMINI_URL}?key={api_key}",
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.7}
                },
                timeout=30
            )
            r.raise_for_status()
            return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                wait_time = 20 * (attempt + 1)
                print(f"[AI] Gemini 429 Too Many Requests! Your Free Quota may be exhausted.")
                if attempt == 0:
                    print(f"[AI] Waiting {wait_time}s to see if it's a per-minute limit...")
                    time.sleep(wait_time)
                    continue
                else:
                    print("[AI] Gemini quota exhausted. Please get a new key or use Groq.")
                    return None
            else:
                print(f"[AI] Gemini error: {e}")
                return None
        except Exception as e:
            print(f"[AI] Gemini error: {e}")
            return None
    
    return None

def _call_ai(config: dict, prompt: str, max_tokens=800) -> str:
    """Tries Groq first (faster, bigger limit), then Gemini."""
    groq_key = config.get("groq", {}).get("api_key", "")
    gemini_key = config.get("gemini", {}).get("api_key", "")
    
    # Try Groq if valid key looks present
    if groq_key and not groq_key.startswith("PASTE"):
        res = _call_groq(groq_key, prompt, max_tokens)
        if res: return res
        print("[AI] Groq fallback failed. Trying Gemini...")
        
    # Try Gemini next
    if gemini_key and not gemini_key.startswith("PASTE"):
        res = _call_gemini(gemini_key, prompt, max_tokens)
        if res: return res
        
    print("[AI] Both AI endpoints failed (or no keys provided). Using default fallback text.")
    return None


# ── Cache ──────────────────────────────────────────────────

def _cache_key(data: dict) -> str:
    return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()


def _init_cache():
    conn = db.get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ai_cache (
            cache_key    TEXT PRIMARY KEY,
            section      TEXT,
            content      TEXT,
            generated_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def _get_cached(section: str, input_data: dict):
    _init_cache()
    key = section + ":" + _cache_key(input_data)
    conn = db.get_conn()
    try:
        row = conn.execute(
            "SELECT content FROM ai_cache WHERE cache_key=?", (key,)
        ).fetchone()
    except:
        row = None
    conn.close()
    return json.loads(row["content"]) if row else None


def _save_cache(section: str, input_data: dict, content):
    _init_cache()
    key = section + ":" + _cache_key(input_data)
    conn = db.get_conn()
    conn.execute("""
        INSERT OR REPLACE INTO ai_cache (cache_key, section, content, generated_at)
        VALUES (?, ?, ?, ?)
    """, (key, section, json.dumps(content), datetime.now().isoformat()))
    conn.commit()
    conn.close()


# ── GitHub helpers ─────────────────────────────────────────

def _fetch_readme(owner: str, repo: str) -> str:
    for branch in ["main", "master"]:
        try:
            r = requests.get(
                f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/README.md",
                timeout=10
            )
            if r.ok and len(r.text) > 50:
                return r.text[:2000]
        except:
            pass
    return ""


def _fetch_repo_languages(owner: str, repo: str) -> dict:
    try:
        r = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/languages",
            timeout=10
        )
        if r.ok:
            return r.json()
    except:
        pass
    return {}


# ══════════════════════════════════════════════════════════
#  PROJECT BULLETS
# ══════════════════════════════════════════════════════════

def generate_project_bullets(config: dict, project: dict, github_username: str, force=False) -> list:
    input_data = {
        "name": project.get("name", ""),
        "description": project.get("description", ""),
        "language": project.get("language", ""),
        "stars": project.get("stars", 0),
    }

    if not force:
        cached = _get_cached("project", input_data)
        if cached:
            print(f"[AI] '{project['name']}' — cached ✓")
            return cached

    readme = _fetch_readme(github_username, project.get("name", ""))
    langs  = _fetch_repo_languages(github_username, project.get("name", ""))
    lang_str = ", ".join(list(langs.keys())[:5]) if langs else project.get("language", "")

    prompt = f"""You are a professional resume writer for software engineering resumes.

Write exactly 4-5 bullet points for this GitHub project to go in a resume.

STRICT RULES:
- Start EVERY bullet with a strong action verb (Built, Designed, Implemented, Achieved, Optimized, Engineered, Developed, Reduced, Improved, Integrated, Automated, Architected)
- Be specific and technical — mention algorithms, data structures, complexity, patterns
- Include measurable outcomes where possible (O(log n), handles Xk requests, reduced by X%, etc.)
- Last bullet MUST be: Tech: [comma separated stack]
- Each bullet is ONE sentence, max 20 words
- Return ONLY a JSON array of strings. No explanation, no markdown fences.

Project: {project.get('name', '')}
Description: {project.get('description', '') or 'Not provided'}
Primary language: {project.get('language', '')}
All languages: {lang_str}
Stars: {project.get('stars', 0)}
README:
{readme or 'Not available'}

Return only the JSON array."""

    print(f"[AI] Writing bullets for: {project['name']}...")
    result = _call_ai(config, prompt)

    if result:
        try:
            clean = result.strip().replace("```json", "").replace("```", "").strip()
            bullets = json.loads(clean)
            _save_cache("project", input_data, bullets)
            return bullets
        except:
            lines = [l.strip().lstrip("-•1234567890.").strip()
                     for l in result.split("\n") if l.strip()]
            lines = [l for l in lines if len(l) > 10]
            _save_cache("project", input_data, lines)
            return lines

    # Fallback
    desc = project.get("description") or project.get("name", "")
    return [
        f"Developed {project.get('name','the project')} with focus on performance and clean architecture.",
        f"Tech: {project.get('language', 'N/A')}"
    ]


# ══════════════════════════════════════════════════════════
#  ACHIEVEMENTS (CF + LC + GitHub)
# ══════════════════════════════════════════════════════════

def generate_achievements(config: dict, cf: dict, lc: dict, gh: dict, force=False) -> dict:
    input_data = {
        "cf_rating": cf.get("rating", 0),
        "cf_solved": cf.get("solved_count", 0),
        "cf_rank":   cf.get("rank", ""),
        "cf_max":    cf.get("max_rating", 0),
        "lc_total":  lc.get("solved_total", 0),
        "lc_easy":   lc.get("solved_easy", 0),
        "lc_medium": lc.get("solved_medium", 0),
        "lc_hard":   lc.get("solved_hard", 0),
        "lc_rank":   lc.get("ranking", 0),
        "gh_repos":  gh.get("public_repos", 0),
        "gh_stars":  gh.get("total_stars", 0),
    }

    if not any(input_data.values()):
        return {"codeforces": [], "leetcode": [], "github": []}

    if not force:
        cached = _get_cached("achievements", input_data)
        if cached:
            print("[AI] Achievements — cached ✓")
            return cached

    prompt = f"""You are a professional resume writer for software engineers.

Write achievement bullet points for a resume based on this competitive programming data.

STRICT RULES:
- Start every bullet with an action verb
- Include exact numbers from the data
- Sound impressive and professional
- 2 bullets per platform maximum
- Return ONLY a JSON object with keys: "codeforces", "leetcode", "github"
  Each value is an array of bullet strings
- No markdown, no explanation, only the JSON object

DATA:
Codeforces:
  Current rating: {cf.get('rating', 0)} ({cf.get('rank', 'unrated')})
  Max rating: {cf.get('max_rating', 0)} ({cf.get('max_rank', '')})
  Problems solved: {cf.get('solved_count', 0)}

LeetCode:
  Total solved: {lc.get('solved_total', 0)}
  Easy: {lc.get('solved_easy', 0)} | Medium: {lc.get('solved_medium', 0)} | Hard: {lc.get('solved_hard', 0)}
  Contest ranking: {lc.get('ranking', 0)}

GitHub:
  Public repos: {gh.get('public_repos', 0)}
  Total stars: {gh.get('total_stars', 0)}
  Top languages: {', '.join(gh.get('top_languages', [])[:4])}

Return only the JSON object."""

    print("[AI] Writing achievement bullets...")
    result = _call_ai(config, prompt)

    if result:
        try:
            clean = result.strip().replace("```json", "").replace("```", "").strip()
            parsed = json.loads(clean)
            _save_cache("achievements", input_data, parsed)
            return parsed
        except:
            pass

    # Fallback
    return {
        "codeforces": [
            f"Achieved Codeforces rating of {cf.get('rating',0)} ({cf.get('rank','')}) through regular contest participation.",
            f"Solved {cf.get('solved_count',0)}+ problems focusing on data structures and algorithms."
        ] if cf.get("rating") else [],
        "leetcode": [
            f"Solved {lc.get('solved_total',0)}+ problems across arrays, graphs, DP, and advanced data structures.",
            f"Maintained contest rating of {lc.get('ranking',0)} — Easy: {lc.get('solved_easy',0)}, Medium: {lc.get('solved_medium',0)}, Hard: {lc.get('solved_hard',0)}."
        ] if lc.get("solved_total") else [],
        "github": [
            f"Maintains {gh.get('public_repos',0)} public repositories with {gh.get('total_stars',0)} total stars across {', '.join(gh.get('top_languages',[])[:3])}."
        ] if gh.get("public_repos") else []
    }


# ══════════════════════════════════════════════════════════
#  TRAINING ENHANCER
# ══════════════════════════════════════════════════════════

def enhance_training_entry(config: dict, entry: str, force=False) -> list:
    input_data = {"entry": entry}

    if not force:
        cached = _get_cached("training", input_data)
        if cached:
            return cached

    prompt = f"""You are a professional resume writer.

Enhance this training/certification entry into exactly 3 bullet points for a resume.

RULES:
- Start each bullet with an action verb
- Be specific and technical
- Sound professional and impressive
- Return ONLY a JSON array of exactly 3 strings
- No markdown, no explanation

Entry: "{entry}"

Return only the JSON array."""

    result = _call_ai(config, prompt)

    if result:
        try:
            clean = result.strip().replace("```json", "").replace("```", "").strip()
            bullets = json.loads(clean)
            _save_cache("training", input_data, bullets)
            return bullets
        except:
            lines = [l.strip().lstrip("-•").strip()
                     for l in result.split("\n") if l.strip() and len(l.strip()) > 10]
            _save_cache("training", input_data, lines)
            return lines

    return [entry]


# ══════════════════════════════════════════════════════════
#  MASTER FUNCTION
# ══════════════════════════════════════════════════════════

def generate_all_ai_content(config: dict, force_regenerate=False) -> dict:
    api_key = config.get("gemini", {}).get("api_key", "")
    groq_key = config.get("groq", {}).get("api_key", "")

    if (not api_key or api_key.startswith("PASTE")) and (not groq_key or groq_key.startswith("PASTE")):
        print("[AI] ⚠️  No AI API keys provided in config.yaml")
        print("     We highly recommend using a FREE Groq key for faster generation.")
        print("     Get a free Groq key at: console.groq.com")

    gh    = db.get_latest_snapshot("github")
    cf    = db.get_latest_snapshot("codeforces")
    lc    = db.get_latest_snapshot("leetcode")
    projs = db.get_projects(limit=6)

    github_username = config.get("profile", {}).get("github_username", "")
    all_exp = list(config.get("experience", [])) + db.get_experience()

    result = {"projects": {}, "achievements": {}, "training": {}}

    for proj in projs:
        result["projects"][proj["name"]] = generate_project_bullets(
            config, proj, github_username, force=force_regenerate
        )

    result["achievements"] = generate_achievements(
        config, cf, lc, gh, force=force_regenerate
    )

    for entry in all_exp:
        result["training"][entry] = enhance_training_entry(
            config, entry, force=force_regenerate
        )

    return result
