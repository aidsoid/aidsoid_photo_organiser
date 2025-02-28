# Code Style Guidelines

## General Rules
- Follow PEP 8 style conventions
- Maximum line length: 120 characters
- Use single quotes for strings
- 4 spaces for indentation (no tabs)

## Naming Conventions
- Functions and variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private members: prefix with single underscore `_name`

## Docstrings
- Use Sphinx/reST-style docstrings for all public functions and classes
- Include parameter types, return types, and exceptions
- Example:
  ```python
  def function_name(param: type) -> return_type:
      """Brief description.

      :param param: Description of parameter.
      :return: Description of return value.
      :raises SomeError: When error occurs.
      """
  ```

## Type Hints
- Add type hints to all function signatures
- Use `typing` module for complex types (`Optional`, `Set`, `Path`, etc.)
- Ensure pyright passes with no errors

## Imports
- Group imports: stdlib → third-party → local
- Use relative imports within the package (e.g., `from .constants import ...`)
- Sort imports alphabetically within groups (enforced by ruff)

## Error Handling
- Define custom exceptions for domain-specific errors
- Log errors with appropriate severity levels
- Use meaningful error messages

## Linting & Formatting
- Run `make local-format` before committing
- All ruff checks must pass
- All pyright type checks must pass

### Ruff Configuration
**Enabled rules:**
- `E`: PEP8 style errors
- `F`: Pyflakes code errors
- `I`: Import order and grouping
- `B`: Potential bugs and best-practice patterns
- `D`: Docstring format (PEP257)
- `N`: Naming conventions (PEP8)

**Ignored rules:**
- `D203`: Incompatible with D211 (no blank line before class)
- `D212`: Incompatible with D213 (multi-line summary second line)

### Formatting Rules
- Line length: 120 characters
- Quote style: single quotes
- Indent style: 4 spaces
