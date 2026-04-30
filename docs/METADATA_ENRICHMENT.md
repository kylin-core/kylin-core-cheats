# Metadata Enrichment

The repository can generate basic title metadata from published cheat manifests:

```sh
python3 tools/enrich_title_metadata.py
python3 tools/fetch_title_media.py
python3 tools/build_catalog.py
python3 tools/validate_catalog.py
```

This fills:

```text
name
platforms
metadataSource
metadataUpdatedAt
```

## Cover Images

`tools/fetch_title_media.py` first tries Sony TMDB. It derives the NP Title ID
by appending `_00`, signs it with the known TMDB HMAC-SHA1 key, then requests:

```text
https://tmdb.np.dl.playstation.net/tmdb2/<NP_TITLE_ID>_<HASH>/<NP_TITLE_ID>.json
```

TMDB works well for many PS4 `CUSA` IDs. PS5 `PPSA` entries often return HTTP
403, so the tool falls back to:

1. PROSPEROPatches: `PPSAxxxxx` -> `Content ID`, publisher, and region.
2. PlayStation Store GraphQL: product metadata and media assets by `Content ID`.

If PROSPEROPatches blocks non-browser requests or returns no page body, add
`contentId` to `titles/<TITLE_ID>/title.json`; the tool will skip the mapping
step and query PlayStation Store directly.

When either provider contains the title, the tool fills localized `name`,
`contentId`, `platforms`, `publisher`, `releaseDate`, `storeUrl`, `iconImage`,
`backgroundImage`, and `coverImage`. Assets are downloaded under:

```text
titles/<TITLE_ID>/media/icon.png
titles/<TITLE_ID>/media/cover.jpg
titles/<TITLE_ID>/media/background.png
```

Titles missing from both providers are skipped so the catalog remains
publishable.

Reasonable provider options:

- Console-local metadata: `kylin-core` can expose installed app metadata and
  icon paths from the console. This is the most reliable source for the current
  installed game.
- Sony TMDB: useful for title names, icons, background images, and content IDs
  when the title exists in TMDB.
- PROSPEROPatches: useful for mapping title IDs to patch versions and region
  data. It is not an official Sony API.
- PlayStation Store GraphQL: useful once a content ID is known. It depends on
  persisted query hashes used by the current web store.
- Key-based commercial/community APIs: possible for cover art, but they require
  credentials and should not be hardcoded into this repository.

Recommended implementation:

1. Run TMDB enrichment:

   ```sh
   python3 tools/fetch_title_media.py
   ```

2. Rebuild and validate:

   ```sh
   python3 tools/build_catalog.py
   python3 tools/validate_catalog.py
   ```

3. Prefer console-local icons for the currently running game if no repository
   media is available.
