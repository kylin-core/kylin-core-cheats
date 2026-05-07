#!/usr/bin/env python3
"""Check local maintenance-tool setup for this repository."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tool_paths import (
    resolve_goldhen_repo_url,
    resolve_goldhen_source,
)

ROOT = Path(__file__).resolve().parents[1]


def status(ok: bool, label: str, detail: str) -> None:
    prefix = "ok" if ok else "warn"
    print(f"{prefix}: {label}: {detail}")


def check_python() -> bool:
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    ok = sys.version_info >= (3, 10)
    status(ok, "python", f"{version} at {Path(sys.executable)}")
    return ok


def check_catalog() -> bool:
    required = (ROOT / "catalog.json", ROOT / "titles")
    missing = [path.relative_to(ROOT).as_posix() for path in required if not path.exists()]
    ok = not missing
    detail = "catalog files present" if ok else f"missing {', '.join(missing)}"
    status(ok, "catalog", detail)
    return ok


def check_converter() -> bool:
    converter_core = ROOT / "tools" / "converter_core"
    ok = (converter_core / "utilities").exists()
    status(
        ok,
        "converter",
        str(converter_core) if ok else f"missing vendored converter core at {converter_core}",
    )
    return ok


def check_goldhen() -> bool:
    source = resolve_goldhen_source()
    expected_dirs = [source / name for name in ("json", "shn", "mc4")]
    ok = source.exists() and any(path.exists() for path in expected_dirs)
    if ok:
        status(True, "goldhen-source", str(source))
        return True

    status(
        True,
        "goldhen-source",
        f"no local checkout found; GoldHEN import will auto-clone {resolve_goldhen_repo_url()} temporarily",
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when optional local setup checks fail.",
    )
    args = parser.parse_args()

    required = [check_python(), check_catalog()]
    optional = [check_converter(), check_goldhen()]

    if not all(required):
        return 1
    if args.strict and not all(optional):
        return 1

    print("done: basic catalog workflow is available")
    if not all(optional):
        print("note: warnings only affect import workflows, not basic validation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
