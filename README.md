# Magellan

**The executor-agnostic execution-optimized plan compiler.** Magellan takes an approved approach and compiles it into a decomposed, context-compiled task graph that Forge, Claude Code, or a cloud agent can each execute — every task carrying exactly the vault decisions, code refs, interfaces, and verification it needs, and nothing more.

> **Status: pre-build.** The direction is committed in [`vault/decisions/`](vault/decisions/) and [`docs/PLAN.md`](docs/PLAN.md). No code yet.

It is the compile layer of the Tolvi stack:

```
Vault → Guild (comprehension) → Bastion (harden) → Magellan (compile) → Forge / Claude Code / cloud (execute)
```

## What it will do

Magellan receives the engineer-approved brief from Guild — the decided approach and scope — and compiles it into an executable plan. It decomposes the approach into a task DAG and, in the same pass, compiles each task's context: the governing vault decisions, the specific code refs, the interface it consumes and produces, and the test that proves it. The engineer owns the *how*; Magellan owns the *cut into tasks* and the *context per cut*.

Its output is a superset of Forge's `tasks.json` — the same task DAG (`id`, `title`, `files`, `dependencies`, `acceptance_criteria`) plus one field per task, `context: { decisions, refs, interfaces }`. Forge reads the core fields it validates; Claude Code and cloud agents read the `context` bundle and execute with exactly-enough context. That is what executor-agnostic means here: a portable task-DAG whose core is Forge-valid and whose enrichment any executor can consume.

## Design principles

- **Per-task context compilation is the point.** Attaching each task exactly its context — no more, no less — is the accuracy↔cost resolver, and the reason Magellan is a Tolvi tool and not generic plan-writing.
- **Accuracy first, cost minimized only where it does not cost accuracy.** When including context and saving cost conflict, include it. The expensive failure is *under*-compiling — an executor guessing — so trim conservatively and tighten the budget by dogfooding.
- **Structural correctness only.** Magellan maximizes an executor's odds by construction (clear interfaces, a test per task, no placeholders, right-sized context). It does not guarantee bug-free execution — regression catching is [Canary](https://github.com/tolvi-labs/canary), precedent compliance is [Bastion](https://github.com/tolvi-labs/bastion).
- **Optional stage.** Opt in when heading into automated or local execution; a quick manual change compiles nothing.

The full rationale is in [`docs/PLAN.md`](docs/PLAN.md) and the decisions behind it live in [`vault/decisions/`](vault/decisions/).

## License

Apache 2.0, in line with the rest of the Tolvi suite.
