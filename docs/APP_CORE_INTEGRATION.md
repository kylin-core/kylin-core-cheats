# App and Core Integration

This repository now provides the catalog side of the workflow.

## App Flow

`kylin-cheat-app` should:

1. Fetch the console current game:

   ```text
   GET http://<host>:9023/api/v1/game/current
   ```

2. Read this repository's `catalog.json`.
3. Match exact `titleId + version`.
4. Fetch the matched `manifest.json`.
5. Pick `preferredFormat`, currently `json`.
6. Download the selected entry path relative to the manifest directory.
7. Verify `size` and `sha256`.
8. Upload the file to `kylin-core`.

## Core Upload Contract

`kylin-core` still needs the upload endpoint. Recommended request:

```text
POST /api/v1/cheats/upload
Content-Type: multipart/form-data
```

Fields:

```text
titleId
version
format
sha256
file
```

Core should write:

```text
/data/kylin/cheats/<TITLE_ID>_<VERSION>.<format>
```

Core should reject:

- unsupported formats outside `json`, `shn`, `mc4`
- filenames from the client
- path traversal
- checksum mismatch when `sha256` is provided
- title/version mismatch unless offline install is explicitly supported

## Current Repository Status

The repository side is ready for App consumption:

- root `catalog.json`
- one `manifest.json` per published `titleId + version`
- `json`, `shn`, and `mc4` files for every published version
- checksums and sizes for every downloadable entry
- validated JSON `id/version` consistency

The remaining work is in `kylin-cheat-app` and `kylin-core`, not this catalog
repository.
