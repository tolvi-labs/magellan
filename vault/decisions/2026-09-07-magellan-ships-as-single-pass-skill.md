---
tags: [decision, magellan]
date: 2026-09-07
repo: magellan
status: active
ticket: none
user_impact: none
product_area: Product scope
---

# Magellan ships as a single-pass Claude Code skill with one DAG approval gate, no per-compile vault writes

**Date:** 2026-09-07
**Repo:** magellan

## Why
The 2026-07-23 decision committed Magellan's product scope (executor-agnostic plan compiler, per-task context compilation) but not its implementation form. Guild and Bastion are both Claude Code skills, not standalone programs, and Magellan's actual work — cutting a brief into tasks and running a handful of `tolvi` lookups per task — is judgment-heavy reasoning an LLM does well in-session, not logic that needs its own runtime. Building it as a program (its own CLI, like Forge) would have meant new packaging and distribution for no accuracy gain.

## How
- **Form:** a single-file skill, `skills/tolvi-magellan/SKILL.md`, matching Bastion's precedent rather than Guild's multi-file structure — Magellan has no multi-track fan-out driving complexity into separate reference docs.
- **Architecture:** single-pass, no subagents. Considered and rejected: per-task subagent fan-out (mirroring Guild's track-readers) — real ceremony that only pays off with plans producing dozens of tasks, which isn't the common case.
- **One hard gate:** the engineer approves the task DAG (Phase 2) before Magellan spends retrieval effort compiling context for it (Phase 3) — matches the "engineer owns scope decisions" pattern Guild and Bastion both hard-gate on. Considered and rejected: no gate at all, reviewed only at the end — risks compiling context for a bad cut before anyone catches it.
- **No vault write-back per compile.** Unlike Guild, a routine compile is mechanical, not a comprehension-forcing judgment call; auto-writing a decision on every run would spam the vault. An engineer override during the DAG gate is captured the normal way (a session log), not by Magellan itself.
- **Interface with Bastion:** Bastion's Step 6 needed a small additive patch (a structured JSON block) to actually deliver the `{how, scope, appliedDirectives, resolvedGaps}` handoff Guild's docs already promised but Bastion never produced — see [[2026-09-07-bastion-emits-structured-brief-json]] in the bastion repo's vault.
- **Forge compatibility, with an honest caveat:** verified directly against Forge's real validator (`forge/src/forge/plan/manifest.py`) that the extra per-task `context` field passes schema validation and is silently dropped, never erroring. But `forge plan load` re-serializes its own internal snapshot from only the 5 known fields, so `context` doesn't survive into `forge plan next/status/complete` — Magellan's delivery message says this plainly rather than overclaiming a benefit Forge-as-executor won't get.

## Outcome
Magellan moved from pre-build to a working skill: `skills/tolvi-magellan/SKILL.md` (Ingest → Decompose+gate → Context-compile → Emit/route), `install.sh`, an updated README, and `tests/scenarios.md` + `fixtures/` + `forge_compat_check.py` as its verification suite (the same prose-scenario convention Guild already established, plus one real executable check since Forge's schema is real code that can be checked directly). Phases 3-4 of the original `PLAN.md` schematic build plan (per-task context compilation, executor adapters) are now implemented, not just planned; dogfooding on a real (non-fixture) repo and task is the natural next step to calibrate the context-budget assumptions the original plan flagged as riskiest.
