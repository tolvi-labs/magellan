# AGENTS.md

Guidance for coding agents working in this repo.

## What this is

Magellan is an executor-agnostic plan compiler, shipped as a Claude Code skill. It takes an approved, Bastion-hardened brief and compiles it into a decomposed task DAG, every task carrying exactly the vault decisions, code refs and interfaces it needs and nothing more.

## Layout

- `skills/tolvi-magellan/` is the skill.
- `tests/forge_compat_check.py` verifies the emitted DAG is consumable by Forge.
- `.claude-plugin/plugin.json` is the manifest.

## Build and test

```bash
python3 tests/forge_compat_check.py
```

## Conventions

- **It never chooses the approach and never executes.** Input is an already-approved brief; output is a task graph. Both boundaries are the product.
- **Executor-agnostic means exactly that.** The DAG must be consumable by Forge, Claude Code or a cloud agent. Anything Forge-specific belongs behind the compatibility check, not in the format.
- **Context is compiled per task.** A task carrying the whole vault has failed at its one job.

## What not to do

- Do not let output drift from what Forge can execute without re-running `tests/forge_compat_check.py`.
