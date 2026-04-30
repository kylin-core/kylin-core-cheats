# Repository Structure

This repository is a published catalog. It contains stable files under
`titles/`, plus root `catalog.json`, schemas, tools, and docs.

Raw archives such as `.rar` files should not be committed. Use them locally with
the migration tools, then commit only generated `titles/` output.

## Published Catalog

```text
catalog.json
titles/
  README.md
  PPSA26344/
    title.json
    01.008.000/
      manifest.json
      PPSA26344_01.008.000.json
      PPSA26344_01.008.000.shn
      PPSA26344_01.008.000.mc4
```

### Root Catalog

`catalog.json` is the lightweight entry point for the App. It lists title IDs,
game names, available versions, manifest paths, preferred formats, and update
metadata.

The App should use exact matching:

```text
current titleId + current version -> catalog entry -> manifest -> file download
```

If an exact version is missing, the App should show that no compatible cheat is
available. It should not silently install a different version.

### Titles Index

`titles/README.md` is a human-readable index for GitHub browsing. It links each
title ID to its folder and each available game version to its version folder.
Regenerate it after title or version changes:

```sh
python3 tools/build_titles_index.py
```

### Title Metadata

`titles/<TITLE_ID>/title.json` stores game-level metadata:

```json
{
  "schemaVersion": 1,
  "titleId": "PPSA26344",
  "name": "Ghost of Yotei",
  "regions": ["US", "EU"],
  "aliases": []
}
```

### Version Manifest

`titles/<TITLE_ID>/<VERSION>/manifest.json` stores all available files for one
`titleId + version`.

Each entry must point to a local file in the same directory and include checksum
metadata.

## File Naming

Published cheat files must use:

```text
<TITLE_ID>_<VERSION>.<format>
```

Examples:

```text
PPSA26344_01.008.000.json
PPSA21159_01.001.000.shn
PPSA08710_01.005.000.mc4
CUSA54714_01.13.mc4
```

Do not encode `fixed`, `new`, `v2`, region names, or game names in published
file names. Put those details in `manifest.json` fields such as `revision`,
`regions`, `source`, `quality`, and `notes`.

## Formats

Supported published formats:

- `json`: preferred format for App display, validation, and future editing.
- `shn`: XML trainer format.
- `mc4`: encrypted trainer format.

Archive formats such as `.rar` are source material only and should stay outside
the repository. They must be unpacked before publishing because `kylin-core`
does not load `.rar` files.

## Multi-ID and Region Compatibility

When the same cheat supports multiple title IDs, publish one stable entry per
title ID. The file can be copied or generated from the same source, but the
runtime filename should match the title ID the console reports.

Example:

```text
titles/PPSA05621/01.001.000/PPSA05621_01.001.000.mc4
titles/PPSA05622/01.001.000/PPSA05622_01.001.000.mc4
```

Use `compatibleTitleIds` in `manifest.json` to preserve the relationship.

## Update Checks

The App should compare:

- `catalogVersion`
- `manifest.revision`
- cheat file `sha256`

If the remote checksum differs from the locally installed checksum, the App can
offer an update and upload the new file to the console.
