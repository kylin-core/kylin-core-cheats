#!/usr/bin/env python3
"""Build titles/README.md as a human-readable title index."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TITLES_DIR = ROOT / "titles"
INDEX_PATH = TITLES_DIR / "README.md"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def version_links(title_dir: Path) -> list[str]:
    links: list[str] = []
    for version_dir in sorted(path for path in title_dir.iterdir() if path.is_dir()):
        manifest_path = version_dir / "manifest.json"
        if not manifest_path.exists():
            continue
        links.append(f"[{version_dir.name}]({title_dir.name}/{version_dir.name}/)")
    return links


def table_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def build_index() -> str:
    rows = []
    for title_path in sorted(TITLES_DIR.glob("*/title.json")):
        title_dir = title_path.parent
        title = load_json(title_path)
        versions = version_links(title_dir)
        if not versions:
            continue
        rows.append(
            {
                "titleId": title["titleId"],
                "name": table_cell(title.get("name", title["titleId"])),
                "platforms": table_cell(", ".join(title.get("platforms", [])) or "-"),
                "versions": "<br>".join(versions),
            }
        )

    lines = [
        "# Titles Index",
        "",
        "Human-readable index for the published cheat title folders.",
        "",
        "| Title ID | Name | Platforms | Versions |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            f"[{row['titleId']}]({row['titleId']}/) | "
            f"{row['name']} | "
            f"{row['platforms']} | "
            f"{row['versions']} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(INDEX_PATH))
    parser.add_argument("--check", action="store_true", help="Print index without writing.")
    args = parser.parse_args()

    text = build_index()
    if args.check:
        print(text, end="")
        return 0

    output = Path(args.output)
    if not output.is_absolute():
        output = ROOT / output
    output.write_text(text, encoding="utf-8")
    print(f"wrote {output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
