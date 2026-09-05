"""
config.py — loads the single source of truth for all tunable settings.

WHY: docs/learning-pipeline explains that only the *soft* capability layer may be
tuned; the *hard* safety rules live in code. This module loads the soft settings
(thresholds, lexicons, auth ladder) from config/agent_config.json so that nothing
in the logic is a magic number. If the file is missing we fall back to safe
built-in defaults so the demo still runs.
"""

import json
import os

# Resolve repo paths relative to this file: src/nexbank_agent/config.py
_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))          # .../<repo>
CONFIG_PATH = os.path.join(REPO_ROOT, "config", "agent_config.json")
KB_PATH = os.path.join(REPO_ROOT, "src", "data", "knowledge_base.json")
TESTS_PATH = os.path.join(REPO_ROOT, "tests", "safety_cases.json")

# Minimal safe defaults (used only if the JSON is unavailable).
_DEFAULTS = {
    "authentication": {
        "levels": ["anonymous", "otp_verified", "biometric_verified", "full_kyc"],
        "session_timeout_minutes": 5,
    },
    "nlu_confidence": {"primary_min": 0.60, "margin_min": 0.15},
    "dialogue": {"max_clarifications": 2},
    "escalation": {"proximity_threshold": 0.7},
    "safety": {"max_input_chars": 1200},
}


def load_config():
    """Return the configuration dict (from file if present, else defaults)."""
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return _DEFAULTS


CONFIG = load_config()

# Auth ladder as an ordered mapping level -> rank, so we can compare "is the
# customer's level high enough for this action?" with a simple >= on the rank.
AUTH_LEVELS = CONFIG.get("authentication", _DEFAULTS["authentication"])["levels"]
AUTH_RANK = {level: i for i, level in enumerate(AUTH_LEVELS)}


def rank(level):
    """Numeric rank of an auth level (unknown levels are treated as anonymous)."""
    return AUTH_RANK.get(level, 0)


def safety_cfg(key, default=None):
    return CONFIG.get("safety", {}).get(key, default)
