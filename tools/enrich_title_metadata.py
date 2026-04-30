#!/usr/bin/env python3
"""Enrich title.json from published manifests without external services."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TITLES_DIR = ROOT / "titles"


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def platform_for_title_id(title_id: str) -> str:
    if title_id.startswith("CUSA"):
        return "PS4"
    return "PS5"


def enrich_title(title_dir: Path) -> bool:
    title_path = title_dir / "title.json"
    if not title_path.exists():
        return False

    title = load_json(title_path)
    manifests = sorted(title_dir.glob("*/manifest.json"))
    if not manifests:
        return False

    names: list[str] = []
    for manifest_path in manifests:
        manifest = load_json(manifest_path)
        if manifest.get("name"):
            names.append(manifest["name"])

    if names:
        title["name"] = names[0]
    title["platforms"] = [platform_for_title_id(title["titleId"])]
    title["metadataSource"] = "published-manifest"
    title["metadataUpdatedAt"] = utc_now()
    if title.get("notes", "").startswith("Name pending"):
        title["notes"] = "Generated from published cheat metadata."

    save_json(title_path, title)
    return True


def main() -> int:
    updated = 0
    for title_dir in sorted(path for path in TITLES_DIR.iterdir() if path.is_dir()):
        if enrich_title(title_dir):
            updated += 1
    print(f"updated {updated} title metadata files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
