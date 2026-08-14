# Codex Antigravity Review Loop

An explicit Codex skill that delegates a local coding task to Google Antigravity CLI (`agy`), verifies the real working-tree changes, runs acceptance checks, and sends bounded correction prompts until the task is accepted or stopped safely.

The project is intentionally an orchestration skill, not an Antigravity replacement. It does not include a model, API key, browser-login bypass, quota bypass, or automatic publishing.

## What it does

```text
User request → Codex acceptance criteria → Antigravity implementation
                                      ↓
                         Codex diff/tests/browser review
                         ↙                         ↘
                  accepted                  focused correction
```

- Maximum 5 Antigravity rounds by default.
- Independent review of the actual diff instead of trusting agent prose.
- Preservation of unrelated user changes.
- Explicit stop conditions for blockers, permissions, credentials, quota, and scope drift.
- Safe defaults: no commit, push, deploy, publish, or destructive permission bypass.

## Prerequisites

1. Install and authenticate Antigravity CLI as described in the [official CLI documentation](https://antigravity.google/docs/cli/install).
2. Confirm it works:

   ```powershell
   agy --version
   agy -p "Reply with exactly AGY_OK. Do not edit files or run commands." --output-format text
   ```

3. Use a Codex installation that can discover user-level skills.

The skill uses the Antigravity account's own quota. Google AI Pro provides its baseline Antigravity quota; AI credits are an optional overage path controlled by Antigravity settings. This repository does not change billing or quota behavior.

## Install in Codex

The recommended installation keeps the skill folder isolated from repository documentation:

```powershell
python <path-to-codex>\skills\.system\skill-installer\scripts\install-skill-from-github.py `
  --repo tandung060604-prog/codex-antigravity-review-loop `
  --path skills/agy-review-loop
```

Restart Codex if the skill does not appear immediately. Invoke it explicitly:

```text
$agy-review-loop

Fix the checkout form validation bug. Add a regression test, run lint and tests, and do not commit or deploy.
```

## Compose with other Codex skills

Recommended order:

1. `codex-longrun` — owns durable project state and exactly one `READY` task.
2. `ponytail` — enforces the smallest coherent implementation and rejects speculative dependencies.
3. `agy-review-loop` — delegates the approved task and independently reviews each round.

See [integration guidance](skills/agy-review-loop/references/integrations.md) and [prompt patterns](skills/agy-review-loop/references/task-prompts.md).

## Repository layout

```text
skills/agy-review-loop/   # installable Codex skill
docs/                     # design and release notes
examples/                 # copyable task prompts
scripts/                  # deterministic repository checks
tests/                    # smoke tests for package structure
.github/workflows/        # CI validation
```

## Development

Run the local validation before opening a pull request:

```powershell
python scripts/validate_repo.py
python -m unittest discover -s tests -p "test_*.py"
```

The official Codex skill validator is also recommended when available:

```powershell
python <skill-creator-root>\scripts\quick_validate.py skills/agy-review-loop
```

## License and contributions

The repository is released under the Apache License 2.0. See [LICENSE](LICENSE) and [CONTRIBUTING.md](CONTRIBUTING.md). Commercial use, hosted services, and paid support are allowed under the license; the project name and marks remain subject to [NOTICE](NOTICE).
