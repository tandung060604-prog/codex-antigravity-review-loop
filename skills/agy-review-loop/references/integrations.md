# Integrating the review loop

`agy-review-loop` works without `codex-longrun` or `ponytail`. Both integrations are optional and are not bundled with this repository.

## Optional layering

Use one owner for each concern:

1. `agy-review-loop` owns the required delegation loop: call `agy`, inspect the real diff, run checks, and request bounded corrections.
2. Optional `codex-longrun` owns the project lifecycle: durable state, task IDs, acceptance criteria, checkpoints, handoffs, and resumption.
3. Optional `ponytail` owns implementation discipline: inspect first, reuse existing code/dependencies, prefer native solutions, and keep the smallest coherent diff.

The layers should not recursively invoke each other. A normal task can use only `agy-review-loop`. For a multi-session project, start with `$codex-longrun`, apply Ponytail when choosing the implementation, then let `agy-review-loop` handle the single `READY` task. Explicit invocation remains available but is not required when Codex selects the skill automatically.

Daily reconciliation is a separate, read-only `codex-longrun` action. It should inspect durable state and Git without calling AGY; delegate only the approved `READY` task afterward.

## Combined prompt template

```text
$codex-longrun

Prepare one READY task for this objective:
<objective>

Use $ponytail principles for the implementation: inspect first, reuse what exists, prefer native/existing dependencies, and avoid speculative abstractions.

Then let $agy-review-loop delegate that READY task to Antigravity CLI. Keep the loop bounded to 5 rounds. Do not modify durable state files from inside Antigravity unless the task explicitly owns them.
```

## Ownership boundaries

- Long-run state (`docs/agent/PROJECT_STATE.md`, `BACKLOG.md`, `HANDOFF.md`) remains a Codex responsibility.
- Product code and task-local tests may be edited by Antigravity within the approved scope.
- Git commits, pushes, releases, and publishing require explicit user authorization even when the repository is public.
- If a task needs a new production dependency, architecture change, secret, or external account, stop and request direction.

## Failure modes

- **Loop churn:** stop after two no-progress rounds and record the blocker.
- **Scope drift:** reject unrelated files and ask Antigravity to revert only its unrelated changes without touching pre-existing user work.
- **Visual false positives:** require a running localhost check or screenshot for UI acceptance; a passing build is not visual proof.
- **Credit/permission exhaustion:** do not bypass limits or permissions; report the exact denied operation.
- **Cost drift:** prefer 1–2 rounds for small tasks, keep review findings compact, and stop after two no-progress rounds.
