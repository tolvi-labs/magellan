---
tags: [decision, magellan]
date: 2026-07-23
repo: magellan
status: active
ticket: none
user_impact: medium
product_area: Product scope
---

# Magellan is the executor-agnostic execution-optimized plan compiler; it inherits Guild's plan-authoring

**Date:** 2026-07-23
**Repo:** magellan

## Why

Guild was reframed to shed plan-authoring and focus on forcing comprehension (see [[2026-07-23-guild-sheds-plan-authoring-to-magellan]]), and nothing else in the stack catches the plan: Bastion never writes one, and Forge only *executes* an already-decomposed `tasks.json`. The plan artifact also has specialized requirements no existing tool is built to meet — it should be executor-agnostic, AI-legible, accuracy-first, cost-minimized, and wired to the vault. Magellan is that tool: it turns an approved approach into an executable, context-compiled plan.

## How

- **It is a compiler, not a brainstormer or an approach-chooser.** Magellan takes Guild's approved brief (`{how, scope, appliedDirectives, resolvedGaps}` — the engineer-decided approach) and compiles it into an executable plan. The engineer owns the *how*; Magellan owns the *cut into tasks* and the *context per cut*.
- **Per-task context compilation is the core mechanism, and the accuracy↔cost resolver.** Accuracy wants to hand the executor everything; cost wants to hand it nothing. Magellan attaches to each task exactly what that task needs — the governing vault decisions, the specific code refs, the interface it consumes/produces, and the test that proves it — retrieved via tolvi, and nothing else. The executor never burns tokens rediscovering what Magellan pinned, and never drifts from what Magellan should have attached. This per-task context bundle is why Magellan is a tolvi tool and not generic writing-plans.
- **Decomposition and context-compilation are one pass.** You cannot cut a task without fixing its `files` (change surface), its `dependencies` (what it consumes/produces), and its `acceptance_criteria` (how it is verified); you cannot attach the right per-task context without having made those cuts. So Magellan owns both: brief in → decomposed, context-compiled task DAG out. This is grounded in the existing contracts — Guild's brief is approach-level, Forge's executor input is a decomposed DAG, so the approach→DAG step has exactly one home.
- **Output contract: a superset of Forge's `tasks.json`.** Forge validates `{feature, stack, tasks:[{id, title, files[], dependencies[], acceptance_criteria[]}]}`, which already holds the accuracy levers — `dependencies` is the Consumes/Produces DAG, `acceptance_criteria` is per-task verification. Magellan adds one field per task: `context: { decisions:[…], refs:[…], interfaces:{consumes, produces} }`. Forge reads the core fields it validates and ignores the rest; Claude Code and cloud agents read the `context` bundle. Executor-agnostic means a portable task-DAG whose core is Forge-valid and whose enrichment any executor can consume. Magellan does not invent a format — it extends the one Forge already validates.
- **Accuracy-first, cost-minimized where it does not cost accuracy.** When including context and saving cost conflict on a task, include it. Accuracy wins ties; cost is optimized only in the clear cases (a task that demonstrably does not touch a decision does not carry it). The dangerous failure mode is *under*-compiling — an executor guessing because Magellan trimmed too hard — so Magellan trims conservatively and the budget is tightened empirically by dogfooding, never by starving tasks up front.
- **Structural correctness only — no overclaim.** Magellan's contribution to correctness is structural: unambiguous interfaces, an acceptance/TDD step per task, no placeholders, and right-sized context per task, so an executor cannot drift or improvise. It does NOT guarantee bug-free or regression-free execution. Regression *catching* stays with Canary; precedent *compliance* stays with Bastion. This is the same discipline applied to Provenance's objective gate: contribute by construction, defer enforcement to the gates.
- **Optional stage.** Four tools back-to-back is real ceremony. Magellan is opt-in when heading into automated or local execution; a quick manual change compiles nothing.
- **Name.** Magellan — it charts the execution route; a compiled plan is a navigated path.

## Outcome

Magellan is committed as a new Tolvi tool: the executor-agnostic plan compiler that inherits Guild's former plan-authoring, decomposes an approved brief into a context-compiled task DAG (a Forge-`tasks.json` superset with a per-task `context` field), optimizes accuracy-first with cost minimized only where it does not cost accuracy, and defers correctness enforcement to Bastion and Canary. The core build loop becomes **Vault → Guild (comprehension) → Bastion (harden approach) → Magellan (compile plan) → Forge (execute)**, with Provenance (record-gate at push) and Canary (test-gate in CI) as the downstream gates; Bastion moves one slot earlier to harden the brief so Magellan compiles once, last. Pre-build: this repo is scaffolded (vault + PLAN + README) and the build follows the evidence-first path (kickoff → Bastion → code) like its siblings. The Guild `SKILL.md` and the marketing-site stack (`Vault → Guild → Bastion → Forge`, [[2026-07-21-guild-relaunch-and-unified-stack]]) still predate Magellan and need reconciliation.
