#!/usr/bin/env python3
"""Import locally collected raw RAR cheat archives into titles/."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from import_goldhen_repository import (
    ROOT,
    TITLES_DIR,
    build_entry,
    clean_name,
    load_converter_functions,
    save_json,
    sanitize_json_payload,
    utc_now,
)

RAW_DIR = ROOT / "raw"
FILENAME_RE = re.compile(
    r"(?P<title>(?:CUSA|PPSA)\d{5})_"
    r"(?P<version>\d{2}(?:\.\d{2,3}){1,2})"
    r".*?\.(?P<format>json|shn|mc4)$",
    re.IGNORECASE,
)
FORMAT_PRIORITY = {"json": 0, "shn": 1, "mc4": 2}


@dataclass(frozen=True)
class RawPayload:
    archive: Path
    path: Path
    title_id: str
    version: str
    fmt: str


def extract_archives(raw_dir: Path, output_dir: Path) -> list[Path]:
    archives = sorted(raw_dir.glob("*.rar"))
    for archive in archives:
        archive_output = output_dir / archive.stem
        archive_output.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                "unar",
                "-quiet",
                "-force-overwrite",
                "-output-directory",
                str(archive_output),
                str(archive),
            ],
            check=False,
        )
    return archives


def collect_payloads(raw_dir: Path, extracted_dir: Path) -> tuple[dict[tuple[str, str], list[RawPayload]], list[str]]:
    groups: dict[tuple[str, str], list[RawPayload]] = {}
    ignored: list[str] = []
    for archive in sorted(raw_dir.glob("*.rar")):
        archive_output = extracted_dir / archive.stem
        for path in sorted(archive_output.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in (".json", ".shn", ".mc4"):
                continue
            match = FILENAME_RE.search(path.name)
            if not match:
                ignored.append(str(path.relative_to(extracted_dir)))
                continue
            payload = RawPayload(
                archive=archive,
                path=path,
                title_id=match.group("title").upper(),
                version=match.group("version"),
                fmt=match.group("format").lower(),
            )
            groups.setdefault((payload.title_id, payload.version), []).append(payload)
    return groups, ignored


def payload_sort_key(payload: RawPayload) -> tuple[float, int, str]:
    return (-payload.path.stat().st_mtime, FORMAT_PRIORITY[payload.fmt], payload.archive.name)


def payload_to_json(payload: RawPayload, funcs: dict) -> dict:
    if payload.fmt == "json":
        return json.loads(payload.path.read_text(encoding="utf-8-sig", errors="replace"))
    if payload.fmt == "shn":
        raw_text = payload.path.read_text(encoding="utf-8-sig", errors="ignore")
        shn_text = funcs["normalize_shn"](
            funcs["remove_xml_junk"](funcs["escape_ampersand"](raw_text))
        )
        return funcs["shn_to_json"](shn_text)
    shn_text = funcs["normalize_shn"](funcs["decrypt_mc4"](payload.path.read_bytes()))
    return funcs["shn_to_json"](shn_text)


def import_payload(payload: RawPayload, funcs: dict, dry_run: bool) -> dict:
    title_id = payload.title_id
    version = payload.version
    version_dir = TITLES_DIR / title_id / version
    title_path = TITLES_DIR / title_id / "title.json"
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
    source_note = f"Local raw archive import. Source archive: raw/{payload.archive.name}."

    if not dry_run:
        version_dir.mkdir(parents=True, exist_ok=True)
        json_path = version_dir / f"{stem}.json"
        shn_path = version_dir / f"{stem}.shn"
        mc4_path = version_dir / f"{stem}.mc4"

        save_json(json_path, json_obj)
        shn_path.write_text(shn_text, encoding="utf-8")
        mc4_path.write_bytes(funcs["encrypt_mc4"](shn_text))

        previous_revision = 0
        manifest_path = version_dir / "manifest.json"
        if manifest_path.exists():
            try:
                previous_revision = int(json.loads(manifest_path.read_text(encoding="utf-8")).get("revision", 0))
            except Exception:
                previous_revision = 0

        manifest = {
            "schemaVersion": 1,
            "titleId": title_id,
            "version": version,
            "name": name,
            "process": process,
            "revision": max(1, previous_revision + 1),
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
                    "metadataSource": "local-raw-import",
                    "metadataUpdatedAt": now,
                    "notes": "Generated from local raw archive import.",
                },
            )

    return {
        "titleId": title_id,
        "version": version,
        "name": name,
        "sourceArchive": f"raw/{payload.archive.name}",
        "sourceFile": payload.path.name,
        "format": payload.fmt,
        "cheatCount": cheat_count,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", default=str(RAW_DIR))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when any archive payload fails.")
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir)
    if not raw_dir.is_absolute():
        raw_dir = ROOT / raw_dir
    if not raw_dir.exists():
        raise SystemExit(f"raw directory not found: {raw_dir}")

    funcs = load_converter_functions()
    with tempfile.TemporaryDirectory(prefix="kylin-raw-import-") as temp:
        temp_dir = Path(temp)
        archives = extract_archives(raw_dir, temp_dir)
        groups, ignored = collect_payloads(raw_dir, temp_dir)

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
                        "candidates": [f"raw/{payload.archive.name}:{payload.path.name}" for payload in payloads],
                    }
                )

    print(
        json.dumps(
            {
                "summary": {
                    "archives": len(archives),
                    "groups": len(groups),
                    "imported" if not args.dry_run else "wouldImport": len(imported),
                    "ignored": len(ignored),
                    "failed": len(failures),
                },
                "imported": imported,
                "ignored": ignored,
                "failures": failures,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 1 if args.strict and failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
