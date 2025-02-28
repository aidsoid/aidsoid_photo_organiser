RUN:=uv run
PYTHON:=$(RUN) python

# Run unit tests (excludes slow/perf tests)
.PHONY: local-test
local-test:
	$(RUN) pytest tests/

# Run slow performance tests only
.PHONY: local-test-slow
local-test-slow:
	$(RUN) pytest -m slow tests/

# Inspect media file metadata
.PHONY: local-ffprobe
local-ffprobe:
	ffprobe -v quiet -print_format json -show_format tests/files/m4v_with_creation_time.m4v

# Run linters and type checker
.PHONY: local-lint
local-lint:
	$(RUN) ruff check .
	$(RUN) ruff format --check .
	$(RUN) pyright

# Auto-format code
.PHONY: local-format
local-format:
	$(RUN) ruff format .

# Build distribution package
.PHONY: local-build
local-build:
	uv build

# Install the built package locally
.PHONY: local-build-install
local-build-install: local-build
	pipx install --force dist/*.whl

# Clean build artifacts
.PHONY: clean
clean:
	rm -rf dist build *.egg-info
