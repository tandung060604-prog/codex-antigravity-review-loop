# Integrating the review loop

## Recommended layering

Use one owner for each concern:

1. `codex-longrun` owns the project lifecycle: durable state, task IDs, acceptance criteria, checkpoints, handoffs, and resumption.
2. `ponytail` owns implementation discipline: inspect first, reuse existing code/dependencies, prefer native solutions, and keep the smallest coherent diff.
3. `agy-review-loop` owns delegation: call `agy`, inspect the real diff, run checks, and request bounded corrections.

The layers should not recursively invoke each other. In practice, start a task with `$codex-longrun`, apply `$ponytail` when choosing the implementation, and explicitly invoke `$agy-review-loop` for the single `READY` task.

## Prompt template

```text
$codex-longrun

Prepare one READY task for this objective:
<objective>

Use $ponytail principles for the implementation: inspect first, reuse what exists, prefer native/existing dependencies, and avoid speculative abstractions.

Then use $agy-review-loop to delegate that READY task to Antigravity CLI. Keep the loop bounded to 5 rounds. Do not modify durable state files from inside Antigravity unless the task explicitly owns them.
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
