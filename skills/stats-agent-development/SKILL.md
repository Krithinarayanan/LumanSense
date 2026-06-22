---
name: stats-agent-development
description: Guidelines and best practices for developing statistics modules and agents.
---

# Statistics Agent Development Guidelines

This skill documents the rules and standards for writing statistics agents and modules.

## Rules

### 1. No Emoji Style Comments or Prints
Do not include emojis in code comments, docstrings, or console print statements (e.g., avoid `🚀 Starting...` or similar). All logging and comments should use clear, professional, and plain text.

### 2. No Hardcoded File Paths
Never hardcode absolute file paths for configuration, data, or log files (e.g. `/home/krithi/.../traffic_history.log`). Instead:
- Use relative paths relative to the current file's directory using `os.path`.
- Use environment variables (e.g. `os.environ.get(...)`).
- Accept the path dynamically as an input parameter with a sensible default or validation.

### 3. Best Practices in Code Generation
- **Type Hints**: Always use clear type hinting (`typing.List`, `typing.Dict`, `typing.Union`, etc.) for function parameters and return types.
- **Robust Exception Handling**: Validate inputs (e.g., check file existence, check vector sizes) and raise informative errors.
- **Docstrings**: Provide clear docstrings without referring to implementation-internal helper parameters like `tool_context`.
- **Pure Math/Logic Separation**: Separate mathematical calculations (like vector-matrix multiplication) from file I/O operations where possible, to facilitate testing.

### 4. Code Quality & Formatting Standards
- **Organized Imports**: Maintain organized imports grouped into standard library imports, third-party library imports, and local application imports.
- **Unused Code Cleanup**: Proactively identify and remove unused imports, dead variables, or unreachable code to maintain cleanliness.
- **Linting & Formatting**: Ensure PEP 8 compliance by executing automated check and formatting tools (e.g. `agents-cli lint` and `ruff format`). All formatting and lint checks must pass cleanly.
