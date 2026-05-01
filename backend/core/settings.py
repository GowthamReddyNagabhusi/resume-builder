"""Application settings loader with environment-first secret handling."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from core.logger import get_logger

ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "config.yaml"
ENV_PATH = ROOT_DIR / ".env"
log = get_logger(__name__)


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

    jwt_secret = os.getenv("JWT_SECRET", "")
    weak_values = {"change-me-in-env", "change_this_to_a_long_random_secret"}
    if not jwt_secret or jwt_secret in weak_values or len(jwt_secret) < 32:
        raise RuntimeError(
            "Invalid JWT_SECRET. Set a strong value in .env. "
            "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
        )

    app_cfg["jwt_secret"] = jwt_secret
    app_cfg["jwt_algorithm"] = os.getenv("JWT_ALGORITHM", auth_cfg.get("jwt_algorithm", "HS256"))
    app_cfg["jwt_exp_minutes"] = int(os.getenv("JWT_EXP_MINUTES", auth_cfg.get("jwt_exp_minutes", 120)))

    # Always read Groq key from env first so keys are never committed.
    groq_cfg["api_key"] = os.getenv("GROQ_API_KEY", groq_cfg.get("api_key", ""))

    log.info("JWT secret validated (len=%d)", len(jwt_secret))

    return cfg
