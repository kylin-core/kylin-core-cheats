# Tools

The public workflow intentionally stays small.

| Tool | Purpose |
| --- | --- |
| `import_goldhen_repository.py` | Auto-clone or read GoldHEN, convert compatible cheats, and publish them under `titles/`. |
| `import_contributor_cheats.py` | Convert contributor-provided `.json`, `.shn`, or `.mc4` files into the repository format. |
| `build_titles_index.py` | Regenerate `titles/README.md`. |
| `build_catalog.py` | Regenerate `catalog.json`. |
| `validate_catalog.py` | Validate names, manifests, sizes, checksums, and JSON payload metadata. |
| `doctor.py` | Print local setup status for the vendored converter core and GoldHEN source. |

Prefer `make`:

```sh
make setup
make update-goldhen-dry-run
make import-cheats-dry-run SOURCE=/path/to/my-cheats
make rebuild
make check
```

Every tool also supports `--help`.

The converter core is vendored in `tools/converter_core`; import commands do
not require a separate converter checkout.
