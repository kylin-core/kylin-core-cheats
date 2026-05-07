# Contributing

Use one of the two supported import routes.

Install the small Python dependency set first:

```sh
make setup
```

## GoldHEN Updates

```sh
make update-goldhen-dry-run
make update-goldhen
```

The GoldHEN repository is cloned into a temporary directory unless
`GOLDHEN_SOURCE=/path/to/GoldHEN_Cheat_Repository` is provided. The converter
core is already included in this repository.

## Contributor Cheats

Put your `.json`, `.shn`, or `.mc4` files in a local folder. Names must include
title ID and version:

```text
CUSA12345_01.00.json
PPSA54321_01.001.000.mc4
```

Then run:

```sh
make import-cheats-dry-run SOURCE=/path/to/my-cheats
make import-cheats SOURCE=/path/to/my-cheats
```

## Before Opening A PR

```sh
make check
git diff
```

Only commit normalized catalog output under `titles/`, generated indexes, and
intentional docs changes. Do not commit local source folders, caches, or
temporary downloads.

Do not add one-off conversion scripts. New cheat sources should go through
either `make update-goldhen` or `make import-cheats SOURCE=...`.
