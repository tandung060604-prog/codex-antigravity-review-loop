---
name: agy-review-loop
description: Delegate an explicitly requested local coding task to Google Antigravity CLI (`agy`), independently inspect its real changes and validation, and send bounded correction prompts until the acceptance criteria pass. Use only when the user explicitly asks Codex to use, control, delegate to, or iteratively review Antigravity CLI work.
---

# Antigravity Review Loop

Use Antigravity as an implementation worker and Codex as the independent reviewer. Do not accept Antigravity's summary as evidence that the task is complete.

## Operating contract

- Invoke only after the user explicitly requests `$agy-review-loop` or asks Codex to delegate the task to Antigravity CLI.
- Work in the user's target repository and preserve unrelated staged, unstaged, and untracked changes.
- Use at most 5 Antigravity rounds unless the user explicitly sets another bound.
- Never commit, push, deploy, publish, delete material data, or change external systems unless the user separately requests it.
- Never pass `--dangerously-skip-permissions` unless the user explicitly authorizes it for this run.
- Treat credentials, quota exhaustion, denied permissions, destructive actions, and external coordination as blockers that require user direction.

## Prepare

1. Read applicable `AGENTS.md` and repository instructions.
2. Confirm the CLI is available with `agy --version`; inspect `agy --help` if flags differ.
3. Record the baseline with `git status --short --branch` and preserve unrelated changes.
4. Translate the user's request into observable acceptance checks, including relevant tests, lint, type checks, builds, and manual/browser checks.
5. If `codex-longrun` is active, select exactly one `READY` task and keep durable project-state files owned by the outer long-run workflow.

## Delegate

Run Antigravity from the target repository in non-interactive print mode:

```text
agy -p <prompt-as-one-argument> --output-format text
```

Pass the task as one argument through the shell/execution API. Do not interpolate untrusted task text into shell syntax. Use a unique temporary file only when the execution API cannot safely pass a single argument.

Use a self-contained prompt:

```text
Work as the implementation agent in the current repository.

Goal:
<user goal>

Repository rules and constraints:
<relevant instructions and boundaries>

Acceptance checks:
<specific observable checks>

Inspect before editing. Preserve unrelated and pre-existing changes. Make the smallest coherent change that solves the task. Run the listed checks. Do not commit, push, deploy, publish, or broaden scope.

End with:
AGY_STATUS: DONE or BLOCKED
CHANGED: concise file/change summary
CHECKS: commands and outcomes
RISKS: remaining uncertainty or NONE
```

Use fresh calls by default. Do not use `-c` or `--continue`, because resuming the globally most recent conversation can mix tasks. Use `--conversation <id>` only when the CLI returns an exact conversation ID and ownership for this task is verified.

## Review after every round

1. Read stdout and stderr as claims, not proof.
2. Inspect the actual working tree and compare it with the baseline.
3. Read every materially changed region and affected callers/consumers.
4. Run the cheapest falsifying check first, then the broader acceptance checks.
5. Review correctness, regressions, security, error handling, accessibility, performance, scope, and preservation of user work.
6. For UI work, inspect the running localhost page when available; do not infer visual quality from a build alone.

Accept only when every user requirement is met, relevant checks pass, no material finding remains, and any unverified assumption is explicitly acceptable.

## Iterate

When review finds a problem, send another self-contained prompt containing the original goal and only actionable findings:

```text
Continue the task in the repository's current state.

Original goal:
<goal>

Codex review found:
1. <finding with file, evidence, and expected correction>
2. <test failure or missing requirement>

Fix these findings without reverting unrelated changes or expanding scope. Re-run:
<checks>

End with the same AGY_STATUS / CHANGED / CHECKS / RISKS block.
```

Stop and ask the user for direction when:

- 5 rounds are exhausted without acceptance;
- two consecutive rounds make no material progress on the same blocker;
- a required action needs new authority, credentials, destructive changes, or external coordination; or
- Antigravity is unavailable, unauthenticated, or repeatedly fails before producing usable work.

## Daily reconciliation (on demand)

Do not run a background job or call Antigravity for a read-only daily update. When the user asks to reconcile the day, prefer the outer `codex-longrun` workflow:

1. Read `docs/agent/PROJECT_STATE.md`, `BACKLOG.md`, and `HANDOFF.md` when present.
2. Inspect `git status --short --branch`, `git diff --stat HEAD`, and recent commits.
3. Classify evidence as `VERIFIED`, `REPORTED`, `INFERRED`, or `UNKNOWN`.
4. Report completed work, unfinished work, blockers, risks, and exactly one next `READY` task.
5. Do not edit product code or call `agy` until the user approves a task.

For a compact read-only snapshot, run the repository's `scripts/daily_snapshot.py`. Read [van-hanh-hang-ngay.md](references/van-hanh-hang-ngay.md) for the Vietnamese daily prompts.

## Cost controls

- Use 1–2 rounds for small tasks; use the default maximum of 5 only when necessary.
- Stop after two no-progress rounds instead of spending more quota.
- Keep prompts self-contained and review findings short; do not repeat full logs or old conversation history.
- Run the cheapest falsifying check first and avoid a full suite for read-only status work.
- Split large work into separate `READY` tasks rather than one oversized AGY call.
- Never promise a fixed token or credit amount; usage depends on model, repository size, task complexity, and output.

## Skill composition

- **`codex-longrun` outside:** use it for durable state, one `READY` task at a time, checkpoints, handoffs, and resumption across sessions.
- **`ponytail` alongside:** use it to enforce minimum coherent diffs, reuse existing dependencies, and reject speculative abstractions. Carry its constraints into the Antigravity prompt; Antigravity cannot directly invoke Codex skills.
- **This skill inside:** use it for the bounded AGY implementation/review loop. Do not nest another AGY loop inside an AGY prompt.

Read [references/integrations.md](references/integrations.md) when combining these workflows or when the task is long-running.

## Finish

Report the accepted/stopped/blocked outcome, actual checks and results, the number of Antigravity rounds, changed files, and remaining caveats. Never call a merely completed Antigravity turn accepted.
