#!/usr/bin/env python3
"""Validate the structured cheat catalog without external dependencies."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TITLES_DIR = ROOT / "titles"
TITLE_RE = re.compile(r"^(?:PPSA|CUSA)\d{5}$")
VERSION_RE = re.compile(r"^\d{2}(?:\.\d{2,3}){1,2}$")
SUPPORTED_FORMATS = {"json", "shn", "mc4"}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_title(title_dir: Path) -> list[str]:
    errors: list[str] = []
    title_id = title_dir.name
    title_path = title_dir / "title.json"

    if not TITLE_RE.match(title_id):
        errors.append(f"{title_dir.relative_to(ROOT)}: directory name is not a title ID")
    if not title_path.exists():
        errors.append(f"{title_dir.relative_to(ROOT)}: missing title.json")
        return errors

    try:
        title = load_json(title_path)
    except Exception as exc:
        return [f"{title_path.relative_to(ROOT)}: invalid JSON: {exc}"]

    if title.get("titleId") != title_id:
        errors.append(f"{title_path.relative_to(ROOT)}: titleId does not match directory")
    if not title.get("name"):
        errors.append(f"{title_path.relative_to(ROOT)}: missing name")

    for version_dir in sorted(path for path in title_dir.iterdir() if path.is_dir()):
        if version_dir.name == "media":
            continue
        errors.extend(validate_manifest(version_dir, title_id))

    return errors


def validate_manifest(version_dir: Path, title_id: str) -> list[str]:
    errors: list[str] = []
    version = version_dir.name
    manifest_path = version_dir / "manifest.json"

    if not VERSION_RE.match(version):
        errors.append(f"{version_dir.relative_to(ROOT)}: directory name is not a version")
    if not manifest_path.exists():
        errors.append(f"{version_dir.relative_to(ROOT)}: missing manifest.json")
        return errors

    try:
        manifest = load_json(manifest_path)
    except Exception as exc:
        return [f"{manifest_path.relative_to(ROOT)}: invalid JSON: {exc}"]

    if manifest.get("titleId") != title_id:
        errors.append(f"{manifest_path.relative_to(ROOT)}: titleId mismatch")
    if manifest.get("version") != version:
        errors.append(f"{manifest_path.relative_to(ROOT)}: version mismatch")
    if manifest.get("preferredFormat") not in SUPPORTED_FORMATS:
        errors.append(f"{manifest_path.relative_to(ROOT)}: invalid preferredFormat")

    entries = manifest.get("entries")
    if not isinstance(entries, list) or not entries:
        errors.append(f"{manifest_path.relative_to(ROOT)}: entries must be non-empty")
        return errors

    seen_formats = set()
    for entry in entries:
        fmt = entry.get("format")
        rel_path = entry.get("path")
        if fmt not in SUPPORTED_FORMATS:
            errors.append(f"{manifest_path.relative_to(ROOT)}: invalid entry format {fmt}")
            continue
        if fmt in seen_formats:
            errors.append(f"{manifest_path.relative_to(ROOT)}: duplicate format {fmt}")
        seen_formats.add(fmt)

        expected_name = f"{title_id}_{version}.{fmt}"
        if rel_path != expected_name:
            errors.append(
                f"{manifest_path.relative_to(ROOT)}: {rel_path} should be {expected_name}"
            )
            continue

        file_path = version_dir / rel_path
        if not file_path.exists():
            errors.append(f"{file_path.relative_to(ROOT)}: missing file")
            continue

        actual_size = file_path.stat().st_size
        if int(entry.get("size", -1)) != actual_size:
            errors.append(f"{file_path.relative_to(ROOT)}: size mismatch")

        actual_sha = sha256_file(file_path)
        if entry.get("sha256") != actual_sha:
            errors.append(f"{file_path.relative_to(ROOT)}: sha256 mismatch")

        if fmt == "json":
            errors.extend(validate_json_payload(file_path, title_id, version, entry))

    preferred = manifest.get("preferredFormat")
    if preferred not in seen_formats:
        errors.append(f"{manifest_path.relative_to(ROOT)}: preferredFormat has no entry")

    return errors


def validate_json_payload(file_path: Path, title_id: str, version: str, entry: dict) -> list[str]:
    errors: list[str] = []
    try:
        payload = load_json(file_path)
    except Exception as exc:
        return [f"{file_path.relative_to(ROOT)}: invalid cheat JSON: {exc}"]

    if payload.get("id") != title_id:
        errors.append(f"{file_path.relative_to(ROOT)}: JSON id mismatch")
    if payload.get("version") != version:
        errors.append(f"{file_path.relative_to(ROOT)}: JSON version mismatch")
    mods = payload.get("mods")
    if not isinstance(mods, list):
        errors.append(f"{file_path.relative_to(ROOT)}: JSON mods must be an array")
        return errors
    if int(entry.get("cheatCount", -1)) != len(mods):
        errors.append(f"{file_path.relative_to(ROOT)}: cheatCount mismatch")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--titles-dir", default=str(TITLES_DIR))
    args = parser.parse_args()

    titles_dir = Path(args.titles_dir)
    if not titles_dir.is_absolute():
        titles_dir = ROOT / titles_dir
    if not titles_dir.exists():
        raise SystemExit(f"titles directory not found: {titles_dir}")

    errors: list[str] = []
    for title_dir in sorted(path for path in titles_dir.iterdir() if path.is_dir()):
        if title_dir.name.startswith("."):
            continue
        errors.extend(validate_title(title_dir))

    if errors:
        for error in errors:
            print(f"error: {error}")
        return 1

    print("catalog structure is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
