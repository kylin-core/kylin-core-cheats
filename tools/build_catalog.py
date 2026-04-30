#!/usr/bin/env python3
"""Build catalog.json from titles/* metadata."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TITLES_DIR = ROOT / "titles"
CATALOG_PATH = ROOT / "catalog.json"
SUPPORTED_FORMATS = ["json", "shn", "mc4"]


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_catalog(catalog_version: int, base_url: str | None) -> dict:
    titles = []

    for title_dir in sorted(TITLES_DIR.iterdir() if TITLES_DIR.exists() else []):
        if not title_dir.is_dir() or title_dir.name.startswith("."):
            continue

        title_path = title_dir / "title.json"
        if not title_path.exists():
            continue

        title_meta = load_json(title_path)
        versions = []
        for version_dir in sorted(title_dir.iterdir()):
            manifest_path = version_dir / "manifest.json"
            if not manifest_path.exists():
                continue

            manifest = load_json(manifest_path)
            rel_manifest = manifest_path.relative_to(ROOT).as_posix()
            preferred = manifest.get("preferredFormat", "json")
            preferred_entry = next(
                (
                    entry
                    for entry in manifest.get("entries", [])
                    if entry.get("format") == preferred
                ),
                {},
            )
            versions.append(
                {
                    "version": manifest["version"],
                    "manifest": rel_manifest,
                    "preferredFormat": preferred,
                    "cheatCount": int(preferred_entry.get("cheatCount", 0)),
                    "updatedAt": manifest.get("updatedAt")
                    or preferred_entry.get("updatedAt")
                    or "",
                    "revision": int(manifest.get("revision", 1)),
                }
            )

        if not versions:
            continue

        title = {
            "titleId": title_meta["titleId"],
            "name": title_meta["name"],
            "regions": title_meta.get("regions", []),
            "aliases": title_meta.get("aliases", []),
            "versions": versions,
        }
        for key in (
            "platforms",
            "publisher",
            "releaseDate",
            "storeUrl",
            "iconImage",
            "coverImage",
            "backgroundImage",
        ):
            if title_meta.get(key):
                title[key] = title_meta[key]
        titles.append(title)

    catalog = {
        "schemaVersion": 1,
        "catalogVersion": catalog_version,
        "generatedAt": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "formats": SUPPORTED_FORMATS,
        "titles": titles,
    }
    if base_url:
        catalog["baseUrl"] = base_url
    return catalog


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog-version", type=int, default=1)
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--output", default=str(CATALOG_PATH))
    parser.add_argument("--check", action="store_true", help="Print catalog without writing.")
    args = parser.parse_args()

    catalog = build_catalog(args.catalog_version, args.base_url)
    text = json.dumps(catalog, indent=2, ensure_ascii=False) + "\n"

    if args.check:
        print(text, end="")
        return 0

    output = Path(args.output)
    if not output.is_absolute():
        output = ROOT / output
    output.write_text(text, encoding="utf-8")
    print(f"wrote {output.relative_to(ROOT)} with {len(catalog['titles'])} titles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
