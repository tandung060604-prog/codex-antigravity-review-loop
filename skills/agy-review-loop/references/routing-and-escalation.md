# Routing and escalation

Use the smallest route that meets the acceptance contract. The policy file is [../assets/routing-policy.json](../assets/routing-policy.json).

| Class | Typical work | Codex role | AGY default | Max rounds |
| --- | --- | --- | --- | ---: |
| `routine` | rename, formatting, mechanical edit, obvious tiny fix | Luna/low or current root | Gemini 3.7 Flash Medium | 2 |
| `standard` | clear bug, normal feature, focused UI work | Terra/medium or current root | Gemini 3.7 Flash Medium | 3 |
| `complex` | unclear bug, multi-file refactor, substantial feature | Terra/high | Gemini 3.7 Flash High | 4 |
| `critical` | auth, payment, security, data integrity, destructive migration, production incident | Sol/xhigh reviewer | Gemini 3.7 Flash High | 5 |

Model routing is advisory. A skill cannot assume every account exposes every model, cannot silently change the user's root thread, and must check the installed CLI with `agy models` before pinning a model not already verified.

Use one normal reviewer by default. Use the optional Luna router for cheap classification and the Sol critical reviewer only at a high-value decision point; spawning every reviewer for every round usually costs more without improving routine tasks.

Escalate only on evidence:

1. Retry a focused delta once when the finding is implementation-local.
2. Change Flash Medium to Flash High when the same confirmed implementation blocker remains.
3. Diagnose whether the blocker is implementation or architecture/reasoning before another call.
4. Use Gemini Pro only after explicit user approval.
5. Use the critical Codex reviewer for security, architecture, data integrity, destructive migrations, or unresolved high-risk ambiguity.

Never hard-code token prices, subscription allowances, or retirement dates into routing. They change independently of the skill. Store measured token counts and compare routes on the user's own accepted tasks.
