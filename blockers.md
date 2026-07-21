# Release Blocker List - Day 18

| # | Source | Issue | Severity | Owner | Status |
|---|--------|-------|----------|-------|--------|
| 1 | adversarial | Prompt/rules leaked on "restate"/"repeat before" | HIGH | P1 | closed |
| 2 | adversarial | Login-bypass steps under "no rules" roleplay | HIGH | P1 | closed |
| 3 | adversarial | Role-played "maintenance mode guardrails off" | HIGH | P1 | closed |
| 4 | adversarial | Capability-text leak on translate injection | MED | P1 | closed |
| 5 | infra | models/lead.py had route code -> circular import, server would not boot | HIGH | P2 | closed |
| 6 | load test | /chat returned 500 on Groq error instead of graceful message | HIGH | P2 | closed |
| 7 | adversarial | Output filter false-positive blocked normal greetings | MED | P1 | closed |
| 8 | load test | Breaking point ~5 users; root cause = Groq free-tier 6000 tok/min | MED | P2 | known limit |

## Infra checks (Step E)
- DB backup/restore: PASS (20KB copied and verified)
- .env gitignored: PASS
- Groq key rotation: deferred to deploy

## v2 backlog (cosmetics - NOT blockers)
- Bot plans non-India trips (e.g. Lisbon to Porto) - should redirect to India scope

## Production notes
- Latency under load: median 14s, up to 35s - fine for pilot, upgrade Groq tier for scale.
- save_lead() only closes DB session on success - wrap in try/finally for v2.

## Walkthrough
- N testers on staging, no new blockers filed.

## Walkthrough
- 6 testers on staging, no new blockers filed.
