#!/usr/bin/env python3
"""Import GoldHEN cheat files into the published titles catalog."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TITLES_DIR = ROOT / "titles"
CONVERTER_DIR = ROOT / "ps4_ps5_aio_cheat_converter"
DEFAULT_SOURCE = Path("/Users/chenpy/Projects/Person/etaHEN/GoldHEN_Cheat_Repository")
SUPPORTED_FORMATS = ("json", "shn", "mc4")
SOURCE_PRIORITY = {"json": 0, "shn": 1, "mc4": 2}
FILENAME_RE = re.compile(
    r"^(?P<title>(?:CUSA|PPSA)\d{5})_"
    r"(?P<version>\d{2}(?:\.\d{2,3}){1,2})"
    r"(?P<suffix>.*?)\.(?P<format>json|shn|mc4)$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class SourceFile:
    path: Path
    title_id: str
    version: str
    suffix: str
    fmt: str


@dataclass
class ImportGroup:
    title_id: str
    version: str
    files: list[SourceFile] = field(default_factory=list)


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        repaired = re.sub(r",(\s*[\]}])", r"\1", text)
        return json.loads(repaired)


def save_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_converter_functions() -> dict:
    if not CONVERTER_DIR.exists():
        raise SystemExit(f"converter directory not found: {CONVERTER_DIR}")

    sys.path.insert(0, str(CONVERTER_DIR))
    from utilities.catch_exceptions_utilities import escape_ampersand, remove_xml_junk_data
    from utilities.json_utilities import shn_to_json_workflow
    from utilities.mc4_utilities import decrypt_mc4_to_shn, encrypt_shn_to_mc4
    from utilities.shn_utilities import json_to_xml_workflow, normalize_xml_entity_idents

    return {
        "shn_to_json": shn_to_json_workflow,
        "decrypt_mc4": decrypt_mc4_to_shn,
        "encrypt_mc4": encrypt_shn_to_mc4,
        "json_to_shn": json_to_xml_workflow,
        "normalize_shn": normalize_xml_entity_idents,
        "escape_ampersand": escape_ampersand,
        "remove_xml_junk": remove_xml_junk_data,
    }


def parse_source_file(path: Path) -> SourceFile | None:
    match = FILENAME_RE.match(path.name)
    if not match:
        return None
    return SourceFile(
        path=path,
        title_id=match.group("title").upper(),
        version=match.group("version"),
        suffix=match.group("suffix"),
        fmt=match.group("format").lower(),
    )


def load_name_map(source_root: Path) -> dict[str, str]:
    names: dict[str, str] = {}
    for mapping_path in (source_root / "shn.txt", source_root / "mc4.txt", source_root / "json.txt"):
        if not mapping_path.exists():
            continue
        for line in mapping_path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            if "=" not in line:
                continue
            filename, name = line.split("=", 1)
            name = name.strip()
            if name and name != "(null)":
                names[filename.strip()] = name
    return names


def collect_groups(source_root: Path) -> tuple[dict[tuple[str, str], ImportGroup], list[str]]:
    groups: dict[tuple[str, str], ImportGroup] = {}
    unparsed: list[str] = []
    for fmt in SUPPORTED_FORMATS:
        fmt_dir = source_root / fmt
        if not fmt_dir.exists():
            continue
        for path in sorted(fmt_dir.iterdir()):
            if not path.is_file() or path.suffix.lower() != f".{fmt}":
                continue
            source = parse_source_file(path)
            if not source:
                unparsed.append(str(path.relative_to(source_root)))
                continue
            key = (source.title_id, source.version)
            groups.setdefault(key, ImportGroup(source.title_id, source.version)).files.append(source)
    return groups, unparsed


def source_rank(source: SourceFile) -> tuple[int, int, str]:
    clean_suffix = source.suffix in ("", "_default", "_default.elf", "_eboot.bin")
    return (SOURCE_PRIORITY[source.fmt], 0 if clean_suffix else 1, source.suffix)


def choose_source(group: ImportGroup) -> SourceFile:
    return sorted(group.files, key=source_rank)[0]


def payload_from_source(source: SourceFile, funcs: dict) -> dict:
    if source.fmt == "json":
        return load_json(source.path)

    if source.fmt == "shn":
        raw_text = source.path.read_text(encoding="utf-8-sig", errors="ignore")
        shn_text = funcs["normalize_shn"](
            funcs["remove_xml_junk"](funcs["escape_ampersand"](raw_text))
        )
        return funcs["shn_to_json"](shn_text)

    shn_text = funcs["normalize_shn"](funcs["decrypt_mc4"](source.path.read_bytes()))
    return funcs["shn_to_json"](shn_text)


def clean_name(value: object, fallback: str) -> str:
    if isinstance(value, str):
        value = value.strip()
        if value and value != "(null)":
            return value
    return fallback


def sanitize_json_payload(payload: dict, title_id: str, version: str, name: str, process: str) -> dict:
    payload["id"] = title_id
    payload["version"] = version
    payload["name"] = name
    payload["process"] = process
    mods = payload.get("mods")
    if isinstance(mods, list):
        for index, mod in enumerate(mods, 1):
            if isinstance(mod, dict) and not clean_name(mod.get("name"), ""):
                mod["name"] = f"Cheat {index}"
    return payload


def build_entry(path: Path, fmt: str, cheat_count: int, source_note: str, now: str) -> dict:
    return {
        "format": fmt,
        "path": path.name,
        "size": path.stat().st_size,
        "sha256": sha256_file(path),
        "cheatCount": cheat_count,
        "source": source_note,
        "quality": "imported",
        "updatedAt": now,
        "notes": "Imported from GoldHEN_Cheat_Repository.",
    }


def write_imported_group(
    group: ImportGroup,
    source: SourceFile,
    source_root: Path,
    name_map: dict[str, str],
    funcs: dict,
    dry_run: bool,
) -> dict:
    title_id = group.title_id
    version = group.version
    version_dir = TITLES_DIR / title_id / version
    title_path = TITLES_DIR / title_id / "title.json"
    stem = f"{title_id}_{version}"
    now = utc_now()

    json_obj = payload_from_source(source, funcs)
    fallback_name = name_map.get(source.path.name, title_id)
    name = clean_name(json_obj.get("name"), fallback_name)
    process = clean_name(json_obj.get("process"), "eboot.bin")
    json_obj = sanitize_json_payload(json_obj, title_id, version, name, process)
    shn_text = funcs["normalize_shn"](funcs["json_to_shn"](json_obj))
    cheat_count = len(json_obj.get("mods", [])) if isinstance(json_obj.get("mods"), list) else 0

    alternatives = sorted(f.path.name for f in group.files if f.path != source.path)
    source_rel = source.path.relative_to(source_root).as_posix()
    source_note = f"GoldHEN_Cheat_Repository import. Source file: {source_rel}."
    if alternatives:
        source_note += f" Other candidate files skipped: {len(alternatives)}."

    if not dry_run:
        version_dir.mkdir(parents=True, exist_ok=True)
        json_path = version_dir / f"{stem}.json"
        shn_path = version_dir / f"{stem}.shn"
        mc4_path = version_dir / f"{stem}.mc4"

        save_json(json_path, json_obj)
        shn_path.write_text(shn_text, encoding="utf-8")
        mc4_path.write_bytes(funcs["encrypt_mc4"](shn_text))

        manifest = {
            "schemaVersion": 1,
            "titleId": title_id,
            "version": version,
            "name": name,
            "process": process,
            "revision": 1,
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
        save_json(version_dir / "manifest.json", manifest)

        if not title_path.exists():
            title = {
                "schemaVersion": 1,
                "titleId": title_id,
                "name": name,
                "regions": [],
                "aliases": [],
                "platforms": ["PS4" if title_id.startswith("CUSA") else "PS5"],
                "metadataSource": "goldhen-import",
                "metadataUpdatedAt": now,
                "notes": "Generated from GoldHEN_Cheat_Repository import.",
            }
            title_path.parent.mkdir(parents=True, exist_ok=True)
            save_json(title_path, title)

    return {
        "titleId": title_id,
        "version": version,
        "name": name,
        "source": source_rel,
        "candidateCount": len(group.files),
        "cheatCount": cheat_count,
    }


def remove_existing_version(version_dir: Path) -> None:
    if version_dir.exists():
        shutil.rmtree(version_dir)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=str(DEFAULT_SOURCE), help="GoldHEN_Cheat_Repository path.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--replace-existing", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when any source group fails.")
    args = parser.parse_args()

    source_root = Path(args.source).expanduser().resolve()
    if not source_root.exists():
        raise SystemExit(f"source repository not found: {source_root}")

    groups, unparsed = collect_groups(source_root)
    name_map = load_name_map(source_root)
    funcs = load_converter_functions()

    imported: list[dict] = []
    skipped_existing: list[str] = []
    failures: list[dict] = []

    for key in sorted(groups):
        group = groups[key]
        version_dir = TITLES_DIR / group.title_id / group.version
        if version_dir.exists() and not args.replace_existing:
            skipped_existing.append(f"{group.title_id}_{group.version}")
            continue
        if args.limit and len(imported) >= args.limit:
            break

        try:
            last_error: Exception | None = None
            for source in sorted(group.files, key=source_rank):
                try:
                    if not args.dry_run and args.replace_existing:
                        remove_existing_version(version_dir)
                    imported.append(
                        write_imported_group(group, source, source_root, name_map, funcs, args.dry_run)
                    )
                    last_error = None
                    break
                except Exception as exc:
                    last_error = exc
            if last_error is not None:
                raise last_error
        except Exception as exc:
            failures.append(
                {
                    "titleId": group.title_id,
                    "version": group.version,
                    "error": str(exc),
                    "candidates": [file.path.name for file in group.files],
                }
            )

    print(
        json.dumps(
            {
                "summary": {
                    "sourceGroups": len(groups),
                    "imported" if not args.dry_run else "wouldImport": len(imported),
                    "skippedExisting": len(skipped_existing),
                    "unparsedFilenames": len(unparsed),
                    "failed": len(failures),
                },
                "imported": imported[:20],
                "skippedExisting": skipped_existing[:20],
                "unparsed": unparsed[:20],
                "failures": failures[:20],
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 1 if args.strict and failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
