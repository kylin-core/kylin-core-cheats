# GoldHEN Import Workflow

This document describes how to import compatible files from a local
`GoldHEN_Cheat_Repository` checkout into this catalog.

## Source Layout

The importer expects the GoldHEN repository to contain these folders:

```text
json/
shn/
mc4/
shn.txt
```

Only `CUSAxxxxx` and `PPSAxxxxx` title IDs are imported. Other IDs such as
`SLUS`, `SCUS`, `SLES`, and `SLPM` are skipped because the current catalog
schema only supports PS4/PS5 IDs.

## Prerequisites

- Project virtual environment with the converter dependencies installed.
- `ps4_ps5_aio_cheat_converter` available at the repository root, usually as a
  symlink to the local converter checkout.
- A local `GoldHEN_Cheat_Repository` checkout, or a custom path passed with
  `--source`.
- `unar` installed for local raw archive imports.

The default GoldHEN source path is developer-local. Use `--source` on other
machines:

```sh
.venv/bin/python tools/import_goldhen_repository.py --source /path/to/GoldHEN_Cheat_Repository --dry-run
python3 tools/audit_goldhen_import.py --source /path/to/GoldHEN_Cheat_Repository
```

## Import Rules

For each parsed `titleId + version`, the importer chooses one source payload and
generates the published catalog files:

```text
titles/<TITLE_ID>/<VERSION>/manifest.json
titles/<TITLE_ID>/<VERSION>/<TITLE_ID>_<VERSION>.json
titles/<TITLE_ID>/<VERSION>/<TITLE_ID>_<VERSION>.shn
titles/<TITLE_ID>/<VERSION>/<TITLE_ID>_<VERSION>.mc4
```

Source priority is:

1. `json`
2. `shn`
3. `mc4`

If multiple files exist for the same format, cleaner filenames are preferred
over suffixed variants such as `_2`, `_default.elf`, or process-specific names.
The selected source file is recorded in `manifest.json` notes.

Existing catalog entries are skipped by default. Use `--replace-existing` only
when intentionally regenerating existing entries.

Imported GoldHEN files include source attribution in each version
`manifest.json` note. If all candidates for a source group fail conversion, the
group is reported and skipped unless `--strict` is used.

## Commands

Run the importer with the project virtual environment because the converter
depends on packages such as `xmltodict` and `pycryptodome`.

Dry-run first:

```sh
.venv/bin/python tools/import_goldhen_repository.py --dry-run
```

Import:

```sh
.venv/bin/python tools/import_goldhen_repository.py
```

Rebuild indexes:

```sh
python3 tools/build_titles_index.py
python3 tools/build_catalog.py
```

Validate the published catalog:

```sh
python3 tools/validate_catalog.py
```

Audit the import back against the GoldHEN source:

```sh
python3 tools/audit_goldhen_import.py
```

Use strict mode in automation if any missing import should fail the job:

```sh
python3 tools/audit_goldhen_import.py --strict
```

## Initial Import Snapshot

The initial GoldHEN import snapshot from 2026-05-02 produced:

- `1991` parsed `CUSA/PPSA + version` source groups
- `1986` imported source groups
- `5` source groups skipped because all available candidates failed conversion
- `232` source files skipped because their title IDs are outside the current schema

The known failed source groups are:

```text
CUSA02629_01.01
CUSA04408_01.18
CUSA10873_01.01
CUSA17196_01.60
CUSA33173_01.02
```

The reverse audit may also report catalog entries that do not exist in GoldHEN.
Those are expected when the project already had manually migrated, local raw, or
PS5 entries before the GoldHEN import. Treat the current
`tools/audit_goldhen_import.py` output as the source of truth after later
imports.

## Local Raw Archive Import

Locally collected `.rar` files can be placed in the ignored `raw/` directory and
imported with:

```sh
.venv/bin/python tools/import_raw_archives.py --dry-run
.venv/bin/python tools/import_raw_archives.py
```

The raw importer extracts each archive with `unar`, scans for `.json`, `.shn`,
and `.mc4` payloads, then rewrites the matching published version under
`titles/`. This is an overwrite operation for the same `titleId + version`.
When multiple raw archives target the same `titleId + version`, the newest
extracted payload is tried first, then remaining candidates are used as
fallbacks if conversion fails.

For an existing `titleId + version`, the raw importer increments
`manifest.revision` and records the selected archive in the manifest notes.
Always inspect the dry-run output before running the real import so the selected
archive is intentional.

After importing raw archives, rebuild and validate:

```sh
python3 tools/build_titles_index.py
python3 tools/build_catalog.py
python3 tools/validate_catalog.py
```

If an archive contains an unsupported or damaged payload, the importer reports
the failure and continues unless `--strict` is passed.

## Local Loose Payload Import

Already extracted local payloads can be staged in:

```text
raw/cheats/json/
raw/cheats/shn/
raw/cheats/mc4/
```

Import them with:

```sh
.venv/bin/python tools/import_loose_cheats.py --dry-run
.venv/bin/python tools/import_loose_cheats.py
```

The loose importer scans for `.json`, `.shn`, and `.mc4` files, parses
`CUSA/PPSA + version` from the filename, normalizes one-digit major versions
such as `1.026.000` to `01.026.000`, and publishes the standard
`json/shn/mc4/manifest.json` output. Existing versions are overwritten and
their `manifest.revision` is incremented.

When multiple loose files target the same `titleId + version`, source priority
is `json`, then `shn`, then `mc4`; failed candidates are skipped in favor of the
next candidate when available. Always review `--dry-run` before importing.

## Publishing Checklist

After any GoldHEN, raw archive, or loose payload import:

1. Review the import output for skipped, failed, or overwritten versions.
2. Rebuild `titles/README.md`.
3. Rebuild `catalog.json`.
4. Run `python3 tools/validate_catalog.py`.
5. Run `python3 tools/audit_goldhen_import.py` if GoldHEN content changed.
6. Review `git diff` and confirm no raw archives, caches, or local converter
   files are staged.
7. Check that source attribution and license notes remain accurate.
