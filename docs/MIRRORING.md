# Repository Mirroring

This repository is mirror-friendly by design.

The published files use relative paths:

```text
catalog.json
titles/<TITLE_ID>/<VERSION>/manifest.json
titles/<TITLE_ID>/<VERSION>/<TITLE_ID>_<VERSION>.<format>
```

That means the same commit can be pushed to GitHub and Gitee without rewriting
catalog paths.

## Recommended App Strategy

Configure the App with a list of catalog URLs, for example:

```text
https://raw.githubusercontent.com/<owner>/<repo>/main/catalog.json
https://gitee.com/<owner>/<repo>/raw/main/catalog.json
```

At runtime:

1. Try the preferred mirror first.
2. If it fails or times out, try the next mirror.
3. Resolve manifest paths relative to the catalog URL that succeeded.
4. Resolve cheat file paths relative to the manifest URL.
5. Verify `size` and `sha256` after every download.

## Build Scripts

The normal workflow does not need mirror-specific changes:

```sh
.venv/bin/python tools/convert_published_cheats.py
python3 tools/enrich_title_metadata.py
python3 tools/build_titles_index.py
python3 tools/build_catalog.py
python3 tools/validate_catalog.py
```

Do not pass `--base-url` when publishing the same catalog to multiple mirrors.
Keeping paths relative lets each mirror serve itself.

Use `--base-url` only for a single fixed host, such as a CDN:

```sh
python3 tools/build_catalog.py --base-url https://cdn.example.com/kylin-core-cheats
```

## Gitee Notes

Use the raw file URL for the App catalog endpoint:

```text
https://gitee.com/<owner>/<repo>/raw/main/catalog.json
```

The human-readable `titles/README.md` uses relative links and should work in
both GitHub and Gitee web views.
