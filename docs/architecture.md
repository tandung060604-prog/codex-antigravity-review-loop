# Architecture

## Responsibilities

| Layer | Required? | Owns | Must not own |
| --- | --- | --- | --- |
| `agy-review-loop` | Yes | AGY calls, diff review, acceptance checks, bounded iteration | billing, credentials, publishing, unrestricted autonomy |
| `codex-longrun` | No | durable state, task sequencing, handoffs, checkpoints | Antigravity conversation continuity |
| `ponytail` | No | minimal-change decisions and dependency discipline | project lifecycle or agent transport |

The core workflow is `Codex → agy-review-loop → Antigravity CLI`. Optional layers guide Codex but are not runtime dependencies of this repository.

## State model

```text
READY → DELEGATED → REVIEWING → ACCEPTED
                         ├──────→ CORRECTION (max 5 rounds)
                         └──────→ BLOCKED / STOPPED
```

Acceptance requires evidence from the working tree and checks. Structured `status: DONE` is only a report field and never changes the state by itself.

## Safety invariants

- A round has a self-contained prompt and a bounded timeout governed by the host execution layer.
- Pre-existing user changes are part of the baseline and are not reverted.
- External state changes require separate user authorization.
- Quota, permissions, credentials, and destructive operations are not bypassed.
