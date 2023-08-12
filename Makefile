PACKAGE := gitman
MODULES := $(wildcard $(PACKAGE)/*.py)

# MAIN TASKS ##################################################################

.PHONY: all
all: format check test mkdocs ## Run all tasks that determine CI status

.PHONY: dev
dev: install .clean-test ## Continuously run all CI tasks when files chanage
	poetry run sniffer

.PHONY: demo
demo: install
	@ echo gitman install
	@ poetry run gitman install --depth 1
ifdef RECORDING_DELAY
	@ sleep $(RECORDING_DELAY)
	@ sleep $(RECORDING_DELAY)
	@ clear
	@ sleep $(RECORDING_DELAY)
endif
	@ echo gitman list
	@ poetry run gitman list --depth 1
ifdef RECORDING_DELAY
	@ sleep $(RECORDING_DELAY)
	@ sleep $(RECORDING_DELAY)
	@ clear
	@ sleep $(RECORDING_DELAY)
endif
	@ echo gitman lock
	@ poetry run gitman lock --depth 1
ifdef RECORDING_DELAY
	@ sleep $(RECORDING_DELAY)
	@ sleep $(RECORDING_DELAY)
	@ clear
	@ sleep $(RECORDING_DELAY)
endif
	@ echo gitman update
	@ poetry run gitman update --depth 1
ifdef RECORDING_DELAY
	@ sleep $(RECORDING_DELAY)
	@ sleep $(RECORDING_DELAY)
	@ clear
	@ sleep $(RECORDING_DELAY)
endif
	@ echo gitman uninstall
	@ poetry run gitman uninstall
ifdef RECORDING_DELAY
	@ sleep $(RECORDING_DELAY)
	@ sleep $(RECORDING_DELAY)
	@ clear
	@ sleep $(RECORDING_DELAY)
endif

# SYSTEM DEPENDENCIES #########################################################

.PHONY: doctor
doctor:  ## Confirm system dependencies are available
	bin/verchew

# PROJECT DEPENDENCIES ########################################################

VIRTUAL_ENV ?= .venv
DEPENDENCIES := $(VIRTUAL_ENV)/.poetry-$(shell bin/checksum pyproject.toml poetry.lock)

.PHONY: install
install: $(DEPENDENCIES) .cache

$(DEPENDENCIES): poetry.lock
	@ poetry config virtualenvs.in-project true
	poetry install
	@ touch $@

ifndef CI
poetry.lock: pyproject.toml
	poetry lock --no-update
	@ touch $@
endif

.cache:
	@ mkdir -p .cache

# CHECKS ######################################################################

.PHONY: format
format: install
	poetry run isort $(PACKAGE) tests
	poetry run black $(PACKAGE) tests
	@ echo

.PHONY: check
check: install format  ## Run formaters, linters, and static analysis
ifdef CI
	git diff --exit-code
endif
	poetry run mypy $(PACKAGE) tests --config-file=.mypy.ini
	poetry run pylint $(PACKAGE) tests --rcfile=.pylint.ini
	poetry run pydocstyle $(PACKAGE) tests

# TESTS #######################################################################

RANDOM_SEED ?= $(shell date +%s)
FAILURES := .cache/pytest/v/cache/lastfailed

PYTEST_OPTIONS :=
#FIXME: non-random testing PYTEST_OPTIONS := --random --random-seed=$(RANDOM_SEED)
ifdef DISABLE_COVERAGE
PYTEST_OPTIONS += --no-cov --disable-warnings
endif
PYTEST_RERUN_OPTIONS := --last-failed --exitfirst

.PHONY: test
test: test-all ## Run unit and integration tests

.PHONY: test-unit
test-unit: install
	@ ( mv $(FAILURES) $(FAILURES).bak || true ) > /dev/null 2>&1
	poetry run pytest $(PACKAGE) $(PYTEST_OPTIONS)
	@ ( mv $(FAILURES).bak $(FAILURES) || true ) > /dev/null 2>&1
	poetry run coveragespace update unit

.PHONY: test-int
test-int: install
	@ if test -e $(FAILURES); then TEST_INTEGRATION=true poetry run pytest tests $(PYTEST_RERUN_OPTIONS); fi
	@ rm -rf $(FAILURES)
	TEST_INTEGRATION=true poetry run pytest tests $(PYTEST_OPTIONS)
	poetry run coveragespace update integration

.PHONY: test-all
test-all: install
	@ if test -e $(FAILURES); then TEST_INTEGRATION=true poetry run pytest $(PACKAGE) tests $(PYTEST_RERUN_OPTIONS); fi
	@ rm -rf $(FAILURES)
	TEST_INTEGRATION=true poetry run pytest $(PACKAGE) tests $(PYTEST_OPTIONS)
	poetry run coveragespace update overall

.PHONY: read-coverage
read-coverage:
	bin/open htmlcov/index.html

# DOCUMENTATION ###############################################################

MKDOCS_INDEX := site/index.html

.PHONY: docs
docs: mkdocs uml ## Generate documentation and UML
ifndef CI
	@ eval "sleep 3; bin/open http://127.0.0.1:8000" &
	poetry run mkdocs serve
endif

.PHONY: mkdocs
mkdocs: install $(MKDOCS_INDEX)
$(MKDOCS_INDEX): docs/requirements.txt mkdocs.yml docs/*.md
	@ mkdir -p docs/about
	@ cd docs && ln -sf ../README.md index.md
	@ cd docs/about && ln -sf ../../CHANGELOG.md changelog.md
	@ cd docs/about && ln -sf ../../CONTRIBUTING.md contributing.md
	@ cd docs/about && ln -sf ../../LICENSE.md license.md
	poetry run mkdocs build --clean --strict

docs/requirements.txt: poetry.lock
	poetry export --with dev --without-hashes --output $@

.PHONY: uml
uml: install docs/*.png
docs/*.png: $(MODULES)
	poetry run pyreverse $(PACKAGE) -p $(PACKAGE) -a 1 -f ALL -o png --ignore tests
	- mv -f classes_$(PACKAGE).png docs/classes.png
	- mv -f packages_$(PACKAGE).png docs/packages.png

docs/demo.gif: docs/demo.cast
	asciicast2gif $< $@
docs/demo.cast: Makefile
	/usr/X11/bin/resize -s 61 127
	poetry run asciinema rec $@ --overwrite --command "make demo CI=true RECORDING_DELAY=1" --title "Gitman Demo"
	poetry run asciinema upload $@

# BUILD #######################################################################

DIST_FILES := dist/*.tar.gz dist/*.whl
EXE_FILES := dist/$(PACKAGE).*

.PHONY: dist
dist: install $(DIST_FILES)
$(DIST_FILES): $(MODULES) pyproject.toml
	rm -f $(DIST_FILES)
	poetry build

.PHONY: exe
exe: install $(EXE_FILES)
$(EXE_FILES): $(MODULES) $(PACKAGE).spec
	# For framework/shared support: https://github.com/yyuu/pyenv/wiki
	poetry run pyinstaller $(PACKAGE).spec --noconfirm --clean

$(PACKAGE).spec:
	poetry run pyi-makespec $(PACKAGE)/__main__.py --onefile --additional-hooks-dir=gitman --name=$(PACKAGE)

# RELEASE #####################################################################

.PHONY: upload
upload: dist ## Upload the current version to PyPI
	git diff --name-only --exit-code
	poetry publish
	bin/open https://pypi.org/project/$(PACKAGE)

# CLEANUP #####################################################################

.PHONY: clean
clean: .clean-build .clean-docs .clean-test .clean-install ## Delete all generated and temporary files

.PHONY: clean-all
clean-all: clean
	rm -rf $(VIRTUAL_ENV)

.PHONY: .clean-install
.clean-install:
	find $(PACKAGE) tests -name '__pycache__' -delete
	rm -rf *.egg-info

.PHONY: .clean-test
.clean-test:
	rm -rf .cache .pytest .coverage htmlcov

.PHONY: .clean-docs
.clean-docs:
	rm -rf docs/*.png site

.PHONY: .clean-build
.clean-build:
	rm -rf *.spec dist build

# HELP ########################################################################

.PHONY: help
help: install
	@ grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
