# Testing Guidelines

## Test Framework
- Use pytest for all tests
- Test files must start with `test_` prefix
- Test functions must start with `test_` prefix

## Test Structure
```
tests/
  __init__.py
  test_file_operations.py
  test_process_files.py
  test_compare_directories_perf.py   # @pytest.mark.slow
  detect_taken_time/
    __init__.py
    test_detect_taken_time.py
    test_get_date_from_exif.py
    test_get_date_from_heic.py
    test_get_date_from_json.py
    test_get_date_from_ffprobe.py
    test_get_date_from_mp4_atoms.py
    test_get_date_from_mkv.py
    test_get_date_from_png.py
    test_get_date_from_filename.py
```

## Running Tests
```bash
# Run all tests (excludes slow tests by default via addopts)
make local-test

# Run slow performance tests only
make local-test-slow

# Run specific test file
uv run pytest tests/detect_taken_time/test_get_date_from_exif.py

# Run with coverage
uv run pytest --cov=. tests/

# Run verbose
uv run pytest -v tests/
```

## Slow Test Marker
- Mark long-running performance tests with `@pytest.mark.slow`
- These are excluded by default (`addopts = "-m 'not slow'"` in pyproject.toml)
- Run them explicitly with `uv run pytest -m slow tests/`

## Writing Tests
- Follow AAA pattern: Arrange, Act, Assert
- Use descriptive test names: `test__<function>__<scenario>__<expected_result>`
- Use `# given:`, `# when:`, `# then:` comments for clarity
- Example:
  ```python
  def test__detect_taken_time__mp4_with_metadata__success():
      # given:
      file_path = Path('tests/files/mp4_with_metadata.mp4')

      # when:
      capture_datetime = detect_taken_time(file_path=file_path)

      # then:
      assert capture_datetime == expected_datetime
  ```

## Test Coverage
- Aim for high coverage of core logic
- Focus on edge cases and error conditions
