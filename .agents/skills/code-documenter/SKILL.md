---
name: code-documenter
description: Guidelines and instructions for automatically documenting Python source code files with PEP 257-compliant docstrings and clean annotations.
---

# Code Documenter Skill

This skill provides comprehensive instructions for verifying, adding, and improving docstrings and comments across all Python source code files to align them with PEP 257 docstring conventions and clear inline commenting guidelines.

## Docstring Conventions (PEP 257)

1. **Module Docstrings**: Every module (Python file) should start with a docstring explaining its purpose, exported classes/functions, and any relevant context or usage examples.
2. **Class Docstrings**: Every class should have a docstring outlining its responsibility, attributes (with types and descriptions), and examples if applicable.
3. **Function/Method Docstrings**: Every function and method should have a docstring detailing:
   - A brief, one-line summary.
   - A detailed description of the logic if non-trivial.
   - **Args**: Input parameters, their types, and meanings.
   - **Returns**: Output return types and description.
   - **Raises**: Any exceptions raised during execution.

## Inline Comments

- Use inline comments sparingly to explain *why* something is done, not *what* the code is doing.
- Keep comments up-to-date with code modifications.

## Automated Verification

Run lint check to verify styling and code quality:
```bash
agents-cli lint
```
