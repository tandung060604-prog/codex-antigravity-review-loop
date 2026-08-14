# Contributing

Thanks for helping improve the Antigravity Review Loop.

## Before opening a pull request

- Keep the installable skill concise and under 500 lines.
- Preserve the explicit-invocation and bounded-loop safety defaults.
- Do not add secrets, credentials, personal data, or unredacted logs.
- Run:

  ```powershell
  python scripts/validate_repo.py
  python -m unittest discover -s tests -p "test_*.py"
  ```

- Explain any behavior change in `CHANGELOG.md`.

## Scope

Changes should improve delegation reliability, review evidence, safety, or documentation. New production dependencies and changes to publishing behavior require an issue or maintainer approval first.
