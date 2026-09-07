# Magellan behavioral scenarios

These are the behavioral tests for the Magellan skill. Magellan is a prose skill with no runnable suite (except `forge_compat_check.py`, which is real code), so a scenario passes when Magellan's observable behavior matches its **Expected** line when traced against `fixtures/`. All scenarios trace against `fixtures/toy-brief.json`, `fixtures/toy-repo/`, and `fixtures/vault/decisions/`.

## M1 — Ingest accepts Bastion's structured brief

Input: `fixtures/toy-brief.json`, passed as Magellan's argument.
Expected: Phase 1 parses it directly as `{how, scope, appliedDirectives, resolvedGaps}` with no restate-and-confirm step — that fallback is only for raw free text.

## M2 — Ingest falls back to restate-and-confirm on free text

Input: the plain sentence "Add a healthz endpoint fronted by the rate limiter" (no JSON block).
Expected: Magellan restates this back as a best-effort `{how, scope}` and asks the engineer to confirm before proceeding — it does not silently invent `appliedDirectives` or `resolvedGaps` from nothing.

## M3 — Decompose self-check: acyclic

Given a deliberately bad cut where task `t2` depends on `t3` and `t3` depends on `t2`.
Expected: the self-check catches the cycle before the DAG is ever shown to the engineer; Magellan re-cuts rather than presenting a non-topological DAG.

## M4 — Decompose self-check: provable

Given a deliberately bad cut where one task has an empty `acceptance_criteria` array.
Expected: the self-check rejects it and re-cuts; no task reaches the DAG gate without at least one acceptance criterion.

## M5 — Decompose self-check: scoped

Given `fixtures/toy-brief.json`'s `scope.out: ["src/auth/middleware.ts"]` and a naive cut that adds a task touching `src/auth/middleware.ts` (e.g. "add an auth bypass allowlist for healthz").
Expected: Magellan does not silently include that file; it surfaces a scope flag in the DAG gate review instead ("touches src/auth/middleware.ts, which is out of scope — intentional?").

## M6 — DAG gate is a hard gate

Given a valid, self-check-passing cut of `fixtures/toy-brief.json` into two tasks (endpoint, rate-limit guard).
Expected: Magellan presents the `MAGELLAN — PROPOSED TASK CUTS` block and stops; it does not proceed to Phase 3 context-compilation until the engineer explicitly approves. A request to merge the two tasks into one triggers a re-cut and a re-run of the self-check before the DAG is shown again.

## M7 — Context compilation: active-only filter

Task's `files` include `src/routes.ts`, which both `fixtures/vault/decisions/2026-06-01-routes-register-in-routes-ts.md` (status: active) and `fixtures/vault/decisions/2025-01-01-healthz-requires-api-key.md` (status: superseded) are topically about.
Expected: only the active decision is attached to the task's `context.decisions`; the superseded one is never attached, even though it is topically on-point.

## M8 — Context compilation: refs and interfaces from the DAG edges

Task "add rate-limit guard on /healthz" depends on task "add /healthz endpoint," and the fixture repo already has `fixtures/toy-repo/src/rateLimiter.ts` exporting `RateLimiter`.
Expected: the guard task's `context.refs` includes `{file: "fixtures/toy-repo/src/rateLimiter.ts", line: 2, symbol: "RateLimiter"}` (an existing, pre-code symbol, found by reading the file, not invented); its `context.interfaces.consumes` names what the endpoint task produces (the route it registers), derived from the DAG edge, not from code that doesn't exist yet.

## M9 — Output, routing, and terminal state

Given a fully compiled plan for `fixtures/toy-brief.json`.
Expected: the output file is written to `docs/superpowers/plans/YYYY-MM-DD-healthz-tasks.json` (gitignored, confirmed via `git check-ignore`); no vault decision is written automatically; the `MAGELLAN — COMPILED PLAN` block names both the Forge caveat ("context will not survive forge plan next/status/complete") and the Claude Code/cloud-agent handoff; Magellan stops there — it does not offer to execute any task itself.
