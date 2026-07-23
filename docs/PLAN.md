# Tolvi Magellan — Go-Forward Plan

**Status:** Pre-build. New tool, designed 2026-07-23. Inherits Guild's former plan-authoring (its Phase 5) and specializes it into an executor-agnostic, context-compiled plan artifact.
**Last updated:** 2026-07-23

## One-line

The compiler that turns an engineer-approved approach into a decomposed, context-compiled task DAG — executor-agnostic, accuracy-first, cost-minimized — that Forge, Claude Code, or a cloud agent can each execute.

## Why it exists

Guild was reframed to shed plan-authoring and force comprehension instead (see the guild vault: `2026-07-23-guild-sheds-plan-authoring-to-magellan`). Nothing else in the stack authors a plan — Bastion never writes one, Forge only executes a decomposed `tasks.json`. The plan artifact also wants properties no existing tool provides: executor-agnostic, AI-legible, accuracy-first, cost-minimized, and vault-wired. Magellan is that tool. See [[2026-07-23-magellan-execution-optimized-plan-compiler]].

## What it is

- **A compiler, not an approach-chooser.** Input is Guild's approved brief (`{how, scope, appliedDirectives, resolvedGaps}`); output is the executable plan. The engineer owns the how; Magellan owns the task cuts and the context per cut.
- **Per-task context compilation is the core mechanism** — each task carries exactly its governing vault decisions, code refs, interfaces, and proving test, retrieved via tolvi. This resolves the accuracy↔cost tension and is the tolvi differentiator.
- **Decomposition and context-compilation are one pass** — cutting a task fixes its files, dependencies, and acceptance criteria; attaching context requires the cut.
- **Output = Forge `tasks.json` superset** — the same task DAG plus `context: { decisions, refs, interfaces:{consumes, produces} }` per task.

## Suite position

```
Vault → Guild (comprehension) → Bastion (harden approach) → Magellan (compile plan) → Forge / Claude Code / cloud (execute)
```

Provenance (record-gate at push) and Canary (test-gate in CI) are the downstream gates. Bastion hardens the brief (moved one slot earlier) so Magellan compiles once, last.

## Schematic build plan (thinnest slice first)

Plan-first; each phase is dogfooded on one real repo before the next. Harden through Bastion before writing code.

1. **The output schema.** Define the executor-agnostic plan format: Forge's `tasks.json` core (`feature`, `stack`, `tasks[]` with `id`/`title`/`files`/`dependencies`/`acceptance_criteria`) plus the per-task `context` field (`decisions`, `refs`, `interfaces`). Verify it round-trips through Forge's existing `load_manifest` validator unchanged (Forge must ignore `context` without erroring). → verify: a compiled plan runs under `forge plan` and is also readable by a Claude Code executor.
2. **Decomposition from a brief.** Given Guild's approved brief, cut the approach into a task DAG with dependency edges and per-task acceptance criteria (no placeholders). → verify: the DAG topologically orders, every task has a proving test, and `files` cover the brief's scope with nothing out-of-scope.
3. **Per-task context compilation.** For each task, retrieve via tolvi the governing decisions, code refs, and interfaces, and attach only those. → verify: dogfood the accuracy↔cost budget — measure executor token use and error rate; confirm under-compiling (executor guessing) is the failure mode being tuned against, and that accuracy wins ties.
4. **Executor adapters (thin).** Confirm the one artifact drives Forge, Claude Code, and a cloud agent, each consuming what it understands. → verify: same plan, three executors, equivalent result.

## Riskiest assumptions (call out, don't hand-wave)

- **Context-budget calibration is empirical.** Too little context → executor drift and inaccuracy (the expensive failure); too much → cost creep back to baseline. This is tuned by dogfooding, not decided up front.
- **Decomposition quality drives execution accuracy.** Badly cut task boundaries cause drift regardless of context. The cut is a first-class part of the compile, not a formality.
- **Retrieval precision.** Attaching the *wrong* decisions/refs is as harmful as attaching too few. Magellan's value is precision, not volume.

## Boundaries (no overclaim)

Magellan contributes to correctness structurally (interfaces, a test per task, no placeholders, right-sized context). It does not guarantee bug-free or regression-free execution — regression catching is Canary, precedent compliance is Bastion. It never chooses the approach (Guild + engineer) and never executes (Forge / the chosen executor).

## Next step

Write the phase-1 kickoff prompt (the output schema slice), run it in this repo, and harden the result through Bastion before any code.
