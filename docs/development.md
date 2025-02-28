# Development Workflow

## Prerequisites
- Python 3.13+
- uv (Python package manager)
- ffmpeg (for video metadata extraction via ffprobe)

## Setup
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies (uv handles this automatically)
uv sync
```

## Build Commands
```bash
# Build distribution package
make local-build

# Install the built package locally via pipx
make local-build-install

# Clean build artifacts
make clean
```

## Run Commands
```bash
# Run via entry point
uv run apo --input-dir <input_dir> --output-dir <output_dir> [--use-hardlinks] [--verbose]

# Example
uv run apo --input-dir ./input/Takeout/Google\ Photos --output-dir ./output --verbose
```

## Test Commands
```bash
# Run all tests (excludes slow tests by default)
make local-test
# or
uv run pytest tests/

# Run slow performance tests only
make local-test-slow

# Run specific test file
uv run pytest tests/detect_taken_time/test_get_date_from_exif.py

# Run with verbose output
uv run pytest -v tests/
```

## Linting & Formatting
```bash
# Check code style and types
make local-lint

# Auto-format code
make local-format
```

## Development Workflow
1. Make changes to code
2. Run `make local-format` to auto-format
3. Run `make local-test` to verify tests pass
4. Run `make local-lint` to check for issues
5. Commit changes
