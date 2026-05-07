"""Shared path resolution helpers for maintenance tools."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GOLDHEN_SOURCE = ROOT.parent / "GoldHEN_Cheat_Repository"
DEFAULT_GOLDHEN_REPO_URL = "https://github.com/GoldHEN/GoldHEN_Cheat_Repository.git"

GOLDHEN_ENV_VARS = (
    "KYLIN_GOLDHEN_SOURCE",
    "GOLDHEN_CHEAT_REPOSITORY",
)
GOLDHEN_REPO_ENV_VARS = (
    "KYLIN_GOLDHEN_REPO_URL",
    "GOLDHEN_CHEAT_REPOSITORY_URL",
)


def resolve_path(value: str | None, fallback: Path | None = None) -> Path | None:
    if value:
        return Path(value).expanduser().resolve()
    if fallback is None:
        return None
    return fallback.expanduser().resolve()


def env_path(names: tuple[str, ...]) -> Path | None:
    for name in names:
        value = os.environ.get(name)
        if value:
            return resolve_path(value)
    return None


def resolve_goldhen_source(value: str | None = None) -> Path:
    return resolve_path(value) or env_path(GOLDHEN_ENV_VARS) or DEFAULT_GOLDHEN_SOURCE.resolve()


def resolve_goldhen_repo_url(value: str | None = None) -> str:
    if value:
        return value
    for name in GOLDHEN_REPO_ENV_VARS:
        env_value = os.environ.get(name)
        if env_value:
            return env_value
    return DEFAULT_GOLDHEN_REPO_URL


def missing_goldhen_message(path: Path) -> str:
    env_names = " or ".join(GOLDHEN_ENV_VARS)
    return (
        f"source repository not found: {path}\n"
        f"Pass --source /path/to/GoldHEN_Cheat_Repository or set {env_names}."
    )
