# Cheat Lookup

This document describes how `kylin-cheat-app` should find a compatible cheat
file in this repository.

## Inputs

The App should start with the current game data from `kylin-core`:

```text
GET http://<host>:9023/api/v1/game/current
```

Required fields:

```text
titleId
version
titleName
```

## Catalog Lookup

Fetch the root catalog:

```text
catalog.json
```

Find a title entry where:

```text
catalog.titles[].titleId == currentGame.titleId
```

Then find a version entry where:

```text
title.versions[].version == currentGame.version
```

Matching must be exact. A cheat for a different game version should not be
installed silently.

## Manifest Lookup

Fetch the matched manifest:

```text
titles/<TITLE_ID>/<VERSION>/manifest.json
```

Use:

```text
manifest.preferredFormat
```

Current preferred format is `json`.

Find the matching entry:

```text
manifest.entries[].format == manifest.preferredFormat
```

The downloadable path is relative to the manifest directory:

```text
titles/<TITLE_ID>/<VERSION>/<entry.path>
```

## Verification

After download, verify:

```text
entry.size
entry.sha256
```

The App should reject the file if either check fails.

## Upload

After verification, upload the selected file to `kylin-core`.

Recommended future endpoint:

```text
POST /api/v1/cheats/upload
```

Core should write:

```text
/data/kylin/cheats/<TITLE_ID>_<VERSION>.<format>
```

## No Match Behavior

If no exact `titleId + version` match exists, show a no-compatible-cheat state.
Do not suggest a nearby version unless the user explicitly opts into manual
selection.

## Metadata

Each `title.json` contains metadata that can be shown in the App:

```text
name
platforms
publisher
coverImage
backgroundImage
```

`coverImage` and `backgroundImage` are optional. If absent, the App should use a
local placeholder or the console-provided game icon when available.
