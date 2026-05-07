#!/usr/bin/env python3
"""Import contributor-provided json/shn/mc4 cheat payloads into titles/."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

from import_goldhen_repository import (
    ROOT,
    TITLES_DIR,
    build_entry,
    clean_name,
    load_converter_functions,
    load_json,
    save_json,
    sanitize_json_payload,
    utc_now,
)

FILENAME_RE = re.compile(
    r"(?:^|_)(?P<title>(?:CUSA|PPSA)\d{5})_"
    r"(?P<version>\d{1,2}(?:\.\d{2,3}){1,2})"
    r"(?:[_\.].*)?\.(?P<format>json|shn|mc4)$",
    re.IGNORECASE,
)
FORMAT_PRIORITY = {"json": 0, "shn": 1, "mc4": 2}


@dataclass(frozen=True)
class ContributorPayload:
    path: Path
    rel_path: str
    title_id: str
    version: str
    fmt: str


def normalize_version(version: str) -> str:
    parts = version.split(".")
    parts[0] = parts[0].zfill(2)
    return ".".join(parts)


def relative_label(path: Path, source_dir: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.relative_to(source_dir).as_posix()


def collect_payloads(source_dir: Path) -> tuple[dict[tuple[str, str], list[ContributorPayload]], list[str]]:
    groups: dict[tuple[str, str], list[ContributorPayload]] = {}
    unparsed: list[str] = []
    for path in sorted(source_dir.rglob("*")):
        if not path.is_file() or path.name == ".DS_Store":
            continue
        rel_path = relative_label(path, source_dir)
        if path.suffix.lower() not in (".json", ".shn", ".mc4"):
            unparsed.append(rel_path)
            continue
        match = FILENAME_RE.search(path.name)
        if not match:
            unparsed.append(rel_path)
            continue
        payload = ContributorPayload(
            path=path,
            rel_path=rel_path,
            title_id=match.group("title").upper(),
            version=normalize_version(match.group("version")),
            fmt=match.group("format").lower(),
        )
        groups.setdefault((payload.title_id, payload.version), []).append(payload)
    return groups, unparsed


def payload_sort_key(payload: ContributorPayload) -> tuple[int, float, str]:
    return (FORMAT_PRIORITY[payload.fmt], -payload.path.stat().st_mtime, payload.rel_path)


def payload_to_json(payload: ContributorPayload, funcs: dict) -> dict:
    if payload.fmt == "json":
        return load_json(payload.path)
    if payload.fmt == "shn":
        raw_text = payload.path.read_text(encoding="utf-8-sig", errors="ignore")
        shn_text = funcs["normalize_shn"](
            funcs["remove_xml_junk"](funcs["escape_ampersand"](raw_text))
        )
        return funcs["shn_to_json"](shn_text)
    shn_text = funcs["normalize_shn"](funcs["decrypt_mc4"](payload.path.read_bytes()))
    return funcs["shn_to_json"](shn_text)


def import_payload(payload: ContributorPayload, funcs: dict, dry_run: bool) -> dict:
    title_id = payload.title_id
    version = payload.version
    version_dir = TITLES_DIR / title_id / version
    title_path = TITLES_DIR / title_id / "title.json"
    manifest_path = version_dir / "manifest.json"
    stem = f"{title_id}_{version}"
    now = utc_now()

    json_obj = payload_to_json(payload, funcs)
    fallback_name = title_id
    if title_path.exists():
        try:
            fallback_name = json.loads(title_path.read_text(encoding="utf-8")).get("name", title_id)
        except Exception:
            fallback_name = title_id
    name = clean_name(json_obj.get("name"), fallback_name)
    process = clean_name(json_obj.get("process"), "eboot.bin")
    json_obj = sanitize_json_payload(json_obj, title_id, version, name, process)
    shn_text = funcs["normalize_shn"](funcs["json_to_shn"](json_obj))
    cheat_count = len(json_obj.get("mods", [])) if isinstance(json_obj.get("mods"), list) else 0
    source_note = f"Contributor cheat import. Source file: {payload.rel_path}."

    previous_revision = 0
    existed = manifest_path.exists()
    if existed:
        try:
            previous_revision = int(json.loads(manifest_path.read_text(encoding="utf-8")).get("revision", 0))
        except Exception:
            previous_revision = 0

    if not dry_run:
        version_dir.mkdir(parents=True, exist_ok=True)
        json_path = version_dir / f"{stem}.json"
        shn_path = version_dir / f"{stem}.shn"
        mc4_path = version_dir / f"{stem}.mc4"

        save_json(json_path, json_obj)
        shn_path.write_text(shn_text, encoding="utf-8")
        mc4_path.write_bytes(funcs["encrypt_mc4"](shn_text))

        revision = max(1, previous_revision + 1)
        manifest = {
            "schemaVersion": 1,
            "titleId": title_id,
            "version": version,
            "name": name,
            "process": process,
            "revision": revision,
            "preferredFormat": "json",
            "regions": [],
            "compatibleTitleIds": [title_id],
            "updatedAt": now,
            "notes": source_note,
            "entries": [
                build_entry(json_path, "json", cheat_count, source_note, now),
                build_entry(shn_path, "shn", cheat_count, source_note, now),
                build_entry(mc4_path, "mc4", cheat_count, source_note, now),
            ],
        }
        save_json(manifest_path, manifest)

        if not title_path.exists():
            save_json(
                title_path,
                {
                    "schemaVersion": 1,
                    "titleId": title_id,
                    "name": name,
                    "regions": [],
                    "aliases": [],
                    "platforms": ["PS4" if title_id.startswith("CUSA") else "PS5"],
                    "metadataSource": "contributor-import",
                    "metadataUpdatedAt": now,
                    "notes": "Generated from contributor cheat import.",
                },
            )

    return {
        "titleId": title_id,
        "version": version,
        "name": name,
        "sourceFile": payload.rel_path,
        "format": payload.fmt,
        "cheatCount": cheat_count,
        "action": "replace" if existed else "create",
        "revision": max(1, previous_revision + 1),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        required=True,
        help="Directory containing contributor json/shn/mc4 files named like CUSA00000_01.00.json.",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when any source group fails.")
    args = parser.parse_args()

    source_dir = Path(args.source).expanduser()
    if not source_dir.is_absolute():
        source_dir = ROOT / source_dir
    source_dir = source_dir.resolve()
    if not source_dir.exists():
        raise SystemExit(f"source directory not found: {source_dir}")

    funcs = load_converter_functions()
    groups, unparsed = collect_payloads(source_dir)
    imported: list[dict] = []
    failures: list[dict] = []

    for key, payloads in sorted(groups.items()):
        last_error: Exception | None = None
        for payload in sorted(payloads, key=payload_sort_key):
            try:
                imported.append(import_payload(payload, funcs, args.dry_run))
                last_error = None
                break
            except Exception as exc:
                last_error = exc
        if last_error is not None:
            failures.append(
                {
                    "titleId": key[0],
                    "version": key[1],
                    "error": str(last_error),
                    "candidates": [payload.rel_path for payload in payloads],
                }
            )

    print(
        json.dumps(
            {
                "summary": {
                    "groups": len(groups),
                    "imported" if not args.dry_run else "wouldImport": len(imported),
                    "create": sum(item["action"] == "create" for item in imported),
                    "replace": sum(item["action"] == "replace" for item in imported),
                    "unparsed": len(unparsed),
                    "failed": len(failures),
                },
                "imported": imported[:100],
                "unparsed": unparsed[:50],
                "failures": failures[:50],
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 1 if args.strict and failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
