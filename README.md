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
aliases/
tools/
docs/
```

`titles/` is the App-facing published catalog. Raw archives are intentionally
not part of this repository.

See:

- [docs/REPOSITORY_STRUCTURE.md](docs/REPOSITORY_STRUCTURE.md)
- [docs/CHEAT_LOOKUP.md](docs/CHEAT_LOOKUP.md)
- [docs/APP_CORE_INTEGRATION.md](docs/APP_CORE_INTEGRATION.md)
- [docs/METADATA_ENRICHMENT.md](docs/METADATA_ENRICHMENT.md)
- [docs/MIRRORING.md](docs/MIRRORING.md)

## Tooling

Standard maintenance workflow:

```sh
.venv/bin/python tools/convert_published_cheats.py
python3 tools/enrich_title_metadata.py
python3 tools/build_titles_index.py
python3 tools/build_catalog.py
python3 tools/validate_catalog.py
```

Run the converter only when adding or changing a published cheat payload. Always
run `build_catalog.py` and `validate_catalog.py` before publishing changes.
