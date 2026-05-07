# GoldHEN Update

`tools/import_goldhen_repository.py` imports compatible cheats from
`GoldHEN_Cheat_Repository` into this catalog.

## What It Does

1. Finds a GoldHEN source checkout, or clones
   `https://github.com/GoldHEN/GoldHEN_Cheat_Repository.git` into a temporary
   directory.
2. Reads GoldHEN `json/`, `shn/`, `mc4/`, and name mapping files.
3. Picks the best source payload for each `CUSA/PPSA + version`.
4. Converts it into this repository's published format:

```text
titles/<TITLE_ID>/<VERSION>/manifest.json
titles/<TITLE_ID>/<VERSION>/<TITLE_ID>_<VERSION>.json
titles/<TITLE_ID>/<VERSION>/<TITLE_ID>_<VERSION>.shn
titles/<TITLE_ID>/<VERSION>/<TITLE_ID>_<VERSION>.mc4
```

Only `CUSAxxxxx` and `PPSAxxxxx` title IDs are imported.

## Run It

Install tool dependencies once:

```sh
make setup
```

Dry-run:

```sh
make update-goldhen-dry-run
```

Import and rebuild:

```sh
make update-goldhen
```

The converter core is vendored under `tools/converter_core`, so this workflow
does not need a separate converter checkout.

## Source Selection

The GoldHEN source is resolved in this order:

1. `GOLDHEN_SOURCE=/path/to/GoldHEN_Cheat_Repository`
2. `--source /path/to/GoldHEN_Cheat_Repository`
3. `KYLIN_GOLDHEN_SOURCE` or `GOLDHEN_CHEAT_REPOSITORY`
4. Existing `../GoldHEN_Cheat_Repository`
5. Temporary clone of the official GoldHEN repository

Use a fork:

```sh
make update-goldhen-dry-run GOLDHEN_REPO=https://github.com/you/GoldHEN_Cheat_Repository.git
```

## Import Rules

Source priority is:

1. `json`
2. `shn`
3. `mc4`

Existing catalog entries are skipped by default. Use `--replace-existing` only
when intentionally regenerating existing entries:

```sh
python3 tools/import_goldhen_repository.py --replace-existing
```

Always review dry-run output before importing.
