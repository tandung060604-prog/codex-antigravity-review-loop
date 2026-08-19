---
name: agy-review-loop
description: Delegate non-trivial local coding, debugging, refactoring, or UI implementation to Google Antigravity CLI (`agy`), then independently review its real changes and validation in bounded correction rounds. Do not use for read-only or status work, trivial or documentation-only edits, or when the user opts out of Antigravity.
---

# Antigravity Review Loop

Use Antigravity as an implementation worker and Codex as the independent reviewer. Do not accept Antigravity's summary as evidence that the task is complete.

## Operating contract

- May activate implicitly for non-trivial local repository implementation tasks that match the description. Explicit `$agy-review-loop` invocation remains supported.
- Do not invoke Antigravity for read-only analysis, status or planning, trivial or documentation-only edits, or when the user says not to use Antigravity.
- Before the first Antigravity round, briefly tell the user that delegation is starting and may consume their Antigravity quota. Continue without asking unless the task needs new authority, Gemini Pro, or a destructive action.
- Work in the user's target repository and preserve unrelated staged, unstaged, and untracked changes.
- Classify the task as `routine`, `standard`, `complex`, or `critical`; use the corresponding 2/3/4/5-round ceiling unless the user sets a lower bound.
- Never commit, push, deploy, publish, delete material data, or change external systems unless the user separately requests it.
- Never pass `--dangerously-skip-permissions` unless the user explicitly authorizes it for this run.
- Treat credentials, quota exhaustion, denied permissions, destructive actions, and external coordination as blockers that require user direction.

## Prepare

1. Read applicable `AGENTS.md` and repository instructions.
2. Confirm the CLI is available with `agy --version`; inspect `agy --help` if flags differ.
3. Record the baseline with `git status --short --branch` and preserve unrelated changes.
4. Translate the user's request into observable acceptance checks, including relevant tests, lint, type checks, builds, and manual/browser checks.
5. Classify risk using [references/routing-and-escalation.md](references/routing-and-escalation.md). Treat model choices as advisory; do not silently change the user's current Codex model.
6. If `codex-longrun` is active, select exactly one `READY` task and keep durable project-state files owned by the outer long-run workflow.

## Delegate

Write the prompt to a unique UTF-8 temporary file outside the target repository, then run one structured round through the bundled helper:

```text
python <skill-root>/scripts/agy_round.py \
  --repo <target-repository> \
  --task-id <safe-task-id> \
  --round 1 \
  --class <routine|standard|complex|critical> \
  --prompt-file <temporary-prompt-file>
```

The helper passes arguments without a shell, pins the policy model, requests `stream-json` with [assets/agy-result.schema.json](assets/agy-result.schema.json), and stores a compact summary under `.agy-review/<task-id>/`. It does not save the raw prompt. Raw JSONL is opt-in with `--save-events` because tool events can contain sensitive data. Ensure `.agy-review/` is ignored before retaining metrics in a product repository.

If the installed CLI lacks `--output-format stream-json` or `--json-schema`, fall back to text mode and report that metrics/schema enforcement are unavailable; do not guess fields.

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

Return only the schema fields: status, changed_files, checks, risks, and blocker.
```

Use fresh calls by default. Do not use `-c` or `--continue`, because resuming the globally most recent conversation can mix tasks. Use `--conversation <id>` only when the CLI returns an exact conversation ID and ownership for this task is verified.

## Review after every round

1. Read the structured round summary as claims, not proof. Record the reported AGY usage metrics but do not infer API cost from them.
2. Inspect the actual working tree and compare it with the baseline.
3. Read every materially changed region and affected callers/consumers.
4. Run the cheapest falsifying check first, then the broader acceptance checks.
5. Review correctness, regressions, security, error handling, accessibility, performance, scope, and preservation of user work.
6. For UI work, inspect the running localhost page when available; do not infer visual quality from a build alone.

Accept only when every user requirement is met, relevant checks pass, no material finding remains, and any unverified assumption is explicitly acceptable.

## Iterate

When review finds a problem, create another prompt file containing only the acceptance contract and actionable delta:

```text
Continue the task in the repository's current state.

Acceptance contract:
<concise goal, allowed scope, and checks>

Finding:
<file and line>

Observed:
<actual behavior>

Expected:
<required behavior>

Evidence:
<test failure, diff, or reproduction>

Allowed scope:
<files or directories>

Fix these findings without reverting unrelated changes or expanding scope. Re-run:
<checks>

Return only the same structured schema.
```

Run the next numbered round with the same task ID. Prefer fresh calls. Pass `--conversation <id>` only when the helper's existing summary proves that ID belongs to an earlier round of the same task.

Do not repeat the same model against the same blocker. Escalate Flash Medium to Flash High after evidence shows an implementation blocker. Use Gemini Pro only after diagnosis and explicit user approval, then pass `--model gemini-3.1-pro-high --approve-pro`. Escalate Codex review to a high-capability reviewer for security, architecture, data integrity, or unresolved ambiguity; do not spend multiple reviewers on routine work.

Stop and ask the user for direction when:

- the class-specific round ceiling is exhausted without acceptance;
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
- Keep raw AGY event logging off unless the user needs an audit trace; compact summaries retain usage without tool payloads.
- Never promise a fixed token or credit amount; usage depends on model, repository size, task complexity, and output.
- Mark Codex/OpenAI token usage `UNKNOWN` unless the host explicitly exposes it; AGY metrics do not include Codex usage.

## Skill composition

- **`codex-longrun` outside:** use it for durable state, one `READY` task at a time, checkpoints, handoffs, and resumption across sessions.
- **`ponytail` alongside:** use it to enforce minimum coherent diffs, reuse existing dependencies, and reject speculative abstractions. Carry its constraints into the Antigravity prompt; Antigravity cannot directly invoke Codex skills.
- **This skill inside:** use it for the bounded AGY implementation/review loop. Do not nest another AGY loop inside an AGY prompt.

Read [references/integrations.md](references/integrations.md) when combining these workflows or when the task is long-running.

## Finish

Report the accepted/stopped/blocked outcome, actual checks and results, the number of Antigravity rounds, changed files, and remaining caveats. Never call a merely completed Antigravity turn accepted.
