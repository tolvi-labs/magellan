# Contributing to Magellan

Magellan is an executor-agnostic plan compiler, shipped as a Claude Code skill: it compiles an approved, Bastion-hardened brief into a task graph that Forge, Claude Code or a cloud agent can execute. Contributions welcome, with one rule that's different here.

## The rule that's different: change the tool, record the why

This project keeps its decision record in the open, in [`vault/`](vault/), and **a change to how Magellan behaves must come with the reasoning.** If your PR changes Magellan's behavior (decomposition, per-task context compilation, the task graph format), include a vault decision that captures *why*:

```shell
tolvi sync decision "Short imperative title"   # writes vault/decisions/YYYY-MM-DD-<slug>.md
```

Commit it alongside your code. PRs that change behavior without a decision will be asked to add one.

## What belongs in the public vault

Engineering decisions only: the *why* of the code. **Never** put client or project names, ticket keys, business strategy, competitive analysis, revenue, PII, or security-incident specifics in this repo; those belong in a private vault. Use placeholders like `PROJ-142` for tickets.

## Local setup

```shell
git clone https://github.com/tolvi-labs/magellan
cd magellan
./install.sh          # symlinks skills/tolvi-magellan into ~/.claude/skills/tolvi-magellan
python3 tests/forge_compat_check.py
```

## Standards

- Magellan never chooses the approach and never executes. Both boundaries are the product.
- Executor-agnostic means exactly that: anything Forge-specific belongs behind the compatibility check, not in the format.
- Re-run `tests/forge_compat_check.py` before any change to the output.

## Code of conduct

By participating, you agree to abide by the [Code of Conduct](./CODE_OF_CONDUCT.md).

## Reporting security issues

See [`SECURITY.md`](./SECURITY.md). Do not file public issues for security vulnerabilities.
