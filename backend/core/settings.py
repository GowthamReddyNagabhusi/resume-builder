"""Application settings loader with environment-first secret handling."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "config.yaml"
ENV_PATH = ROOT_DIR / ".env"


def _load_yaml_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _load_local_env() -> None:
    if not ENV_PATH.exists():
        return
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        clean = line.strip()
        if not clean or clean.startswith("#") or "=" not in clean:
            continue
        key, value = clean.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def get_settings() -> dict[str, Any]:
    """Load app settings with env vars overriding file-based values."""
    _load_local_env()
    cfg = _load_yaml_config()

    app_cfg = cfg.setdefault("app", {})
    auth_cfg = cfg.setdefault("auth", {})
    groq_cfg = cfg.setdefault("groq", {})

    app_cfg["jwt_secret"] = os.getenv("JWT_SECRET", auth_cfg.get("jwt_secret", "change-me-in-env"))
    app_cfg["jwt_algorithm"] = os.getenv("JWT_ALGORITHM", auth_cfg.get("jwt_algorithm", "HS256"))
    app_cfg["jwt_exp_minutes"] = int(os.getenv("JWT_EXP_MINUTES", auth_cfg.get("jwt_exp_minutes", 120)))

    # Always read Groq key from env first so keys are never committed.
    groq_cfg["api_key"] = os.getenv("GROQ_API_KEY", groq_cfg.get("api_key", ""))

    return cfg
