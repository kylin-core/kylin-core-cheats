PYTHON ?= python3
VENV_PYTHON := .venv/bin/python
RUN_PYTHON := $(if $(wildcard $(VENV_PYTHON)),$(VENV_PYTHON),$(PYTHON))
PYTHON_ENV := PYTHONDONTWRITEBYTECODE=1
GOLDHEN_ARG := $(if $(GOLDHEN_SOURCE),--source "$(GOLDHEN_SOURCE)",)
GOLDHEN_REPO_ARG := $(if $(GOLDHEN_REPO),--goldhen-repo "$(GOLDHEN_REPO)",)
SOURCE_ARG := $(if $(SOURCE),--source "$(SOURCE)",)

.PHONY: help setup doctor check rebuild validate titles-index catalog \
	update-goldhen-dry-run update-goldhen import-cheats-dry-run import-cheats

help:
	@printf '%s\n' 'Common targets:'
	@printf '  %-26s %s\n' 'make check' 'Validate the published catalog.'
	@printf '  %-26s %s\n' 'make rebuild' 'Regenerate titles/README.md and catalog.json, then validate.'
	@printf '  %-26s %s\n' 'make update-goldhen-dry-run' 'Preview GoldHEN auto-clone/import.'
	@printf '  %-26s %s\n' 'make update-goldhen' 'Import from GoldHEN, then rebuild.'
	@printf '  %-26s %s\n' 'make import-cheats-dry-run' 'Preview contributor cheat import from SOURCE=...'
	@printf '  %-26s %s\n' 'make import-cheats' 'Import contributor cheats from SOURCE=..., then rebuild.'
	@printf '  %-26s %s\n' 'make doctor' 'Check Python, catalog files, converter core, and GoldHEN source.'
	@printf '  %-26s %s\n' 'make setup' 'Create .venv and install tool dependencies.'
	@printf '%s\n' ''
	@printf '%s\n' 'Variables:'
	@printf '  %-24s %s\n' 'SOURCE=/path' 'Directory with contributor .json/.shn/.mc4 files.'
	@printf '  %-24s %s\n' 'GOLDHEN_SOURCE=/path' 'Optional existing GoldHEN_Cheat_Repository checkout.'
	@printf '  %-24s %s\n' 'GOLDHEN_REPO=url' 'Optional GoldHEN git URL for temporary auto-clone.'

setup:
	$(PYTHON) -m venv .venv
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -r requirements-tools.txt

doctor:
	$(PYTHON_ENV) $(RUN_PYTHON) tools/doctor.py

check: validate

rebuild: titles-index catalog validate

validate:
	$(PYTHON_ENV) $(RUN_PYTHON) tools/validate_catalog.py

titles-index:
	$(PYTHON_ENV) $(RUN_PYTHON) tools/build_titles_index.py

catalog:
	$(PYTHON_ENV) $(RUN_PYTHON) tools/build_catalog.py

update-goldhen-dry-run:
	$(PYTHON_ENV) $(RUN_PYTHON) tools/import_goldhen_repository.py $(GOLDHEN_ARG) $(GOLDHEN_REPO_ARG) --dry-run

update-goldhen:
	$(PYTHON_ENV) $(RUN_PYTHON) tools/import_goldhen_repository.py $(GOLDHEN_ARG) $(GOLDHEN_REPO_ARG)
	$(MAKE) rebuild

import-cheats-dry-run:
	@if [ -z "$(SOURCE)" ]; then printf '%s\n' 'SOURCE is required, for example: make import-cheats-dry-run SOURCE=./my-cheats'; exit 2; fi
	$(PYTHON_ENV) $(RUN_PYTHON) tools/import_contributor_cheats.py $(SOURCE_ARG) --dry-run

import-cheats:
	@if [ -z "$(SOURCE)" ]; then printf '%s\n' 'SOURCE is required, for example: make import-cheats SOURCE=./my-cheats'; exit 2; fi
	$(PYTHON_ENV) $(RUN_PYTHON) tools/import_contributor_cheats.py $(SOURCE_ARG)
	$(MAKE) rebuild
