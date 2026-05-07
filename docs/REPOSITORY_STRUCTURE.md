# Repository Structure

This repository is a published catalog. Source cheats are imported through one
of two routes:

- GoldHEN update: `make update-goldhen`
- Contributor cheats: `make import-cheats SOURCE=/path/to/cheats`

Only normalized catalog output is committed.

## Published Layout

```text
catalog.json
schemas/
titles/
  README.md
  <TITLE_ID>/
    title.json
    <VERSION>/
      manifest.json
      <TITLE_ID>_<VERSION>.json
      <TITLE_ID>_<VERSION>.shn
      <TITLE_ID>_<VERSION>.mc4
tools/
```

## Root Catalog

`catalog.json` is the lightweight app entry point. It lists title IDs, names,
available versions, manifest paths, preferred formats, revisions, and update
metadata.

Clients should match exactly:

```text
current titleId + current version -> catalog entry -> manifest -> file download
```

If an exact version is missing, the app should show that no compatible cheat is
available.

## Title Metadata

`titles/<TITLE_ID>/title.json` stores game-level metadata:

```json
{
  "schemaVersion": 1,
  "titleId": "PPSA26344",
  "name": "Game Name",
  "regions": [],
  "aliases": [],
  "platforms": ["PS5"]
}
```

## Version Manifest

`titles/<TITLE_ID>/<VERSION>/manifest.json` stores all published files for one
`titleId + version`. Each entry points to a file in the same directory and
includes size and SHA-256 metadata.

`manifest.revision` should increase whenever a published payload for the same
`titleId + version` changes. Import tools handle this for contributor cheats;
GoldHEN imports create revision `1` for new entries unless replacing existing
entries intentionally.

## File Naming

Published cheat files must use:

```text
<TITLE_ID>_<VERSION>.<format>
```

Examples:

```text
CUSA54714_01.13.json
PPSA08710_01.005.000.mc4
```

Do not encode `fixed`, `new`, `v2`, region names, or game names in published
file names. Put those details in manifest fields such as `revision`, `regions`,
`source`, `quality`, and `notes`.

## Generated Files

After imports or manual catalog edits:

```sh
make rebuild
```

This regenerates `titles/README.md` and `catalog.json`, then validates the
catalog.
