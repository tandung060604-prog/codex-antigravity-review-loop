# Task prompt patterns

Keep each task prompt self-contained and testable. Replace bracketed text before sending.

## UI motion

```text
Use $agy-review-loop for the current localhost project.

Add restrained, accessible motion to the existing interface:
- section entrance and scroll reveal;
- staggered card/list entry;
- subtle hover/focus motion for interactive blocks;
- responsive behavior and prefers-reduced-motion support.

Inspect the existing stack and dependencies first. Reuse what is already installed; do not rewrite the app or add a motion library unless the current stack clearly requires it. Preserve content and behavior. Verify the running localhost page, console, lint, tests, and build. Do not commit or deploy.
```

## Bug fix

```text
Use $agy-review-loop to fix [bug] in [area]. Reproduce it first, identify the root cause, add the smallest regression check, run [commands], and preserve unrelated changes. Do not commit or broaden scope.
```

## Feature

```text
Use $agy-review-loop to implement [feature] for [user value]. Acceptance criteria: [list]. Keep the existing architecture unless a change is necessary, add focused tests, run [commands], and do not commit, push, or deploy.
```
