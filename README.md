# Kylin Core Cheats

Structured cheat catalog for `kylin-core`.

This repository is intended to be consumed by:

- `kylin-cheat-app`: matches the current PS5 title ID and version, downloads a
  compatible cheat file, and uploads it to the console.
- `kylin-core`: loads the uploaded cheat file from the console runtime
  directory and hot-reloads it when the file changes.

## Runtime Contract

`kylin-core` currently resolves cheat files from:

```text
/data/kylin/cheats/<TITLE_ID>_<VERSION>.json
/data/kylin/cheats/<TITLE_ID>_<VERSION>.shn
/data/kylin/cheats/<TITLE_ID>_<VERSION>.mc4
```

Resolution order is `json`, then `shn`, then `mc4`.

The published repository layout mirrors that contract while adding metadata for
App search, download, update checks, and verification.

## Repository Layout

```text
catalog.json
schemas/
titles/<TITLE_ID>/title.json
titles/<TITLE_ID>/<VERSION>/manifest.json
titles/<TITLE_ID>/<VERSION>/<TITLE_ID>_<VERSION>.<format>
tools/
docs/
```

`titles/` is the App-facing published catalog. Raw archives are intentionally
not part of this repository. The local `raw/` folder is ignored by git and is
only used as a temporary input folder for collected archives.

See:

- [docs/REPOSITORY_STRUCTURE.md](docs/REPOSITORY_STRUCTURE.md)
- [docs/CHEAT_LOOKUP.md](docs/CHEAT_LOOKUP.md)
- [docs/APP_CORE_INTEGRATION.md](docs/APP_CORE_INTEGRATION.md)
- [docs/METADATA_ENRICHMENT.md](docs/METADATA_ENRICHMENT.md)
- [docs/MIRRORING.md](docs/MIRRORING.md)
- [docs/GOLDHEN_IMPORT.md](docs/GOLDHEN_IMPORT.md)

## Credits

The cheat payloads in this catalog are collected from public network sources
and community releases. Some entries were imported from the GoldHEN cheat
repository and normalized into this project's published catalog structure.

Original cheat authors and contributors retain credit for their work. When a
payload is imported from a known source, the source file is recorded in the
version `manifest.json` notes.

When publishing this catalog, keep source attribution and license obligations in
mind. The GoldHEN cheat repository is distributed under GPLv3; imported content
from that repository should retain appropriate attribution and license context.

## Tooling

Common maintenance commands:

```sh
.venv/bin/python tools/convert_published_cheats.py
.venv/bin/python tools/import_goldhen_repository.py --dry-run
.venv/bin/python tools/import_raw_archives.py --dry-run
.venv/bin/python tools/import_loose_cheats.py --dry-run
python3 tools/enrich_title_metadata.py
python3 tools/build_titles_index.py
python3 tools/build_catalog.py
python3 tools/validate_catalog.py
python3 tools/audit_goldhen_import.py
```

Run import scripts with `--dry-run` first and review the selected source files.
Always run `build_titles_index.py`, `build_catalog.py`, and
`validate_catalog.py` before publishing changes. Run `audit_goldhen_import.py`
after GoldHEN imports to check that source files and manifests still line up.

## Release Checklist

Before publishing a catalog update:

1. Import or convert payloads as needed.
2. Rebuild `titles/README.md` with `python3 tools/build_titles_index.py`.
3. Rebuild `catalog.json` with `python3 tools/build_catalog.py`.
4. Validate with `python3 tools/validate_catalog.py`.
5. Run `python3 tools/audit_goldhen_import.py` when GoldHEN content changed.
6. Review `git diff` for unintended source archive, cache, or metadata churn.
7. Confirm credits and license notes are still accurate.
