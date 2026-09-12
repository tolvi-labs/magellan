# Magellan

**The executor-agnostic execution-optimized plan compiler.** Magellan takes an approved, Bastion-hardened brief and compiles it into a decomposed, context-compiled task DAG that Forge, Claude Code, or a cloud agent can each execute, every task carrying exactly the vault decisions, code refs, and interfaces it needs, and nothing more.

It is the compile layer of the Tolvi stack:

```
Vault → Guild (comprehension) → Bastion (harden) → Magellan (compile) → Forge / Claude Code / cloud (execute)
```

## Install

```shell
git clone https://github.com/tolvi-labs/magellan
cd magellan
./install.sh          # symlinks skills/tolvi-magellan into ~/.claude/skills/tolvi-magellan
```

Invoke `/tolvi-magellan <bastion-hardened brief>` in Claude Code. Use `--copy` for a frozen snapshot, or `--uninstall` to remove. Magellan reads the repo's `vault/` (run `tolvi init` if you don't have one); set `ANTHROPIC_API_KEY` to enable ranked retrieval via `tolvi ask`.

## What it does

Magellan receives Bastion's hardened brief and compiles it into an executable plan. It decomposes the approach into a task DAG and, in the same pass, compiles each task's context: the governing vault decisions, the specific code refs, the interface it consumes and produces, and the test that proves it. The engineer owns the *how*; Magellan owns the *cut into tasks* and the *context per cut*.

Its output is a superset of Forge's `tasks.json`: the same task DAG (`id`, `title`, `files`, `dependencies`, `acceptance_criteria`) plus one field per task, `context: { decisions, refs, interfaces }`. Forge reads the core fields it validates; Claude Code and cloud agents read the `context` bundle and execute with exactly-enough context.

## Core loop

```
/tolvi-magellan <brief>
  ├─ 1. Ingest       → parse Bastion's structured JSON brief (or restate free text and confirm)
  ├─ 2. Decompose     → cut into a task DAG; self-check acyclic/provable/scoped
  ├─    [DAG gate]    → the engineer approves the cuts before context is compiled
  ├─ 3. Compile       → per task: active decisions, code refs, interfaces — accuracy wins ties
  └─ 4. Emit & route  → write tasks.json, hand off to Forge / Claude Code / a cloud agent, and stop
```

**One caveat that matters:** if Forge is the executor, `forge plan load` re-serializes its own internal snapshot using only the 5 fields it has always validated: `context` never reaches `forge plan next/status/complete`. Claude Code and cloud-agent executors read Magellan's output file directly and don't hit this limitation.

## Design principles

- **Per-task context compilation is the point.** Attaching each task exactly its context, no more and no less, is the accuracy↔cost resolver, and the reason Magellan is a Tolvi tool and not generic plan-writing.
- **Accuracy first, cost minimized only where it does not cost accuracy.** The expensive failure is *under*-compiling (an executor guessing), so context is trimmed conservatively.
- **Structural correctness only.** Magellan maximizes an executor's odds by construction (clear interfaces, a test per task, no placeholders, right-sized context). It does not guarantee bug-free execution. Regression catching is [Canary](https://github.com/tolvi-labs/canary), precedent compliance is [Bastion](https://github.com/tolvi-labs/bastion).
- **Optional stage.** Opt in when heading into automated or local execution; a quick manual change compiles nothing.

The full rationale is in [`docs/PLAN.md`](docs/PLAN.md) and the decisions behind it live in [`vault/decisions/`](vault/decisions/).

## License

Apache 2.0, in line with the rest of the Tolvi suite.
