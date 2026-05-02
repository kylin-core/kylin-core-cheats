#!/usr/bin/env python3
"""Audit imported GoldHEN sources against the published catalog."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TITLES_DIR = ROOT / "titles"
DEFAULT_SOURCE = Path("/Users/chenpy/Projects/Person/etaHEN/GoldHEN_Cheat_Repository")
FILENAME_RE = re.compile(
    r"^(?P<title>(?:CUSA|PPSA)\d{5})_"
    r"(?P<version>\d{2}(?:\.\d{2,3}){1,2})"
    r"(?P<suffix>.*?)\.(?P<format>json|shn|mc4)$",
    re.IGNORECASE,
)
SOURCE_RE = re.compile(r"Source file: ([^.]+\.(?:json|shn|mc4))")


def collect_source_groups(source_root: Path) -> tuple[dict[tuple[str, str], list[str]], list[str]]:
    groups: dict[tuple[str, str], list[str]] = {}
    unparsed: list[str] = []
    for fmt in ("json", "shn", "mc4"):
        fmt_dir = source_root / fmt
        if not fmt_dir.exists():
            continue
        for path in sorted(fmt_dir.iterdir()):
            if not path.is_file() or path.suffix.lower() != f".{fmt}":
                continue
            match = FILENAME_RE.match(path.name)
            rel = path.relative_to(source_root).as_posix()
            if not match:
                unparsed.append(rel)
                continue
            key = (match.group("title").upper(), match.group("version"))
            groups.setdefault(key, []).append(rel)
    return groups, unparsed


def collect_manifest_keys(source_root: Path) -> tuple[set[tuple[str, str]], list[tuple[str, str]], list[tuple[str, str]]]:
    manifest_keys: set[tuple[str, str]] = set()
    missing_entry_files: list[tuple[str, str]] = []
    missing_source_refs: list[tuple[str, str]] = []

    for manifest_path in sorted(TITLES_DIR.glob("*/*/manifest.json")):
        title_id = manifest_path.parts[-3]
        version = manifest_path.parts[-2]
        manifest_keys.add((title_id, version))
        rel_manifest = manifest_path.relative_to(ROOT).as_posix()

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception as exc:
            missing_entry_files.append((rel_manifest, f"invalid manifest json: {exc}"))
            continue

        for entry in manifest.get("entries", []):
            entry_path = manifest_path.parent / entry.get("path", "")
            if not entry_path.exists():
                missing_entry_files.append((rel_manifest, f"missing entry {entry.get('path')}"))

        match = SOURCE_RE.search(manifest.get("notes", ""))
        if match and not (source_root / match.group(1)).exists():
            missing_source_refs.append((rel_manifest, match.group(1)))

    return manifest_keys, missing_entry_files, missing_source_refs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=str(DEFAULT_SOURCE), help="GoldHEN_Cheat_Repository path.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when any audit gap exists.")
    args = parser.parse_args()

    source_root = Path(args.source).expanduser().resolve()
    if not source_root.exists():
        raise SystemExit(f"source repository not found: {source_root}")

    source_groups, unparsed = collect_source_groups(source_root)
    manifest_keys, missing_entry_files, missing_source_refs = collect_manifest_keys(source_root)
    missing_imports = sorted(source_groups.keys() - manifest_keys)
    extra_manifests = sorted(manifest_keys - source_groups.keys())

    report = {
        "summary": {
            "sourceGroups": len(source_groups),
            "manifestKeys": len(manifest_keys),
            "sourceGroupsWithoutManifest": len(missing_imports),
            "manifestKeysNotInGoldHENSource": len(extra_manifests),
            "unparsedSourceFiles": len(unparsed),
            "missingPublishedEntryFiles": len(missing_entry_files),
            "missingSourceFilesReferencedByManifest": len(missing_source_refs),
        },
        "sourceGroupsWithoutManifest": [f"{title_id}_{version}" for title_id, version in missing_imports[:50]],
        "manifestKeysNotInGoldHENSource": [f"{title_id}_{version}" for title_id, version in extra_manifests[:50]],
        "unparsedSourceFiles": unparsed[:50],
        "missingPublishedEntryFiles": missing_entry_files[:50],
        "missingSourceFilesReferencedByManifest": missing_source_refs[:50],
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))

    has_gaps = bool(missing_imports or missing_entry_files or missing_source_refs)
    return 1 if args.strict and has_gaps else 0


if __name__ == "__main__":
    raise SystemExit(main())
