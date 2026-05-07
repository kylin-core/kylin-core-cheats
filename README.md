# Kylin Core Cheats

Structured cheat catalog for `kylin-core`.

This repository publishes normalized cheat files under `titles/` plus a root
`catalog.json` for apps to consume. Source cheat files are converted into the
published repository format; raw source folders are not part of the catalog.

## Quick Start

Install the small Python dependency set and validate the checked-out catalog:

```sh
make setup
make check
```

`make check` does not download anything. It only validates the files already in
this repository.

## Import Workflows

There are only two supported import routes.

### 1. Update From GoldHEN

This route pulls cheats from
`https://github.com/GoldHEN/GoldHEN_Cheat_Repository.git`, converts compatible
`json`, `shn`, and `mc4` files, writes the normalized catalog entries, then
rebuilds the indexes.

Dry-run first:

```sh
make update-goldhen-dry-run
```

Import:

```sh
make update-goldhen
```

If you do not pass `GOLDHEN_SOURCE`, the tool auto-clones GoldHEN into a
temporary directory and deletes it when the command exits. Use
`GOLDHEN_SOURCE=/path/to/GoldHEN_Cheat_Repository` only when you want to reuse a
local checkout.

This route requires network access unless `GOLDHEN_SOURCE` points to an
existing local checkout.

### 2. Import Contributor Cheats

This route is for cheats written or collected by contributors. Put `.json`,
`.shn`, or `.mc4` files in any local folder. File names must include title ID
and version, for example:

```text
CUSA12345_01.00.json
PPSA54321_01.001.000.shn
```

Dry-run first:

```sh
make import-cheats-dry-run SOURCE=/path/to/my-cheats
```

Import:

```sh
make import-cheats SOURCE=/path/to/my-cheats
```

The importer generates the standard `json`, `shn`, `mc4`, and `manifest.json`
files under `titles/<TITLE_ID>/<VERSION>/`.

## Validate

After any change:

```sh
make check
```

To rebuild generated indexes:

```sh
make rebuild
```

`make rebuild` regenerates `titles/README.md` and `catalog.json`, then validates
the catalog.

## Repository Layout

```text
catalog.json
schemas/
titles/<TITLE_ID>/title.json
titles/<TITLE_ID>/<VERSION>/manifest.json
titles/<TITLE_ID>/<VERSION>/<TITLE_ID>_<VERSION>.json
titles/<TITLE_ID>/<VERSION>/<TITLE_ID>_<VERSION>.shn
titles/<TITLE_ID>/<VERSION>/<TITLE_ID>_<VERSION>.mc4
tools/
```

Runtime file names follow:

```text
<TITLE_ID>_<VERSION>.<format>
```

Supported formats are `json`, `shn`, and `mc4`. The preferred published format
is `json`, but all three are generated when importing.

## Tooling Notes

The JSON/SHN/MC4 converter core is vendored under `tools/converter_core`, so no
separate converter checkout is needed. GoldHEN is cloned into a temporary
directory when `GOLDHEN_SOURCE` is not provided. Use `GOLDHEN_REPO` only when
testing a GoldHEN fork.

Useful commands:

```sh
make help
make setup
make doctor
make check
make rebuild
```

See [tools/README.md](tools/README.md) for the small tool list.

## Credits

Some entries are imported from the GoldHEN cheat repository and normalized into
this catalog structure. Original cheat authors and contributors retain credit
for their work. When a payload is imported from a known source, the source file
is recorded in `manifest.json` notes.

The converter core under `tools/converter_core` is extracted from
`ReverseTelnet/ps4_ps5_aio_cheat_converter` with local non-GUI fixes and is
distributed under GPLv3; see `tools/converter_core/LICENSE`.
